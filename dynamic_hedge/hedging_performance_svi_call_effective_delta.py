import Utilities.hedging_utility as hedge_util
from Utilities.utilities import *
import Utilities.svi_prepare_vol_data as svi_data
import Utilities.svi_calibration_utility as svi_util
import Utilities.hedging_performance_utility as hp_util
import QuantLib as ql
import pandas as pd
import math
import numpy as np
import datetime
import timeit
import os
import pickle


start = timeit.default_timer()

calendar = ql.China()
daycounter = ql.ActualActual()

with open(os.path.abspath('..') +'/intermediate_data/hedging_daily_params_calls.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..') +'/intermediate_data/hedging_dates_calls.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..') +'/intermediate_data/hedging_daily_svi_dataset_calls.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]

# Hedge option using underlying 50ETF
daily_hedge_errors = {}
daily_pct_hedge_errors = {}
option_last_close_Ms = {}

for idx_date,date in enumerate(dates[0:len(dates)-8]):
    try:
        print(idx_date)
        calibrate_date = to_ql_date(dates[idx_date])
        hedge_date = to_ql_date(dates[idx_date+1])
        liquidition_date = to_ql_date(dates[idx_date+2])

        # Liquidition Date Dataset
        dataset_on_liquidition_date = daily_svi_dataset.get(to_dt_date(liquidition_date))
        cal_vols, put_vols, maturity_dates, spot, rf_pcprs = dataset_on_liquidition_date

        # SELECT CALL OPTION DATA!!
        expiration_dates = to_ql_dates(maturity_dates)
        orgnized_data_liquidition_date = svi_util.orgnize_data_for_hedging(
            liquidition_date , daycounter, cal_vols, expiration_dates, spot)
        optiontype = ql.Option.Call

        # Hedge Date Data Set
        dataset_on_hedge_date = daily_svi_dataset.get(to_dt_date(hedge_date))
        cal_vols_h, put_vols_h, maturity_dates_h, spot_on_hedge_date, pcprs_on_hedge_date = dataset_on_hedge_date
        expiration_dates_h = to_ql_dates(maturity_dates_h)
        orgnized_data_hedge_date = svi_util.orgnize_data_for_hedging(
            hedge_date, daycounter, cal_vols_h, expiration_dates_h, spot_on_hedge_date)

        calibrated_params = daily_params.get(to_dt_date(calibrate_date)) # on calibrate_date
        curve_on_hedge_date = svi_data.get_curve_treasury_bond(hedge_date,daycounter)

        # Local Vol Surface
        cal_vols_c, put_vols_c, maturity_dates_c, spot_c, rf_c  = daily_svi_dataset.get(to_dt_date(calibrate_date))

        black_var_surface = hedge_util.get_local_volatility_surface(calibrated_params,to_ql_dates(maturity_dates_c),calibrate_date,daycounter,calendar,spot_c,rf_c)

        hedge_error_Ms = {}
        hedge_error_pct_Ms = {}
        for nbr_month in range(4):
            params_Mi = calibrated_params[nbr_month]
            rf_on_hedge_date = pcprs_on_hedge_date.get(nbr_month)
            moneyness_l, strikes_l, close_prices_l, expiration_date_l = orgnized_data_liquidition_date.get(nbr_month)
            moneyness_h, strikes_h, close_prices_h, expiration_date_h = orgnized_data_hedge_date.get(nbr_month)
            rf = curve_on_hedge_date.zeroRate(liquidition_date, daycounter, ql.Continuous).rate()
            hedge_errors = []
            hedge_errors_pct = []
            moneyness = []
            print('liquidition date : ', liquidition_date, ',', nbr_month)
            for idx_k,k in enumerate(strikes_h):
                if k in close_prices_l.keys():
                    close_l = close_prices_l.get(k)
                else:
                    print('strike not found in L date')
                    continue
                close_h = close_prices_h.get(k)
                # No arbitrage condition
                ttm = daycounter.yearFraction(hedge_date,expiration_date_h)
                if close_h < spot_on_hedge_date - k*math.exp(-rf_on_hedge_date*ttm):
                    continue
                delta = hedge_util.calculate_effective_delta_svi(hedge_date,daycounter,calendar,params_Mi,spot,rf,k,expiration_date_h,optiontype)
                if math.isnan(delta): continue
                print('delta : ',delta)
                cash_on_hedge_date = hedge_util.calculate_cash_position(hedge_date, close_h, spot_on_hedge_date, delta)
                hedge_error = hedge_util.calculate_hedging_error(hedge_date,liquidition_date,
                                                      daycounter,spot,close_l,delta,cash_on_hedge_date,rf)
                if close_h == 0 : continue
                hedge_error_pct = hedge_error/close_h
                hedge_error = round(hedge_error,4)
                hedge_error_pct = round(hedge_error_pct, 4)
                hedge_errors.append(hedge_error)
                hedge_errors_pct.append(hedge_error_pct)
                moneyness.append(round(spot_on_hedge_date/k,4))
            print('moneyness : ',moneyness)
            print('hedge errors pct : ', hedge_errors_pct)
            hedge_error_Ms.update({nbr_month:[moneyness,hedge_errors]})
            hedge_error_pct_Ms.update({nbr_month:[moneyness,hedge_errors_pct]})
        if idx_date != 0:
            #print('liquidition date : ',liquidition_date)
            #print('hedge errors pct : ',hedge_error_pct_Ms)
            key_date1 = datetime.date(liquidition_date.year(),liquidition_date.month(),liquidition_date.dayOfMonth())
            daily_hedge_errors.update({key_date1: hedge_error_Ms})
            daily_pct_hedge_errors.update({key_date1: hedge_error_pct_Ms})
    except Exception as e:
        print(e)
        continue

stop = timeit.default_timer()
print('calibration time : ',stop-start)

print('daily_hedge_errors = ',daily_hedge_errors)
print('daily_pct_hedge_errors = ',daily_pct_hedge_errors)
with open(os.path.abspath('..') +'/intermediate_data/hedging_daily_hedge_errors_svi_call.pickle','wb') as f:
    pickle.dump([daily_hedge_errors,daily_pct_hedge_errors],f)



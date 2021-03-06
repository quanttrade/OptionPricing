import QuantLib as ql
import pandas as pd
import os
from Utilities.svi_read_data import get_wind_data
import data_access.wind_data as wd
from WindPy import w
from datetime import date,datetime
import pickle
w.start()

evalDate = ql.Date(1, 7, 2017)
endDate = ql.Date(20, 10, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()

data = w.wsd("SR801.CZC", "close", "2017-05-27", "2017-09-27", "")
print(data.Times)
print(data.Data)
df = pd.DataFrame(data=data.Data[0], index=data.Times)
df.to_json(os.path.abspath('..') + '\marketdata\spotclose_sr' + '.json')

underlyingdata = pd.read_json(os.path.abspath('..') +'\marketdata\spotclose_sr' + '.json')

spot_ts = underlyingdata.values.tolist()
dates_ts = underlyingdata.index.tolist()

underlyings = {}
for i,d in enumerate(dates_ts):
    dt = date(d.year,d.month,d.day)
    spot = spot_ts[i][0]
    underlyings.update({dt:spot})
with open(os.path.abspath('..')+'/intermediate_data/spotclose_sr.pickle','wb') as f:
    pickle.dump([underlyings],f)




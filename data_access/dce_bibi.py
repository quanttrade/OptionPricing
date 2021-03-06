#!/usr/bin/env python
# encoding: utf-8
from bs4 import BeautifulSoup
import requests
import random
import re
import os
import time
import pickle
import string


def randheader():  # 随机生成User-Agent

    head_user_agent = ['Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
                       'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0;'
                       ' SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; '
                       'Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0;'
                       ' SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; '
                       'Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219'
                       ' Firefox/2.0.0.12 Navigator/9.0.0.6',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/28.0.1500.95 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729;'
                       ' .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000'
                       ' Chrome/26.0.1410.43 Safari/537.1 ',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92'
                       ' Safari/537.1 LBBROWSER',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75'
                       ' Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 '
                       'TaoBrowser/3.0 Safari/536.11',
                       'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
                       'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0']
    return {'Host': 'www.dce.com.cn',
            'Connection': 'keep - alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept - Language': 'zh - CN, zh;q = 0.8',
            'User-Agent': head_user_agent[random.randrange(0, len(head_user_agent))]}


def to_int(number):
    try:
        if number[:1] != '-':
            sign = 1
        else:
            sign = -1
            number = number[1:]
        l = len(number)
        a, b, to, c = l // 4, l % 4, 0, 0
        while a >= 0:
            to += 10 ** (3 * a) * int(number[max(0, b + c * 4 - 3):b + c * 4])
            a -= 1
            c += 1
        return to * sign
    except ValueError:
        return None


def geturl(url, header, tries_num=20, sleep_time=0.1, time_out=10, max_retry=20):
    sleep_time_p = sleep_time
    time_out_p = time_out
    tries_num_p = tries_num
    try:
        res = requests.get(url, headers=header, timeout=time_out)
        res.raise_for_status()
    except requests.RequestException as e:
        sleep_time_p += 5
        time_out_p += 5
        tries_num_p += - 1
        if tries_num_p > 0:
            time.sleep(sleep_time_p)
            print(url, 'URL Connection Error: 第', max_retry - tries_num_p, u'次 Retry Connection', e)
        res = geturl(url, header, tries_num_p, sleep_time_p, time_out_p, max_retry)
    return res


def spider(codename, firstdate):
    pos_condition = pd.DataFrame()
    date_range = w.tdays(firstdate, "2017-08-28", "").Data[0]
    for i in range(len(date_range)):
        time.sleep(3)
        date = date_range[i]
        year, month, day = date.year, date.month, date.day
        url = 'http://www.dce.com.cn/publicweb/quotesdata/memberDealPosiQuotes.html?memberDealPosiQuotes.variety=' \
              + codename + '&memberDealPosiQuotes.trade_type=0&year=' + str(year) + '&month=' + str(
            month - 1) + '&day=' + str(day) \
              + '&contract.contract_id=all&contract.variety_id=' + codename
        result = geturl(url, header=randheader())
        soup = BeautifulSoup(result.text, 'html.parser')
        content_list = pd.Series(soup.find_all(re.compile("td"))[14:-12])
        if len(content_list) == 0:
            pass
        else:
            content = soup.find_all(re.compile("span"))
            data = pd.DataFrame()
            content_list = content_list.apply(lambda x: x.string)
            data['会员简称1'] = content_list[content_list.index % 12 == 1].tolist()
            data['成交量'] = content_list[content_list.index % 12 == 2].apply(to_int).tolist()
            data['增减1'] = content_list[content_list.index % 12 == 3].apply(to_int).tolist()
            data['会员简称2'] = content_list[content_list.index % 12 == 5].tolist()
            data['持买单量'] = content_list[content_list.index % 12 == 6].apply(to_int).tolist()
            data['增减2'] = content_list[content_list.index % 12 == 7].apply(to_int).tolist()
            data['会员简称3'] = content_list[content_list.index % 12 == 9].tolist()
            data['持卖单量'] = content_list[content_list.index % 12 == 10].apply(to_int).tolist()
            data['增减3'] = content_list[content_list.index % 12 == 11].apply(to_int).tolist()
            data['代码'] = content[0].string[67:75].strip()
            data['日期'] = content[0].string[-8:]
            data.to_json('DCE\\' + codename + content[0].string[-8:] + '.json')
            # with open(, 'wb') as f:
            #   pickle.dump([data], f, pickle.HIGHEST_PROTOCOL)


def get_data():
    # fd = {'i': '2013/10/18', 'jm': '2013/03/22', 'j': '2011/04/15'}
    fd = {'l': '2010/01/01', 'fb': '2013/12/06', 'cs': '2014/12/19', 'p': '2010/01/01'}

    # fd = {'v': '2009/05/25', 'b': '2004/12/22', 'm': '	2000/07/17', 'a': '1999/01/04', 'y': '2006/01/09',
    #       'jd': '2013/11/08', 'bb': '2013/12/06', 'jm': '2013/03/22', 'j': '2011/04/15', 'pp': '2014/02/28',
    #       'l': '2007/07/31', 'i': '2013/10/18', 'fb': '2013/12/06', 'c': '2004/09/22', 'cs': '2014/12/19',
    #       'p': '2007/10/29'}
    try:
        os.mkdir('dce')
    except FileExistsError:
        pass
    for code in fd.keys():
        print("正在爬取 " + code + ' 成交持仓数据……')
        spider(code, fd[code])


# url = "http://www.dce.com.cn/publicweb/quotesdata/dayQuotesCh.html?dayQuotes.variety=all&dayQuotes.trade_type=0&year=2017&month=7&day=31"
url = "http://www.dce.com.cn/publicweb/quotesdata/exportDayQuotesChData.html?dayQuotes.variety=all&dayQuotes.trade_type=0&year=2017&month=7&day=31"
result = geturl(url, header=randheader())
print(result.text)
rows = result.text.split('\n')
# columsOfRow1 = rows[1].split('\t\t')
# print(columsOfRow1)
# print(url)
# # soap = BeautifulSoup(result.text, 'html.parser')
# # tag = soap.find_all(re.compile('tr'))[1]
# item = []
# origin = []
# for child in tag.children:
#     origin.append(child.string)
#     item.append(bytearray(child.string.encode('utf-8')).translate(None, string.whitespace))
# print(item)
# for i in item:
#     print(i.decode('utf-8'))

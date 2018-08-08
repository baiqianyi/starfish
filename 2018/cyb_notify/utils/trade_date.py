import datetime
import tushare as ts

def get_trade_date(back=4,back_start=0):
    date = (datetime.datetime.now()-datetime.timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S")[:10]
    df = ts.get_k_data('399300', index=True,start=date)
    # print (df)
    if back_start == 0:
        date_list = list(df.loc[:,"date"][-back:])
    else:
        date_list = list(df.loc[:, "date"][-back:-1*back_start])
    re_list = []
    for d in date_list:
        re_list.append(datetime.datetime(year=int(d[:4]),month=int(d[5:7]),day=int(d[8:10]),hour=9,minute=30,second=0))
    return re_list


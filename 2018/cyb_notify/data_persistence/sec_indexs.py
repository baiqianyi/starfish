import os
import tushare as ts
print(os.getcwd())
os.chdir('C:\\Users\\baiqy\\Desktop\\tmp\\starfish\\2018\\cyb_notify')
print(os.getcwd())
import requests
import datetime
import pymysql
import time

class IndustryData:
    def __init__(self):
        self.industry_page = r'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._BKHY&sty=FPGBKI&sortType=(ChangePercent)&sortRule=-1&page=1&pageSize=100&js=var%20XWZSgeRR={rank:[(x)],pages:(pc),total:(tot)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.628606915911589&_=' + str(int(datetime.datetime.now().timestamp() * 1000))
        self.stock_page = lambda code:"http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C."+code+"1&sty=FCOIATA&sortType=(ChangePercent)&sortRule=-1&page=1&pageSize=20&js=var%20lpNTNepq={rank:[(x)],pages:(pc),total:(tot)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.628606915911589&_=" + str(int(datetime.datetime.now().timestamp() * 1000))
        self.industrys_data = None
        self.history = {}
        self.min_time_range = 60
        self.time_delta = 20
        self.DATA_RAIL_GRAIN = datetime.timedelta(seconds=self.time_delta)
        self.time_rail = self.generate_rail_grain(datetime.datetime.now())
        self.dt = datetime.datetime.now()
        self.i = 0
        self.min_list = {}
        self.cursor = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='1111', db='dfcf_industrys')
        self.cyb_cursor = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='1111', db='follow_cyb')

    def industrys(self):
        dataList = []
        html = self.downLoad(self.industry_page)
        html = html.split("\",\"")
        for h in html:
            h = h.split(",")
            if len(h) > 11:
                industry_code = h[1]
                # min_range = self.min_list.get(industry_code)
                # if isinstance(min_range,float) or isinstance(min_range,int):
                #     industry_up = float(h[3])-min_range
                # else:
                industry_up = float(h[3])
                top_stock = h[7]
                top_up = float(h[11])
                dataList.append((industry_code,industry_up,top_stock,top_up))
            else:
                dataList.append((None, -1,None, -1))
        self.industrys_data = dataList
        # self.stock_as_history()
        return dataList

    def industry_stock(self,i_code):
        datalist = []
        html = self.downLoad(self.stock_page(i_code[0]))
        html = html.split("\",\"")
        for h in html:
            h = h.split(",")
            code = h[1]
            if h[5][-1] == "%":
                up = float(h[5][0:len(h[5])-1])
            else:
                up = None
            datalist.append((code,up))
        return datalist

    def stock_as_history(self):
        amBegin = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=9, minute=30, second=30))
        amEnd = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=11, minute=30, second=0))
        pmBegin = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=13, minute=0, second=0))
        pmEnd = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=15, minute=0, second=0))

        while True:
            time.sleep(0.5)
            try:
                now = datetime.datetime.now()
                if not (now.date().isoweekday() == 6 or now.date().isoweekday() == 7):
                    if (amBegin < now and now < amEnd) or (pmBegin < now and now < pmEnd):
                        if  self.i >= len(self.time_rail):
                            break
                        self.dt = self.time_rail[self.i]
                        if self.dt <= now:
                            self.industrys()
                            self.i = self.i + 1
                            print([self.dt, self.i])
                            for data in self.industrys_data:
                                self.to_mysql([self.dt, data[1],data[2], data[3]],data[0])
                            # break
                            #cyb data
                            # cyb = ts.get_realtime_quotes('159915')  # Single stock symbol
                            # up = (float(cyb.loc[0, 'price']) / float(cyb.loc[0, 'pre_close']) - 1) * 100
                            up = self.cyb_real()
                            self.to_mysql_cyb((self.dt, up),"sec_cyb")
                            # sz50 = ts.get_realtime_quotes("510050")
                            # up = (float(sz50.loc[0, 'price']) / float(sz50.loc[0, 'pre_close']) - 1) * 100
                            up = self.sz50_real()
                            self.to_mysql_cyb((self.dt, up), "sec_sz50")
                            sz50 = ts.get_realtime_quotes("510500")
                            up = (float(sz50.loc[0, 'price']) / float(sz50.loc[0, 'pre_close']) - 1) * 100
                            self.to_mysql_cyb((self.dt, up), "sec_zz500")
                        else:
                            print(" continue 1")
                            time.sleep(2)
                            continue
                    elif now > pmEnd:
                        break
                    else:
                        print(" continue 2")
                        time.sleep(2)
                        continue
                else:
                    break
            except Exception as e:
                print(e)
    # def stock_as_csv(self,data,code):
    #     with open('resource\\yestoday_' + code + '.csv',"a", newline = "") as csvfile:
    #         spamwriter = csv.writer(csvfile)
    #         spamwriter.writerow(data)
    #
    # def read_csv(self,code,length = 181):
    #     if os.path.exists('resource\\yestoday_' + code + '.csv') :
    #         with open('resource\\yestoday_' + code + '.csv', "r", encoding="utf-8") as f:
    #             read = list(csv.reader(f))
    #             leng = len(read)
    #             rows = []
    #             if leng > length:
    #                 for row in read[-leng:]:
    #                     rows.append(float(row[2])-float(read[-length][2]))
    #             elif leng > 0:
    #                 for row in read:
    #                     rows.append(float(row[2]) - float(read[-leng][2]))
    #             else:
    #                 rows = []
    #     else:
    #         rows = []
    #     return rows

    def generate_rail_grain(self, date):
        pmBegin = datetime.datetime.combine(date.date(), datetime.time(hour=9, minute=20, second=0))
        pmEnd = datetime.datetime.combine(date.date(), datetime.time(hour=11, minute=30, second=0))
        amBegin = datetime.datetime.combine(date.date(), datetime.time(hour=13, minute=0, second=0))
        amEnd = datetime.datetime.combine(date.date(), datetime.time(hour=15, minute=20, second=0))
        tmpTime = pmBegin
        todayRange = []
        while True:
            todayRange.append(tmpTime)
            if (amBegin <= tmpTime and amEnd > tmpTime) or (pmBegin <= tmpTime and pmEnd > tmpTime):
                tmpTime = tmpTime + self.DATA_RAIL_GRAIN
            elif pmEnd <= tmpTime and amBegin > tmpTime:
                tmpTime = amBegin
            else:
                break
        return todayRange

    def to_mysql(self,data=(), table=""):
        print(data,"----",table)
        try:
            self.cursor.cursor().execute("create table if not exists " + table +
                                         " (datetime datetime,industry_up float(16),top_stock char(6),top_stock_up float(16),PRIMARY KEY(datetime));")
            sql = "replace into " + table + \
                  " (datetime, industry_up, top_stock, top_stock_up) VALUES (%s,%s, %s, %s)"
            self.cursor.cursor().execute(sql, data)
            self.cursor.commit()
        except Exception as e:
            # 发生错误时回滚
            print(e)
            self.cursor.rollback()

    def to_mysql_cyb(self,data=(),table=""):
        try:
            # self.cyb_cursor.cursor().execute("create table if not exists " + table +
                                         # " (datetime datetime,industry_up float(16),PRIMARY KEY(datetime));")
            sql = "replace into " + table + " (datetime, up) VALUES (%s,%s);"
            self.cyb_cursor.cursor().execute(sql, data)
            self.cyb_cursor.commit()
        except Exception as e:
            # 发生错误时回滚
            print(e)
            self.cyb_cursor.rollback()

    def real_data(self,code='sh510050'):
        url = 'https://hq.sinajs.cn/?_=0.16804779545995818&list=' + code
        t = self.downLoad(url).split(",")
        yes_final = float(t[2])
        now = float(t[3])
        return (now/yes_final - 1)*100

    def cyb_real(self):
        # ''etf
        cyb = ts.get_realtime_quotes('cyb')  # Single stock symbol
        time.sleep(0.4)
        return (float(cyb.loc[0, 'price']) / float(cyb.loc[0, 'pre_close']) - 1)*100

    def sz50_real(self):
        sz50 = ts.get_realtime_quotes('sz50')  # Single stock symbol
        time.sleep(0.4)
        return (float(sz50.loc[0, 'price']) / float(sz50.loc[0, 'pre_close']) - 1)*100


    def downLoad(self,url):
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Cache-Control': 'max-age=0',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
        }
        s = requests.session()
        s.headers.update(headers)
        r = s.get(url=url,  timeout=10)  # 带参数的GET请求;;;params={'wd': 'python'},
        import time
        time.sleep(1)
        return r.text

if __name__ == "__main__":
    industry = IndustryData()
    industry.stock_as_history()



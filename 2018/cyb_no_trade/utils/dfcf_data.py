import requests
import datetime
import csv
import os
import tushare as ts
import time
import os
os.chdir('C:\\Users\\baiqy\\Desktop\\quant\\cyb_no_trade')
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
        self.dt = None
        self.i = 0
        self.min_list = {}
        self.min_fix = 0.1
        self.six_industry = 0
        self.down_six_industry = 0
        self.dataList = ()
        self.weights = self.weight_six_industry_init()


    def industrys(self):
        self.industrys_data = []
        dataList = []
        industry_list = []
        html = downLoad(self.industry_page)
        html = html.split("\",\"1")
        for h in html:
            h = h.split(",")
            industry_code = h[1]
            # 去掉工艺商品
            if industry_code == "BK0440":
                continue
            min_range = self.min_list.get(industry_code)
            if isinstance(min_range,float) or isinstance(min_range,int):
                industry_up = float(h[3])-min_range #+ self.min_fix
            else:
                # self.min_list[industry_code] = 0.0
                industry_up = float(h[3])
            industry_list.append(float(h[3]))
            top_stock = h[7]
            top_up = float(h[11])
            dataList.append((industry_code,industry_up,top_stock,float(top_up)))
            # self.industrys_data.append((industry_code,float(h[3]),top_stock,float(top_up)))
        dataList = sorted(dataList, key=lambda dataList: dataList[1], reverse=True)
        self.dataList = dataList
        industry_list = sorted(industry_list, key=lambda x: x, reverse=True)
        self.six_industry = industry_list[5]
        self.down_six_industry = industry_list[-6]
        self.stock_as_history()
        return dataList

    def stock_as_history(self):
        while True:
            if  self.i >= len(self.time_rail):
                break
            self.dt = self.time_rail[self.i]
            now = datetime.datetime.now()
            if self.dt <= now:
                self.i = self.i + 1
                for data in self.industrys_data:
                    if self.history.get(data[0]) != None and len(self.history.get(data[0])) > 60//self.time_delta*self.min_time_range+1:
                        self.history[data[0]].append(data[1])
                        self.min_list[data[0]] = min(self.history.get(data[0])[-60//self.time_delta*self.min_time_range:])
                        # self.min_list[data[0]] = self.history.get(data[0])[-60//self.time_delta*self.min_time_range]
                    elif self.history.get(data[0]) == None :
                        self.history[data[0]] = [0.0]
                        self.min_list[data[0]] = 0.0
                    else:
                         self.history[data[0]].append(data[1])
                         # self.min_list[data[0]] = 0.0
                         self.min_list[data[0]] = min(self.history.get(data[0]))
                break
            else:
                break

    def weight_six_industry(self):
        import utils.weight_point as wp
        return wp.weight_point(self.dataList,self.weights)

    def weight_six_industry_init(self):
        weights = {}
        with open('config\\industry_weights-2018-7-21.info', 'r') as f:
            for line in f.readlines():
                weights[str(line.strip()).split("\t")[1]] = int(line.strip().split("\t")[2])
        return  weights

    def getIndustrySix(self):
        return self.six_industry

    def getDownIndustrySix(self):
        return self.down_six_industry

    def stock_as_csv(self,data,code):
        with open('resource\\yestoday_' + code + '.csv',"a", newline = "") as csvfile:
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow(data)

    def read_csv(self,code,length = 181):
        if os.path.exists('resource\\yestoday_' + code + '.csv') :
            with open('resource\\yestoday_' + code + '.csv', "r", encoding="utf-8") as f:
                read = list(csv.reader(f))
                leng = len(read)
                rows = []
                if leng > length:
                    for row in read[-leng:]:
                        rows.append(float(row[1])-float(read[-length][1]))
                elif leng > 0:
                    for row in read:
                        rows.append(float(row[1]) - float(read[-leng][1]))
                else:
                    rows = []
        else:
            rows = []
        return rows

    def generate_rail_grain(self, date):
        pmBegin = datetime.datetime.combine(date.date(), datetime.time(hour=9, minute=30, second=0))
        pmEnd = datetime.datetime.combine(date.date(), datetime.time(hour=11, minute=30, second=0))
        amBegin = datetime.datetime.combine(date.date(), datetime.time(hour=13, minute=0, second=0))
        amEnd = datetime.datetime.combine(date.date(), datetime.time(hour=15, minute=0, second=0))
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

def downLoad(url):
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Cache-Control': 'max-age=0',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
    }
    s = requests.session()
    s.headers.update(headers)
    r = s.get(url=url, params={'wd': 'python'}, timeout=10)  # 带参数的GET请求
    import time
    time.sleep(1)
    return r.text

if __name__ == "__main__":
    industry = IndustryData()
    print(industry.industrys())
    print(industry.weight_six_industry())

    print(industry.industrys())
    print(industry.industrys())





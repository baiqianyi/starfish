import requests
import re
import time
import datetime
import pymysql

class Data:
    def __init__(self):
        self.industry_sec_data = []
        self.INDUSTRY_NUM = 66
        self.DATA_RAIL_GRAIN = datetime.timedelta(seconds=10)
        self.thsConfigList = [
            "http://q.10jqka.com.cn/thshy/index/field/199112/order/desc/page/1/ajax/1/",
            "http://q.10jqka.com.cn/thshy/index/field/199112/order/desc/page/2/ajax/1/"
        ]
        self.cursor = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='1111', db='sec_industrys')
        self.dt = None
        self.time_rail = None
    #初始化，创建表
    def init(self):
        self.time_rail = self.generate_rail_grain(datetime.datetime.now())
        for i in range(self.INDUSTRY_NUM):
            self.cursor.cursor().execute("create table if not exists industry_"+ str(i+1) +
                " (datetime datetime,code char(16),price float(16),top_stock float(16),top_stock_price float(16),"
                "upRDown float(16),clearRAll float(16),PRIMARY KEY(datetime));")

#爬取数据
    def sec_industry_data(self):
        # 同挂顺行业 http://q.10jqka.com.cn/thshy/
        # "http://q.10jqka.com.cn/thshy/index/field/199112/order/desc/page/1/ajax/1/"
        # "http://q.10jqka.com.cn/thshy/index/field/199112/order/desc/page/2/ajax/1/"
        dataList = []
        for url in self.thsConfigList:
            headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Cache-Control': 'max-age=0',
                       'Connection': 'keep-alive',
                       'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
                       }
            s = requests.session()
            s.headers.update(headers)
            r = s.get(url=url, params={'wd': 'python'},timeout=10)  # 带参数的GET请求
            r.encoding = 'GBK'
            text = "</tr>" +r.text + "<tr>"
            textData = re.split(r"</tr>[\S\s]*?<tr>",text)
            for i in range(1,len(textData)):
                textData[i] = "</td>" + textData[i] + "<td>"
                rowSplited = re.split("</td>[\s\S]*?<td",textData[i])
                if len(rowSplited) > 4 :
                    searchCode = re.search(r'\d{6}',rowSplited[2])
                    name = searchCode.group()#881149
                    upOrDown = float(re.search(r'(\d\.\d{2})|(\-\d\.\d{2})',rowSplited[3]).group())#板块涨跌
                    topStockCode =  re.search(r'\d{6}',rowSplited[10]).group()#600293
                    topStockUpOrDown = float(re.search(r'(\d{1,3}\.\d{2})|(\-\d{1,3}\.\d{2})',rowSplited[12]).group())#0.750
                    upRDown = float(re.search(r'\d{1,4}',rowSplited[7]).group())/(float(re.search(r'\d{1,4}',rowSplited[7]).group())+float(re.search(r'\d{1,4}',rowSplited[8]).group()))#上涨家数/(下跌家数+上涨）
                    if float(rowSplited[5][1:]) == 0:
                        clearRAll = 9999
                    else:
                        clearRAll = float(rowSplited[6][1:])/float(rowSplited[5][1:])
                    rowData = []
                    rowData.append(self.dt)
                    rowData.append(name)
                    rowData.append(upOrDown)
                    rowData.append(topStockCode)
                    rowData.append(topStockUpOrDown)
                    rowData.append(upRDown)
                    rowData.append(clearRAll)

                    if len(dataList) == 0:
                        dataList.append(rowData)
                    elif rowData[2] >= dataList[0][2]:
                        dataList.insert(0, rowData)
                        # break
                    elif rowData[2] <= dataList[-1][2]:
                        dataList.append(rowData)
                    else:
                        for j in range(0,len(dataList)-1):
                            if rowData[2] <= dataList[j][2] and rowData[2] >= dataList[j + 1][2]:
                                dataList.insert(j+1,rowData)
                                break
            print("dataList="+str(dataList))
            return dataList

    def write_to_mysql(self, sec_data):
        for i in range(len(sec_data)):
            try:
                sql = "replace into industry_" + str(i+1) + \
                      " (datetime, code, price,top_stock, top_stock_price,upRDown,clearRAll) VALUES (%s,%s, %s, %s, %s, %s,%s)"
                self.cursor.cursor().execute(sql, sec_data[i])
                self.cursor.commit()
            except Exception as e:
            # 发生错误时回滚
                print(e)
                self.cursor.rollback()

    def run(self):
        amBegin = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=9, minute=30, second=30))
        amEnd = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=11, minute=30, second=0))
        pmBegin = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=13, minute=0, second=0))
        pmEnd = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=15, minute=0, second=0))

        i = 0
        while True:
            self.dt = self.time_rail[i]
            now = datetime.datetime.now()
            if i >= len(self.time_rail):
                break
            try:
                if not (now.date().isoweekday() == 6 or now.date().isoweekday() == 7):
                    if (amBegin <= now and now <= amEnd) or (pmBegin <= now and now <= pmEnd):
                        if self.dt <= now:
                            i = i + 1
                            self.write_to_mysql(self.sec_industry_data())
                    else:
                        print("today should be rest")
                else:
                    print("today should be rest")
                time.sleep(1)
            except Exception as e:
                print(e)
                time.sleep(1)
                continue

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

    def downLoad(self,url):
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Cache-Control': 'max-age=0',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
        }
        s = requests.session()
        s.headers.update(headers)
        r = s.get(url=url, params={'wd': 'python'}, timeout=10)  # 带参数的GET请求
        r.encoding = 'GBK'
        return r.text

data = Data()
data.init()
data.run()




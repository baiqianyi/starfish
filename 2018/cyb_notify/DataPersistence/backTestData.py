import csv
import config
import os
import datetime
import pymysql
import re
import pandas as pd

class BackTestData:
    def __init__(self):
        self.path = config.secondDataPath
        self.historyData = []  # {code:pd.dataFrame()}前28天的数据。用时生成。只需要行业内要比较的股票间
        self.halfHourData = []  # 内部是code和价格的映射{code:price}
        self.pathList = []
        self.codeList = []
        self.industryCode = []
        self.timeList = []
        self.exsitsTableSet = set()
        self.secdb = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='SecData')
        self.histdb = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='histData')
        self.industrydb = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='industryData')
        self.HEART_BEAT = 10
        self.basics = None

    def init(self):

        self.pathList = self.getListDataPath("D:\\begin")
        self.exsitsTableSet = self.getExsitsTableList(self.pathList)
        # self.pathList = self.getListDataPath("D:\\begin")
        self.codeList = self.getCodeList()
        self.timeList = self.getTimeList()
        #881129 完成
        self.industryCode = self.readIndustryCode()[1:]
        # self.basics = pd.DataFrame.from_csv("E:\\bqyApps\\quant\\cyb_notify\\resource\\basics.csv")


    def extractDataFromTxt(self, path):
        # paths = self.getListDataPath(self.path)
        # codePaths = []
        # for path in paths:
        #     if code == path[-10:-4]:
        #         codePaths.append(code)
        # for path in paths:
        code = None
        if re.match(r'\d{6}.txt', path[-10:]):
            code = path[-10:-4]
        with open(path, 'r') as f:
            reader = f.readlines()
            # reader = csv.reader(f)
            firstLayerList = []
            firstRowNum = 0
            for row in reader:
                row = row.split(",")
                if firstRowNum != 0:
                    if re.match(r'\d{8}',str(row[0])) and re.match(r'\d{5,6}',str(row[1])) and str(row[2]) != "" and re.match(r'\d*',str(row[4])) != "" and str(row[6]) != "":
                        date = datetime.date(year=int(row[0][:4]), month=int(row[0][4:6]), day=int(row[0][6:]))
                        time = datetime.time(hour=int(str(row[1])[:-4]), minute=int(str(row[1])[-4:-2]),
                                             second=int(str(row[1])[-2:]))
                        price = float(row[2])
                        tradeVolume = float(row[4])  # 成交额
                        tradeDirection = int(row[6][0])  # 成交方向
                        firstLayer = FirstLayer(date=date, time=time, price=price, tradeVolume=tradeVolume,
                                                tradeDirection=tradeDirection)
                        firstLayerList.append(firstLayer)
                else:
                    firstRowNum = firstRowNum+1
            f.close()
        return firstLayerList, code

    def toMysql(self):

        # 使用cursor()方法获取操作游标
        cursor = self.secdb.cursor()
        timeRange = int(4* 60)
        timedelta = datetime.timedelta(seconds=self.HEART_BEAT)
        '''
        1.生成股票列表
        2.判断存在，新建表
        3.导入数据
        '''
        for i in range(len(self.codeList)):
            # sql = "create table if not exists " + "s" + self.codeList[i] + " (datetime datetime, price float(8),volume float(16),tradeDirection int(1), PRIMARY KEY(datetime));"
            cursor.execute("create table if not exists " + "s" + self.codeList[i] + " (datetime datetime, price float(8),volume float(16),tradeDirection tinyint(1), PRIMARY KEY(datetime));")


        for path in self.pathList:
            firstLayerList, code = self.extractDataFromTxt(path)
            #genetate today time range
            today = None
            amBegin = datetime.datetime.combine(firstLayerList[0].date, datetime.time(hour=9, minute=30, second=30))
            amEnd = datetime.datetime.combine(firstLayerList[0].date, datetime.time(hour=11, minute=30, second=0))
            pmBegin = datetime.datetime.combine(firstLayerList[0].date, datetime.time(hour=13, minute=0, second=0))
            pmEnd = datetime.datetime.combine(firstLayerList[0].date, datetime.time(hour=15, minute=0, second=0))
            todayRange = []
            tempTime = amBegin
            railData = []

            while True:
                todayRange.append(tempTime)
                if (amBegin <= tempTime and amEnd > tempTime) or (pmBegin <= tempTime and pmEnd > tempTime):
                    tempTime = tempTime + timedelta
                elif amEnd <= tempTime and pmBegin > tempTime:
                    tempTime = pmBegin
                else:
                    break

            timeRangeIndex = 0
            volume = 0
            for i in range(len(firstLayerList)-1):
                firstLayer = firstLayerList[i]
                firstLayer1 = firstLayerList[i+1]
                if firstLayer.date == today :
                    if  datetime.datetime.combine(firstLayer.date,firstLayer.time) <= todayRange[timeRangeIndex] and  datetime.datetime.combine(firstLayer1.date,firstLayer1.time) > todayRange[timeRangeIndex]:
                        price = firstLayer.price*((firstLayer1.time-todayRange[timeRangeIndex].time).seconds/float((firstLayer1.time-firstLayer.time).seconds))+firstLayer1.price*(abs((firstLayer.time-todayRange[timeRangeIndex].time).seconds)/float((firstLayer1.time-firstLayer.time).seconds))
                        price = round(price,2)
                        tradeDirection = 1
                        if (firstLayer1.time-todayRange[timeRangeIndex].time).seconds > abs((firstLayer.time-todayRange[timeRangeIndex].time).seconds):
                            tradeDirection = firstLayer.tradeDirection
                        else:
                            tradeDirection = firstLayer1.tradeDirection
                        volume = volume + firstLayer.tradeVolume
                        railData.append((todayRange[timeRangeIndex],price,volume,tradeDirection))
                        volume = 0
                        timeRangeIndex = timeRangeIndex + 1

                elif firstLayer.date > today or today == None:
                    amBegin = datetime.datetime.combine(firstLayer.date,
                                                        datetime.time(hour=9, minute=30, second=30))
                    amEnd = datetime.datetime.combine(firstLayer.date,
                                                      datetime.time(hour=11, minute=30, second=0))
                    pmBegin = datetime.datetime.combine(firstLayer.date,
                                                        datetime.time(hour=13, minute=0, second=0))
                    pmEnd = datetime.datetime.combine(firstLayer.date,
                                                      datetime.time(hour=15, minute=0, second=0))
                    today = firstLayer.date

                elif datetime.datetime.combine(firstLayer.date,firstLayer.time) < todayRange[timeRangeIndex] and  datetime.datetime.combine(firstLayer1.date,firstLayer1.time) < todayRange[timeRangeIndex]:
                    volume = volume + firstLayer.tradeVolume

            addSql = "REPLACE INTO " + "s" + code + "(datatime,\
                price,\
                volume,\
                tradeDirection,\
              ) VALUES ('%s', '%f', '%f', '%d')"

            try:
                # 执行sql语句
                # mysqldate = datetime.datetime.combine(firstLayer.date, firstLayer.time).strptime('%Y-%m-%d %H:%M:%S')
                # print(mysqldate)
                for data in railData:
                    cursor.execute(addSql,
                               (data[0], data[1], data[2], data[3]))
                # 执行sql语句
                self.secdb.commit()
            except:
                # 发生错误时回滚
                self.secdb.rollback()

        # 关闭数据库连接
        # self.db.close()
    def toMysqlTest(self):

        # 使用cursor()方法获取操作游标
        self.secdb = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='SecData')
        cursor = self.secdb.cursor()

        '''
        1.生成股票列表
        2.判断存在，新建表
        3.导入数据
        '''
        for i in range(len(self.codeList)):
            # sql = "create table if not exists " + "s" + self.codeList[i] + " (datetime datetime, price float(8),volume float(16),tradeDirection int(1), PRIMARY KEY(datetime));"
            cursor.execute("create table if not exists "  + self.codeList[
                i] + " (datetime datetime, price float(16),volume float(16),tradeDirection tinyint(1), PRIMARY KEY(datetime));")

        for p in self.pathList:
            # 记录读写位置
            self.writeMysqlPosition(p)
            self.textToMysql(p)
            self.secdb.close()
        # for p in self.pathList:
        # while True:
        #     if not queue.empty():
        #         p = queue.get()
        #         self.writeMysqlPosition(p)
        #         self.textToMysql(p)
        #         print("Thread " + str(treadId))
        #         self.secdb.close()
        #     else:
        #         break
            #记录读写位置
            # self.writeMysqlPosition(p)
            # self.textToMysql(p)
            # self.secdb.close()
        # 关闭数据库连接

    def generateTimeTange(self,firstLayerList,i):
        # genetate today time range
        timedelta = datetime.timedelta(seconds=self.HEART_BEAT)
        amBegin = datetime.datetime.combine(firstLayerList[i].date,
                                            datetime.time(hour=9, minute=30, second=0))
        amEnd = datetime.datetime.combine(firstLayerList[i].date,
                                          datetime.time(hour=11, minute=30, second=0))
        pmBegin = datetime.datetime.combine(firstLayerList[i].date,
                                            datetime.time(hour=13, minute=0, second=0))
        pmEnd = datetime.datetime.combine(firstLayerList[i].date,
                                          datetime.time(hour=15, minute=0, second=0))
        todayRange = []
        tempTime = amBegin

        while True:
            todayRange.append(tempTime)
            if (amBegin <= tempTime and amEnd > tempTime) or (pmBegin <= tempTime and pmEnd > tempTime):
                tempTime = tempTime + timedelta
            elif amEnd <= tempTime and pmBegin > tempTime:
                tempTime = pmBegin
            else:
                break
        return todayRange

    def getExsitsTableList(self,pathList):
        reSet = set()
        for path in pathList:
            code = path[-10:]
            if re.match(r'(000|002)\d{3}.txt', code) or re.match(r'3\d{5}.txt', code) or re.match(r'6\d{5}.txt', code):
                reSet.add(path[-10:-4])
        return reSet


    def readToMysqlPositon(self):
        path = config.writePositionPath
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                return line
        # with open(path, 'r') as f:
        #     reader = csv.reader(f)
        #     for line in reader:
        #         return line

    def writeMysqlPosition(self,path):
        with open(config.writePositionPath, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(path)
            f.close()


    # for path in self.pathList:
    def textToMysql(self,path,cursor=None):
        print('this is '+ path)
        firstLayerList, code = self.extractDataFromTxt(path)
        self.secdb = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='SecData')

        cursor = self.secdb.cursor()
        today = None
        railData = []
        timeRangeIndex = 0
        volume = 0
        todayRange = self.generateTimeTange(firstLayerList,0)

        i = 0
        while True:
        # for i in range(len(firstLayerList) - 1):
            firstLayer = firstLayerList[i]
            firstLayer1 = firstLayerList[i + 1]
            if firstLayer.date == today:
                if timeRangeIndex+1 > len(todayRange)-1 :
                    lastHasGetData = False
                    if not todayRange[-1].strftime('%Y-%m-%d %H:%M:%S') == railData[-1][0]:
                        for j in range(i, len(firstLayerList)):
                            if firstLayerList[j].date > today:
                                tempLay = firstLayerList[j - 1]
                                railData.append((
                                    todayRange[-1].strftime('%Y-%m-%d %H:%M:%S'), tempLay.price, tempLay.tradeVolume,
                                    tempLay.tradeDirection))
                                lastHasGetData = True
                                break
                    else:
                        lastHasGetData = True


                    if not lastHasGetData:
                        railData.append((
                            todayRange[-1].strftime('%Y-%m-%d %H:%M:%S'), firstLayerList[-1].price, firstLayerList[-1].tradeVolume,
                            firstLayerList[-1].tradeDirection))

                elif datetime.datetime.combine(firstLayer.date, firstLayer.time) < todayRange[
                    timeRangeIndex] and datetime.datetime.combine(firstLayer1.date, firstLayer1.time) >= \
                        todayRange[timeRangeIndex]:
                    #price caculate has a problem.
                    # if ((firstLayer1.datetime - todayRange[timeRangeIndex]).seconds > )
                    # price = firstLayer.price * (
                    # (firstLayer1.datetime - todayRange[timeRangeIndex]).seconds / float(
                    #     (firstLayer1.datetime - firstLayer.datetime).seconds)) + firstLayer1.price * (
                    # abs((firstLayer.datetime - todayRange[timeRangeIndex]).seconds) / float(
                    #     (firstLayer1.datetime - firstLayer.datetime).seconds))
                    tradeDirection = 1
                    if (firstLayer1.datetime - todayRange[timeRangeIndex]).seconds > abs(
                            (firstLayer.datetime - todayRange[timeRangeIndex]).seconds):
                        tradeDirection = firstLayer.tradeDirection
                        price = round(firstLayer.price, 2)
                    else:
                        tradeDirection = firstLayer1.tradeDirection
                        price = round(firstLayer1.price, 2)
                    volume = volume + firstLayer.tradeVolume
                    railData.append((todayRange[timeRangeIndex].strftime('%Y-%m-%d %H:%M:%S'), price, volume, tradeDirection))
                    volume = 0
                    timeRangeIndex = timeRangeIndex + 1

                elif firstLayer.time >= datetime.time(hour=9,minute=0,second=0) and firstLayer.time < datetime.time(hour=9,minute=30,second=0):
                    railData.append(
                        (firstLayer.datetime.strftime('%Y-%m-%d %H:%M:%S'), firstLayer.price, firstLayer.tradeVolume, firstLayer.tradeDirection))

                elif datetime.datetime.combine(firstLayer.date, firstLayer.time) < todayRange[
                    timeRangeIndex] and datetime.datetime.combine(firstLayer1.date, firstLayer1.time) < \
                        todayRange[timeRangeIndex]:
                    volume = volume + firstLayer.tradeVolume

                elif datetime.datetime.combine(firstLayer.date, firstLayer.time) >= todayRange[
                    timeRangeIndex] :
                    price = round(firstLayer.price, 2)
                    volume = volume + firstLayer.tradeVolume
                    tradeDirection = firstLayer.tradeDirection
                    railData.append((todayRange[timeRangeIndex].strftime('%Y-%m-%d %H:%M:%S'), price, volume, tradeDirection))
                    volume = 0
                    timeRangeIndex = timeRangeIndex + 1
                    i = i - 1

                elif todayRange[timeRangeIndex].time == datetime.time(hour=15,minute=0,second=0):
                    lastHasGetData = False
                    for j in range(i, len(firstLayerList)):
                        if firstLayerList[j].date > today:
                            tempLay = firstLayerList[j - 1]
                            railData.append((
                                todayRange[-1].strftime('%Y-%m-%d %H:%M:%S'), tempLay.price, tempLay.tradeVolume,
                                tempLay.tradeDirection))
                            lastHasGetData = True
                            break
                    if not lastHasGetData:
                        railData.append((
                            todayRange[-1].strftime('%Y-%m-%d %H:%M:%S'), firstLayerList[-1].price,
                            firstLayerList[-1].tradeVolume,
                            firstLayerList[-1].tradeDirection))

            elif today == None:
                today = firstLayer.date
                todayRange = self.generateTimeTange(firstLayerList,i)
                timeRangeIndex = 0
                railData.append(
                    (firstLayer.datetime.strftime('%Y-%m-%d %H:%M:%S'), firstLayer.price, firstLayer.tradeVolume,
                     firstLayer.tradeDirection))

            elif firstLayer.date != today:
                today = firstLayer.date
                todayRange = self.generateTimeTange(firstLayerList,i)
                timeRangeIndex = 0
                railData.append(
                    (firstLayer.datetime.strftime('%Y-%m-%d %H:%M:%S'), firstLayer.price, firstLayer.tradeVolume,
                     firstLayer.tradeDirection))

            i = i + 1

            if i > len(firstLayerList) - 2:
                if timeRangeIndex < len(todayRange):
                    tmpList = todayRange[timeRangeIndex:]
                    for tmpIndex in range(len(tmpList)):
                        railData.append((todayRange[timeRangeIndex].strftime('%Y-%m-%d %H:%M:%S'), firstLayerList[-1].price, firstLayerList[-1].tradeVolume, firstLayerList[-1].tradeDirection))
                break

        addSql = "replace INTO "  + path[-13:-11] + code + " (datetime,price,volume, tradeDirection) VALUES (%s, %s, %s, %s)"

        try:
            # 执行sql语句
            # mysqldate = datetime.datetime.combine(firstLayer.date, firstLayer.time).strptime('%Y-%m-%d %H:%M:%S')
            # print(mysqldate)
            # for data in railData:
            cursor.executemany(addSql,railData)
            # 执行sql语句
            self.secdb.commit()
            # self.secdb.close()
        except Exception as e:
            # 发生错误时回滚
            print(e)
            self.secdb.rollback()

    def industryData(self):
        secCursor = self.secdb.cursor()
        cursor = self.industrydb.cursor()
        #init
        # for indutry in self.indutryCode:
        #     for stock in indutry[1:]:
        #         secCursor.execute("create table  if not exists " + stock + " (datetime datetime, price float(16),volume float(16),tradeDirection tinyint(1), PRIMARY KEY(datetime));")
        '''
        1.生成行业表
        2.判断存在，新建表
        3.导入数据
        '''
        # for i in range(len(self.industryCode)):
        #     if self.industryCode[i][0] == "881166":
        #         self.industryCode=[self.industryCode[i]]
        #         break
        for indutry in self.industryCode:
            cursor.execute("create table if not exists " + "i" + str(indutry[0])
                           + " (datetime datetime, price float(16),volume float(16), PRIMARY KEY(datetime))")

            beginTime = datetime.datetime(year=2010, month=1, day=1, hour=9, minute=30, second=0)
            endTime = beginTime + datetime.timedelta(hours=6)
            while True:

                beginTime,endTime,timeRange = self.getTimeRange(beginTime)
                if beginTime == None:
                    break
                tmpMap = {}
                if  beginTime != None:
                    for stock in indutry[1:]:
                        if stock[2:] in self.exsitsTableSet:
                            secCursor.execute("select datetime,price,volume from "+ stock + " where datetime between \"" + beginTime.strftime('%Y-%m-%d %H:%M:%S') + "\" and \"" + endTime.strftime('%Y-%m-%d %H:%M:%S') + "\";")
                            stockData = list(secCursor.fetchall())
                            #去空值
                            if not len(stockData) <= 1:
                                if stockData[1][0] > beginTime and stockData[1][0] < beginTime + datetime.timedelta(seconds=10):
                                    del stockData[1]
                                tmpMap[stock] = stockData

                tmpIndustryData = []

                i = 0
                while True:
                    if i==0:
                        print(datetime.datetime.now(),":",timeRange[0]," ; ",indutry[0])
                    mean = 0.0
                    volume = 0.0
                    tmpTest1 = []
                    tmpTest2 = []
                    for key in tmpMap.keys():
                        tmpTest1.append((key,tmpMap[key][0]))
                        tmpTest2.append((key,tmpMap[key][-1]))
                        if i < len(timeRange) and i >= len(tmpMap[key]):
                            mean = mean + tmpMap[key][-1][1]
                            volume = 0.0
                        else:
                            atomData = tmpMap[key][i]
                            if atomData[0] == timeRange[i]:
                                mean = mean + atomData[1]
                                volume = volume + atomData[2] * atomData[1]
                            else:
                                for tmpAtomData in tmpMap[key][i:]:
                                    if tmpAtomData[0] >= timeRange[i]:
                                        mean = mean + tmpAtomData[1]
                                        volume = volume + atomData[2] * atomData[1]
                                        break

                    if len(list(tmpMap))==0:
                        mean = 0
                    else:
                        mean = mean / float(len(tmpMap))

                    #时间，平均值，成交量
                    tmpIndustryData.append([timeRange[i].strftime('%Y-%m-%d %H:%M:%S'),mean,volume])
                    i = i + 1
                    if i >= len(timeRange):
                        break
                print(len(tmpMap), mean, tmpTest1)
                print(len(tmpMap), mean, tmpTest2)
                print(tmpIndustryData[0])
                print(tmpIndustryData[-1])
                try:
                    cursor.executemany("replace into " + "i" + str(indutry[0])+ " (datetime,price,volume) VALUES (%s, %s, %s)",tmpIndustryData)
                    self.industrydb.commit()
                except Exception as e:
                    # 发生错误时回滚
                    print(e)
                    self.secdb.rollback()


    def SortedMysqlIndustryData(self, i, datetime):
        # 使用cursor()方法获取操作游标
        cursor = self.industrydb.cursor()
        tempMap = {}
        tmpList = []
        '''
        1.生成行业表
        2.判断存在，新建表
        3.导入数据
        '''

        for indutry in self.industryCode:
            cursor.execute("create table if not exists Industry"  + str(indutry[0]) + " (datetime datetime, industryCode char(8),volume float(16),upDown float(8),firstsStockcCode char(8),firstsStockUpDown float(8), PRIMARY KEY(datetime))")

        # codeSql = "select\
        # table_name\
        # from information_schema.tables where\
        # table_schema = 'secdb' and table_type = 'base table';"
        # cursor.execute(codeSql)
        # codeTableName = cursor.fetchall()
        #get
        #define a funtion which gives the begintime and endtime
        beginTime = datetime.datetime(year=2009,month=1,day=1,hour=9, minute=30, second=0)
        endTime = beginTime + datetime.timedelta(hour=6)

        codes = self.getCodeTable()
        while True:
            industryPrice = {}
            for industry in self.industryCode:
                industryCode = industry[0]
                stockCode = industry[1:]

                stocksSql = "select price,volume from "
                for code in stockCode:
                    if re.match(r'(000|002)\d{3}', code) or re.match(r'3\d{5}', code):
                        code = "SZ" + code
                    elif re.match(r'6\d{5}', code):
                        code = "SH" + code
                    else:
                        print("code has be wrong")
                    stocksSql = stocksSql + code
                    stocksSql = stocksSql+" WHERE datetime BETWEEN "+ beginTime.strptime('%Y-%m-%d %H:%M:%S') +" AND " + endTime.strptime('%Y-%m-%d %H:%M:%S')+";"

                    try:
                    # 执行sql语句
                        scursor = self.secdb.cursor()
                        scursor.execute(stocksSql)
                        # 执行sql语句
                        self.secdb.commit()
                        data = scursor.fetchall()
                        firstLayer = FirstLayer()
                        firstLayer.datetime = datetime.datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S')
                        firstLayer.price = data[1]
                        firstLayer.tradeVolume = data[2]

                        if tempMap.get(code) == None:
                            tempMap[code] = [firstLayer]
                        else:
                            tempMap[code].append(firstLayer)
                    except:
                        # 发生错误时回滚
                        self.industrydb.rollback()

                for i in range(len(tempMap[(tempMap.keys())[0]])):
                    meanSum = 0
                    volume = 0
                    for code in tempMap.keys():
                        meanSum = meanSum + tempMap[code][i].price
                        volume = volume + tempMap[code][i].tradeVolume
                    mean = float(meanSum)/len(stockCode)
                    time = tempMap[code][i].datetime
                    if industryPrice.get(code) == None:
                        industryPrice[industryCode] = [(datetime,mean,volume)]
                    else:
                        industryPrice[industryCode].append((datetime,mean,volume))

            def compare(x):
                return x[2]
            for i in range(len(industryPrice[industryPrice.keys()[0]])):
                tmpList = []
                for key in industryPrice.keys():
                    tmpList.append((key,industryPrice[key][i][0],industryPrice[key][i][1]))
                tmpList = self.sort(tmpList,compare)

                for indutry in self.industryCode:
                    writeSql = "replace INTO " + "i" + str(industry) +"(datetime,price,volume) VALUES('%s', '%f','%f'); "
                    cursor.execute(writeSql,tmpList[i-1])

            beginTime,endTime = self.getDateTime(beginTime=beginTime)
            if beginTime == None or endTime == None:
                break


    def getTimeRange(self,beginTime):
        timeRange = []
        beginTime = beginTime + datetime.timedelta(hours=24)
        tmpTime = None
        recuTime = 0
        while True:
            cursor = self.secdb.cursor()
            sql = "select datetime from sh000001 where datetime = \"" + beginTime.date().strftime("%Y-%m-%d") + " 09:30:00\""
            cursor.execute(sql)
            dt = cursor.fetchone()
            if dt != None:
                tmpTime = dt[0]
                break
            else:
                beginTime = beginTime + datetime.timedelta(hours=24)
                recuTime = recuTime + 1
            if recuTime > 20:
                return None,None,None

        for time in self.timeList:
            timeRange.append(datetime.datetime.combine(tmpTime.date(),time))
        return datetime.datetime.combine(tmpTime.date(),self.timeList[0]),datetime.datetime.combine(tmpTime.date(),self.timeList[-1]),timeRange

    def getListDataPath(self, path):
        pathList = []
        readPosition = 0
        for subPath in os.listdir(path):
            subPath = path + "\\" + subPath
            if os.path.isdir(subPath):
                pathList.extend(self.getListDataPath(subPath))
            elif re.match(r'(000|002|001)\d{3}.txt', subPath[-10:]) or re.match(r'(3|6)\d{5}.txt', subPath[-10:]):
            # elif re.match(r'000016.txt', subPath[-10:]):
                pathList.append(subPath)

        if self.readToMysqlPositon() != None:
            for i in range(len(pathList)):
                # if pathList[i] == self.readToMysqlPositon():
                if pathList[i] == "":
                    readPosition = i
                    break
            pathList = pathList[readPosition:]
        # self.pathList = pathList
        return pathList

    def getListDataPath001Version(self, path):
        pathList = []
        readPosition = 0
        for subPath in os.listdir(path):
            subPath = path + "\\" + subPath
            if os.path.isdir(subPath):
                pathList.extend(self.getListDataPath001Version(subPath))
            elif re.match(r'(001)\d{3}.txt', subPath[-10:]):
                pathList.append(subPath)

        # if self.readToMysqlPositon() != None:
        #     for i in range(len(pathList)):
        #         if pathList[i] == self.readToMysqlPositon():
        #             readPosition = i
        #             break
        #     pathList = pathList[readPosition:]
        # self.pathList = pathList
        return pathList

    def getCodeList(self):
        for path in self.pathList:
            if not path in self.codeList:
                self.codeList.append(path[-13:-11]+path[-10:-4])
        return self.codeList

    def runToMysql(self):
        self.getListDataPath(config.secondDataPath)
        self.toMysql()

    def getHalfHourData(self,beginTime,timeRange=30):

        endTime = beginTime + datetime.timedelta(minutes=timeRange)
        railData =[ {} for i in range(timeRange*60//self.HEART_BEAT)]
        timedelta = datetime.timedelta(seconds=self.HEART_BEAT)
        timelist = []
        for i in range(timeRange*60//self.HEART_BEAT):
           timelist.append(beginTime + datetime.timedelta(seconds=i*self.HEART_BEAT))
        cursor = self.secdb.cursor()
        for code in self.codeList:
            cursor.execute("create table if not exists " + code + " (datetime datetime, price float(8),volume float(16),tradeDirection int(1))")
            sql = "SELECT datetime,price FROM "+code+ " WHERE BETWEEN "+ beginTime.strptime('%Y-%m-%d %H:%M:%S') +" AND " + endTime.strptime('%Y-%m-%d %H:%M:%S')+";"

            try:
                # 执行SQL语句
                cursor.execute(sql)
                # 获取所有记录列表
                mysqlSearch = cursor.fetchall()
                if len(mysqlSearch) < 10:
                    print('there is no code data at this time!')
                    # raise Exception("抛出一个异常")  # 异常被抛出，print函数无法执行
                    break
                for row in mysqlSearch:
                    timeIndex = datetime.datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S')
                    price = float(row[1])
                mysqlIndex = 0
                for i in range(len(timelist)):
                    satisfiedData = False
                    for j in range(mysqlIndex,mysqlIndex+15):
                        if timelist[i] >= datetime.datetime.strptime(mysqlSearch[j][0],'%Y-%m-%d %H:%M:%S') and timelist[i] <= datetime.datetime.strptime(mysqlSearch[j+1][0],'%Y-%m-%d %H:%M:%S'):
                            satisfiedData = True
                            #time.delta可能不能比大小
                            if timelist[i]-datetime.datetime.strptime(mysqlSearch[j][0],'%Y-%m-%d %H:%M:%S') > -1*timelist[i] + datetime.datetime.strptime(mysqlSearch[j+1][0],'%Y-%m-%d %H:%M:%S'):
                                railData[i][code] = mysqlSearch[j+1][1]
                                mysqlIndex = j+1
                            else :
                                railData[i][code] = mysqlSearch[j][1]
                                mysqlIndex = j

                    if satisfiedData == False:
                        print('None data')
                        railData[i][code] = mysqlSearch[mysqlIndex + 15][1]
                        raise Exception("There is null time range at this time!")  # 异常被抛出，print函数无法执行
            except:
                print("Error: unable to fecth data")
        return railData

    def getHistData(self,codeList,beginTime, endTime):
        secondCursor = self.secdb.cursor()
        cursor = self.histdb.cursor()
        for code in codeList:
            createTable = "create table if not exists " + code + " (date date, open float(8),high float(8),low float(8),close float(8),volume float(16))"
            cursor.execute(createTable)

            cursor.execute("select max(datetime) form " + code)
            secondCursor.execute("select max(datetime) form " + code)
            newDateTime = cursor.fetchone()
            newEndDateTime = secondCursor.fetchone()
            if newDateTime == None:
                beginTime = datetime.datetime(year=2009, month=1, day=1, hour=9, minute=30, second=30)
                endTime = beginTime + datetime.timedelta(minutes=330)
            else:
                beginTime = datetime.datetime.strptime(newDateTime, '%Y-%m-%d %H:%M:%S')
                endTime = beginTime + datetime.timedelta(minutes=330)
            while True:
                if newDateTime >= newEndDateTime:
                    break
                sql = "select datetime,price,volume from " +code +"where between" + beginTime.strptime(
                    '%Y-%m-%d %H:%M:%S') + " AND " + endTime.strptime('%Y-%m-%d %H:%M:%S') + ";"
                secondCursor.execute(sql)
                oneDayData = secondCursor.fetchall()
                date = datetime.datetime.strptime(oneDayData[0][0]).date()
                low = 999999
                high = 0
                open = oneDayData[0][1]
                close = oneDayData[-1][1]
                vol = 0
                for secData in oneDayData:
                    if secData[1] > high:
                        high = secData[1]
                    if secData[1] < low:
                        low = secData[1]
                    vol = vol + secData[2]
                bar = [date.strftime('%Y-%m-%d %H:%M:%S'),open,close,high, low,vol]
                addSql = "INSERT INTO " + code + "(date,open,high,low,close,price,volume) VALUES ('%s', '%f', '%f', '%f', '%f','%f', '%f')"
                cursor.execute(addSql,bar)
                beginTime,endTime = self.getDateTime(beginTime)


        # sql = "SELECT datetime,price FROM "
        # for code in codeList:
        #     sql = sql + code + " join "
        # sql = sql + " on id = id WHERE BETWEEN " + beginTime.strptime(
        #         '%Y-%m-%d %H:%M:%S') + " AND " + endTime.strptime('%Y-%m-%d %H:%M:%S') + ";"

        # cursor = self.histdb.cursor()
        # cursor.execute(sql)
        # mysqlSearch = cursor.fetchall()
        # if len(mysqlSearch) < 10:
        #     print('there is no code data at this time!')
        #     # raise Exception("抛出一个异常")  # 异常被抛出，print函数无法执行
        # for row in mysqlSearch:
        #     timeIndex = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        #     price = float(row[1])

    def readIndustryCode(self):
        csvFile = open(config.resourcePath + "\\newIndustryCode.csv", "r")
        reader = csv.reader(csvFile)  # 返回的是迭代类型
        self.industryCodeData = []
        for item in reader:
            #[] first item is indstry code,others are stock code.
            self.industryCodeData.append(item)
        csvFile.close()
        return self.industryCodeData

    def getCodes(self):
        csvFile = open(config.resourcePath + "\\industryCode.csv", "r")
        reader = csv.reader(csvFile)  # 返回的是迭代类型
        codes = []
        for item in reader:
            # [] first item is indstry code,others are stock code.
            for i in range(1,len(item)):
                codes.append(item[i])
        csvFile.close()
        return codes

    def getCodeTable(self):
        codes = self.getCodes()
        codeTable = []
        for code in codes:
            if re.match(r'(000|002|001)\d{3}', code) or re.match(r'3\d{5}', code):
                codeTable.append("SZ"+code)
            elif re.match(r'6\d{5}', code):
                codeTable.append("SH" + code)
            else:
                print ("code has be wrong")
        return codeTable

    def sort(self,list,func = None):
        if func == None:
            def x(a):
                return a
            func = x
        self.funcList = []
        for v in list:
            self.funcList.append(func(v))
        for i in range(len(self.funcList)-1,0,-1):
            for j in range(0,i):
                if self.funcList[j] < self.funcList[j+1]:
                    tmp = self.funcList[j+1]
                    self.funcList[j+1] = self.funcList[j]
                    self.funcList[j] = tmp
                    tmp = list[j+1]
                    list[j+1] = list[j]
                    list[j] = tmp
        return list

    def getTimeList(self):
        timedelta = datetime.timedelta(seconds=self.HEART_BEAT)
        amBegin = datetime.datetime(year=2017,month=11,day=18,hour=9, minute=30, second=0)
        amEnd = datetime.datetime(year=2017,month=11,day=18,hour=11, minute=30, second=0)
        pmBegin = datetime.datetime(year=2017,month=11,day=18,hour=13, minute=0, second=0)
        pmEnd = datetime.datetime(year=2017,month=11,day=18,hour=15, minute=0, second=0)
        todayRange = []
        tempTime = amBegin

        while True:
            todayRange.append(tempTime)
            if (amBegin <= tempTime and amEnd > tempTime) or (pmBegin <= tempTime and pmEnd > tempTime):
                tempTime = tempTime + timedelta
            elif amEnd <= tempTime and pmBegin > tempTime:
                tempTime = pmBegin
            else:
                break
        for i in range(len(todayRange)):
            todayRange[i] = todayRange[i].time()
        return todayRange

class FirstLayer:
    def __init__(self, code = None,date=None, time=None, price=None, tradeVolume=None, tradeDirection=None):
        self.code = code
        self.date = date
        self.time = time
        self.price = price
        self.tradeVolume = tradeVolume  # 成交额
        self.tradeDirection = tradeDirection
        self.datetime = datetime.datetime.combine(self.date,self.time)


# if __name__ == '__main__':#theads has to be exits
#     backTestData = BackTestData()
#     pathList = backTestData.init()
#     # backTestData.industryData()
#     import multiprocessing
#
#     queue = multiprocessing.Queue()
#     for p in pathList:
#         queue.put(p)
#     # secdb.close()
#     for i in range(2):
#         backTestData = BackTestData()
#         p = multiprocessing.Process(target=backTestData.toMysqlTest, args=(queue, i,))
#         p.daemon = True
#         p.start()
        # p.join()
    # backTestData.toMysqlTest(p)



# backTestData = BackTestData()
# backTestData.init()
# backTestData.industryData()
# backTestData.toMysqlTest()

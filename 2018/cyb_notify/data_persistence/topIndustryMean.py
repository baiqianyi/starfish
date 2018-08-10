import datetime

import pymysql

from data_persistence.backTestData import BackTestData
from dao.industryDao import IndustryDao
from utils.sortedIndustryCode import SortedIndustryCode


class QuantDataPersistence:
    def __init__(self):
        self.quantdb = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='sec_industrys')
        self.industryDao = IndustryDao()
        self.backTestData = BackTestData()
        self.backTestData.timeList = self.backTestData.getTimeList()
        self.sortedIndustryCode = SortedIndustryCode()


    def topIndustryMeanAndA50Coefficient(self):
        beginTime = datetime.datetime(year=2010,month=1,day=3)

        while True:
            #拿出一天的行业数据
            beginTime,endTime,timeRange = self.backTestData.getTimeRange(beginTime)
            print(beginTime)
            if beginTime == None:
                break
            tmpSortedIndustry = self.sortedIndustryCode.getSortedIndustryData(beginTime=beginTime,endTime=endTime,timeRange=timeRange)
            #求a50行业因子
            coefficientList = []
            topIndustryData = tmpSortedIndustry[2:6]
            for j in range(len(tmpSortedIndustry[0])):
                coefficient = 1.0
                for i in range(len(tmpSortedIndustry)):
                    # print(i,j,len(topIndustryData),len(topIndustryData[i]))
                    if tmpSortedIndustry[i][j][1] == "i881155" or tmpSortedIndustry[i][j][1] == "i881157":
                        coefficient = float(i)/float(len(tmpSortedIndustry)) * coefficient
                coefficientList.append((tmpSortedIndustry[0][j][0].strftime('%Y-%m-%d %H:%M:%S'),coefficient))
            try:
                cursor = self.quantdb.cursor()
                cursor.executemany("REPLACE INTO a50coefficient " + " (datetime,coefficient) VALUES (%s,%s)",coefficientList)
                # 执行sql语句
                self.quantdb.commit()
            except Exception as e:
                print(e)
                # 发生错误时回滚
                self.quantdb.rollback()
            # #求平均值
            # #暂存数据结构
            tmpMeanList = []

            for j in range(len(topIndustryData[0])):
                mean = 0.0
                for i in range(len(topIndustryData)):
                    mean = mean + topIndustryData[i][j][2]
                mean = mean/float(len(topIndustryData))
                tmpMeanList.append((topIndustryData[0][j][0],mean))

            try:
                cursor = self.quantdb.cursor()
                cursor.executemany("REPLACE INTO topIndustryMean" + " (datetime,price) VALUES (%s, %s)", tmpMeanList)
                # 执行sql语句
                self.quantdb.commit()
            except Exception as e:
                print(e)
                # 发生错误时回滚
                self.quantdb.rollback()

if __name__ == '__main__':
    quantDataPersistence = QuantDataPersistence()
    quantDataPersistence.topIndustryMeanAndA50Coefficient()



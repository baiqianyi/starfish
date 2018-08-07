import pymysql
import config as config


class IndustryDao:
    def __init__(self):
        self.idb =  pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='industryData')
        self.tableList = self.readIndustryCode()
        # for i in range(len(self.tableList)):
        #     self.tableList[i] = (self.tableList[i],)

    def findAllIndustryData(self,beginTime=None,endTime=None):
        cursor = self.idb.cursor()
        tmp = []
        if beginTime == None or endTime == None:
            for table in self.tableList:
                cursor.execute("select datetime,price from " + table)
                tmp.append(list(cursor.fetchall()))
        else:
            for table in self.tableList:
                cursor.execute(
                        "select datetime,price from " + table +" where datetime BETWEEN \"" + beginTime.strftime('%Y-%m-%d %H:%M:%S') + "\" and \"" + endTime.strftime('%Y-%m-%d %H:%M:%S') + "\"")
                tmp.append(list(cursor.fetchall()))
        # cursor.executemany("select datetime,price from %s where datetime BETWEEN \"" + beginTime.strftime('%Y-%m-%d %H:%M:%S') + "\" and \"" + endTime.strftime('%Y-%m-%d %H:%M:%S') + "\"",self.tableList)
        return self.tableList,tmp

    def readIndustryCode(self):
        path = config.resourcePath + "\\newIndustryCode.csv"
        industryCode = []
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:
               industryCode.append("i" + line.split(",")[0])
        return  industryCode




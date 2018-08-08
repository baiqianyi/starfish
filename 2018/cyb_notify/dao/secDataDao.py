import pymysql

class SecDataDao:
    def __init__(self):
        self.sdb = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='sec_data')

    def getDataBetween(self,stockCode,beginTime=None,endTime=None):
        cursor = self.sdb.cursor()
        if beginTime == None or endTime == None:
            sql = "select datetime,price from " + stockCode
        else:
            sql = "select datetime,price from " + stockCode + " where datetime between \"" + beginTime + "\" and \"" + endTime + "\";"
        cursor.execute(sql)
        return cursor.fetchall()



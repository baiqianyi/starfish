import pymysql

class A50CYBDao:
    def __init__(self):
        self.quantdb = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='a50cybQuant')

    def getA50Coefficient(self):
        sql = "select * from A50Coefficient;"
        cursor = self.quantdb.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def getIndustryTopMean(self):
        sql = "select * from topindustrymean;"
        cursor = self.quantdb.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

# l = A50CYBDao().getIndustryTopMean()
# for i in range(9,1000):
#     print(l[i])

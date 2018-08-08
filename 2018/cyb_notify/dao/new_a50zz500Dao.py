import pymysql

class A50ZZ500Dao:
    def __init__(self):
        self.quantdb = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='sec_data')

    def get_a50(self):
        sql = "select * from zz50;"
        cursor = self.quantdb.cursor()
        cursor.execute(sql)
        self.quantdb.commit()
        return cursor.fetchall()

    def get_zz500(self):
        sql = "select * from zz500;"
        cursor = self.quantdb.cursor()
        cursor.execute(sql)
        self.quantdb.commit()
        return cursor.fetchall()
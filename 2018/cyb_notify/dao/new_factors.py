import pymysql

class new_factors:
    def __init__(self):
        self.db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='sec_industrys')
        self.i_list = []
        cursor = self.db.cursor()
        for i in range(1,51):
            sql = "select * from industry_"+str(i) + ";"
            try:
                # 执行sql语句
                # mysqldate = datetime.datetime.combine(firstLayer.date, firstLayer.time).strptime('%Y-%m-%d %H:%M:%S')
                # print(mysqldate)
                cursor.execute(sql)
                # 执行sql语句
                self.db.commit()
            except:
                # 发生错误时回滚
                self.db.rollback()
            self.i_list.append(cursor.fetchall())
    def get_a50_factor(self):
        coefficientList = []
        for j in range(len(self.i_list[-1])):
            coefficient = 1.0
            tmp_i_num = 0
            for i in range(len(self.i_list)):
                # 49
                # 0
                # 881119
                # print(i,j,self.i_list[i][j][1])

                if j> 0 and (self.i_list[i][j][1] == "881155" or self.i_list[i][j][1] == "881157" or self.i_list[i][j][1] == "881156"):
                    tmp_i_num = tmp_i_num + 1
                    coefficient = (1-float(i+1.0) / float(66+1.0)) * coefficient
            if tmp_i_num == 0:
                coefficientList.append((self.i_list[0][j][0], 1.0/64.0))
            elif tmp_i_num == 1:
                coefficientList.append((self.i_list[0][j][0], coefficient * 1.0 / 16.0))
            elif tmp_i_num == 2:
                coefficientList.append((self.i_list[0][j][0], coefficient * 1.0 / 4.0))
            else:
                coefficientList.append((self.i_list[0][j][0], coefficient))
        return coefficientList

    def get_in_mean(self):
        m_list = []
        for j in range(len(self.i_list[0])):
            m = 0.0
            for i in range(4,6):
                m = m + float(self.i_list[i][j][2])
            m = m / 2.0
            m_list.append((self.i_list[0][j][0],m))
        return m_list
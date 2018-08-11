import pymysql
import datetime

import tushare as ts


class HearMysql:
    def __init__(self):
        # BK04401
        self.tables = ['bk0420', 'bk0421', 'bk0422', 'bk0424', 'bk0425', 'bk0427', 'bk0428', 'bk0429', 'bk0433',
                       'bk0436', 'bk0437', 'bk0438', 'bk0440', 'bk0447', 'bk0448', 'bk0450', 'bk0451', 'bk0454',
                       'bk0456', 'bk0457', 'bk0458', 'bk0459', 'bk0464', 'bk0465', 'bk0470', 'bk0471', 'bk0473',
                       'bk0474', 'bk0475', 'bk0476', 'bk0477', 'bk0478', 'bk0479', 'bk0480', 'bk0481', 'bk0482',
                       'bk0484', 'bk0485', 'bk0486', 'bk0537', 'bk0538', 'bk0539', 'bk0545', 'bk0546', 'bk0725',
                       'bk0726', 'bk0727', 'bk0728', 'bk0729', 'bk0730', 'bk0731', 'bk0732', 'bk0733', 'bk0734',
                       'bk0735', 'bk0736', 'bk0737', 'bk0738', 'bk0739', 'bk0740', 'bk0910']
        # 去掉工艺商品
        del self.tables[self.tables.index("bk0440")]
        self.cursor = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='1111',
                                      db='dfcf_industrys').cursor()
        self.sec_cursor = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='1111',
                                      db='follow_cyb').cursor()
        self.up_list_list = []

    def get_indst_six_list(self, begin_time, end_time):
        self.data_sorted(begin_time, end_time)
        six_list = []
        for up in self.up_list_list:
            six_list.append(up[5])
            # self.six_list.append(up[-6])
        return six_list

    def get_weight_six(self, begin_time, end_time):
        import utils.weight_point as wp
        self.data_sorted(begin_time, end_time)
        weights = {}
        import os
        import config.config as config
        os.chdir('C:\\Users\\baiqy\\Desktop\\tmp\\starfish\\2018\\cyb_notify')
        with open('config\\industry_weights-2018-7-21.info', 'r') as f:
            for line in f.readlines():
                weights['bk'+str(line.strip()).split("\t")[1][2:]] = int(line.strip().split("\t")[2])

        six_list = []
        for up in self.up_list_list:
            six_list.append(wp.weight_point(up,weights))
        return six_list

    def get_down_indst_six_list(self, begin_time, end_time):
        self.data_sorted(begin_time, end_time)
        down_six_list = []
        for up in self.up_list_list:
            # self.six_list.append(up[5])
            down_six_list.append(up[-6])
        return down_six_list

    def data_sorted(self, begin_time, end_time):
        self.up_list_list = []
        begin_time = begin_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
        for i in range(len(self.tables)):
            sql = "select industry_up from " + self.tables[i] + " where datetime>= \"" + begin_time + "\" and datetime <=\"" + end_time + "\";"
            self.cursor.execute(sql)
            up_list = self.cursor.fetchall()
            if i == 0:
                for up in up_list:
                    self.up_list_list.append([(self.tables[i], up[0])])
            else:
                for j in range(len(up_list)):
                    self.up_list_list[j].append((self.tables[i], up_list[j][0]))

        for i in range(len(self.up_list_list)):
            self.up_list_list[i] = self.sort_list(self.up_list_list[i])


    def get_cyb_up(self,begin_time):
        cyb = []
        df  = self.get_sec_data(begin_time, begin_time + datetime.timedelta(minutes=int(6.5 * 60)))
        if len(df) > 0 and len(df[0]) > 0:
            o_price = float(df[0][1]) - float(df[0][2])
            for i in range(len(df)):
                cyb.append(float(df[i][1]) / o_price)
        return cyb

    def sort_list(self, list, sort_index=1, reverse=True):
        return sorted(list, key=lambda list: list[sort_index], reverse=reverse)

    def get_sec_data(self,begin_time,end_time,table="sec_cyb"):
        begin_time = begin_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
        sql = "select * from " + table + " where datetime>= \"" + begin_time + "\" and datetime <= \"" + end_time + "\";"
        print(sql)
        self.sec_cursor.execute(sql)
        return self.sec_cursor.fetchall()

    def get_data(self,date,table='sec_cyb'):
        fail_check = 0
        import utils.trade_date as td
        if date == None:
            date = td.get_trade_date(5)
        hm = HearMysql()
        re_cyb = []
        six_list = []
        for d in date:
            cyb = []
            # ins_list = hm.get_indst_six_list(d, d + datetime.timedelta(minutes=int(6.5 * 60)))
            # # down_ins_list = hm.get_down_indst_six_list(d, d + datetime.timedelta(minutes=int(6.5 * 60)))
            # tmp_ins_list = []
            # # down_tmp_ins_list = []
            # for up in ins_list:
            #     tmp_ins_list.append(up[1])
            tmp_ins_list = self.get_weight_six(d, d + datetime.timedelta(minutes=int(6.5 * 60)))
            # for up in down_ins_list:
            #     down_tmp_ins_list.append(up[1])
            date = d.strftime('%Y-%m-%d %H:%M:%S')[:10]
            print(date)
            # df = ts.get_tick_data(code='399006', date=date, retry_count=3, pause=1.1, src='nt')
            df  = self.get_sec_data(d, d + datetime.timedelta(minutes=int(6.5 * 60)),table=table)
            if len(df) > 10 and len(df[0]) > 1:
                # o_price = float(df[0][1]) - float(df[0][2])
                for i in range(len(df)):
                    cyb.append(float(df[i][1]))
            else:
                fail_check = fail_check + 1
            tmp_list_1 = []
            tmp_list_2 = []
            for i in range(len(tmp_ins_list)):
                tmp_list_1.append(cyb[int(float(i) / float(len(tmp_ins_list)) * len(cyb))])
                # tmp_list_1.append(down_tmp_ins_list[int(float(i) / float(len(tmp_ins_list)) * len(down_tmp_ins_list))])
                tmp_list_2.append(tmp_ins_list[i])
            print(tmp_list_1)
            print(tmp_list_2)
            re_cyb.extend(tmp_list_1[50:])
            six_list.extend(tmp_list_2[50:])
        return re_cyb, six_list, fail_check

def weight_mean(list, mean_num=30):
    mean = 0
    t_list = []
    if len(list) > mean_num:
        t_list = list[-1 * mean_num:]
    else:
        t_list = list
    if len(t_list) > 0:
        i_sum = 0
        for i in range(len(t_list)):
            i_sum = i_sum + i + 1
        for i in range(len(t_list)):
            mean = mean + float(i + 1) / float(i_sum) * float(t_list[i])
    else:
        return 0
    return mean


def var(list):
    if len(list) > 50:
        # mean = sum(list)/float(len(list))
        vs = 0
        for l in list:
            vs = vs + (l - 0) ** 2
        re = (vs / float(len(list))) ** 0.5
        return re
    else:
        return 1


if __name__ == "__main__":
    hm = HearMysql()
    mon = 5
    day = 28

    # date = [datetime.datetime(year=2018,month=4,day=25,hour=9,minute=30,second=0),datetime.datetime(year=2018,month=4,day=25,hour=9,minute=30,second=0),datetime.datetime(year=2018,month=4,day=24,hour=9,minute=30,second=0),datetime.datetime(year=2018,month=4,day=23,hour=9,minute=30,second=0)]
    six_list = hm.get_indst_six_list(datetime.datetime(year=2018, month=mon, day=day, hour=9, minute=30, second=0),
                                     datetime.datetime(year=2018, month=mon, day=day, hour=15, minute=30, second=0))
    down_six_list = hm.get_down_indst_six_list(
        datetime.datetime(year=2018, month=mon, day=day, hour=9, minute=30, second=0),
        datetime.datetime(year=2018, month=mon, day=day, hour=15, minute=30, second=0))
    print(six_list)
    plot_list = []
    down_plot_list = []
    for up in six_list:
        plot_list.append(up[1])
    for up in down_six_list:
        down_plot_list.append(up[1])
    date = (datetime.datetime(year=2018, month=mon, day=day, hour=9, minute=30, second=0)).strftime(
        '%Y-%m-%d %H:%M:%S')[:10]
    print(date)
    # df = ts.get_tick_data(code='399006', date=date, retry_count=3, pause=1.1, src='nt')
    # cyb = []
    # print(df)
    # o_price = float(df.loc[0, 'price']) - float(df.loc[0, 'change'])
    # for i in df.index:
    #     cyb.append(float(df.loc[i, 'price']) / o_price)

    cyb = hm.get_cyb_up(datetime.datetime(year=2018, month=mon, day=day, hour=9, minute=30, second=0))
    tmp_list_1 = []
    list3 = []
    m_list_3 = []
    m_mean_list = []
    list4 = []

    def plot(list_1, list_2, list_3):
        global tmp_list_2, tmp_list_1, list3, m_mean_list, list4
        length = len(list_1)
        tmp_list_2 = []
        tmp_list_3 = []
        t_l_3 = []
        t_l_4 = []
        var_l = []
        for i in range(length):
            tmp_list_1.append((list_1[i] - 1) * 100)
            tmp_list_2.append(list_2[int(float(i) / float(length) * len(list_2))])
            tmp_list_3.append(list_3[int(float(i) / float(length) * len(list_3))])
            # cyb
            # k = 0.6120632594742823
            # b = 0.8750740185542881
            # sz50
            # k = 0.6087915519828788
            # b = 0.6601106693828737
            t_l_3.append((0.85 * tmp_list_1[-1] - tmp_list_2[-1] + 0.76))
            list3.append( weight_mean(t_l_3,4))#/ var(t_l_3))
            #y=0.86x+1.4  down_up_rate
            # down 6,,,-0.77
            #-0.1
            t_l_4.append((0.82 * weight_mean(tmp_list_1, 2) - 1.0 * weight_mean(tmp_list_3, 2) - 0.775) )
            list4.append(weight_mean(t_l_4))#/ var(t_l_4))
            # t_l_4.append((0.9 * weight_mean(tmp_list_3, 2) - 1.0 * weight_mean(tmp_list_2, 2) + 1.4))
            # list4.append(t_l_4[-1])
            # m_list_3.append(weight_mean(list_3,60))
            # var_l.append(var(list_3))
            # if var(list_3) < 0.2:
            #     print(list_3)
        print("var_l", var_l)
        import matplotlib.pyplot as plt
        print(tmp_list_1)
        plt.plot(tmp_list_1, 'r')
        print(tmp_list_2)
        plt.plot(tmp_list_2, 'b')
        print(list3)
        plt.plot(list3, 'g')
        # plt.plot(m_mean_list,'g')
        plt.plot(list4, "y")
        plt.show()

    plot(cyb, plot_list, down_plot_list)

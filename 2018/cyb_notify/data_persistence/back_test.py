import datetime
import tushare as ts
import os
import pymysql
os.chdir('C:\\Users\\baiqy\\Desktop\\tmp\\starfish\\2018\\cyb_notify')
import config.config as config

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
        self.cyb = []
        # self.cyb_list = []
        import utils.trade_date as td
        self.trade_dates = td.get_trade_date(30)
        self.cyb_bs = []
        self.cyb_b_index = -1

    def get_indst_six_list(self, begin_time, end_time):
        self.data_sorted(begin_time, end_time)
        six_list = []
        for up in self.up_list_list:
            six_list.append(up[5])
            # self.six_list.append(up[-6])
        return six_list

    def cyb_industry_factor(self,begin_time, end_time):
        cyb_weight = config.cyb_weight
        cyb = self.get_cyb_up(begin_time)
        self.data_sorted(begin_time, end_time)
        # cxg = self.get_cxg()
        res_list = []

        for i in range(len(self.up_list_list)):
            res = 0
            for j in range(len(self.up_list_list[i])):
                if cyb_weight.get('BK'+self.up_list_list[i][j][0][2:]) != None:
                    res = res + cyb_weight.get('BK'+self.up_list_list[i][j][0][2:])*(cyb[i]-self.up_list_list[i][j][1])
            res = res/sum(cyb_weight.values())
            res_list.append(res)
        return res_list

    def get_weight_industry(self,begin_time, end_time):
        self.data_sorted(begin_time, end_time)
        six_list = []
        for up in self.up_list_list:
            six_list.append(up[5])

    def get_weight_six(self, begin_time, end_time):
        import utils.weight_point as wp
        self.data_sorted(begin_time, end_time)
        weights = {}
        import os
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
            sql = "select industry_up from " + self.tables[
                i] + " where datetime>= \"" + begin_time + "\" and datetime <=\"" + end_time + "\";"
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
        # if len(df) > 0 and len(df[0]) > 0:
        #     o_price = float(df[0][1]) - float(df[0][2])
        #     for i in range(len(df)):
        #         cyb.append(float(df[i][1]) / o_price)
        for d in df:
            cyb.append(d[1])
        self.cyb = cyb
        return  self.cyb

    def sort_list(self, list, sort_index=1, reverse=True):
        return sorted(list, key=lambda list: list[sort_index], reverse=reverse)

    def get_sec_data(self,begin_time,end_time,table="sec_cyb"):
        begin_time = begin_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
        sql = "select * from " + table + " where datetime>= \"" + begin_time + "\" and datetime <= \"" + end_time + "\";"
        print(sql)
        self.sec_cursor.execute(sql)
        return self.sec_cursor.fetchall()

    def get_data(self,table='sec_cyb'):
        fail_check = 0
        import utils.trade_date as td
        date = td.get_trade_date(9)
        hm = HearMysql()
        re_cyb = []
        six_list = []
        for d in date:
            cyb = []
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

    def day_diff_list(self, date):
        # cyb_k,cyb_b = self.cyb_b(date)
        # self.cyb_bs.append((cyb_k,cyb_b))
        # print(len(self.cyb_bs),self.cyb_bs)
        cyb_bs = [0.7, 0.93425461114193864, 0.92577010461717701, 0.8572226522602906, 0.39991379525025555, 0.41924387094986615, 0.69498900698535537, 0.7832686320027531, 0.78819831925581296, 0.90770220937926771, 0.90846554756284581, 0.73787868891845998, 0.84591184715579759, 1.0107988845706863, 0.96315734298102096, 1.233259640083745, 1.2208382398314621, 1.19681679859111, 0.65509191850010173, 0.56632187447485038, 0.59357071140356543, 0.59195086122476959, 0.53869667331051052, 0.56287101562624486, 0.71253339530578652, 0.89098102335433671]
        begin_time =  datetime.datetime.combine(date.date(), datetime.time(hour=9, minute=29, second=59))
        end_time = datetime.datetime.combine(date.date(), datetime.time(hour=15, minute=00, second=59))
        weight_six = self.get_weight_six(begin_time, end_time)
        industry_diff = self.cyb_industry_factor(begin_time, end_time)
        # self.get_cyb_up(begin_time)
        # cache_list = []
        self.cyb_b_index = self.cyb_b_index + 1
        for i in range(len(weight_six)):
            cyb_industry = industry_diff[i]
            cyb_six_industry = 0.3*self.cyb[i] - weight_six[i] + cyb_bs[self.cyb_b_index]
            # cyb_diff = cyb_six_industry + wei_b * cyb_industry
            yield cyb_six_industry,cyb_industry

    def cyb_b(self,date):
        import data_persistence.leastsq as lt
        for i in range(len(self.trade_dates)):
            if self.trade_dates[i].day == date.day and self.trade_dates[i].month == date.month:
                if   i >= 5 :
                    return lt.cyb_result(self.trade_dates[i-5:i])
                elif i < 5 :
                    return 0.8,0.7

        #     cache_list.append(cyb_diff)
        # return cyb_six_industry ,industry_diff

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

class utils:
    @staticmethod
    def get_base_list():
        return
if __name__ == "__main__":
    hm = HearMysql()
    mon = 7
    day = 18
    cyb_b = 0.7
    begin_time = datetime.datetime(year=2018, month=mon, day=day, hour=9, minute=30, second=0)
    end_time = datetime.datetime(year=2018, month=mon, day=day, hour=15, minute=30, second=0)
    weight_six = hm.get_weight_six(begin_time,end_time)
    industry_diff = hm.cyb_industry_factor(begin_time,end_time)
    cyb = hm.cyb
    base = 0
    change_0_time = 0
    base_factor = 0
    plot_list1 = []
    plot_list2 = []
    plot_list3 = []
    for i in range(len(weight_six)):
        factor_ = 0
        cyb_industry = industry_diff[i]
        cyb_six_industry = cyb[i]-weight_six[i]+cyb_b
        if cyb_six_industry < 0 and cyb_industry < 0:
            factor_ = -1
        elif cyb_six_industry > 0 and cyb_industry > 0:
            factor_ = 1
        raw_f = factor_ * (abs(cyb_six_industry * industry_diff[i])) ** 0.5
        tmp_base_factor = base_factor
        base_factor = base_factor + raw_f

        if i > 20 :
           if tmp_base_factor * base_factor < 0:
               change_0_time = change_0_time + 1
               base = raw_f

        plot_list2.append(raw_f )
        # plot_list3.append((cyb[i]-weight_six[i]+cyb_b)+industry_diff[i])
        plot_list1.append(raw_f - base)
    date = (datetime.datetime(year=2018, month=mon, day=day, hour=9, minute=30, second=0)).strftime(
        '%Y-%m-%d %H:%M:%S')[:10]

    def plot(list_1, list_2,list_3=[],list_4=[]):
        import matplotlib.pyplot as plt
        print(list_1)
        plt.plot(list_1, 'r')
        print(list_2)
        plt.plot(list_2, 'b')
        if list_3 != []:
            plt.plot(list_3, 'y')
        if list_4 != []:
            plt.plot(list_4, 'g')
        plt.show()

    plot(cyb, plot_list2,plot_list3,plot_list1)

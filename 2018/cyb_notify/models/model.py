import datetime
import utils.email_notify as en
import pymysql

class model:
    def __init__(self,log=None):
        self.logger = log
        self.begin_delta_time = datetime.timedelta(seconds=360)
        self.std_buy = -0.826
        self.std_sell = 0.37
        # 0.34453064057819965, -0.58066720314595333
        self.amEnd = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=11, minute=30, second=30))
        self.pmBegin = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=13, minute=0, second=0))

        self.last_report_time = None
        self.tmp_six_indst = None

        self.max_diff = 0
        self.min_diff = 0

        self.diff_change_0_time = 0
        self.base_change_0_time = 0
        self.base_factor = 0
        self.tmp_diff = 0
        self.base = 0

        self.max_diff_time = None
        self.min_diff_time = None

        self.analysis_cursor = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='1111',
                                          db='analysis')
        self.diff_list = []

    #1为500，2为50，3为不做操作，0为空仓
    # 0.38850739380403643, -0.3196062508549381, 0.18273999548929595, 0.25591966139562783
    #0.3885, -0.31960, 0.18274, 0.256
    def position(self,six_indst = 0.2,cyb_real=None, sz50_real=None,cyb_b=0.73,sz50_b=0.73,cyb_industry=0.0):
        if self.tmp_six_indst != six_indst:
            sz50_diff = sz50_real - six_indst + sz50_b
            self.tmp_six_indst = six_indst
            # cyb_six_industry = 0.256 * cyb_real - (1-0.183)*six_indst + cyb_b + 0.183*cyb_industry#- cyb_b2
            # 0.37, -0.826, 0.266
            cyb_diff = 0.266 * cyb_real + (- six_indst + cyb_b)# + 0.2415 * cyb_industry
            # base_cyb_diff = self.base_diff(cyb_diff)
            self.diff_list.append(cyb_diff)
            if len(self.diff_list) > 10:
                del self.diff_list[0]
            cyb_diff = self.weight_mean(self.diff_list)
            self.store_analysis(cyb_real, cyb_industry, 0, six_indst, cyb_b)
            self.store_m(cyb_diff)
            sell_notify = False
            buy_notify = False
            msg = ""
            if cyb_diff > self.std_sell:
                sell_notify = True
            if cyb_diff < self.std_buy:
                buy_notify = True
            if sell_notify:
                msg = " <font color=\"red\">sell_point_time : "+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"</font>"
                en.email_notify(title="sell notify", msg=msg)
                import time
                time.sleep(30)
            if buy_notify:
                msg = " <font size=\"5\" face=\"verdana\" color=\"red\">buy_point_time : " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "</font>"
                en.email_notify(title="buy notify", msg=msg)
                import time
                time.sleep(30)
            msg = msg  + "vmware <br> cyb_diff : " + str(cyb_diff)  + "<br> cyb_min_diff : " + str(self.min_diff)  +" , cyb_min_diff_time : " + str(self.min_diff_time) +"<br> cyb_max_diff : " + str(self.max_diff) +" , cyb_max_diff_time : " + str(self.max_diff_time) +"<br> cyb_std_sell : " + str(self.std_sell) +"<br> cyb_std_buy : " + str(self.std_buy)+" <br> cyb_industry : " + str(cyb_industry) + "<br> six_indst : "+str(six_indst)+"<br> six_i : " + str(six_indst) +  "<br> a50_diff : " + str(sz50_diff) + " <br> sz50_real : " + str(sz50_real) + "<br> cyb_real : " + str(cyb_real) + "<br> cyb_b : " + str(cyb_b) + "<br> sz50_b : " + str(sz50_b)

            if (self.last_report_time == None or self.last_report_time + datetime.timedelta(seconds=300) < datetime.datetime.now()) and datetime.datetime.now() > datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=9, minute=36, second=0)):
                self.last_report_time = datetime.datetime.now()
                en.email_notify(title="5 minutes notify",msg=msg)
            self.logger.info(msg)

    def weight_mean(self,list, mean_num=5):
        mean = 0.0
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
                mean = mean + float(i + 1) / float(i_sum) * t_list[i]
        else:
            return 0
        return mean

    def var(self,list):
        if len(list) > 50:
            mean = 0
            vs = 0
            for l in list:
                vs = vs + (l-mean)**2
            re = (vs/float(len(list)))**0.5
            return re
        else:
            return 1

    def store_m(self,cyb_diff):
        if self.max_diff < cyb_diff:
            self.max_diff = cyb_diff
            self.max_diff_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.min_diff > cyb_diff:
            self.min_diff = cyb_diff
            self.min_diff_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    def base_diff(self,diff):
        self.base_factor = self.base_factor + diff
        now = datetime.datetime.now()
        if now > datetime.datetime.combine(now.date(),datetime.time(hour=9,minute=40,second=0)):
            if self.tmp_diff * diff < 0:
                self.diff_change_0_time = self.diff_change_0_time + 1
            if diff * self.base_factor < 0:
                self.base_change_0_time = self.base_change_0_time + 1
                self.tmp_diff = diff
                return 0
            if self.base_change_0_time > 0 and diff * self.base_factor > 0 and self.base == 0:
                self.base = diff/2.0
        else:
            return diff

        self.tmp_diff = diff

        if diff * self.base_factor > 0:
            return diff - self.base
        else :
            return 0

    def store_analysis(self,cyb,cyb_industry_diff, cyb_six_industry_diff,six_indst,cyb_b):
        try:
            sql = "replace into analysis_data (datetime, cyb,cyb_industry_diff, cyb_six_industry_diff,six_indst,cyb_b) VALUES (%s,%s,%s,%s,%s,%s);"
            self.analysis_cursor.cursor().execute(sql,(datetime.datetime.now(), cyb,cyb_industry_diff, cyb_six_industry_diff,six_indst,cyb_b))
            self.analysis_cursor.commit()
        except Exception as e:
            # 发生错误时回滚
            print(e)
            self.analysis_cursor.rollback()

if __name__ == "__main__":
    m = model()
    print(m.base_diff(-1))
    print(m.base_diff(-1))
    m.position(six_indst=-1,cyb_real=1,sz50_real=-1,cyb_b=0.7,sz50_b = 0.6,cyb_industry=1)
    m.position(six_indst=-1.1, cyb_real=1, sz50_real=-1, cyb_b=0.7, sz50_b=0.6, cyb_industry=1)
    m.position(six_indst=-1, cyb_real=1, sz50_real=-1, cyb_b=0.7, sz50_b=0.6, cyb_industry=1)


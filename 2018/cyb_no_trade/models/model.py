import datetime
import utils.email_notify as en
import pymysql
class model:
    def __init__(self,log=None):
        self.logger = log
        self.begin_delta_time = datetime.timedelta(seconds=400)
        self.mean_delta_time = datetime.timedelta(seconds=1200)
        self.std_buy = -0.6
        self.std_sell = 0.6

        self.industry_emtry = 0.27
        self.cyb_factor_list = []
        self.cyb_diff_list = []
        self.sz50_diff_list = []
        self.sz50_factor_list = []
        self.industry_six_list = []
        self.down_cyb_diff_list = []
        self.amEnd = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=11, minute=30, second=30))
        self.pmBegin = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=13, minute=0, second=0))
        self.cyb_real_data = None
        self.sz50_real_data = None
        self.wait_time = 25
        self.buy_time = 0
        self.sell_time = 0
        self.sell_check_point = None
        self.buy_check_point = None
        self.last_report_time = None
        self.tmp_six_indst = None
        self.max_diff = 0
        self.min_diff = 0

        self.diff_change_0_time = 0
        self.change_0_time = 0
        self.base_factor = 0
        self.tmp_diff = 0
        self.base = 0
        self.tmp_base_factor = 0

        self.max_diff_time = None
        self.min_diff_time = None

        self.analysis_cursor = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='1111',
                                          db='analysis')

    #1为500，2为50，3为不做操作，0为空仓
    def position(self, time, six_indst = 0.2,cyb_real=None, sz50_real=None,cyb_b=0.73,sz50_b=0.73,cyb_industry=0.0):

        if self.tmp_six_indst != six_indst:
            sz50_diff = sz50_real - six_indst + sz50_b
            cyb_b2 = 0
            # if self.std_buy - sz50_diff > 0:
            #     cyb_b2 = self.std_buy - sz50_diff
            self.tmp_six_indst = six_indst

            cyb_six_industry = cyb_real - six_indst + cyb_b #- cyb_b2
            factor_ = 0
            if cyb_six_industry < 0 and cyb_industry < 0:
                factor_ = -1
            elif cyb_six_industry > 0 and cyb_industry > 0:
                factor_ = 1
            cyb_diff =  factor_ * (abs(cyb_six_industry * cyb_industry))**0.5
            base_cyb_diff = self.base_diff(cyb_diff)
            self.store_m(base_cyb_diff)
            msg = "<br> base_cyb_diff : " + str(base_cyb_diff)  + "<br> cyb_diff : " + str(cyb_diff)  + "<br> cyb_min_diff : " + str(self.min_diff)  +" , cyb_min_diff_time : " + str(self.min_diff_time) +"<br> cyb_max_diff : " + str(self.max_diff) +" , cyb_max_diff_time : " + str(self.max_diff_time) +"<br> cyb_std_sell : " + str(self.std_sell) +"<br> cyb_std_buy : " + str(self.std_buy)+" <br> cyb_industry : " + str(cyb_industry) + "<br> cyb_six_indestry : " + str(cyb_six_industry) + "<br> six_indst : "+str(six_indst)+"<br> six_i : " + str(six_indst) +  "<br> a50_diff : " + str(sz50_diff) + " <br> sz50_real : " + str(sz50_real) + "<br> cyb_real : " + str(cyb_real) + "<br> cyb_b : " + str(cyb_b) + "<br> sz50_b : " + str(sz50_b)


            if self.last_report_time == None or self.last_report_time + datetime.timedelta(seconds=100) < datetime.datetime.now():
                self.last_report_time = datetime.datetime.now()
                en.email_notify(title="2 minutes notify",msg=msg)
            self.logger.info(msg)
            if time < datetime.datetime.combine(time.date(),datetime.time(hour=9,minute=30,second=0)) + self.begin_delta_time :
                self.logger.info("wait...")
                return 3

    def weight_mean(self,list, mean_num=60):
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
        self.tmp_base_factor = self.base_factor
        self.base_factor = self.base_factor + diff
        now = datetime.datetime.now()
        if now > datetime.datetime.combine(now.date(),datetime.time(hour=9,minute=40,second=0)):
            if self.tmp_diff * diff < 0:
                self.diff_change_0_time = self.diff_change_0_time + 1
            if self.tmp_base_factor * self.base_factor < 0:
                self.change_0_time = self.change_0_time + 1
                self.base = diff
        else:
            return diff

        self.tmp_diff = diff

        if self.diff_change_0_time <= 0:
            return diff
        elif self.tmp_base_factor * diff > 0:
            return diff
        elif self.change_0_time <= 0:
            return 0
        else:
            return diff - self.base




if __name__ == "__main__":
    m = model()
    print(m.base_diff(1))
    print(m.position(datetime.datetime.now(), a50_factor=0.2, cyb_factor=0.4, cyb_real=2, sz50_real=3))

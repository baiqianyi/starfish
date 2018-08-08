import datetime
import tushare as ts
import time
import requests
import config.config as config
import os


os.chdir('C:\\Users\\baiqy\\Desktop\\tmp\\starfish\\2018\\cyb_notify')
class judge_industry:
    def __init__(self,dfcf_data):
        self.dfcf_data = dfcf_data
        self.data = self.dfcf_data.industrys()
        self.stock_data = None
        self.maxUpIndustryPlateList = self.data[0:4]
        self.sixIndustry = self.data[5][1]
        self.firstBatchRaisedStop = {}
        self.industryPreSatData = []
        self.industryPreSatisfied = []
        self.cyb = self.cyb_real()


    def get_six_industry(self):
        return self.sixIndustry

    def preSatisfied(self):
        self.industryPreSatisfied = []
        #用行业的平均涨幅评估大盘行情。行情不好不能做。
        # if self.sixIndustry < 0.4:
        #     return
        # if datetime.datetime.now() > datetime.datetime.combine(datetime.datetime.now().date(),datetime.time(hour=10,minute=0,second=0)):
        #     return
        for i in range(len(self.maxUpIndustryPlateList)):
            if self.maxUpIndustryPlateList[i][3] > 9.8 and self.maxUpIndustryPlateList[i][1] > 1:
                            self.industryPreSatisfied.append(self.maxUpIndustryPlateList[i])

    def sz50_factor(self):
        factor = 1.0
        num = 0
        for i in range(len(self.data)):
            if self.data[i][0] == 'BK0475' or self.data[i][0] == "BK0473" or self.data[i][0] == "BK0474" or self.data[i][0] == "BK0477":
                factor = factor*(1-float(i+1)/float(len(self.data)+0.01))
                num = num + 1
        if num != 4:
            return 0
        else:
            return factor**0.25

    def cyb_factor(self):
        factor = 1.0
        num = 0
        for i in range(len(self.data)):
            if self.data[i][0] == 'BK0737' or self.data[i][0] == 'BK0728':
                factor = factor * (1 - float(i + 1) / float(len(self.data) + 0.01))
                num = num + 1
                break
        if num != 2:
            return 0
        else:
            return factor**0.5

    def cyb_industry_factor(self):
        cyb_weight = config.cyb_weight
        # cxg = self.get_cxg()
        res = 0
        cyb = self.cyb * 0.9
        for i in range(len(self.data)):
            if cyb_weight.get(self.data[i][0]) != None:
                res = res + cyb_weight.get(self.data[i][0])*(cyb-self.data[i][1])
        res = res/sum(cyb_weight.values())
        return res

    def get_cxg(self):
        url = '''http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=BK05011&sty=CTBF&st=z&sr=&p=&ps=&cb=var%20pie_data=&js=(x)&token=28758b27a75f62dc3065b81f7facb365&_=1532611140585'''
        up = self.downLoad(url).split(",")[4][:-1]
        return float(up)

    def cyb_real(self):
        # ''etf
        cyb = ts.get_realtime_quotes('cyb')  # Single stock symbol
        self.cyb = (float(cyb.loc[0, 'price']) / float(cyb.loc[0, 'pre_close']) - 1)*100
        time.sleep(0.4)
        return self.cyb

    def sz50_real(self):
        sz50 = ts.get_realtime_quotes('sz50')  # Single stock symbol
        time.sleep(0.4)
        return (float(sz50.loc[0, 'price']) / float(sz50.loc[0, 'pre_close']) - 1)*100

    def getIndustrySix(self):
        return self.dfcf_data.getIndustrySix()

    def getDownIndustrySix(self):
        return self.dfcf_data.getDownIndustrySix()

    def weight_six_industry(self):
        w_in = self.dfcf_data.weight_six_industry()
        if w_in != None:
            return w_in
        else:
            return self.cyb_real()

    def downLoad(self,url):
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Cache-Control': 'max-age=0',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
                   }
        print(url)

        s = requests.session()
        s.headers.update(headers)
        r = s.get(url=url, params={'wd': 'python'}, timeout=10)  # 带参数的GET请求
        import time
        time.sleep(1)
        return r.text

    # def getCodeData(self,usedPlates=[]):
    #     self.preSatisfied()
    #     if usedPlates != []:
    #         self.industryPreSatData = []
    #         if self.industryPreSatisfied != []:
    #             for plate in self.industryPreSatisfied:
    #                 for usedPlate in usedPlates:
    #                     if plate[0] != usedPlate:
    #                         self.industryPreSatData.append(self.dfcf_data.industry_stock(plate))
    #     else:
    #         self.industryPreSatData = []
    #         if self.judgeSZ50() == True:
    #             self.industryPreSatData.append("510050")
    #             return self.industryPreSatData
    #         if self.industryPreSatisfied != []:
    #             for plate in self.industryPreSatisfied:
    #                 industry_stock_data = self.dfcf_data.industry_stock(plate)
    #                 self.industryPreSatData.append((industry_stock_data,plate,len(industry_stock_data)))
    #     return self.industryPreSatData


if __name__ == "__main__":
    import utils.dfcf_data as dfcf_data
    d = dfcf_data.IndustryData()
    judge = judge_industry(d)
    print (judge.get_cxg())
    print(str(judge.weight_six_industry()))
    print(judge.sz50_real())
    mean = judge.get_six_industry()
    a50efficient = judge.sz50_factor()
    cyb = judge.cyb_factor()
    print(judge.cyb_industry_factor())
    print(judge,mean,a50efficient,cyb)
    print (judge.cyb_real(),judge.sz50_real())
    import models.n_model as model
    import logging
    import logging.handlers
    import utils.dfcf_data as dfcf_data

    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG)

    rf_handler = logging.handlers.TimedRotatingFileHandler('sz50_cyb.log.2018-04-24', when='midnight', interval=1, backupCount=7,
                                                           atTime=datetime.time(0, 0, 0, 0))
    rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(rf_handler)
    model = model.model(log=logger)
    print(model.position(datetime.datetime.now(), mean, a50efficient,cyb_real=judge.cyb_real(),sz50_real=judge.sz50_real()))
#[([('601969', 10.06), ('000825', 10.02), ('600507', 7.36), ('000898', 5.26), ('600782', 5.01), ('000717', 4.34), ('600581', 3.92), ('002110', 3.88), ('000932', 3.74), ('601003', 3.62), ('600019', 2.9), ('000655', 2.78), ('000959', 2.62), ('600282', 2.52), ('603878', 2.43), ('000761', 2.39), ('600569', 2.29), ('600808', 1.97), ('000708', 1.95), ('601005', 1.9)]]


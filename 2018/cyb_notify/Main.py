import os
cur_path = os.path.abspath(".")
os.chdir(cur_path)

import utils.industry_judge as factors
import datetime as dt
import time
import models.model as model
import logging.handlers
import utils.dfcf_data as dfcf_data
import configparser
import data_persistence.leastsq as leastsq

logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG)

rf_handler = logging.handlers.TimedRotatingFileHandler('logs\\cyb.log', when='midnight', interval=1, backupCount=7, atTime=dt.time(0, 0, 0, 0))
rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(rf_handler)

amBegin = dt.datetime.combine(dt.datetime.now().date(),dt.time(hour=9,minute=30,second=30))
amEnd = dt.datetime.combine(dt.datetime.now().date(),dt.time(hour=11,minute=30,second=0))
pmBegin = dt.datetime.combine(dt.datetime.now().date(),dt.time(hour=13,minute=0,second=0))
pmEnd = dt.datetime.combine(dt.datetime.now().date(),dt.time(hour=15,minute=0,second=0))
buyBegin = dt.datetime.combine(dt.datetime.now().date(),dt.time(hour=9,minute=44,second=25))

oneMinuteOpenTime = 0
allStocksOpen = None
model = model.model(log=logger)
dfcf = dfcf_data.IndustryData()
cyb_k, cyb_b = leastsq.cyb_result()
sz50_k, sz50_b = leastsq.sz50_result()
past_config = configparser.ConfigParser()  # 注意大小写
past_config.read("config\\past.info")  # 配置文件的路径
keep_alive_time = 0

while True:
    try:
        now = dt.datetime.now()
        judgd_factors = factors.judge_industry(dfcf)
        mean = judgd_factors.get_six_industry()
        a50_f = judgd_factors.sz50_factor()
        cyb_f = judgd_factors.cyb_factor()
        cyb_real = judgd_factors.cyb_real()
        sz50_real = judgd_factors.sz50_real()
        industry_six = judgd_factors.weight_six_industry()
        down_industry_six = judgd_factors.getDownIndustrySix()
        cyb_industry = judgd_factors.cyb_industry_factor()
        print(judgd_factors,mean,a50_f,cyb_f,sz50_real,cyb_real)
        if not (now.date().isoweekday() == 6 or now.date().isoweekday() == 7):
            if (amBegin < now and now < amEnd) or (pmBegin < now and now < pmEnd) :
                model.position(six_indst=industry_six,cyb_real=cyb_real, sz50_real=sz50_real,cyb_b=cyb_b,sz50_b=sz50_b,cyb_industry=cyb_industry)
            elif now > pmEnd:
                break
            else:
                time.sleep(1)
        else:
            time.sleep(1)
    except Exception as e:
        logger.error(e)
        time.sleep(1)
        continue
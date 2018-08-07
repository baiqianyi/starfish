import tushare as ts
import datetime
import os
import re

print(os.getcwd())
os.chdir('C:\\Users\\baiqy\\Desktop\\quant\\cyb_no_trade')
print(os.getcwd())

date = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')[:10]
print (date)
df = ts.get_tick_data(code='399006' ,date=date, retry_count=3, pause=1.1,src='nt')
cyb = []
o_price = float(df.loc[0,'price'])

for i in df.index:
    cyb.append(float(df.loc[i,'price'])/o_price)

print(cyb)
#print(float(df.loc[:,'pre_close'])/float(df.loc[0,'price']))

means = []
f = open("sz50_cyb.log."+date, "rb", buffering=0)
ls = f.readlines()
tip = 0
m_tip = 0
m_mean = 0
m_mean_list = []
for l in ls:
    if "mean : " in str(l):
        tip = tip + 1
        m_tip = m_tip + 1
        if tip % 2 == 0:
            mean = str(l)[str(l).index(" m : ")+4:][:5]
            if not "f" in mean:
                means.append(float(mean))
        # m = str(l)[str(l).index(" m : ") + 7:][:5]
        # if m_tip %40 == 0 :
        #     m_mean = 0
        # elif m_tip %40 != 39:
        #     if not "m" in m:
        #        m_mean = m_mean + float(m)
        # else:
        #     m_mean = m_my
                # ean / 40.0
        #     m_mean_list.append(m_mean)
            # print (float(str(l)[str(l).index("mean : ")+7:][:8]))
print (m_mean_list)
print (means)
# (cyb,mean)
tmp_list_1 = []
tmp_list_2 = []
list_3 = []
def plot(list_1,list_2):
    global tmp_list_2,tmp_list_1,list_3,m_mean_list
    length = len(list_1)
    tmp_list_2 = []
    for i in range(length):
        tmp_list_1.append((list_1[i]-1)*100)
        tmp_list_2.append(list_2[int(float(i)/float(length)*len(list_2))])
        list_3.append((tmp_list_1[-1]-1*tmp_list_2[-1]))

    import matplotlib.pyplot as plt
    plt.plot(tmp_list_1,'r')
    plt.plot(tmp_list_2,'b')
    plt.plot(list_3,'g')
    # plt.plot(m_mean_list,'g')
    plt.show()

plot(cyb,means)

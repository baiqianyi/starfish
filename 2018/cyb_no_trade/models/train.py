import utils.optimization as op
import models.backtest as backtest
import models.model as model
import models.n_model as n_model
import params.params as params
import matplotlib.pyplot as plt
# self,confirmTimeRange=60,cyb_a=1.0,cyb_b=0.0,a50_a=0.5,a50_b=0.0,a50_i=0.5,nullPosition_a=-0.5,nullPosition_b=0.5):

bk = backtest.BackTest()
bk.init()

def target(param = [60,1.0]):
    # param = params.Params(confirmTimeRange=param[0],cyb_a=param[1],cyb_b=param[2],a50_a=param[3],a50_b=param[4],a50_i=param[5],nullPosition_a=param[6],nullPosition_b=param[7])
    assetsList = bk.backTest(model=n_model.model(param))
    return assetsList[-1][1]/float(assetsList[0][1])

assetsTmp = []
jizhuns_1 = []
jizhuns_2 = []
# param = params.Params(77.27002356461057, 1.130201296374449, 0.6292347628432234, 0.41534654636643015, 0.35097135129373974, 2.183442215192209, -1.3263119040871745, 1.5286825646700342)
# param = [200,2.5]
assetsList= bk.backTest(model=n_model.model())

for assets in assetsList:
    assetsTmp.append(assets[1])
for jz in bk.a50DataList:
    jizhuns_1.append(jz[1]/bk.a50DataList[0][1]*1000.0)
for jz in bk.zz500DataList:
    jizhuns_2.append(jz[1]/bk.zz500DataList[0][1]*1000.0)
plt.plot(assetsTmp,'b')
plt.plot(jizhuns_1,'r')
plt.plot(jizhuns_2,'g')
plt.show()
print(assetsTmp[-1]/float(assetsTmp[0]))
# opt=op.Optimization()
# opt.optimizate(func=target,initValue=[40, 1.0],rangeList=[(40,600),(0.1,2.5)],stopTime=19,initPointNum=12,variateRate=0.1,evolutionRate=0.04)
# opt.optimizate(func=target,initValue=[40, 3.0, 1.0, 1.0,2.5, 2.0, -2.0, 3.0978067876429032],rangeList=[(40,600),(2,10.0),(-1.5,2.3),(0.0,2.8),(-0.0,3.8),(1.0,5.1),(-4.4,-0.0),(0.0,4.6)],stopTime=19,initPointNum=12,variateRate=0.1,evolutionRate=0.05)



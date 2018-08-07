import datetime
import pymysql
import dao.secDataDao as sec_data
import dao.a50cybCircleDao as quant_data
import dao.new_a50zz500Dao as new_a50zz500Dao
import dao.new_factors
class BackTest:
    def __init__(self):
        self.secdb = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='sec_data')
        self.industrydb = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='sec_industrys')
        self.sec_dao = sec_data.SecDataDao()
        self.new_a50zz500Dao = new_a50zz500Dao.A50ZZ500Dao()
        self.new_factors = dao.new_factors.new_factors()
        self.quantDao = quant_data.A50CYBDao()
        #需要初始化的数据
        self.industryMeanList = []
        self.a50IndustrCoefficientList = []
        self.timeRail = self.getTimeRail()
        #[（time,assets）]
        # self.assetsList = []
        self.initAsset = 1000
        #创业板，a50价格数据
        self.cybDataList = []
        self.a50DataList = []
        #暂存数据
        self.tmpHoldCode = None
        self.positionNum = 0

    #初始化数据
    def init(self):
        # self.zhongzheng500List = self.sec_dao.getDataBetween("sh000905")
        self.a50IndustrCoefficientList = self.dataFilter(self.new_factors.get_a50_factor())
        self.industryMeanList = self.dataFilter(self.new_factors.get_in_mean())
        # self.zz500DataList = self.dataFilter(self.new_a50zz500Dao.get_zz500())
        # self.a50DataList = self.dataFilter(self.new_a50zz500Dao.get_a50())

    def backTest(self,model):
        # tmpPositionNum = 0
        assetsList = [(self.industryMeanList[0][0],1000.0)]

        changePositionTime = 0
        tmpPositionNo = 0
        date = None

        for i in range(len(self.industryMeanList)):
            time = self.industryMeanList[i][0]
            if time.date() != date:
                date =time.date()
                changePositionTime = 0

            if changePositionTime >= 2 :
                assetsList.append((time, self.positionNoAsset(assetsList, tmpPositionNo, i, False)))
            else:
                positionNo = model.position(time, self.industryMeanList[i][1],self.a50IndustrCoefficientList[i][1])
                #不调仓
                if tmpPositionNo == positionNo or positionNo == 3:
                    assetsList.append((time, self.positionNoAsset(assetsList,tmpPositionNo,i,False)))
                #需要调仓
                elif changePositionTime == 0:
                    assetsList.append((time, self.positionNoAsset(assetsList,positionNo,i,True)))
                    changePositionTime = changePositionTime + 1
                    tmpPositionNo = positionNo
                #之前是空仓的话可以调仓
                elif tmpPositionNo == 2:
                        assetsList.append((time, self.positionNoAsset(assetsList,positionNo,i,True)))
                        changePositionTime = changePositionTime + 1
                        tmpPositionNo = positionNo
                elif changePositionTime < 2 and tmpPositionNo != 2:
                    assetsList.append((time, self.positionNoAsset(assetsList, tmpPositionNo, i, False)))

            # if changePositionTime >= 2 or (changePositionTime < 2 and tmpPositionNo != 2):
            #     assetsList.append((time, self.positionNoAsset(assetsList, tmpPositionNo, self.positionNum, i, False)))
            # else:
            #     positionNo = model.position(time, self.industryMeanList[i][1], self.a50IndustrCoefficientList[i][1])
            #     #不调仓
            #     if tmpPositionNo == positionNo:
            #         assetsList.append((time, self.positionNoAsset(assetsList,positionNo,self.positionNum,i,False)))
            #     #需要调仓
            #     elif changePositionTime == 0:
            #         assetsList.append((time, self.positionNoAsset(assetsList,positionNo,self.positionNum,i,True)))
            #         changePositionTime = changePositionTime + 1
            #         tmpPositionNo = positionNo
            #     #之前是空仓的话可以调仓
            #     elif tmpPositionNo == 2:
            #             assetsList.append((time, self.positionNoAsset(assetsList,positionNo,self.positionNum,i,True)))
            #             changePositionTime = changePositionTime + 1
            #             tmpPositionNo = positionNo
            #         # else:
            #         #     assetsList.append((time,  self.positionNoAsset(assetsList,tmpPositionNo,self.positionNum,i,False)))
        return assetsList
    def a50Effect(self,tmpSortedIndustry):
        for i in range(len(tmpSortedIndustry)):
            # print(i,j,len(topIndustryData),len(topIndustryData[i]))
            if tmpSortedIndustry[i][1] == "881155" or tmpSortedIndustry[i][1] == "881157":
                coefficient = float(i) / float(len(tmpSortedIndustry)) * coefficient

    def getTimeRail(self):
        cursor = self.industrydb.cursor()
        sql = "select datetime from industry_1;"
        cursor.execute(sql)
        dt = list(cursor.fetchall())
        length = len(dt)
        i=0
        while True:
            time = dt[i][0]
            if not time.time() >= datetime.time(hour=9,minute=30,second=0) and time.time() <= datetime.time(hour=15,minute=0,second=0):
                del dt[i]
                length = len(dt)
            i = i + 1
            if i >= length:
                break

        for i in range(len(dt)):
            if dt[i][0] >= datetime.datetime(year=2010,month=6,day=1,hour=0,minute=0,second=0):
                dt = dt[i:]
                break
        return dt

    # 1为500，2为50，3为不做操作，0为空仓
    def positionNoAsset(self,assetsList, positionNo,i,is_change_position):
        # print (assetsList[-1][1])
        asset = float(assetsList[-1][1])
        if is_change_position:
            if positionNo == 1:
                self.positionNum = asset / float(self.zz500DataList[i][1])
            elif positionNo == 2:
                self.positionNum = asset / float(self.a50DataList[i][1])
            return asset
        else:
            if positionNo == 1:
                return self.positionNum * self.zz500DataList[i][1]
            elif positionNo == 2:
                return self.positionNum * self.a50DataList[i][1]
            elif positionNo == 0:
                return asset
            elif positionNo == 3:
                return asset


    def dataFilter(self,dataList):
        filteredData = []
        tmpIndex = 0
        if isinstance(dataList[0][0], str):
            for time in self.timeRail:
                for i in range(tmpIndex,len(dataList)-1):
                    if datetime.datetime.strptime(dataList[i][0],'%Y-%m-%d %H:%M:%S') <= time[0] and datetime.datetime.strptime(dataList[i+1][0],'%Y-%m-%d %H:%M:%S') >= time[0]:
                        if abs(time[0].timestamp()-datetime.datetime.strptime(dataList[i][0],'%Y-%m-%d %H:%M:%S').timestamp()) > abs(time[0].timestamp()-datetime.datetime.strptime(dataList[i+1][0],'%Y-%m-%d %H:%M:%S').timestamp()):
                            filteredData.append([datetime.datetime.strptime(dataList[i+1][0],'%Y-%m-%d %H:%M:%S'),dataList[i+1][1]])
                        else:
                            filteredData.append([datetime.datetime.strptime(dataList[i][0],'%Y-%m-%d %H:%M:%S'),dataList[i][1]])
                        tmpIndex = i
                        break
                    elif datetime.datetime.strptime(dataList[i][0],'%Y-%m-%d %H:%M:%S') > time[0]:
                        filteredData.append([datetime.datetime.strptime(dataList[i][0],'%Y-%m-%d %H:%M:%S'),dataList[i][1]])
                        tmpIndex = i
                        break
        else:
            for time in self.timeRail:
                for i in range(tmpIndex, len(dataList)-1):
                    if dataList[i][0] <= time[0] and dataList[i + 1][0] >= time[0]:
                        if abs(time[0].timestamp() - dataList[i][0].timestamp()) > abs(
                                        time[0].timestamp() - dataList[i + 1][0].timestamp()):
                            filteredData.append(dataList[i + 1])
                        else:
                            filteredData.append(dataList[i])
                        tmpIndex = i
                        break
                    elif dataList[i][0] > time[0]:
                        filteredData.append(dataList[i])
                        tmpIndex = i
                        break

        return filteredData

def generateList(list,num):
    tmp = []
    for l in list:
        tmp.append(l[num])
    return tmp
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    backTest =  BackTest()
    backTest.init()
    plt.plot(backTest.timeRail[-1441*1:],generateList(backTest.industryMeanList[-1441*1:],1),'r')
    # plt.show()
    # plt.plot(backTest.timeRail[1441 * 5:1441 * 6], generateList(backTest.industryMeanList[1441 * 5:1441 * 6], 1), 'r')
    # plt.plot(backTest.timeRail[-1441*1:],generateList(backTest.a50IndustrCoefficientList[-1441*1:],1),'bo')
    plt.show()
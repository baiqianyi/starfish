import config
import dao.industryDao as iDao

class SortedIndustryCode:
    def __init__(self):
        self.data = []
        self.iDao =  iDao.IndustryDao()

        self.yestodayPrice = {}

    def a50Coefficient(self):
        return

    #查询时间段最好不要太长，否则内存不足
    def getSortedIndustryData(self,beginTime,endTime,timeRange):
        tableList,data = self.iDao.findAllIndustryData(beginTime,endTime)
        resultList = []
        # for industry in tmpSortedIndustry:
        # yestodayPrice[industry[-1][1]] = industry[-1][2]


        for i in range(len(data)):
            resultList.append([])

        # timeRangeLength = len(data[0])
        timeRangeLength = 1442
        for i in range(timeRangeLength):
            tmp = []
            for industry in range(len(data)):
                yestodayPrice = self.yestodayPrice.get(tableList[industry])
                if yestodayPrice != None :
                    if timeRange[i] == data[industry][i][0]:
                        if yestodayPrice != -1 and yestodayPrice !=0:
                            tmp.append((data[industry][i][0], tableList[industry],
                                        data[industry][i][1] / yestodayPrice-1.0))
                        elif data[industry][0][1] != 0:
                            tmp.append((data[industry][i][0], tableList[industry],
                                        data[industry][i][1] / data[industry][0][1] - 1.0))
                        else:
                            tmp.append((data[industry][i][0], tableList[industry],0))
                        # tmp.append((data[industry][i][0], tableList[industry],
                        #             data[industry][i][1] / data[industry][0][1] - 1.0))
                    else:
                        del data[industry][i]
                        # tmp.append((data[industry][i][0], tableList[industry],
                        #             data[industry][i][1] / data[industry][0][1] - 1.0))
                        if yestodayPrice != -1:
                            tmp.append((data[industry][i][0], tableList[industry],
                                        data[industry][i][1] / yestodayPrice-1.0))
                        else:
                            tmp.append((data[industry][i][0], tableList[industry],
                                        data[industry][i][1] / data[industry][0][1] - 1.0))
                    if i >= timeRangeLength - 1:
                        self.yestodayPrice[tableList[industry]] = data[industry][i][1]
                else:
                    if timeRange[i] == data[industry][i][0]:
                        tmp.append((data[industry][i][0], tableList[industry],
                                data[industry][i][1] / data[industry][0][1] - 1.0))
                    else:
                        del data[industry][i]
                        tmp.append((data[industry][i][0], tableList[industry],data[industry][i][1] / data[industry][0][1]-1.0))
                    if i >= timeRangeLength - 1:
                        self.yestodayPrice[tableList[industry]] = data[industry][i][1]
                if industry == 53 and i == 1441:
                    print(data[industry][i][0] , self.yestodayPrice.get(tableList[industry]))
                if industry == 53 and i == 0:
                    print(data[industry][i][0] , self.yestodayPrice.get(tableList[industry]))

            sortedTMmpData = self.sortBySpecialNum(tmp,len(tableList),func=self.compare)
            for sortNum in range(0,len(tableList)):
                resultList[sortNum].append(sortedTMmpData[sortNum])
        return resultList

    def compare(self,tuple) :
        return tuple[2]

    #最大排序
    def sortBySpecialNum(self,list,num,func=None):
        if func == None:
            def x(a):
                return a
            func = x
        # 需要遍历获得最da值的次数
        # 要注意一点，当要排序N个数，已经经过N - 1次遍历后，已经是有序数列
        funcList = []
        for el in list:
            funcList.append(func(el))
        for i in range(len(list)):
            temp = None
            index = i  # 用来保存最大值得索引

            # 寻找第i个大的数值
            for j in range(i,num):
                # 65 64 65
                # print(len(funcList),index,j)
                if funcList[index] < funcList[j]:
                    index = j

            # 将找到的第i个小的数值放在第i个位置上
            temp = list[index]
            list[index] = list[i]
            list[i] = temp

            temp = funcList[index]
            funcList[index] = funcList[i]
            funcList[i] = temp

        return list[:num]





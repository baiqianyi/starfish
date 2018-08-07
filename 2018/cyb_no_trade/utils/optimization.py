import numpy
import random
import math
import matplotlib.pyplot as plt
import datetime

class Optimization:
    def __init__(self):
        return

    def optimizate(self,func,initValue,rangeList,stopTime,initPointNum = 10,variateRate=0.1,evolutionRate=0.05):#params是一个list,rangeList是变量区间序列[(begin,)]
        initPoint = []
        runTime = 0
        initPoint.append(initValue)
        for i in range(initPointNum):
            tempInitValue = []
            for j in range(len(rangeList)):
                tempInitValue.append(random.random() * (float(rangeList[j][1]) - float(rangeList[j][0])) + float(rangeList[j][0]))
            initPoint.append(tempInitValue)

        while True:
            initPoint,funcList = self.sort(initPoint, func=func)
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),";",initPoint[0],";",funcList)

            variateNum = int(initPointNum * variateRate)
            initPoint = self.evolution(initPoint,evolutionRate=evolutionRate)
            initPoint = self.variation(sortList=initPoint, variateNum=variateNum, rangeList=rangeList)
            if stopTime == None:
                if self.funcList[0] - self.funcList[-1] < self.funcList[0] * 0.03:
                    return initPoint[0]
            else:
                if runTime > stopTime:
                    return initPoint[0]
                else:
                    runTime = runTime + 1

    def variation(self,sortList,variateNum,rangeList):
        if len(sortList) < variateNum:
            raise Exception("变异数不能大于变量数")
        sortList = sortList[0:len(sortList) - variateNum]
        groupPoint = []
        for i in range(len(sortList[0])):
            value = 0
            for j in range(1,len(sortList)):
                value = value + sortList[j][i]
            groupPoint.append(value/float(len(sortList)-1))
        for i in range(variateNum):
            point = []
            for j in range(len(sortList[i])):
                if rangeList != None and rangeList[j] != None:
                    scale = abs(1.1 * (groupPoint[j] - sortList[0][j]))
                    if scale <= 0:
                        scale = 0.01
                    average = sortList[0][j] + 1.3*(sortList[0][j] - groupPoint[j])
                    if average - scale > rangeList[j][0] and average + scale < rangeList[j][1]:
                        newPointCoordinate = self.rangeNormalDistribution(average=average,scale=abs(scale))
                    elif average - scale <= rangeList[j][0]:
                        newPointCoordinate = self.rangeNormalDistribution(average=(sortList[0][j] + rangeList[j][0])/2.0, scale=abs(rangeList[j][0] - sortList[0][j])/2.0)
                    elif average+ scale >= rangeList[j][1]:
                        newPointCoordinate = self.rangeNormalDistribution(average=(sortList[0][j] + rangeList[j][1])/2.0, scale=abs(rangeList[j][1]-sortList[0][j])/2.0)
                point.append(newPointCoordinate)
            sortList.append(point)
        return sortList

    def rangeNormalDistribution(self,average,scale,recursion=11):
        randomNum = numpy.random.normal(loc=average,scale = scale/2.0,size=1)
        if randomNum > average - scale and randomNum < average + scale:
            return randomNum[0]
        else:
            if recursion > 0:
                return self.rangeNormalDistribution(average,scale,recursion-1)
            else:
                return average

    def evolution(self,sortList,evolutionRate=0.01):
        #evolutionRate应该取0.0x
        target = sortList[0]
        evolutionList = sortList[1:]
        for i in range(len(evolutionList)):
            for j in range(len(evolutionList[i])):
                evolutionList[i][j] = evolutionList[i][j] + evolutionRate * (target[j] - evolutionList[i][j])
        evolutionList.insert(0,target)
        return evolutionList

    def sort(self,vlist,func):
        funcList = []
        for v in vlist:
            funcList.append(func(v))
            print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),";",v,";",funcList[-1],";",len(funcList))
        for i in range(len(funcList)-1,0,-1):
            for j in range(0,i):
                if funcList[j] < funcList[j+1]:
                    tmp = funcList[j+1]
                    funcList[j+1] = funcList[j]
                    funcList[j] = tmp
                    tmp = vlist[j+1]
                    vlist[j+1] = vlist[j]
                    vlist[j] = tmp
        return vlist,funcList
#
# def func(x):
#     if isinstance(x,list):
#         x=x[0]
#     else:
#         x=x
#     return 1*((x**4) * math.sin(x)+1/float(x))
#
# op = Optimization()
# # print(op.sort([1,-1,2,-2],func=lambda x:x))
# #rangeList是一个二位数组
# v= op.optimizate(func=func,initValue=[2],rangeList=[(-3,3)],stopTime=8,initPointNum = 9,variateRate=0.25)
# print(v)
# x = numpy.linspace(-3, 3, 100)
# y = []
# for xs in x:
#     y.append(func(xs))
# plt.plot(x,y)
# plt.plot(v,func(v), 'ro')
# plt.show()
#

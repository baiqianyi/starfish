class Sort:
    def sort(self,list,func = None):
        if func == None:
            def x(a):
                return a
            func = x
        self.funcList = []
        for v in list:
            self.funcList.append(func(v))
        for i in range(len(self.funcList)-1,0,-1):
            for j in range(0,i):
                if self.funcList[j] < self.funcList[j+1]:
                    tmp = self.funcList[j+1]
                    self.funcList[j+1] = self.funcList[j]
                    self.funcList[j] = tmp
                    tmp = list[j+1]
                    list[j+1] = list[j]
                    list[j] = tmp
        return list
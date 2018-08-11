import data_persistence.back_test as db
import utils.trade_date as td
import utils.optimization as op

class opt_factors:
    def __init__(self):
        self.trade_dates = td.get_trade_date(26)
        print(len(self.trade_dates),self.trade_dates)
        self.hm = db.HearMysql()
        self.position = False
        self.diff_list = []
        self.cyb_list = []
        self.diff_plot = []
        self.diffs_and_cybs()

        self.std_sell = 1.1630461573520512
        self.std_buy = -1.3097007527231481
        self.cyb_plot = [0]
        self.sell_plot_index = []
        self.sell_plot = []
        self.buy_plot_index = []
        self.buy_plot = []

    def opt(self):
        # def optimizate(self, func, initValue, rangeList, stopTime, initPointNum=10, variateRate=0.1, evolutionRate=0.05)
        opt = op.Optimization()
        return opt.optimizate(self.profit,[0.6, -0.8],[(0.2,1.1),(-1.1,-0.3)],stopTime=40,initPointNum=45, variateRate=0.05, evolutionRate=0.04)

    def profit(self,params,std_sell=0.8,std_buy=0.8,wei_b=0,wait_i=24):
        std_sell = params[0]
        std_buy = params[1]
        if len(params)>2:
            wei_b = params[2]
        if len(params)>3:
            wait_i = params[3]
        profit = 0
        # tmp_yes_diff = 0
        for date in range(len(self.trade_dates)):

            diffs = self.diff_list[date][wait_i:]
            cybs = self.cyb_list[date][wait_i:]
            index = 0
            position_change = False
            tmp_diff = []
            for diff in diffs:
                diff = diff[0] #+ wei_b * diff[1]
                tmp_diff.append(diff)
                # if len(self.tmp_diff) > 10:
                #     del self.tmp_diff[0]
                diff = self.weight_mean(tmp_diff)
                diff = diff# + tmp_yes_diff
                if diff < std_buy and not self.position:
                    buy_point = int(index/len(diffs)*len(cybs))
                    # if buy_point > len(cybs):
                    #     buy_point = len(cybs)-1
                    profit = profit + cybs[-1]-cybs[buy_point]
                    self.position = True
                    break
                if diff > std_sell and self.position:
                    sell_point = int(index/len(diffs)*len(cybs))
                    # if sell_point > len(cybs):
                    #     sell_point = len(cybs)-1
                    profit = profit  + cybs[sell_point]
                    self.position = False
                    position_change = True
                index = index + 1
            # tmp_yes_diff = diffs[-1][0]/2.0
            if self.position and not position_change :
                profit = profit + cybs[-1]
        return profit

    def profit_plot(self,params,std_sell=0.8,std_buy=0.8,wei_b=0,wait_i=0):
        std_sell = params[0]
        std_buy = params[1]
        if len(params)>2:
            wei_b = params[2]
        if len(params)>3:
            wait_i = params[3]

        profit = 0
        yes_tmp = 0
        for date in range(len(self.trade_dates)):
            diffs = self.diff_list[date][wait_i:]
            cybs = self.cyb_list[date][wait_i:]
            print("len(diffs)", len(diffs))
            print("len(diffs)", len(cybs))
            index = 0
            position_change = False
            tmp_diff = []
            for diff in diffs:
                diff = diff[0] #+ wei_b * diff[1]
                tmp_diff.append(diff)
                # if len(self.tmp_diff) > 10:
                #     del self.tmp_diff[0]
                diff = self.weight_mean(tmp_diff)
                self.diff_plot.append(diff)
                if diff < std_buy and not self.position:
                    buy_point = int((index)/len(diffs)*len(cybs))
                    # if buy_point > len(cybs):
                    #     buy_point = len(cybs)-1
                    profit = profit+cybs[-1]-cybs[buy_point]
                    self.position = True
                    self.buy_plot.append(self.cyb_plot[-1]+cybs[buy_point])
                    self.buy_plot_index.append(len(self.cyb_plot)+index)
                    break
                if diff > std_sell and self.position:
                    sell_point = int((index)/len(diffs)*len(cybs))
                    # if sell_point > len(cybs):
                    #     sell_point = len(cybs)-1
                    profit = profit + cybs[sell_point]
                    self.position = False
                    position_change = True
                    self.sell_plot.append(self.cyb_plot[-1]+cybs[sell_point])
                    self.sell_plot_index.append(len(self.cyb_plot) + index)
                index = index + 1
            if self.position and not position_change :
                profit = profit + cybs[-1]
            self.cyb_plot.extend([yes_tmp + cyb for cyb in cybs])
            yes_tmp = self.cyb_plot[-1]
        print(profit)
        self.plot()
        return profit

    def diffs_and_cybs(self):
        for date in self.trade_dates:
            diff = list(self.hm.day_diff_list(date))
            cyb = self.hm.cyb
            if cyb != []:
            # cyb_bs = self.hm.cyb_b(self.trade_dates)
                self.diff_list.append(diff)
                self.cyb_list.append(cyb)

    def weight_mean(self,list, mean_num=5):
        mean = 0
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
                mean = mean + float(i + 1) / float(i_sum) * float(t_list[i])
        else:
            return 0
        return mean

    def plot(self):
        import matplotlib.pyplot as plt
        print('self.cyb_plot',self.cyb_plot)
        plt.plot(self.cyb_plot, 'r')
        # plt.plot(self.diff_plot, 'b')
        plt.plot(self.buy_plot_index,self.buy_plot, 'yo')
        plt.plot(self.sell_plot_index,self.sell_plot, 'go')
        plt.show()

if __name__ == "__main__":
    of = opt_factors()
    print(of.profit_plot((0.56, -0.65)))
    # print(of.profit_plot((0.53544878327638823, -0.7024661070125342)))
    # print(of.profit((1.14, -1.28)))
    # print(of.profit_plot((1.0, -1)))
    # print(of.profit_plot((1.0, -1.2)))
    # print(of.profit_plot((0.9, -1.2)))
    # print(of.profit_plot((1, -1.2)))
    # of.plot()
    # print(of.opt())
    # 1.1970208517431806, -1.3356908447452751
    # 1.163046157352
    #
    # 0512, -1.3097007527231481
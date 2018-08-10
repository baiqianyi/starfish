import data_persistence.back_test as db
import utils.trade_date as td
import utils.optimization as op


class opt_factors:
    def __init__(self):
        self.trade_dates = td.get_trade_date(40)
        self.hm = db.HearMysql()
        self.position = False
        self.diff_list = []
        self.cyb_list = []
        self.diffs_and_cybs()

    def opt(self):
        # def optimizate(self, func, initValue, rangeList, stopTime, initPointNum=10, variateRate=0.1, evolutionRate=0.05)
        opt = op.Optimization()
        return opt.optimizate(self.profit,[0.5,-0.5],[(0.3,0.7),(-0.7,-0.3)],stopTime=20,initPointNum=10, variateRate=0.1, evolutionRate=0.05)

    def profit(self,std_sell,std_buy,wei_b=1,wait_i = 0):
        profit = 0
        for date in range(len(self.trade_dates)):
            diffs = self.diff_list[date]
            cybs = self.cyb_list[date]
            index = 0
            position_change = False
            for diff in diffs:
                diff = diff[0] + wei_b * diff[2]
                if diff < std_buy and not self.position:
                    buy_point = int((index+wait_i)/len(diffs))
                    profit = profit+cybs[-1]-cybs[buy_point]
                    self.position = True
                    break
                if diff > std_sell and self.position:
                    sell_point = int((index+wait_i)/len(diffs))
                    profit = profit + cybs[sell_point]
                    self.position = False
                    position_change = True
                index = index + 1
            if self.position and not position_change :
                profit = profit + cybs[-1]
        return profit

    def diffs_and_cybs(self):
        for date in self.trade_dates:
            diffs = self.hm.day_diff_list(date)
            cybs = self.hm.get_cyb_up(date)
            self.diff_list.append(diffs)
            self.cyb_list.append(cybs)

if __name__ == "__main__":
    of = opt_factors()
    print(of.opt())
import tushare as ts
import requests
import re
import os
os.chdir('C:\\Users\\baiqy\\Desktop\\quant\\cyb_notify')

class cyb_weight:

    def __init__(self):
        self.all = ts.get_stock_basics()

    def industry_weights(self):
        cyb_stock_codes = self.cyb_codes()
        weight_map = {}
        for stock in cyb_stock_codes:
            print(stock)
            stock_weight = self.stock_cyb_weight(stock)
            print(stock_weight)
            stock_industry = self.get_industry(stock)
            print(stock_industry)
            if stock_industry != None:
                print(weight_map)
                if weight_map.get(stock_industry) == None:
                    weight_map[stock_industry] = stock_weight
                else:
                    weight_map[stock_industry] = weight_map[stock_industry] + stock_weight
            else:
                raise Exception("get industry None")

        for item in weight_map.items():
            with open('config\\cyb_industry_weight.info', 'w') as f:
                f.write(str(item[0])+"\t"+str(item[1]))
        print (weight_map)
        return weight_map

    def cyb_codes(self):
        url = '''http://vip.stock.finance.sina.com.cn/corp/go.php/vII_NewestComponent/indexid/399006.phtml'''
        html = self.downLoad(url)
        codes = []
        for e in html.split("<td><div align=\"center\"><a href=")[1:]:
            e = re.search("\d{6}", e)
            if e:
                codes.append(e.group(0))
        return codes

    def get_industry(self, code):
        industrys = self.industry_codes()
        for ind in industrys:
            text = self.downLoad(self.industry_url(ind,1))
            for stock in text.split('\",\"'):
                if code == re.search(",\d{6}", stock).group(0)[1:]:
                    return ind
        return None

    def industry_codes(self):
        codes = []
        with open('config\\industry_weights-2018-7-21.info', 'r') as f:
            for line in f.readlines():
                codes.append(str(line.strip()).split("\t")[1])
        return codes

    def industry_url(self,code,page=1):
        url = '''http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cb=jQuery1124006419221619504589_1532789970650&type=CT&token=4f1862fc3b5e77c150a2b985b12db0fd&js=(%7Bdata%3A%5B(x)%5D%2CrecordsTotal%3A(tot)%2CrecordsFiltered%3A(tot)%7D)&sty=FCOIATC&cmd=C.'''+code+'''1&st=(ChangePercent)&sr=-1&p=1&ps=400&_=1532789970665'''
        return url

    def stock_cyb_weight(self,code):
        return self.all.ix[code]['outstanding']*self.price(code)

    def price(self, code):
        cyb = ts.get_realtime_quotes(code)
        return float(cyb.loc[0, 'price'])

    def downLoad(self, url):
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Cache-Control': 'max-age=0',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
                   }
        s = requests.session()
        s.headers.update(headers)
        r = s.get(url=url, timeout=10)  # 带参数的GET请求;;;params={'wd': 'python'},
        import time
        time.sleep(1)
        return r.text

if __name__ == '__main__' :
    cw = cyb_weight()
    print(cw.industry_weights())

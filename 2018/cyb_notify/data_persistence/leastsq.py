##最小二乘法
import numpy as np   ##科学计算库
# import scipy as sp   ##在numpy基础上实现的部分算法库
# import matplotlib.pyplot as plt  ##绘图库
from scipy.optimize import leastsq  ##引入最小二乘法算法
import data_persistence.hear_mysql as hear_mysql

b_infinity = 0.6

h = hear_mysql.HearMysql()

'''
    设定拟合函数和偏差函数
    函数的形状确定过程：
    1.先画样本图像
    2.根据样本图像大致形状确定函数形式(直线、抛物线、正弦余弦等)
'''

##需要拟合的函数func :指定函数的形状
def func(p,x):
    k,b=p
    return k*x+b

##偏差函数：x,y都是列表:这里的x,y更上面的Xi,Yi中是一一对应的
def error(p,x,y):
    return func(p,x)-y

'''
    主要部分：附带部分说明
    1.leastsq函数的返回值tuple，第一个元素是求解结果，第二个是求解的代价值(个人理解)
    2.官网的原话（第二个值）：Value of the cost function at the solution
    3.实例：Para=>(array([ 0.61349535,  1.79409255]), 3)
    4.返回值元组中第一个值的数量跟需要求解的参数的数量一致
'''

#k,b的初始值，可以任意设定,经过几次试验，发现p0的值会影响cost的值：Para[1]
p0=[0.85,0.77]

#把error函数中除了p0以外的参数打包到args中(使用要求)
def cyb_result():
    cyb, six, fail_check = h.get_data('sec_cyb')
    print(cyb)
    print(six)
    p0 = [0.85, 0.77]
    ##样本数据(Xi,Yi)，需要转换成数组(列表)形式
    Xi = np.array(cyb)
    Yi = np.array(six)
    if fail_check >=2:
        import configparser
        past_config = configparser.ConfigParser()  # 注意大小写
        past_config.read("config\\past.info")  # 配置文件的路径

        return 0.8,float(past_config['cyb_sz50']["cyb_b"])

    Para=leastsq(error,p0,args=(Xi,Yi))
    k, b = Para[0]
    return k,b

def sz50_result():
    sz50, six, fail_check = h.get_data('sec_sz50')
    Xi = np.array(sz50)
    Yi = np.array(six)
    p0 = [0.85, 0.77]
    if fail_check >= 2:
        import configparser
        past_config = configparser.ConfigParser()  # 注意大小写
        past_config.read("config\\past.info")  # 配置文件的路径
        return 0.8, float(past_config['cyb_sz50']["sz50_b"])
    Para = leastsq(error, p0, args=(Xi, Yi))
    k, b = Para[0]
    return k, (1*b+0*b_infinity)

if __name__ == "__main__":
    print(cyb_result())

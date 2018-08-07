# coding:utf8
from __future__ import division

import ctypes
import os
import subprocess
import traceback
import win32api
import win32gui
from io import StringIO
import time
import pandas as pd
import pyperclip
import win32com.client
import win32con
# from PIL import ImageGrab

# from log import log
import logging

log = logging.getLogger("trade")
class HTClientTrader:
    def __init__(self):
        self.Title = '网上股票交易系统5.0'
        self.project_copy_data = pd.DataFrame

        self.init()
        self.numMap = {0:48,
      1:49,
      2:50,
      3:51,
      4:52,
      5:53,
      6:54,
      7:55,
      8:56,
      9:57}

        self.refresh_entrust_hwnds = None

    def init(self, config_path=None, user='010420050223', password='724893', communication =r'a@13111218185', exe_path="C:\htwt\\xiadan.exe"):
        """
        登陆银河客户端
        :param config_path: 银河登陆配置文件，跟参数登陆方式二选一
        :param user: 银河账号
        :param password: 银河明文密码
        :param exe_path: 银河客户端路径
        :return:
        """
        if config_path is not None:
            # account = '010420050223'
            user = '010420050223'
            password = '724893'
            communication = r'a@13111218185'
        self.login(user, password,communication, exe_path)

    def login(self, user, password,communication, exe_path):
        if self._has_main_window():
            log.info('检测到交易客户端已启动，连接完毕')
            # self.keepLive()
            # self._get_handles()
            return
        else:
            if not self._has_login_window():
                if not os.path.exists(exe_path):
                    raise FileNotFoundError('在　{} 未找到应用程序，请用 exe_path 指定应用程序目录'.format(exe_path))
                else:
                    subprocess.Popen(exe_path)
        # 检测登陆窗口
            for _ in range(10):
                if self._has_login_window():
                    break
                time.sleep(0.5)
            if not self._has_login_window():
                raise Exception('启动客户端失败，无法检测到登陆窗口')
            else:
                log.info('成功检测到客户端登陆窗口')
        # 登陆
        # self._set_trade_mode()
            for _ in range(10):
                # self._set_login_name(user)
                self._set_login_password(password)
                self._set_communication_password(communication)
            # self._set_login_verify_code()
                self._click_login_button()
                time.sleep(0.5)
                if not self._has_login_window():
                    break
            # self._click_login_verify_code()
            for _ in range(20):
                if self._has_main_window():
                    time.sleep(1)
                    # self._get_handles()
                    break
                time.sleep(1)

            if not self._has_main_window():
                raise Exception('启动交易客户端失败')
            else:
                log.info('客户端登陆成功')
        self.keepLive()
        return

    def keepLive(self):
        #弹出窗口的确定键坐标：（672，536）-（747-560）75*24
        #营业部公告确定键(726,565)-(801,589) 75*24
        self._mouse_click(750,570)
        time.sleep(0.2)
        #超时重新连接确定框(506,437)-(590,458) 84*21
        self._mouse_click(550,445)
        time.sleep(0.2)
        self._mouse_click(700,550)
        time.sleep(0.2)
        self._mouse_click(540,450)
        time.sleep(0.2)
        self._mouse_click(680, 530)  #虚拟机的弹窗
        time.sleep(0.2)
        self.clickY()
        time.sleep(0.2)
        self.clickEnter()
        time.sleep(0.2)
        win32gui.SendMessage(self.refresh_entrust_hwnd, win32con.BM_CLICK, None, None)  # 刷新持仓

    def clickEnter(self,time=1):#回车键
        for i in range(time):
            win32api.keybd_event(0x0D, 0, 0, 0)
            win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)

    def clickF6(self):#双向买卖
        win32api.keybd_event(0x75, 0, 0, 0)
        win32api.keybd_event(0x75, 0, win32con.KEYEVENTF_KEYUP, 0)

    def clickF4(self):#查询
        win32api.keybd_event(0x73, 0, 0, 0)
        win32api.keybd_event(0x73, 0, win32con.KEYEVENTF_KEYUP, 0)

    def clickF3(self):#查询
        win32api.keybd_event(0x72, 0, 0, 0)
        win32api.keybd_event(0x72, 0, win32con.KEYEVENTF_KEYUP, 0)

    def clickF2(self):
        win32api.keybd_event(0x71, 0, 0, 0)
        win32api.keybd_event(0x71, 0, win32con.KEYEVENTF_KEYUP, 0)

    def clickF1(self):
        win32api.keybd_event(0x70, 0, 0, 0)
        win32api.keybd_event(0x70, 0, win32con.KEYEVENTF_KEYUP, 0)

    def clickTab(self):  # 查询
        win32api.keybd_event(9, 0, 0, 0)
        win32api.keybd_event(9, 0, win32con.KEYEVENTF_KEYUP, 0)

    def clickY(self):
        win32api.keybd_event(89, 0, 0, 0)
        win32api.keybd_event(89, 0, win32con.KEYEVENTF_KEYUP, 0)

    def click(self,num):
        win32api.keybd_event(num, 0, 0, 0)
        win32api.keybd_event(num, 0, win32con.KEYEVENTF_KEYUP, 0)

    def clickYes(self):
        self._mouse_click(550,470)
        time.sleep(0.5)

    def _set_login_password(self, password):
        time.sleep(0.5)
        try:
            input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x3F4)
            win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, password)
        except Exception :
            return

    def _set_communication_password(self,communication):##not finished
        time.sleep(0.4)
        # input_hwnd = win32gui.FindWindowEx(self.login_hwnd, 1, 'Edit', None)  # 获取hld下第一个为edit控件的句柄
        try :
            input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x3E9)
            win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, communication)
        except Exception :
            return
        #描述：搜索类名和窗体名匹配的窗体，并返回这个窗体的句柄。不区分大小写，找不到就返回0。
# 参数：
# hwndParent：若不为0，则搜索句柄为hwndParent窗体的子窗体。
# hwndChildAfter：若不为0，则按照z-index的顺序从hwndChildAfter向后开始搜索子窗体，否则从第一个子窗体开始搜索。
# lpClassName：字符型，是窗体的类名，这个可以在Spy++里找到。
# lpWindowName：字符型，是窗口名，也就是标题栏上你能看见的那个标题。


    def _has_login_window(self):
        # for title in ['用户登录']:
        title = '用户登录'
        self.login_hwnd = win32gui.FindWindow(None, title)
        # print(self.login_hwnd)
        if self.login_hwnd != 0:
            return True
        return False

    # def _input_login_verify_code(self, code):
    #     input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x000003E9)
    #     win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, code)

    # def _click_login_verify_code(self):
    #     input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x000003F4)
    #     rect = win32gui.GetWindowRect(input_hwnd)
    #     self._mouse_click(rect[0] + 5, rect[1] + 5)

    @staticmethod
    def _mouse_click(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def _click_login_button(self):
        time.sleep(0.5)
        try:
            input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x3EE)
            win32gui.SendMessage(input_hwnd, win32con.BM_CLICK, None, None)
        except Exception:
            return None

    def _has_main_window(self):
        # try:
        title = self.Title
        self.login_hwnd = win32gui.FindWindow(None, title)
        # print(self.login_hwnd)
        if self.login_hwnd != 0:
            time.sleep(1)
            self._get_handles()
            self.keepLive()
            self._set_foreground_window(self.login_hwnd)
            time.sleep(2)
            return True
        else:
            return False

        # except:
        #     return False
        return True

    # def _grab_verify_code(self):
    #     verify_code_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x56ba)
    #     self._set_foreground_window(self.login_hwnd)
    #     time.sleep(1)
    #     rect = win32gui.GetWindowRect(verify_code_hwnd)
    #     return ImageGrab.grab(rect)

    def _get_handles(self):
        #要用的框架都在afxFrameOrView
        #左边的交易栏在AfxWnd/HexinScrollWndAfx/HexinScrollWnd2/
        # trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        # operate_frame_hwnd = win32gui.GetDlgItem(trade_main_hwnd, 0xE900)  # 操作窗口框架
        # operate_frame_afx_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 0x81)  # 操作窗口框架
        # hexin_hwnd = win32gui.GetDlgItem(operate_frame_afx_hwnd, 0xC8)# 左部折叠菜单控件
        # scroll_hwnd = win32gui.GetDlgItem(hexin_hwnd, 0x81)  # 左部折叠菜单控件
        # right_view_hwnd = win32gui.GetDlgItem(scroll_hwnd, 0xE901)  # 右侧买卖控件
        # # 获取委托窗口所有控件句柄
        # win32api.PostMessage(right_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F1, 0)
        # time.sleep(0.5)
        #F6双向买卖
        self.clickF6()
        time.sleep(2)
        trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        self.operate_frame_hwnd = win32gui.GetDlgItem(trade_main_hwnd, 0xE900)  # 操作窗口框架
        entrust_window_hwnd = win32gui.GetDlgItem(self.operate_frame_hwnd, 0xE901)  # 委托窗口框架

        self.entrust_list_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x417)#持仓
        self.buy_stock_code_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x408)  # 买入代码输入框
        self.buy_price_hwnd = win32gui.GetDlgItem(entrust_window_hwnd,  0x409)  # 买入价格输入框
        self.buy_amount_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x40A)  # 买入数量输入框
        self.buy_btn_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x3EE)  # 买入确认按钮
        self.refresh_entrust_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x8016)  # 刷新持仓按钮
        self.full_satisfed_buy_num_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x3FA)  #


        self.operate_frame_hwnd = win32gui.GetDlgItem(trade_main_hwnd, 0xE900)  # 操作窗口框架
        entrust_window_hwnd = win32gui.GetDlgItem(self.operate_frame_hwnd, 0xE901)  # 委托窗口框架
        self.sell_stock_code_hwnd = win32gui.GetDlgItem(entrust_window_hwnd,0x40B )  # 卖出代码输入框
        self.sell_price_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x422)  # 卖出价格输入框
        self.sell_amount_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x40F)  # 卖出数量输入框
        self.sell_btn_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x3F0)  # 卖出确认按钮
        self.full_satisfed_sell_num_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x3FB)

        self.position_list_hwnd = win32gui.GetDlgItem(entrust_window_hwnd,0x417)#猜想是持仓W

        # 撤单窗口 F3
        # win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F3, 0)
        time.sleep(0.5)
        self.clickF3()
        self.clickEnter()
        time.sleep(0.2)
        self.operate_frame_hwnd = win32gui.GetDlgItem(trade_main_hwnd, 0xE900)  # 操作窗口框架
        entrust_window_hwnd = win32gui.GetDlgItem(self.operate_frame_hwnd, 0xE901)  # 委托窗口框架
        self.cancel_all_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x7531)  # 撤单窗口框架
        # self.cancel_stock_code_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 3348)  # 卖出代码输入框
        # self.cancel_query_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 3349)  # 查询代码按钮
        self.cancel_buy_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x7532)  # 撤买
        self.cancel_sell_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x7533)  # 撤卖

        # 查询 F4
        self.clickF4()
        time.sleep(0.2)
        try:
            self.operate_frame_hwnd = win32gui.GetDlgItem(trade_main_hwnd, 0xE900)  # 操作窗口框架
            entrust_window_hwnd = win32gui.GetDlgItem(self.operate_frame_hwnd, 0xE901)  # 委托窗口框架
            self.capital_hwnd = win32gui.FindWindowEx(entrust_window_hwnd, 5, 'Static', None)
            self.capital_hwnd = win32gui.GetDlgItem(entrust_window_hwnd,0x000003F4)#资金余额
            self.chexin_sub_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x3F9)#可取金额
            self.stock_capital_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x3F6)#股票市值
            self.cash_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x3F8) #可用现金
            self.whole_capital_hwnd =  win32gui.GetDlgItem(entrust_window_hwnd, 0x3F7) #总资产
            self.cash_capital_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x5CB)  # 现金资产
        except Exception:
            return None

        #买一卖一查询
        self.clickF6()
        time.sleep(0.2)
        self.operate_frame_hwnd = win32gui.GetDlgItem(trade_main_hwnd, 0xE900)  # 操作窗口框架
        entrust_window_hwnd = win32gui.GetDlgItem(self.operate_frame_hwnd, 0xE901)  # 委托窗口框架
        self.sellAndBuyWin_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x0) # 买五卖五行情
        self.sell1 = win32gui.GetDlgItem(self.sellAndBuyWin_hwnd, 0x3FD)  # 卖一价格
        self.buy1 = win32gui.GetDlgItem(self.sellAndBuyWin_hwnd, 0x3FA)  # 卖一价格
        # self.printPrice_hwnd = win32gui.GetDlgItem(self.sellAndBuyWin_hwnd, 0x3FA)  # 卖一价格

    def buy(self, stock_code, amount, price=None, **kwargs):
        """
        买入股票
        :param stock_code: 股票代码
        :param price: 买入价格
        :param amount: 买入股数
        :return: bool: 买入信号是否成功发出
        """
        self.clickYes()
        self.clickEnter()
        if amount < 100:
            return
        amount = str(int(amount) // 100 * 100)
        price = str(price)
        self.clickF6()
        time.sleep(0.5)
        try:
            win32gui.SendMessage(self.buy_stock_code_hwnd, win32con.BM_CLICK, None, None)
            win32gui.SendMessage(self.buy_stock_code_hwnd, win32con.WM_SETTEXT, None, stock_code)  # 输入买入代码
            if price != None:
                win32gui.SendMessage(self.buy_price_hwnd, win32con.WM_SETTEXT, None, price)  # 输入买入价格
            time.sleep(0.1)
            # amount="10000"
            for i in range(3):
                self.clickTab()
            for s in amount:
                self.click(self.numMap[int(s)])
            # print(win32api.GetKeyboardState())
            # win32gui.SendMessage(self.buy_amount_hwnd, win32con.WM_SETTEXT, None, amount)  # 输入买入数量
            time.sleep(1)
            try:
                win32gui.PostMessage(self.buy_btn_hwnd, win32con.BM_CLICK, None, None)  # 买入确定
                # self.clickY()
            except Exception:
                time.sleep(0.5)
            # self.click(20)  # 大写
            time.sleep(0.4)
            self.clickY()
            # print('hehe')
            time.sleep(0.5)
            self.clickEnter(1)
            time.sleep(0.4)
            self.clickEnter(1)

            self.keepLive()
        except:
            traceback.print_exc()
            return False
        return True

    def sell(self, stock_code='600000', amount=100,price=None, **kwargs):
        """
        买出股票
        :param stock_code: 股票代码
        :param price: 卖出价格
        :param amount: 卖出股数
        :return: bool 卖出操作是否成功
        """
        self.clickEnter()
        amount = str(int(amount) // 100 * 100)
        # price = str(price)
        self.clickF6()
        time.sleep(0.2)
        win32gui.SendMessage(self.sell_stock_code_hwnd, win32con.BM_CLICK, None, None)
        win32gui.SendMessage(self.sell_stock_code_hwnd, win32con.WM_SETTEXT, None, stock_code)  # 输入卖出代码
        # win32gui.SendMessage(self.sell_stock_code_hwnd, win32con.WM_SETTEXT, None, stock_code)  # 输入卖出代码
        time.sleep(0.5)
        if price != None :
            win32gui.SendMessage(self.sell_price_hwnd,win32con.WM_SETTEXT, None, str(price))
            # win32gui.SendMessage(self.sell_price_hwnd, win32con.WM_SETTEXT, None, "21.21")
            # (self.sell_price_hwnd, win32con.WM_SETTEXT, None, price)  # 输入卖出价格
            # win32gui.SendMessage(self.sell_price_hwnd, win32con.BM_CLICK, None, None)  # 输入卖出价格
        for i in range(3):
            self.clickTab()
        for s in amount:
            self.click(self.numMap[int(s)])
        time.sleep(0.3)
        win32gui.PostMessage(self.sell_btn_hwnd, win32con.BM_CLICK, None, None)  # 卖出确定
        time.sleep(0.1)
        self.clickY()
        time.sleep(0.4)
        self.clickEnter(1)
        # time.sleep(0.6)
        # self.clickEnter()
        # time.sleep(0.4)
        # self.clickY()
        return True

    def cancel_entrust(self,direction = 'all',stock_code  = None):
        """
        撤单
        :param stock_code: str 股票代码
        :param direction: str 'buy' 撤买， 'sell' 撤卖， 'all' 全撤
        :return: bool 撤单信号是否发出
        """
        self.clickEnter()
        self.clickF6()
        try:
            win32gui.SendMessage(self.refresh_entrust_hwnd, win32con.BM_CLICK, None, None)  # 刷新持仓
            time.sleep(0.5)
            # win32gui.SendMessage(self.cancel_stock_code_hwnd, win32con.WM_SETTEXT, None, stock_code)  # 输入撤单
            # win32gui.SendMessage(self.cancel_query_hwnd, win32con.BM_CLICK, None, None)  # 查询代码
            # time.sleep(0.2)
            if direction == 'buy':
                win32gui.PostMessage(self.cancel_buy_hwnd, win32con.BM_CLICK, None, None)  # 撤买
            elif direction == 'sell':
                win32gui.PostMessage(self.cancel_sell_hwnd, win32con.BM_CLICK, None, None)  # 撤卖
            elif direction == 'all':
                win32gui.PostMessage(self.cancel_all_hwnd, win32con.BM_CLICK, None, None)  # 全撤
            time.sleep(0.5)
            self.clickEnter()
            time.sleep(0.5)
            self.clickEnter()
            time.sleep(0.6)
            self.clickEnter()
            time.sleep(0.6)
            self.clickEnter()
            # self.clickF6()
        except:
            traceback.print_exc()
            return False
        time.sleep(0.1)
        return True

    def getBuyAmount(self,code='600000',percent = 0.99):
        entrust_window_hwnd = win32gui.GetDlgItem(self.operate_frame_hwnd, 0xE901)  # 委托窗口框架
        # win32gui.SetWindowPos(entrust_window_hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
        #                       win32con.SWP_NOMOVE | win32con.SWP_NOACTIVATE | win32con.SWP_NOOWNERZORDER | win32con.SWP_SHOWWINDOW)
        self.clickF6()
        self.clickF1()
        # self.buy_stock_code_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x40B)  # 卖出代码输入框
        win32gui.PostMessage(self.refresh_entrust_hwnd,win32con.BM_CLICK, None, None)
        time.sleep(0.4)
        win32gui.SendMessage(self.buy_stock_code_hwnd, win32con.WM_SETTEXT, None, code)  # 输入卖出代码
        buff = ctypes.create_unicode_buffer(32)
        # full_satisfed_buy_str = win32gui.GetDlgItemText(entrust_window_hwnd, 0x3FA)
        win32gui.SendMessage(win32gui.GetDlgItem(entrust_window_hwnd, 0x3FA), win32con.WM_GETTEXT, 32,
                             buff)
        full_satisfed_buy_str = buff.value
        # print(buff.value)  # 读取文本
        # print(win32gui.GetWindowText(win32gui.GetDlgItem(entrust_window_hwnd, 0x3FA)))
        full_satisfed_buy_num = 0.0  #
        buy_num = 0.0
        if not full_satisfed_buy_str == "":
            full_satisfed_buy_num = float(full_satisfed_buy_str)
            buy_num = int(full_satisfed_buy_num * percent/100)*100
        return buy_num,int(full_satisfed_buy_num)

    # def getSellAmount(self,code='600000',percent = 1):
    #     self.clickF6()
    #     self.clickF2()
    #     entrust_window_hwnd = win32gui.GetDlgItem(self.operate_frame_hwnd, 0xE901)  #委托窗口框架
    #     # self.sell_stock_code_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x40B)   #卖出代码输入框
    #     win32gui.SendMessage(self.sell_stock_code_hwnd, win32con.WM_SETTEXT, None,code)  #输入卖出代码
    #     # print('haha')
    #     win32gui.PostMessage(self.refresh_entrust_hwnd,win32con.BM_CLICK, None, None)
    #     time.sleep(0.3)
    #     # full_satisfed_sell_str = win32gui.GetDlgItemText(entrust_window_hwnd, 0x3FB)
    #     buff = ctypes.create_unicode_buffer(32)
    #     win32gui.SendMessage(win32gui.GetDlgItem(entrust_window_hwnd, 0x3FB), win32con.WM_GETTEXT, 32,
    #                          buff)
    #     full_satisfed_sell_str = buff.value
    #     full_satisfed_sell_num = 0.0  #
    #     sell_num = 0.0
    #     if not full_satisfed_sell_str == "" :
    #         full_satisfed_sell_num = float(full_satisfed_sell_str)  #
    #         sell_num = int(full_satisfed_sell_num * percent / 100) * 100
    #     return sell_num,full_satisfed_sell_num

    def getSellAmount(self, code='600000', percent=1.0):
        codes,nums = self.getSellCode()
        if codes==None or nums==None:
            return 0,0
        if codes==[] or nums==[]:
            return 0,0
        for i in range(len(codes)):
            #code必须在codes里，不然报错了
            if codes[i] == code:
                return int(float(nums[i]) * percent / 100.0) * 100,nums[i]

    def buyAll(self,code = '600000',percent = 1.0):

        firstBuyAmount,fullBuyAmount = self.getBuyAmount(code=code,percent=percent)
        firstBuyAmount, fullBuyAmount = self.getBuyAmount(code=code, percent=percent)
        # print('firstBuyAmount',firstBuyAmount);print('fullBuyAmount',fullBuyAmount)
        firstLeftAmount = fullBuyAmount - firstBuyAmount
        if fullBuyAmount <=100:
            return
        self.buy(code, firstBuyAmount)
        leftAmount = firstLeftAmount
        while True:
            time.sleep(7)
            self.cancel_entrust(direction="buy")
            time.sleep(0.8)
            buyAmount, fullBuyAmount = self.getBuyAmount(code=code,percent=percent)
            # print('firstBuyAmount', firstBuyAmount);
            # print('fullBuyAmount', fullBuyAmount)
            if fullBuyAmount - leftAmount >= 100:
                buyAmount = fullBuyAmount - leftAmount
                self.buy(code, buyAmount)
            else:
                break

    def sellAll(self, code='600000', percent=1):
        firstSellAmount, fullSellAmount = self.getSellAmount(code=code,percent=percent)
        firstSellAmount, fullSellAmount = self.getSellAmount(code=code, percent=percent)
        firstLeftAmount = fullSellAmount - firstSellAmount
        # firstSellAmount = 1000
        # print(firstLeftAmount,fullSellAmount)
        if float(firstSellAmount) == 0:
            print(code+"可卖数量为零")
            return
        self.sell(code, firstSellAmount)
        leftAmount = firstLeftAmount
        sell_time = 0
        while True:
            sell_time = sell_time + 1
            time.sleep(6)
            self.cancel_entrust(direction="all")
            time.sleep(1)
            sellAmount, fullSellAmount = self.getSellAmount(code=code,percent=percent)
            if float(fullSellAmount) == 0  or float(sellAmount) == 0:
                print("可卖数量为零")
                return
            if fullSellAmount - leftAmount >= 100:
                sellAmount = fullSellAmount - leftAmount
                self.sell(code, int(sellAmount))
            elif sell_time > 20:
                break
            else:
                continue

    def sellAllBetweenSell1AndBuy1(self,code='600000', percent=1.0):
        firstSellAmount, fullSellAmount = self.getSellAmount(code=code, percent=percent)
        firstSellAmount, fullSellAmount = self.getSellAmount(code=code, percent=percent)
        firstLeftAmount = fullSellAmount - firstSellAmount
        # firstSellAmount = 1000
        # print(firstLeftAmount, fullSellAmount)
        if float(firstSellAmount) == 0:
            print("可卖数量为零")
            return
        sell1,buy1 =  self.getSell1AndBuy1(code)
        # print(sell1,buy1)
        price = (sell1+buy1)/2
        price = str(price).split('.')[0]+'.'+str(price).split('.')[1][:2]
        # print(price,"price")
        self.sell(code, firstSellAmount,price=price)
        leftAmount = firstLeftAmount
        while True:
            time.sleep(7)
            self.cancel_entrust(direction="all")
            time.sleep(1)
            sellAmount, fullSellAmount = self.getSellAmount(code=code, percent=percent)
            # sellAmount = 1000
            # fullSellAmount = 1000
            if float(fullSellAmount) == 0 or float(sellAmount) == 0:
                print(code+"可卖数量为零")
                return
            if fullSellAmount - leftAmount >= 100:
                sellAmount = fullSellAmount - leftAmount
                self.sell(code, int(sellAmount))
                sell1, buy1 = self.getSell1AndBuy1(code)
                price = (sell1 + buy1) / 2
                price = str(price).split('.')[0]+str(price).split('.')[1][:2]
                self.sell(code, sellAmount, price=price)
            else:
                break

    def getSell1AndBuy1(self,code):
        self.clickF6()
        time.sleep(0.1)
        win32gui.SendMessage(self.sell_stock_code_hwnd, win32con.WM_SETTEXT, None, code)
        time.sleep(0.1)
        trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        self.operate_frame_hwnd = win32gui.GetDlgItem(trade_main_hwnd, 0xE900)  # 操作窗口框架
        entrust_window_hwnd = win32gui.GetDlgItem(self.operate_frame_hwnd, 0xE901)  # 委托窗口框架
        self.sellAndBuyWin_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 0x0)  # 买五卖五行情窗口
        self.sell1_hwnd = win32gui.GetDlgItem(self.sellAndBuyWin_hwnd, 0x3FD)  # 卖一价格
        self.buy1_hwnd = win32gui.GetDlgItem(self.sellAndBuyWin_hwnd, 0x3FA)  # 卖一价格
        buff1 = ctypes.create_unicode_buffer(32)
        win32gui.SendMessage(self.sell1_hwnd, win32con.WM_GETTEXT, 32,
                             buff1)
        sell1_str = buff1.value
        buff2 = ctypes.create_unicode_buffer(32)
        win32gui.SendMessage(self.buy1_hwnd, win32con.WM_GETTEXT, 32,
                             buff2)
        buy1_str = buff2.value
        return float(sell1_str),float(buy1_str)

    def getSellCode(self):
        dataf = self.get_entrust()
        # print("dataf",dataf)
        # print(len(dataf),"len(dataf)")
        codeList = []
        sellNumList = []
        if len(dataf)==0:
            return (None,None)
        for i in range(len(dataf)):
        #     if int(dataf.iloc[i,3]) != 0:
            code = dataf.iloc[i,0]
            num = int(dataf.iloc[i,3])
            codeList.append(code)
            sellNumList.append(num)
        return codeList,sellNumList

    @property
    def position(self):
        return self.get_position()

    def get_position(self):
        win32gui.SendMessage(self.refresh_entrust_hwnd, win32con.BM_CLICK, None, None)  # 刷新持仓
        time.sleep(0.1)
        self._set_foreground_window(self.position_list_hwnd)
        time.sleep(0.1)
        data = self._read_clipboard()
        return self.project_copy_data(data)

    @staticmethod
    def project_copy_data(copy_data):
        reader = StringIO(copy_data)
        df = pd.read_csv(reader, delim_whitespace=True)
        # print(df,"df")
        return df.to_dict('records')

    def _read_clipboard(self):
        self.clickF6()
        clickW()
        self._mouse_click(800, 550)#点击查询框
        for _ in range(15):
            try:
                win32api.keybd_event(17, 0, 0, 0)
                win32api.keybd_event(67, 0, 0, 0)
                win32api.keybd_event(67, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.2)
                return pyperclip.paste()
            except Exception as e:
                log.error('open'
                          ' clipboard failed: {}, retry...'.format(e))
                time.sleep(1)
        else:
            raise Exception('read clipbord failed')

    @staticmethod
    def _project_position_str(raw):
        # raw.encode("GBK")
        reader = StringIO(raw)
        # print(type(reader),type(raw))
        # print(reader, raw)
        import numpy as np
        df = pd.read_csv(reader, delim_whitespace=True,dtype={'证券代码': np.str})
        # print(df.iloc[0,1],"df")
        return df

    @staticmethod
    def _set_foreground_window(hwnd):
        shell = win32com.client.Dispatch('WScript.Shell')
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(hwnd)

    @property
    def entrust(self):
        return self.get_entrust()

    def get_entrust(self):
        win32gui.SendMessage(self.refresh_entrust_hwnd, win32con.BM_CLICK, None, None)  # 刷新持仓
        time.sleep(0.2)
        self._set_foreground_window(self.entrust_list_hwnd)
        time.sleep(0.2)
        data = self._project_position_str(self._read_clipboard())
        # print(data)
        return data#self.project_copy_data;self.entrust_list_hwnd


def\
        clickW():
    win32api.keybd_event(87, 0, 0, 0)
    win32api.keybd_event(87, 0, win32con.KEYEVENTF_KEYUP, 0)





# def _set_login_verify_code(self):
#     verify_code_image = self._grab_verify_code()
#     image_path = tempfile.mktemp() + '.jpg'
#     verify_code_image.save(image_path)
#     result = helpers.recognize_verify_code(image_path, 'yh_client')
#     time.sleep(0.2)
#     self._input_login_verify_code(result)
#     time.sleep(0.4)

# def _set_trade_mode(self):
#     input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x4f4d)
#     win32gui.SendMessage(input_hwnd, win32con.BM_CLICK, None, None)

# def _set_login_name(self, user):
#     time.sleep(0.5)
#     print(self.login_hwnd)
#     input_hwnd = win32gui.FindWindowEx(self.login_hwnd, 2, 'ComboBox', None)  # 获取hld下第一个为edit控件的句柄
#     win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, user)
    # input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x000003E9)
    # win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, user)
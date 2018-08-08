#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

class email_notify:
    def __init__(self,title="title",msg="测试"):
        self.my_sender = 'bqy710697439@163.com'  # 发件人邮箱账号
        self.my_pass = 'a13111218185'  # 发件人邮箱密码
        self.my_user = 'bqy710697439@163.com'  # 收件人邮箱账号，我这边发送给自己
        self.msg = msg
        self.title = title
        self.mail()

    def mail(self):
        ret = True
        try:
            msg = MIMEText(self.msg, 'plain', 'utf-8')
            msg['From'] = formataddr(["bqy710697439", self.my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr(["bqy710697439", self.my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = self.title  # 邮件的主题，也可以说是标题

            server = smtplib.SMTP_SSL("smtp.163.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
            server.login(self.my_sender, self.my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.my_sender, [self.my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
            print("邮件发送成功")
        except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
            ret = False
            print("邮件发送失败")
        return ret

if __name__ == "__main__":
    ne = email_notify("大喵","test")
    ne.mail()
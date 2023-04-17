# -*- coding: utf-8 -*-

import config
import discuz
import urllib2
import re
from bs4 import BeautifulSoup

# 选项填在这里 替换成你需要的！！！
option_A = r'看涨'
option_B = r'看跌'
# 投注范围填在这里 
bet_min = 20
bet_max = 200

class Bocai_machine(object):
    def __init__(self):
        self.my_account  = discuz.Discuz()
        self.page = 1
        self.record = {}
     #  self.record_pattern = re.compile(r"[\r\n](\d{1,3}|1000)\s+on\s+([AB])", re.IGNORECASE)
        regex = r"[\r\n](\d{1,3}|1000)\s*(?:水滴?)?\s*(" + option_A + r"|" + option_B + r")"
        self.record_pattern = re.compile(regex, re.S)

        if not config.USERNAME:
            config.USERNAME = raw_input("请输入用户名：")
        if not config.PASSWORD:
            config.PASSWORD = raw_input("请输入密码：")

        if not self.my_account.login(config.USERNAME, config.PASSWORD):
            self.login_flag = False
            print 'login failed'
        else:
            self.login_flag = True
            print 'login succeed'
        self.tid = raw_input('请输入帖子tid:')
        while True:
            option = raw_input("请输入胜利选项(A/B)：")
            if option not in ['A', 'B']:
                print("输入错误，请重新输入！")
            else:
                break

        while True:
            odds = raw_input("请输入获胜赔率：")
            try:
                odds = float(odds)
                if odds < 0.1 or odds > 9.9:
                    print("输入错误，请重新输入！")
                else:
                    break
            except ValueError:
                print("输入错误，请重新输入！")

        while True:
            # 提示用户输入回复的页数
            page = raw_input("请输入回复的页数：")

            # 尝试将用户输入转换为整数
            try:
                page = int(page)
            except ValueError:
                # 如果转换失败，提示用户重新输入
                print("请输入大于 0 的整数！")
                continue

            # 判断用户输入是否大于 0
            if page <= 0:
                # 如果不是，提示用户重新输入
                print("请输入大于 0 的整数！")
                continue

            # 如果用户输入合法，输出回复页数并退出循环
            print("回复的页数是：%d" % page)
            self.page = page
            break

        print("您选择的是{}，获胜赔率为{}".format(option, odds))
        self.victory = option
        if self.victory == 'A':
            self.defeat = 'B'
        else:
            self.defeat = 'A'
        self.odds  = odds

    def extract_text(self, s):
        """
        提取符合格式的选择和数量
        :param s: 待识别的字符串
        :return: 如果符合格式则返回元组(选择, 数量)，否则返回None
        """
        match = self.record_pattern.search(s)

        if match:
            quantity = match.group(1)  # 提取选择和数量
            result = match.group(2)

            if result == option_A:
                option = 'A'
            elif result == option_B:
                option = 'B'
            else:
                option = 'Z'

            # 投注金额
            bet = int(quantity)
            if bet > bet_max:
                option = 'Z'
                bet = 0
            elif bet < bet_min:
                option = 'Z'
                bet = 0
            return option, bet
        else:
            return 'I', 0

    def extract_td_tags(self, soup):
        td_tags = soup.find_all('td', {'class': 't_f'})
        for tag in td_tags:
            if tag.find('div') is None and tag.find('i') is None:
                pid = tag['id'].split('_')[1]
                text = tag.get_text().encode('utf-8')

                # 提取投注信息
                option, quantity = self.extract_text(text)
                self.record[pid.encode("utf-8")] = [option, quantity]

    def scan_tid(self):
        for page in range(self.page):
            if self.login_flag == True:
                request =  urllib2.Request(config.DOMAIN + r'forum.php?mod=viewthread&tid=' + self.tid + r'&extra=&page=' + str(page+1))
                response = urllib2.urlopen(request).read().decode('utf-8')

                bs = BeautifulSoup(response, 'html.parser')
                self.extract_td_tags(bs)


    def preview(self):
        for pid, rec in self.record.items():
            if rec[0] == 'I':
                print "pid %s 投注信息未识别" % (pid)
                continue
            elif rec[0] == 'Z':
                print "pid %s 投注金额无效" % (pid)
                continue

            if rec[0] == self.victory:
                print "pid %s 投注了 %d 水滴并胜利，预期加水 %d" % (pid, rec[1], rec[1]*self.odds)
            else:
                print "pid %s 投注了 %d 水滴并失利，预期扣水 %d" % (pid, rec[1], rec[1])

        while True:
            choice = raw_input("是否开始评分？(Y/N) ").upper()
            if choice == "Y":
                # 继续执行程序
                break
            elif choice == "N":
                exit()  # 退出程序
            else:
                # 提示重新输入
                print("请重新输入！")

    def rate(self):
        for pid, record in self.record.items():
            if record[0] == self.victory:
                self.my_account.rate(self.tid,pid, record[1]*self.odds ,"恭喜您！预测正确")
                print "rate %d for pid %s" % (record[1]*self.odds, pid)
            elif record[0] == self.defeat:
                self.my_account.rate(self.tid, pid, -record[1], "很遗憾！预测失败")
                print "rate %d for pid %s" % (-record[1], pid)


if __name__ == '__main__':
    bocai_machine = Bocai_machine()
    # 扫描用户投注信息
    bocai_machine.scan_tid()
    # 预览投注情况
    bocai_machine.preview()
    # 为用户信息进行评分
    bocai_machine.rate()

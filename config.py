# -*- coding: utf-8 -*-

DOMAIN = r'https://bbs.uestc.edu.cn/'
# 下面填入你的用户名
USERNAME=r''
# 下面填入你的密码
PASSWORD=r''

LOGINFIELD = r'username'
HOMEURL = DOMAIN
LOGINURL= DOMAIN + r'member.php?mod=logging&action=login&loginsubmit=yes&loginhash=LXlmu&inajax=1'
POSTURL = DOMAIN + r'forum.php?mod=post&actionDOMAIN=newthread&fid=FID&extra=&topicsubmit=yes'
REPLYURL= DOMAIN + r'forum.php?mod=post&action=reply&tid=TID&extra=&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'
RATEURL = DOMAIN + r'forum.php?mod=misc&action=rate&ratesubmit=yes&infloat=yes&inajax=1'

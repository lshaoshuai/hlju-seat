from bs4 import BeautifulSoup
from multiprocessing import Pool
import os,time,random,requests,threading
from datetime import datetime, date, timedelta
from lxml import etree
import schedule
import json
from threading import Thread
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from requests.cookies import RequestsCookieJar

init_url = "http://seat1.lib.hlju.edu.cn/login?targetUri=%2F"

login_url = "http://seat1.lib.hlju.edu.cn/auth/signIn"

history_url = "http://seat1.lib.hlju.edu.cn/history?type=SEAT" 

search_url = "http://seat1.lib.hlju.edu.cn/freeBook/ajaxSearch?"

free_seat = {}

def search(username,password):
    
    # 固定请求头
    Referer_header = {
        "Content-Type" : "application/x-www-form-urlencoded",
        "Host": "seat1.lib.hlju.edu.cn",
        "Connection": "keep-alive",
        "Cache-Control" : "max-age=0",
        "Origin": "http://seat1.lib.hlju.edu.cn",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9"
    } 

    s = requests.Session()

    login_resp = s.get(init_url)
    soup = BeautifulSoup(login_resp.content, "lxml")
    token_value = soup.find(id = "SYNCHRONIZER_TOKEN").get('value')
    cookie_value = ''
    for key,value in login_resp.cookies.items():  
        if key == "JSESSIONID" :
            cookie_value = value
            break

    Referer_header["Referer"] = init_url
    Referer_header["Cookie"] = "JSESSIONID=" + cookie_value
    Referer_header["Content-Length"] = "127"
    datas = {
        "authid": "-1",
        "SYNCHRONIZER_URI": "/login"
    }
    datas["SYNCHRONIZER_TOKEN"] = token_value
    datas["username"] = username
    datas["password"] = password
    s.post(login_url, data=datas, headers=Referer_header)
    resp = s.get(search_url + "onDate=" + (date.today() + timedelta(days =+1)).strftime("%Y-%m-%d") + "&building=" +"&room=" +"&hour=8"+"&startMin="+"&endMin="+"&power="+"&window=")
    soup = BeautifulSoup(resp.content, "lxml")
    lis = soup.find_all("li")
    for li in lis:
        if li.get("id"):
            free_seat[li.get("id").strip("\\\"")] = li.find("dt").get_text().strip().replace("\\n", "")

    print(free_seat)

def stmp(send_msg):
    
    my_sender='**********@qq.com'    
    my_pass = '**********'        
    my_user='**********@qq.com'     
    def mail():
        ret=True
        try:
            msg = MIMEText("more than 8 hour seat" + str(send_msg),'plain','utf-8')
            msg['From']=formataddr(["seat",my_sender])  
            msg['To']=formataddr(["FK",my_user])           
            msg['Subject']="seat mail"                
    
            server=smtplib.SMTP_SSL("smtp.qq.com", 465) 
            server.login(my_sender, my_pass)  
            server.sendmail(my_sender,[my_user,],msg.as_string())
            server.quit() 
        except Exception: 
            ret=False
        return ret
    
    ret=mail()
    if ret:
        print("mail send sccessfully")
    else:
        print("mail fail to send")

def main():
    print((date.today() + timedelta(days =+1)).strftime("%Y-%m-%d"))
    print("-------------------------script start to run-------------------------")
    search("**********","**********")

if __name__ == '__main__':
    main()
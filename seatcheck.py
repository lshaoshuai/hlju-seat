from bs4 import BeautifulSoup
from multiprocessing import Pool
import os,time,random,requests,threading
from datetime import datetime, date, timedelta
from lxml import etree
import schedule
import json
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


init_url = "http://seat1.lib.hlju.edu.cn/login?targetUri=%2F"

login_url = "http://seat1.lib.hlju.edu.cn/auth/signIn"

hlju_url = "http://seat1.lib.hlju.edu.cn"

map_url = "http://seat1.lib.hlju.edu.cn/map"

res_url = "http://seat1.lib.hlju.edu.cn/selfRes"

seat_url = "http://seat1.lib.hlju.edu.cn/mapBook/getSeatsByRoom?room=22&date=2019-10-14"

history_url = "http://seat1.lib.hlju.edu.cn/history?type=SEAT"

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

user_info = [
    {"username": "20165166","password":"20165166"},
    {"username": "20166508","password":"20166508"},
    {"username": "20175528","password":"20175528"},
    {"username": "20163789","password":"20163789"},
    {"username": "20165365","password":"20165365"},
    {"username": "20163208","password":"20163208"},
    {"username": "20164511","password":"ry19981020"},
    {"username": "20164452","password":"20164452"}
]


def cancel(username,password):

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
    datas["username"] = str(username)
    datas["password"] = str(password)
    s.post(login_url, data=datas, headers=Referer_header)
    try:
        resp1 = s.post(seat_url,timeout=0.5)
    except Exception as e:
        print("error"+str(e))
    resp2 = s.post(history_url)
    soup = BeautifulSoup(resp2.content, "lxml")
    href = ""
    a = soup.find_all("a","normal showLoading")
    if len(a):
        return True
        
    else:
        return False

def stmp(send_msg):
    
    my_sender='1939125539@qq.com'    
    my_pass = 'otksiotmnbnkbbfh'        
    my_user='1939125539@qq.com'     
    def mail():
        ret=True
        try:
            msg = MIMEText(str(send_msg),'plain','utf-8')
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

def job():
    send_stmp = {}
    for user in user_info:
        if(cancel(user["username"],user["password"])):
            send_stmp[user["username"]] = "ok"
            print(user["username"])
        else:
            send_stmp[user["username"]] = "fail"
    print(send_stmp)
    stmp(send_stmp)


def run():
    job()

def main():
    run()

if __name__ == '__main__':
    main()

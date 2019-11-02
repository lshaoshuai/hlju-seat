from bs4 import BeautifulSoup
from multiprocessing import Pool
import os,time,random,requests,threading
from datetime import datetime, date, timedelta
from lxml import etree
import schedule
import json


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
    # {"username": "20150105","password":"20150105"},
    # {"username": "20150121","password":"20150121"},
    # {"username": "20150159","password":"20150159"},
    # {"username": "20150160","password":"20150160"},
    # {"username": "20150161","password":"20150161"},
    # {"username": "20150162","password":"20150162"},
    # {"username": "20150163","password":"20150163"},
    # {"username": "20150168","password":"20150168"},
    # {"username": "20150169","password":"20150169"},
    # {"username": "20150170","password":"20150170"},
    # {"username": "20150171","password":"20150171"},
    # {"username": "20150172","password":"20150172"},
    # {"username": "20150174","password":"20150174"},
    # {"username": "20150175","password":"20150175"},
    # {"username": "20150176","password":"20150176"},
    # {"username": "20150178","password":"20150178"},
    # {"username": "20150179","password":"20150179"},
    # {"username": "20150180","password":"20150180"},
    # {"username": "20150181","password":"20150181"},
    # {"username": "20150182","password":"20150182"}
    {"username": "20150219","password":"20150219"},
    {"username": "20150220","password":"20150220"},
    {"username": "20150222","password":"20150222"}
    
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
        resp1 = s.post(seat_url,timeout=0.05)
    except Exception as e:
        print("error"+str(e))
    resp2 = s.post(history_url)
    soup = BeautifulSoup(resp2.content, "lxml")
    href = ""
    a = soup.find_all("a","normal showLoading")
    if len(a):
        href = a[0]["href"]
    print(href)
    if len(href):
        s.post(hlju_url + href)


def job():
    for user in user_info:
        cancel(user["username"],user["password"])

def run():
    job()

def main():
    run()

if __name__ == '__main__':
    main()

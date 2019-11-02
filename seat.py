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

seat_url = "http://seat1.lib.hlju.edu.cn/mapBook/getSeatsByRoom?"

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

floors = [16,21,22,29,30,31,32,36]

def seat(username,password):

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
   
    file = open("C:\\Users\\lshao\\Desktop\\图书馆攻略组\\seat.txt", "a")
    file.seek(0) #定位到0
    file.truncate() #清空文件
    for floor in floors:
        file.write('\n' + "第" + str(floor) + "楼:" + '\n')
        resp = s.post(seat_url + "room=" + str(floor) + "&date=2019-10-21")
        soup = BeautifulSoup(resp.content, "lxml")
        lis = soup.find_all("li")
        for li in lis:
            if li.get("id"):
                file.write(" " + li.get("id") + " " + li.find("a").get_text() + " ")
    file.close()


def job():
    seat("20150005","20150005")

def run():
    job()

def main():
    run()

if __name__ == '__main__':
    main()

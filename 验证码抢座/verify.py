
from bs4 import BeautifulSoup
from multiprocessing import Pool
import os,time,random,requests,threading
from datetime import datetime, date, timedelta
from lxml import etree
import schedule
import json
from threading import Thread

init_url = "http://seat1.lib.hlju.edu.cn/login?targetUri=%2F"

login_url = "http://seat1.lib.hlju.edu.cn/auth/signIn"

hlju_url = "http://seat1.lib.hlju.edu.cn"

map_url = "http://seat1.lib.hlju.edu.cn/map"

res_url = "http://seat1.lib.hlju.edu.cn/selfRes"


site_info = []
with open("/root/record.json",'r') as load_f:
    site_info = json.load(load_f)

cache = {}

def login(username,password,seat,start,end,cookie_value):

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

    Referer_header["Cookie"] = "JSESSIONID=" + cookie_value
    try:
        resp = requests.get(hlju_url,headers=Referer_header)
    except Exception as e:
        print("error %s" % e)
    soup = BeautifulSoup(resp.content, "lxml")
    print(soup.find_all('a')[0].text)
    if(soup.find_all('a')[0].text == "ie浏览器"):
        saveinfo(username,"false")

def saveinfo(username,login):
    for info in site_info:
        if(info["username"] == username):
            info["login"] = login
    with open("/root/record.json","w") as f:
        json.dump(site_info,f)

def start():

    print('Start to Login %s ' % datetime.now())

    login_threads = []

    for info in site_info:
        thread = threading.Thread(target=login, args=(info["username"],info["password"],info["seat"],info["start"],info["end"],info["cookie_value"],))
        login_threads.append(thread)

    for i in range(len(site_info)):
        login_threads[i].start()

    for i in range(len(site_info)):
        login_threads[i].join()


def run():
    start()

def main():
    print((date.today() + timedelta(days =+1)).strftime("%Y-%m-%d"))
    print("-------------------------script start to run-------------------------")
    run()

if __name__ == '__main__':
    main()

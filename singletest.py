
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

site_info = [

]

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
    resp = requests.get(map_url,headers=Referer_header)
    soup = BeautifulSoup(resp.content, "lxml")
    print(soup.find_all('a')[0].text)
    new_syt_value  = soup.find(id = "SYNCHRONIZER_TOKEN").get('value')
    Referer_header["Referer"] = map_url
    site_datas = {
        "authid": "-1",
        "SYNCHRONIZER_URI": "/map"
    }
    site_datas["SYNCHRONIZER_TOKEN"] = new_syt_value
    site_datas["seat"] = seat
    site_datas["date"] = (date.today() + timedelta(days =+1)).strftime("%Y-%m-%d") 
    site_datas["start"] = start
    site_datas["end"] = end
    cache["datas" + username] = site_datas
    cache["headers" + username] = Referer_header
   
def crawler(username):
    
    redis_datas = cache["datas" + username]
    redis_headers = cache["headers" + username]
    try:
        resp = requests.post(res_url,data=redis_datas, headers=redis_headers,timeout=5)
        print("time %s user %s" % (datetime.now(),username))
    except Exception as e:
        print("error %s" % e)
    

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

    threads = []
    for info in site_info:
        thread = threading.Thread(target=crawler, args=(info["username"],))
        threads.append(thread)

    print('cache %s' % datetime.now())
    time.sleep(60-datetime.now().second)
    print('Start to crawler %s' % datetime.now())

    for i in range(len(site_info)):
        threads[i].start()

    for i in range(len(site_info)):
        threads[i].join()

def run():
    start()

def main():
    print((date.today() + timedelta(days =+1)).strftime("%Y-%m-%d"))
    print("-------------------------script start to run-------------------------")
    run()

if __name__ == '__main__':
    main()

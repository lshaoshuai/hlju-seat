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

site_info = [
    {"username": "20165166","password":"20165166","seat":"24797","start":"420","end":"1320"},
    {"username": "20150112","password":"20150112","seat":"24637","start":"420","end":"1320"},
    {"username": "20166508","password":"20166508","seat":"24772","start":"420","end":"1320"}
]

def login(username,password,seat,start,end):

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

    resp3 = s.get(map_url)
    soup2 = BeautifulSoup(resp3.content, "lxml")
    new_syt_value  = soup2.find(id = "SYNCHRONIZER_TOKEN").get('value')

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


    time.sleep(60 - datetime.now().second)
    print('Start to crawler %s' % datetime.now())
    try:
        s.post(res_url,data=site_datas, headers=Referer_header, timeout=3)
        print("time %s user %s" % (datetime.now(),username))
    except Exception as e:
        print("error %s" % e)

    
def job(info):  
    print('Start from %s Task %s (pid=%s) is running...' % (datetime.now(),info["username"],os.getpid()))
    login(info["username"],info["password"],info["seat"],info["start"],info["end"])
    print('End of %s Task %s end.' % (datetime.now(),info["username"]))

def multiprocess():
    print('Current process %s.' % os.getpid()) 
    p=Pool(processes=3) 
    for info in site_info:
        p.apply_async(job,args=(info,)) 
    print('Wating for all subprocess done...') 
    p.close() 
    p.join() 

def run():
    multiprocess()

def main():
    print((date.today() + timedelta(days =+1)).strftime("%Y-%m-%d"))
    print("start to run")
    run()

if __name__ == '__main__':
    main()

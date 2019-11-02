
from bs4 import BeautifulSoup
from multiprocessing import Pool
import os,time,random,requests,threading
from datetime import datetime, date, timedelta
from lxml import etree
import schedule
import json

# 获取JSESSIONID和SYT
init_url = "http://seat1.lib.hlju.edu.cn/login?targetUri=%2F"

# 登录网站
login_url = "http://seat1.lib.hlju.edu.cn/auth/signIn"

# 图书馆
hlju_url = "http://seat1.lib.hlju.edu.cn"

# 刷新SYT
map_url = "http://seat1.lib.hlju.edu.cn/map"

# 抢座
res_url = "http://seat1.lib.hlju.edu.cn/selfRes"

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

# 抢座信息(现在默认为提前一个小时)
site_info = [
    {"username": "20150005","password":"20150005","seat":"24629","start":"420","end":"1320"},
    {"username": "20150006","password":"20150006","seat":"24630","start":"420","end":"1320"},
    {"username": "20165166","password":"20165166","seat":"24797","start":"420","end":"1320"},
    {"username": "20166508","password":"20166508","seat":"24772","start":"420","end":"1320"}
]

def login(username,password,seat,start,end):

    # 创建一个会话
    s = requests.Session()

    # 获取JSESSIONID和SYT
    login_resp = s.get(init_url)
    soup = BeautifulSoup(login_resp.content, "lxml")
    token_value = soup.find(id = "SYNCHRONIZER_TOKEN").get('value')
    cookie_value = ''
    for key,value in login_resp.cookies.items():  
        if key == "JSESSIONID" :
            cookie_value = value
            break
    
    # print(token_value,cookie_value)

    #登录
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
    
    # 不需要进入到登录页面
    # resp2 = s.post(hlju_url)

    time.sleep(60-datetime.now().second)
    print('Start to rycle %s' % datetime.now())
    d = 5
    while d > 0:
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
        try:
            resp4 = s.post(res_url,data=site_datas, headers=Referer_header,timeout=2)
        except Exception as e:
            print("error")
        html_data = etree.HTML(resp4.text).xpath('/html/body/div[3]/div[3]/div/div/dl/dd[1]/text()')
        print(datetime.now(),username,html_data[0]) 
        d-=1
        time.sleep(0.2)

    
    

def job(info):
    print('Start from %s Task %s (pid=%s) is running...' % (datetime.now(),info["username"],os.getpid()))
    login(info["username"],info["password"],info["seat"],info["start"],info["end"])
    print('End of %s Task %s end.' % (datetime.now(),info["username"]))

def multiprocess():
    print('Current process %s.' % os.getpid()) 
    p=Pool(processes=4) 
    for info in site_info:
        p.apply_async(job,args=(info,)) 
    print('Wating for all subprocess done...') 
    p.close() 
    p.join() 

def job1():
    login('20152456','20152456','21346','420','480')


def run():
    # multiprocess()
    schedule.every().day.at("18:29:00").do(multiprocess)
    while True:
        schedule.run_pending()


def main():
    print((date.today() + timedelta(days =+1)).strftime("%Y-%m-%d"))
    print("-------------------------script start to run-------------------------")
    run()

if __name__ == '__main__':
    main()

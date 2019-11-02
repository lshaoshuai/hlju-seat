
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

history_url = "http://seat1.lib.hlju.edu.cn/history?type=SEAT" 

# 抢座信息(现在默认为提前一个小时)
site_info = [
    # {"username": "20150262","password":"20150262","seat":"24817","start":"420","end":"1320"},#1
    # {"username": "20150263","password":"20150263","seat":"24803","start":"420","end":"1320"},#2
    # {"username": "20150160","password":"20150160","seat":"24792","start":"420","end":"1320"},#4
    # {"username": "20150161","password":"20150161","seat":"24799","start":"420","end":"1320"},#5
    # {"username": "20150175","password":"20150175","seat":"24767","start":"420","end":"1320"},#14
    {"username": "20150181","password":"20150181","seat":"24760","start":"420","end":"1320"},#19
    {"username": "20150182","password":"20150182","seat":"24759","start":"420","end":"1320"},#20
    {"username": "20150261","password":"20150261","seat":"22351","start":"420","end":"1320"},#17
    # {"username": "20163208","password":"20163208","seat":"24756","start":"420","end":"1320"},#16
    # {"username": "20165166","password":"20165166","seat":"24797","start":"420","end":"1320"},
    # {"username": "20166508","password":"20166508","seat":"24772","start":"420","end":"1320"},
    # {"username": "20175528","password":"20175528","seat":"36510","start":"420","end":"1320"},
    # {"username": "20163789","password":"20163789","seat":"36496","start":"420","end":"1320"},
    # {"username": "20150970","password":"20150970","seat":"36486","start":"420","end":"1320"}
    # {"username": "20150262","password":"20150262","seat":"36503","start":"1260","end":"1320"}
]


cache = {}

send_stmp = {}

def login(username,password,seat,start,end):

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
    cache["datas" + username] = site_datas
    cache["headers" + username] = Referer_header
   
def crawler(username):
    
    redis_datas = cache["datas" + username]
    redis_headers = cache["headers" + username]
    try:
        resp4 = requests.post(res_url,data=redis_datas, headers=redis_headers,timeout=5)
        html_data = etree.HTML(resp4.text).xpath('/html/body/div[3]/div[3]/div/div/dl/dd[1]/text()')
        print(datetime.now(),username,html_data[0]) 
    except Exception as e:
        print("error %s" % e)
    
    Referer_header = {
        "Host": "seat1.lib.hlju.edu.cn",
        "Connection": "keep-alive",
        "Origin": "http://seat1.lib.hlju.edu.cn",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9"
    } 
    Referer_header["Cookie"] = redis_headers["Cookie"]
    resp = requests.get(history_url,headers=Referer_header,timeout=5)
    soup = BeautifulSoup(resp.content, "lxml")
    a = soup.find_all("a","normal showLoading")
    if len(a):
        send_stmp[username] = "ok"
    else:
        send_stmp[username] = "fail"
    

def start():

    print('Start to Login %s ' % datetime.now())

    login_threads = []

    # 创建线程，但是未启动
    for info in site_info:
        thread = threading.Thread(target=login, args=(info["username"],info["password"],info["seat"],info["start"],info["end"],))
        login_threads.append(thread)

    # 启动线程
    for i in range(len(site_info)):
        login_threads[i].start()

    for i in range(len(site_info)):
        login_threads[i].join()

    threads = []
    # 创建线程，但是未启动
    for info in site_info:
        thread = threading.Thread(target=crawler, args=(info["username"],))
        threads.append(thread)

    print('cache %s' % datetime.now())
    time.sleep(59-datetime.now().second)
    print('Start to crawler %s' % datetime.now())

    # 启动线程
    for i in range(len(site_info)):
        threads[i].start()

    for i in range(len(site_info)):
        threads[i].join()

def run():
    schedule.every().day.at("18:29:00").do(start)
    while True:
        schedule.run_pending()

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

def main():
    print((date.today() + timedelta(days =+1)).strftime("%Y-%m-%d"))
    print("-------------------------script start to run-------------------------")
    run()
    print("send order mail")
    stmp(send_stmp)

if __name__ == '__main__':
    main()

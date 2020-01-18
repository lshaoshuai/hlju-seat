from PIL import Image, ImageDraw
from bs4 import BeautifulSoup
from io import BytesIO
from collections import defaultdict
from aip import AipOcr
from datetime import datetime, date, timedelta
import os,time,random,requests,threading,sys
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json

site_info = []

with open("C:\\Users\\lshao\\Desktop\\verifycode\\record.json",'r') as load_f:
    site_info = json.load(load_f)


init_url = "http://seat1.lib.hlju.edu.cn/login?targetUri=%2F"

login_url = "http://seat1.lib.hlju.edu.cn/auth/signIn"

hlju_url = "http://seat1.lib.hlju.edu.cn"

map_url = "http://seat1.lib.hlju.edu.cn/map"

res_url = "http://seat1.lib.hlju.edu.cn/selfRes"

# config = {
#     'appId': '17663328', 17779212
#     'apiKey': '	EG6651jtGBT7qQhY0dNtjLnf', EUWF6SqfHOPGsN4Lr0LDnBFf
#     'secretKey': 'qbVwXPQ9HomUG0aN1StvpQNl12fvOVKy' 66wdZlCGcphObNnOEO5BFnyYvfnTteTF
# }

# client = AipOcr(**config)
class unlockScrapy(object):
    # super().__init__()的作用也就显而易见了，就是执行父类的构造函数，使得我们能够调用父类的属性。

    def __init__(self, driver,username):
        super(unlockScrapy, self).__init__()
        # selenium驱动
        self.driver = driver
        self.username = username
        # self.WAPPID = '百度文字识别appid'
        # self.WAPPKEY = '百度文字识别appkey'
        # self.WSECRETKEY = '百度文字识别secretkey'
        # 百度文字识别sdk客户端
        # self.WCLIENT = AipOcr(self.WAPPID, self.WAPPKEY, self.WSECRETKEY)
        self.WAPPID = '17779212'
        self.WAPPKEY = 'EUWF6SqfHOPGsN4Lr0LDnBFf'
        self.WSECRETKEY = '66wdZlCGcphObNnOEO5BFnyYvfnTteTF'
        # 百度文字识别sdk客户端
        self.WCLIENT = AipOcr(self.WAPPID, self.WAPPKEY, self.WSECRETKEY)
        print("--------------初始化-----------")
    
        # 下载图片
    def downloadImg(self):
        codeSrc = self.driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/img").get_attribute("src")
        print(codeSrc)
        resp = requests.get(codeSrc)
        fh = open("C:\\Users\\lshao\\Desktop\\verifycode\\" + self.username +"code.jpeg", "wb")
        fh.write(resp.content)
        fh.close()
        
    def gettext(self):
        text_list = []
        text = self.driver.find_element_by_xpath("/html/body/div[2]/div/div[2]/span").get_attribute("innerHTML")
        print(text.split(":")[1].replace('"',' ').split())
        text_list = text.split(":")[1].replace('"',' ').split()
        return text_list

    # 读取图片文件
    def getFile(self, filePath):
        with open(filePath, 'rb') as fp:
            print("-------------------读取图片-------------------")
            return fp.read()

    # 图片二值化，便于识别其中的文字

    """
    # 请求参数
    recognize_granularity:是否定位单字符位置，big：不定位单字符位置，默认值；small：定位单字符位置
    item['chars'] :+chars	array	单字符结果，recognize_granularity=small时存在
    """
    # 识别下面大图中的文字及坐标
    def getPos(self, words):

        try:
            print("开始识别大图...")
            op = {'language_type': 'CHN_ENG', 'recognize_granularity': 'small'}

            res = self.WCLIENT.general(
                self.getFile("C:\\Users\\lshao\\Desktop\\verifycode\\" + self.username +"code.jpeg"), options=op)

            # 所有文字的位置信息
            allPosInfo = []
            # 需要的文字的位置信息
            needPosInfo = []
            # 每日50000次,超时报错{'error_code': 17, 'error_msg': 'Open api daily request limit reached'}
            print(res)
            print("-----------------\n")
            print(res['words_result'])
            print("-----------------\n")

            for item in res['words_result']:
                allPosInfo.extend(item['chars'])
                print(item['chars'])  # 文字及位置信息,见百度api
                print("--------------")
            # 筛选出需要的文字的位置信息
            for word in words:
                for item in allPosInfo:
                    if word == item['char']:
                        needPosInfo.append(item)
                        time.sleep(1)
                        print('筛选出的文字: ' + item['char'])

            # 返回出现文字的位置信息
            print(needPosInfo)
            print("大图识别完成...")
            return needPosInfo
            
        except Exception as e:
            print(e)

    # 点击大图上的文字
    def clickWords(self, wordsPosInfo):
        # 获取到大图的element
        #  /html/body/div[3]/div[3]/img
        imgElement = self.driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/img')
        # 根据上图文字在下图中的顺序依次点击下图中的文字
        for info in wordsPosInfo:
            # move_to_element_with_offset(to_element, xoffset, yoffset) ——移动到距某个元素（左上角坐标）多少距离的位置
            ActionChains(self.driver).move_to_element_with_offset(
                to_element=imgElement, xoffset=info['location']['left'] + 20,
                yoffset=info['location']['top'] + 20).click().perform()
            time.sleep(1)

    def getPixel(self,image,x,y,G,N):
        L = image.getpixel((x,y))
        if L > G:
            L = True
        else:
            L = False
    
        nearDots = 0
        if L == (image.getpixel((x - 1,y - 1)) > G):
            nearDots += 1
        if L == (image.getpixel((x - 1,y)) > G):
            nearDots += 1
        if L == (image.getpixel((x - 1,y + 1)) > G):
            nearDots += 1
        if L == (image.getpixel((x,y - 1)) > G):
            nearDots += 1
        if L == (image.getpixel((x,y + 1)) > G):
            nearDots += 1
        if L == (image.getpixel((x + 1,y - 1)) > G):
            nearDots += 1
        if L == (image.getpixel((x + 1,y)) > G):
            nearDots += 1
        if L == (image.getpixel((x + 1,y + 1)) > G):
            nearDots += 1
    
        if nearDots < N:
            return image.getpixel((x,y-1))
        else:
            return None

    def clearNoise(self,image,G,N,Z):
        draw = ImageDraw.Draw(image)
    
        for i in range(0,Z):
            for x in range(1,image.size[0] - 1):
                for y in range(1,image.size[1] - 1):
                    color = self.getPixel(image,x,y,G,N)
                    if color != None:
                        draw.point((x,y),color)

    def convert(self):
        img = Image.open("C:\\Users\\lshao\\Desktop\\verifycode\\" + self.username +"code.jpeg")
        width = img.size[0]#长度
        height = img.size[1]#宽度
        # img_array=img.load()
        img = img.point(lambda p: p * 3)
        img.save("C:\\Users\\lshao\\Desktop\\verifycode\\code1.jpeg")
        for i in range(0,width):#遍历所有长度的点
            for j in range(0,height):#遍历所有宽度的点
                data = img.getpixel((i,j))#打印该图片的所有点
                if (data[0]<=100 and data[1]<=120 and data[2]<=100 ):
                    img.putpixel((i,j),(255,255,255))
                if (data[0]>=100 and data[1]>=120 and data[2]>=100 ):
                    img.putpixel((i,j),(255,255,255))
                if (data[0]>=90 and data[1]>=90 and data[2]<=50 ):
                    img.putpixel((i,j),(255,255,255))
                if (data[0]>=100 and data[1]>=100 and data[2]<=120 ):
                    img.putpixel((i,j),(255,255,255))
                if (data[0]<=120 and data[1]>=90 and data[2]>=90 ):
                    img.putpixel((i,j),(255,255,255))
        img = img.convert('L')
        self.clearNoise(img,170,2,1)
        threshold = 170
        table = []
        for j in range(256):
            if j < threshold:
                table.append(0)
            else:
                table.append(1)
        img = img.point(table, '1')  
        img.save("C:\\Users\\lshao\\Desktop\\verifycode\\" + self.username +"code.jpeg")

    # 若出现点击图片,则破解
    def pic_main(self):
        try:
            ##  先下载图片
            time.sleep(1)
            self.downloadImg()
            text = self.gettext()
            print("-------------图片下载完成---------------\n")
            ## 图片二值化,方便识别
            self.convert()
            print("-------------图片二值化---------------\n")

            ## 读取图片(调用百度ocr)识别大图文字及位置信息
            posInfo = self.getPos(text)

            ## 点击提交按钮 ,在点击之前确认一下,大图与小图数字是否完全相等,若不相等,则重新识别
            print(type(text))
            print(type(posInfo))
            print(len(text))
            print(len(posInfo))
            ### 提交之前先判断一下,大小图字数是否一致,若不等,重新生成图片,重新识别
            while len(text) != len(posInfo) or posInfo is None:
                ## 刷新图片
                # /html/body/div[3]/div[4]/div/a
                
                self.driver.find_elements_by_xpath('/html/body/div[2]/div/div[2]/div')[0].click()
                time.sleep(2)

                ## 下载图片
                self.downloadImg()
                print("----------------------------------")
                ## 图片二值化,方便识别
                self.convert()
                ## 识别大图文字及位置信息
                text = self.gettext()
                posInfo = self.getPos(text)

            print('匹配成功，开始点击')
            ##  按顺序模拟点击
            self.clickWords(posInfo)
            ## 点选文字后提交
            # self.driver.find_elements_by_xpath('//*[@id="sliderddnormal-choose"]/div[2]/div[4]/a')[0].click()
            self.driver.implicitly_wait(5)
            self.driver.find_element_by_xpath('//*[@id="login"]/dd[5]/input').click()
            print("模拟点击完成,已提交...点选图片破解成功...")

        except:
            print("无点选文字点击图片")

def crawler(username,password):
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

    resp = requests.get(hlju_url,headers=Referer_header)
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(executable_path='C:\\Users\\lshao\\Desktop\\chromedriver',chrome_options=chrome_options)

    print(driver.get_cookies())
    driver.get("http://seat1.lib.hlju.edu.cn/login")
    driver.maximize_window() # 全屏网页窗口

    time.sleep(3)
    input_name = driver.find_element_by_xpath('//*[@id="login"]/dd[1]/input')
    input_name.clear()
    input_name.send_keys(username)
    input_pass = driver.find_element_by_xpath('//*[@id="login"]/dd[2]/input')
    input_pass.clear()
    input_pass.send_keys(password)

    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="login"]/dd[3]/input').click()
    time.sleep(1)
    # print(driver.page_source)
    driver.switch_to.frame(0)
    unlock = unlockScrapy(driver,username)
    unlock.pic_main()
    # driver.switch_to.default_content()
    # driver.implicitly_wait(5)
    # driver.find_element_by_xpath('//*[@id="login"]/dd[5]/input').click()
    info = driver.get_cookies()
    saveinfo(username,info[0]["value"])
    driver.close()

def saveinfo(username,cookie_value):
    for info in site_info:
        if(info["username"] == username):
            info["cookie_value"] = cookie_value
            info["login"] = "true"
    with open("C:\\Users\\lshao\\Desktop\\verifycode\\record.json","w") as f:
        json.dump(site_info,f)
        print("加载入文件完成...")
    # print(str(site_info))

def run():

    print('Start to Login %s ' % datetime.now())
    login_threads = []
    for info in site_info:
        if (info["login"] == "false"):
            print(info["username"] + "unlogin")
            crawler(info["username"],info["password"])
    # for info in site_info:
    #     thread = threading.Thread(target=crawler, args=(info["username"],info["password"],))
    #     login_threads.append(thread)

    # for i in range(len(site_info)):
    #     login_threads[i].start()

    # for i in range(len(site_info)):
    #     login_threads[i].join()

if __name__ == '__main__':
    # text = pytesseract.image_to_string('C:\\Users\\lshao\\Desktop\\verifycode\\1.png', config='eng')
    print('Task %s Start.' % datetime.now())
    run()
    # saveinfo('20165166','8FB55BF4CC79F3233DE4607E5B507CF6')
    print('Task %s end.' % datetime.now())
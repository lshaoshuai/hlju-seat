from PIL import Image, ImageDraw
import pytesseract
from io import BytesIO
from collections import defaultdict
from aip import AipOcr
from datetime import datetime, date, timedelta
import os,time,random,requests,threading,sys
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def getPixel(image,x,y,G,N):
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

def clearNoise(image,G,N,Z):
    draw = ImageDraw.Draw(image)
 
    for i in range(0,Z):
        for x in range(1,image.size[0] - 1):
            for y in range(1,image.size[1] - 1):
                color = getPixel(image,x,y,G,N)
                if color != None:
                    draw.point((x,y),color)

def downloadImg():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(executable_path='C:\\Users\\lshao\\Desktop\\chromedriver',chrome_options=chrome_options)
    driver.get("http://seat1.lib.hlju.edu.cn/simpleCaptcha/chCaptcha")
    driver.maximize_window()
    codeSrc = driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/img").get_attribute("src")
    print(codeSrc)
    resp = requests.get(codeSrc)
    fh = open("C:\\Users\\lshao\\Desktop\\verifycode\\code.jpeg", "wb")
    fh.write(resp.content)
    fh.close()
                            
def getcolor():
    img = Image.open("C:\\Users\\lshao\\Desktop\\verifycode\\code.jpeg")
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
            # else:
            #     img.putpixel((i,j),(0,0,0))
    img.save("C:\\Users\\lshao\\Desktop\\verifycode\\code2.jpeg")
    img = img.convert('L')
    clearNoise(img,170,2,1)
    img.save("C:\\Users\\lshao\\Desktop\\verifycode\\code3.jpeg")
    threshold = 170
    table = []
    for j in range(256):
        if j < threshold:
            table.append(0)
        else:
            table.append(1)
    img = img.point(table, '1')  
   
    img.save("C:\\Users\\lshao\\Desktop\\verifycode\\code4.jpeg")

def convert():
    im = Image.open("C:\\Users\\lshao\\Desktop\\verifycode\\code.jpeg")
    im1 = im.point(lambda p: p * 2)
    im2 = im1.convert('L')
    # for i in range(0,width):#遍历所有长度的点
    #     for j in range(0,height):#遍历所有宽度的点
    threshold = 200
    table = []
    for j in range(256):
        if j < threshold:
            table.append(0)
        else:
            table.append(1)
    im3 = im2.point(table, '1')   
    clearNoise(im3,200,7,7)      
    im3.save("C:\\Users\\lshao\\Desktop\\verifycode\\code1.jpeg")

class unlockScrapy(object):
    # super().__init__()的作用也就显而易见了，就是执行父类的构造函数，使得我们能够调用父类的属性。

    def __init__(self):
        super(unlockScrapy, self).__init__()

        self.WAPPID = '17062614'
        self.WAPPKEY = 'E15mYUgfBRVV3ohVVZZVcCCc'
        self.WSECRETKEY = 'ClxgLmf2U0DwgX9mSvZG7v4zInrrCT92'
        # 百度文字识别sdk客户端
        self.WCLIENT = AipOcr(self.WAPPID, self.WAPPKEY, self.WSECRETKEY)
        print("--------------初始化-----------")
        # 识别下面大图中的文字及坐标
    def getPos(self):

        try:
            print("开始识别大图...")
            op = {'language_type': 'CHN_ENG', 'recognize_granularity': 'small'}
            #accurategeneral
            res = self.WCLIENT.general(
                self.getFile("C:\\Users\\lshao\\Desktop\\verifycode\\code4.jpeg"), options=op)

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

            # 返回出现文字的位置信息
            print(needPosInfo)
            print("大图识别完成...")
            return needPosInfo
            
        except Exception as e:
            print(e)
    # 读取图片文件
    def getFile(self, filePath):
        with open(filePath, 'rb') as fp:
            print("-------------------读取图片-------------------")
            return fp.read()

if __name__ == '__main__':
    # text = pytesseract.image_to_string('C:\\Users\\lshao\\Desktop\\verifycode\\1.png', config='eng')
    print('Task %s Start.' % datetime.now())
    downloadImg()
    getcolor()
    unlock = unlockScrapy()
    unlock.getPos()
    print('Task %s end.' % datetime.now())
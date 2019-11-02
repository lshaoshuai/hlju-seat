import sys, os
from PIL import Image, ImageDraw
import pytesseract
from io import BytesIO
import requests
from collections import defaultdict
from aip import AipOcr
from datetime import datetime, date, timedelta

config = {
    'appId': '17663328',
    'apiKey': '	EG6651jtGBT7qQhY0dNtjLnf',
    'secretKey': 'qbVwXPQ9HomUG0aN1StvpQNl12fvOVKy'
}

client = AipOcr(**config)

def get_file_content(file):
    with open(file, 'rb') as fp:
        return fp.read()

def img_to_str(image_path):
    image = get_file_content(image_path)
    result = client.basicGeneral(image)
    return result

def convert():
    resp = requests.get("http://xsxk.hlju.edu.cn/xsxk/servlet/ImageServlet?d=1572488494125",timeout=1)
    image = Image.open(BytesIO(resp.content))
    imgry = image.convert('L')  
    threshold=150
    table=[]
    for i in range(256):
        if(i<threshold):
            table.append(0)
        else:
            table.append(1)
    im = imgry.point(table,"1")
    im.save('C:\\Users\\lshao\\Desktop\\verifycode\\imgb1.jpg')


if __name__ == '__main__':
    # text = pytesseract.image_to_string('C:\\Users\\lshao\\Desktop\\verifycode\\1.png', config='eng')
    print('Task %s Start.' % datetime.now())
    convert()
    text = img_to_str('C:\\Users\\lshao\\Desktop\\verifycode\\imgb1.jpg')
    print(text['words_result'][0]['words'])
    print('Task %s end.' % datetime.now())
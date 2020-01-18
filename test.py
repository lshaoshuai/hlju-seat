from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import base64
from PIL import Image
from aip import AipOcr

"""

https://www.jianshu.com/p/d59b47bc4812
利用Python3安装aip

https://blog.csdn.net/qq_38787214/article/details/87902291
Python3 super().__init__()测试及理解

https://www.cnblogs.com/duanwandao/p/9802795.html

https://blog.csdn.net/pythoncsdn111/article/details/96453839
https://blog.csdn.net/qq_42992919/article/details/98483845

https://blog.csdn.net/hhy1107786871/article/details/88342976


"""


# 破解携程反爬验证
class unlockScrapy(object):
    # super().__init__()的作用也就显而易见了，就是执行父类的构造函数，使得我们能够调用父类的属性。

    def __init__(self, driver):
        super(unlockScrapy, self).__init__()
        # selenium驱动
        self.driver = driver
        # self.WAPPID = '百度文字识别appid'
        # self.WAPPKEY = '百度文字识别appkey'
        # self.WSECRETKEY = '百度文字识别secretkey'
        # 百度文字识别sdk客户端
        # self.WCLIENT = AipOcr(self.WAPPID, self.WAPPKEY, self.WSECRETKEY)
        self.WAPPID = '17062614'
        self.WAPPKEY = 'E15mYUgfBRVV3ohVVZZVcCCc'
        self.WSECRETKEY = 'ClxgLmf2U0DwgX9mSvZG7v4zInrrCT92'
        # 百度文字识别sdk客户端
        self.WCLIENT = AipOcr(self.WAPPID, self.WAPPKEY, self.WSECRETKEY)
        print("5" * 10)




    ## 切换二维码登录,在切换回来,就会滑动出现
    ## 滑动出现后,输错一次密码,再登录,就会出现文字顺序验证码

    # 破解滑动
    ##  cpt - img - double - right - outer
    def unlockScroll(self):
        try:
            # 滑块element
            print("1" * 10)
            scrollElement = self.driver.find_elements_by_class_name(
                'cpt-img-double-right-outer')[0]
            print("2" * 10)
            ActionChains(self.driver).click_and_hold(
                on_element=scrollElement).perform()
            ActionChains(self.driver).move_to_element_with_offset(
                to_element=scrollElement, xoffset=30, yoffset=10).perform()
            ActionChains(self.driver).move_to_element_with_offset(
                to_element=scrollElement, xoffset=100, yoffset=20).perform()
            ActionChains(self.driver).move_to_element_with_offset(
                to_element=scrollElement, xoffset=200, yoffset=50).perform()
            print("滑块破解成功")
        except:
            print("无滑块")

    # 下载上面的小图和下面的大图
    def downloadImg(self):

        # 小图的src
        """//*[@id="sliderddnormal-choose"]/div[2]/div[1]/img"""
        # "/html/body/div[3]/div[1]/img"
        time.sleep(1)
        codeSrc = self.driver.find_element_by_xpath(
            "//*[@id='sliderddnormal-choose']/div[2]/div[1]/img").get_attribute("src")
        print(codeSrc)
        print("6" * 10)
        # 大图的src
        # "/html/body/div[3]/div[3]/img"
        checkSrc = self.driver.find_element_by_xpath(
            "//*[@id='sliderddnormal-choose']/div[2]/div[3]/img").get_attribute("src")
        print("7" * 10)
        print(codeSrc.split(','))

        """
        https://www.cnblogs.com/wswang/p/7717997.html
        Python解码base64遇到Incorrect padding错误
        
        """
        # 保存下载

        # 由于其src是base64编码的，因此需要以base64编码形式写入,
        # 由于标准的Base64编码后可能出现字符+和/，在URL中就不能直接作为参数，所以又有一种"url safe"的base64编码
        # base64.urlsafe_b64decode(base64_url)
        # fh.write(base64.b64decode(codeSrc.split(',')[1]))
        fh = open("code.jpeg", "wb")
        fh.write(base64.urlsafe_b64decode(codeSrc.split(',')[1]))
        fh.close()

        fh = open("checkCode.jpeg", "wb")
        fh.write(base64.urlsafe_b64decode(checkSrc.split(',')[1]))
        fh.close()



    """
    https://www.cnblogs.com/kongzhagen/p/6295925.html
    7. 点操作:
    im.point(function) #,这个function接受一个参数，且对图片中的每一个点执行这个函数
    比如：out=im.point(lambdai:i*1.5)#对每个点进行50%的加强
    """
    # 图片二值化，便于识别其中的文字
    def chageImgLight(self):
        im = Image.open("code.jpeg")
        im1 = im.point(lambda p: p * 4)
        im1.save("code.jpeg")
        im = Image.open("checkCode.jpeg")
        im1 = im.point(lambda p: p * 4)
        im1.save("checkCode.jpeg")

    # 读取图片文件
    def getFile(self, filePath):
        with open(filePath, 'rb') as fp:
            print("8读取图片" * 2)
            return fp.read()


    """
    # 请求参数
    language_type : 	识别语言类型，默认为CHN_ENG中英文混合；。可选值包括：
    detect_direction :是否检测图像朝向，默认不检测, ture 是检测
    # 返回参数
    words_result
    """
    # 识别上面小图中的文字
    def iTow(self):
        try:
            print("开始识别小图...")
            op = {'language_type': 'CHN_ENG', 'detect_direction': 'true'}
            res = self.WCLIENT.basicAccurate(
                self.getFile('code.jpeg'), options=op)  # options 可选参数
            words = ''
            print("9" * 10)
            # http://ai.baidu.com/docs#/OCR-Python-SDK/80d64770
            print(res['words_result'])  # api已经定好的  array	定位和识别结果数组
            print("10" * 10)
            for item in res['words_result']:
                if item['words'].endswith('。'):
                    words = words + item['words'] + '\r\n'
                else:
                    words = words + item['words']
            print('小图中的文字: ' + words)
            print("小图文字识别完成")
            return words
        except:
            return 'error'


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

            res = self.WCLIENT.accurate(
                self.getFile('checkCode.jpeg'), options=op)

            # 所有文字的位置信息
            allPosInfo = []
            # 需要的文字的位置信息
            needPosInfo = []
            print("#1" * 10)
            # 每日50000次,超时报错{'error_code': 17, 'error_msg': 'Open api daily request limit reached'}
            print(res)
            print(res['words_result'])
            print("#2" * 10)
            print("11" * 10)
            for item in res['words_result']:
                allPosInfo.extend(item['chars'])
                print(item['chars'])  # 文字及位置信息,见百度api

                print("12" * 10)
            # 筛选出需要的文字的位置信息
            for word in words:
                for item in allPosInfo:
                    if word == item['char']:
                        needPosInfo.append(item)
                        time.sleep(1)
                        print('大图中的文字: ' + item['char'])

            # 返回出现文字的位置信息

            print(needPosInfo)

            print("13" * 10)
            print("大图识别完成...")
            return needPosInfo
        except Exception as e:
            print(e)

    """
    https://blog.csdn.net/huilan_same/article/details/52305176
    ActionChains: 模拟鼠标操作比如单击、双击、点击鼠标右键、拖拽等等
    selenium之 玩转鼠标键盘操作（ActionChains）
    https://blog.csdn.net/ccggaag/article/details/75717186
    web自动化测试第6步：模拟鼠标操作（ActionChains）
    """

    # 点击大图上的文字
    def clickWords(self, wordsPosInfo):
        # 获取到大图的element
        #  /html/body/div[3]/div[3]/img
        imgElement = self.driver.find_element_by_xpath(
            '//*[@id="sliderddnormal-choose"]/div[2]/div[3]/img')
        # 根据上图文字在下图中的顺序依次点击下图中的文字
        for info in wordsPosInfo:
            # move_to_element_with_offset(to_element, xoffset, yoffset) ——移动到距某个元素（左上角坐标）多少距离的位置
            ActionChains(self.driver).move_to_element_with_offset(
                to_element=imgElement, xoffset=info['location']['left'] + 20,
                yoffset=info['location']['top'] + 20).click().perform()
            time.sleep(1)


    # 若出现点击图片,则破解
    def pic_main(self):
        try:
            ##  先下载图片
            time.sleep(1)
            self.downloadImg()
            print("14-0" * 10)
            ## 图片二值化,方便识别
            self.chageImgLight()

            ## 读取图片(调用百度ocr),识别小图文字
            text = self.iTow()
            ## 读取图片(调用百度ocr)识别大图文字及位置信息
            posInfo = self.getPos(text)

            ## 点击提交按钮 ,在点击之前确认一下,大图与小图数字是否完全相等,若不相等,则重新识别
            print(type(text))
            print(type(posInfo))
            print(len(text))
            print(len(posInfo))
            print("14" * 10)
            ### 提交之前先判断一下,大小图字数是否一致,若不等,重新生成图片,重新识别
            while len(text) != len(posInfo) or posInfo is None:
                ## 刷新图片
                # /html/body/div[3]/div[4]/div/a
                self.driver.find_elements_by_xpath(
                    '//*[@id="sliderddnormal-choose"]/div[2]/div[4]/div/a')[0].click()
                time.sleep(2)

                ## 下载图片
                self.downloadImg()
                print("14-1" * 10)
                ## 图片二值化,方便识别
                self.chageImgLight()

                ## 识别小图文字
                text = self.iTow()
                ## 识别大图文字及位置信息
                posInfo = self.getPos(text)

            print('匹配成功，开始点击')
            ##  按顺序模拟点击
            self.clickWords(posInfo)
            ## 点选文字后提交
            self.driver.find_elements_by_xpath(
                '//*[@id="sliderddnormal-choose"]/div[2]/div[4]/a')[0].click()

            print("模拟点击完成,已提交...点选图片破解成功...")
        except:
            print("无点选文字点击图片")







    # 破解滑动,点选文字图片
def unlock(name,pwd):
    # 创建浏览器对象
    driver = webdriver.Chrome(executable_path='C:\\Users\\lshao\\Desktop\\chromedriver')
    # 打开Chrome浏览器，需要将Chrome的驱动放在当前文件夹,也可以房子啊google.exe同目录下,需设置到环境变量
    # login_url = 'https://hotels.ctrip.com/hotel/6278770.html#ctm_ref=hod_hp_hot_dl_n_2_7'
    #             "https://passport.ctrip.com/user/login?BackUrl=https%3A%2F%2Fhotels.ctrip.com%2Fhotel%2F6278770.html%23ctm_ref%3Dhod_hp_hot_dl_n_2_7 "

    # 登录页面
    login_url = "https://passport.ctrip.com/user/login?BackUrl=https%3A%2F%2Fhotels.ctrip.com%2Fhotel%2F6278770.html%23ctm_ref%3Dhod_hp_hot_dl_n_2_7"
    driver.get(login_url)
    driver.maximize_window() # 全屏网页窗口
    time.sleep(3)
    # 切换账号密码登录表单
    # js1 = 'document.querySelector("#j_loginTab1").style.display="none";'
    # browser.execute_script(js1)
    # time.sleep(1)
    # js2 = 'document.querySelector("#j_loginTab2").style.display="block";'
    # browser.execute_script(js2)
    # driver.find_element_by_id('lbNormal').click()
    # time.sleep(3)


    #  输入账号密码
    input_name = driver.find_element_by_id('nloginname')
    input_name.clear()
    input_name.send_keys(name)
    input_pass = driver.find_element_by_id('npwd')
    input_pass.clear()
    input_pass.send_keys(pwd)
    time.sleep(3)

    # 此时可能出现有滑动验证码与点选文字
    ##  若出现滑块,则开始破解滑块
    unlock = unlockScrapy(driver)
    unlock.unlockScroll()

    ## 若出现点选文字,开始破解点选文字
    unlock.pic_main()

    # 点击登录
    print("3" * 10)
    """
    //*[@id="nsubmit"]
    """
    # browser.find_element_by_xpath('//*[@class="form__button"]/button').click()
    driver.find_element_by_xpath('//*[@class="form_btn form_btn--block"]').click()
    time.sleep(19)


# 如果破解成功，html的title会变
    if unlock.driver.title != '携程在手，说走就走':
        print('破解成功')
    else:
        # 再次尝试
        print('破解失败，再次破解')
        unlock.main()
        # 再次点击登录
        print("3" * 10)
        """
        //*[@id="nsubmit"]
        """
        # browser.find_element_by_xpath('//*[@class="form__button"]/button').click()
        driver.find_element_by_xpath('//*[@class="form_btn form_btn--block"]').click()
        time.sleep(19)
    time.sleep(9)



if __name__ == '__main__':
    name = str(input("请输入账号:"))
    pwd = str(input('请输入密码:'))
    for i in range(2):
        unlock(name,pwd)
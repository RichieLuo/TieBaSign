# -*- coding:utf-8 -*-
import os
import requests
import hashlib
import time
import copy
import logging
import random
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API_URL
LIKIE_URL = "http://c.tieba.baidu.com/c/f/forum/like"
TBS_URL = "http://tieba.baidu.com/dc/common/tbs"
SIGN_URL = "http://c.tieba.baidu.com/c/c/forum/sign"
USERINFO_URL="http://tieba.baidu.com/f/user/json_userinfo"
DATA_URL = "https://www.dongchedi.com/motor/pc/car/series/car_dealer_price?car_ids=56417,48718,57582,48999,49819&city_name=%E5%8D%97%E5%AE%81"

HEADERS2 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
}
HEADERS = {
    'Host': 'tieba.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
}
SIGN_DATA = {
    '_client_type': '2',
    '_client_version': '9.7.8.0',
    '_phone_imei': '000000000000000',
    'model': 'MI+5',
    "net_type": "1",
}

# VARIABLE NAME
COOKIE = "Cookie"
BDUSS = "BDUSS"
EQUAL = r'='
EMPTY_STR = r''
TBS = 'tbs'
PAGE_NO = 'page_no'
ONE = '1'
TIMESTAMP = "timestamp"
DATA = 'data'
FID = 'fid'
SIGN_KEY = 'tiebaclient!!!'
UTF8 = "utf-8"
SIGN = "sign"
KW = "kw"

HASFALSE = False
global FAILCOUNT
FAILCOUNT = 0
global FAILSTR
FAILSTR = ""
global FAILSTRR
FAILSTRR = ""

s = requests.Session()

def get_userinfo(bduss):
    logger.info("获取user_info开始")
    headers = copy.copy(HEADERS)
    headers.update({COOKIE: EMPTY_STR.join([BDUSS, EQUAL, bduss])})
    try:
        user_info = s.get(url=USERINFO_URL, headers=headers, timeout=5)
    except Exception as e:
        logger.error("获取user_info出错" + str(e))
        logger.info("重新获取user_info开始")
        user_info = s.get(url=USERINFO_URL, headers=headers, timeout=5)
    logger.info("获取user_info结束")
    return user_info

def get_carinfo():
    logger.info("获取info开始")
    headers = copy.copy(HEADERS2)
    try:
        car_info = s.get(url=DATA_URL, headers=headers, timeout=5).json()
    except Exception as e:
        logger.error("获取car_info出错" + str(e))
        logger.info("重新获取car_info开始")
        car_info = s.get(url=DATA_URL, headers=headers, timeout=5).json()
    logger.info("获取car_info结束")
    return car_info

def get_tbs(bduss):
    logger.info("获取tbs开始")
    headers = copy.copy(HEADERS)
    headers.update({COOKIE: EMPTY_STR.join([BDUSS, EQUAL, bduss])})
    try:
        tbs = s.get(url=TBS_URL, headers=headers, timeout=5).json()[TBS]
        #logger.info(tbs)
        #user_info=get_userinfo(bduss)
        #logger.info(user_info)
    except Exception as e:
        logger.error("获取tbs出错" + str(e))
        logger.info("重新获取tbs开始")
        tbs = s.get(url=TBS_URL, headers=headers, timeout=5).json()[TBS]
    logger.info("获取tbs结束")
    return tbs


def get_favorite(bduss):
    logger.info("获取关注的贴吧开始")
    # 客户端关注的贴吧
    returnData = {}
    i = 1
    data = {
        'BDUSS': bduss,
        '_client_type': '2',
        '_client_id': 'wappc_1534235498291_488',
        '_client_version': '9.7.8.0',
        '_phone_imei': '000000000000000',
        'from': '1008621y',
        'page_no': '1',
        'page_size': '200',
        'model': 'MI+5',
        'net_type': '1',
        'timestamp': str(int(time.time())),
        'vcode_tag': '11',
    }
    data = encodeData(data)
    try:
        res = s.post(url=LIKIE_URL, data=data, timeout=5).json()
    except Exception as e:
        logger.error("获取关注的贴吧出错" + e)
        sendEmail("90：获取关注的贴吧出错" + e)
        return []
    returnData = res
    if 'forum_list' not in returnData:
        returnData['forum_list'] = []
    if res['forum_list'] == []:
        return {'gconforum': [], 'non-gconforum': []}
    if 'non-gconforum' not in returnData['forum_list']:
        returnData['forum_list']['non-gconforum'] = []
    if 'gconforum' not in returnData['forum_list']:
        returnData['forum_list']['gconforum'] = []
    while 'has_more' in res and res['has_more'] == '1':
        i = i + 1
        data = {
            'BDUSS': bduss,
            '_client_type': '2',
            '_client_id': 'wappc_1534235498291_488',
            '_client_version': '9.7.8.0',
            '_phone_imei': '000000000000000',
            'from': '1008621y',
            'page_no': str(i),
            'page_size': '200',
            'model': 'MI+5',
            'net_type': '1',
            'timestamp': str(int(time.time())),
            'vcode_tag': '11',
        }
        data = encodeData(data)
        try:
            res = s.post(url=LIKIE_URL, data=data, timeout=5).json()
        except Exception as e:
            logger.error("获取关注的贴吧出错" + e)
            sendEmail("122：获取关注的贴吧出错" + e)
            continue
        if 'forum_list' not in res:
            continue
        if 'non-gconforum' in res['forum_list']:
            returnData['forum_list']['non-gconforum'].append(res['forum_list']['non-gconforum'])
        if 'gconforum' in res['forum_list']:
            returnData['forum_list']['gconforum'].append(res['forum_list']['gconforum'])

    t = []
    for i in returnData['forum_list']['non-gconforum']:
        if isinstance(i, list):
            for j in i:
                if isinstance(j, list):
                    for k in j:
                        t.append(k)
                else:
                    t.append(j)
        else:
            t.append(i)
    for i in returnData['forum_list']['gconforum']:
        if isinstance(i, list):
            for j in i:
                if isinstance(j, list):
                    for k in j:
                        t.append(k)
                else:
                    t.append(j)
        else:
            t.append(i)
    logger.info("获取关注的贴吧结束")
    return t


def encodeData(data):
    s = EMPTY_STR
    keys = data.keys()
    for i in sorted(keys):
        s += i + EQUAL + str(data[i])
    sign = hashlib.md5((s + SIGN_KEY).encode(UTF8)).hexdigest().upper()
    data.update({SIGN: str(sign)})
    return data


def client_sign(bduss, tbs, fid, kw):
    # 客户端签到
    logger.info("开始签到贴吧：" + kw)
    data = copy.copy(SIGN_DATA)
    data.update({BDUSS: bduss, FID: fid, KW: kw, TBS: tbs, TIMESTAMP: str(int(time.time()))})
    data = encodeData(data)
    res = s.post(url=SIGN_URL, data=data, timeout=5).json()
    return res
def sendEmail(msg,title):
    mail_user = os.environ["EMAILUSER"]
    mail_host = os.environ["EMAILHOST"]
    mail_pass = os.environ['EMAILPASS']
    mail_port = os.environ['EMAILPORT']
    sender = os.environ["EMAILSENDER"]
    receivers = [os.environ["EMAITO"]] 
  
    message = MIMEText(msg,'html','utf-8') 
    message['Subject'] = title
    message['From'] = formataddr([mail_user, sender])
    message['To'] = receivers[0] 
  
    try: 
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_host,mail_port) 
        smtpObj.ehlo()  # 发送SMTP 'ehlo' 命令
        smtpObj.starttls()
        smtpObj.login(sender,mail_pass) 
        smtpObj.sendmail(sender,receivers,message.as_string()) 
        smtpObj.quit() 
        logger.info("发送邮件成功") 
    except smtplib.SMTPException as e: 
        logger.error("发送邮件失败",e)
def handle_response(sign_resp,index,name):
    #sign_resp = json.loads(sign_resp)
    error_code = sign_resp['error_code']
    sign_bonus_point = 0
    cont_sign_num = 0
    user_sign_rank = 99999
    # logger.info(sign_resp)
    try:
        # Don't know why but sometimes this will trigger key error.
        sign_bonus_point = int(sign_resp['user_info']['sign_bonus_point'])
        cont_sign_num= int(sign_resp['user_info']['cont_sign_num'])
        user_sign_rank=int(sign_resp['user_info']['user_sign_rank'])
    except KeyError:
        pass
    if error_code == '0':
        logger.info("签到成功,经验+%d" % sign_bonus_point)
        logger.info("连续签到：%d 天" %cont_sign_num)
        logger.info("排名：%d " %user_sign_rank)
        return "签到成功,经验+"+str(sign_bonus_point)
    else:
        
        if error_code == '160002':
            logger.error("之前已签到")
            return '之前已签到'
        else:
            HASFALSE=True
            logger.error("签到失败****************************************")
            global FAILCOUNT
            FAILCOUNT =FAILCOUNT+1
            global FAILSTR
            FAILSTR=FAILSTR+'<p>'+'用户'+str(index)+'：'+name+'</p>'
            return '签到失败'
def main():
    time.sleep(55)
    car_info=get_carinfo()
    global FAILSTRR
    FAILSTRR=FAILSTRR+'<p>'+'英朗1.5自精(2021)：'+car_info["data"]["48718"]["dealer_price"]+'，优惠：'+car_info["data"]["48718"]["cut_price"]+'</p>'
    #FAILSTRR=FAILSTRR+'<p>'+'威朗Pro乐享版(2022)：'+car_info["data"]["56417"]["dealer_price"]+'，优惠：'+car_info["data"]["56417"]["cut_price"]+'</p>'
    #FAILSTRR=FAILSTRR+'<p>'+'朗逸1.5自舒(2022)：'+car_info["data"]["57582"]["dealer_price"]+'，优惠：'+car_info["data"]["57582"]["cut_price"]+'</p>'
    #FAILSTRR=FAILSTRR+'<p>'+'宝来1.5自精(2021)：'+car_info["data"]["49819"]["dealer_price"]+'，优惠：'+car_info["data"]["49819"]["cut_price"]+'</p>'
    #FAILSTRR=FAILSTRR+'<p>'+'伊兰特1.5精英(2021)：'+car_info["data"]["48999"]["dealer_price"]+'，优惠：'+car_info["data"]["48999"]["cut_price"]+'</p>'
    if(str(car_info["data"]["48718"]["cut_price"])!='4.50万'):
        sendEmail(FAILSTRR,'价格有变！')
    
    b = os.environ['BDUSS'].split('#')
    for n, i in enumerate(b):
        if(len(i) <= 0):
            logger.info("未检测到BDUSS")
            continue
        logger.info("---------------------------------------------开始签到第" + str(n+1) + "个用户---------------------------------------------")
        tbs = get_tbs(i)
        favorites = get_favorite(i)
        for j in favorites:
            time.sleep(random.randint(1,5))
            sign_resp= client_sign(i, tbs, j["id"], j["name"])
            #logger.info(sign_resp)
            res = handle_response(sign_resp,n+1,j["name"])
        logger.info("完成第" + str(n+1) + "个用户签到")
    sendEmail('<h3>所有用户签到结束</h3><p>失败数量：'+str(FAILCOUNT)+'</p>'+FAILSTR+'<p>感谢使用</p>','今日签到结果')
    logger.info("所有用户签到结束")
    
    


if __name__ == '__main__':
    main()

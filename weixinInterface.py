# -*- coding: utf-8 -*-
import hashlib
import web
import lxml
import time
import os
import md5
import urllib2,json
from lxml import etree
import random

class WeixinInterface:

    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render(self.templates_root)

    def GET(self):
        #获取输入参数
        data = web.input()
        signature=data.signature
        timestamp=data.timestamp
        nonce=data.nonce
        echostr=data.echostr
        #自己的token
        token="zhangjinglong" #这里改写你在微信公众平台里输入的token
        #字典序排序
        list=[token,timestamp,nonce]
        list.sort()
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()
        #sha1加密算法        

        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr
        
    def POST(self):        
        str_xml = web.data() #获得post来的数据
        xml = etree.fromstring(str_xml)#进行XML解析
        content=xml.find("Content").text#获得用户所输入的内容
        msgType=xml.find("MsgType").text
        fromUser=xml.find("FromUserName").text
        toUser=xml.find("ToUserName").text
        
        if msgType == 'text':
            content = xml.find("Content").text
            if content == 'help':
                return self.render.reply_text(fromUser, toUser, int(time.time()), u"随便看看？（对不起我功能有限QAQ）")
            else:
                if type(content).__name__ == "unicode":
                    content = content.encode('UTF-8')
                #return self.render.reply_text(fromUser,toUser,int(time.time()),u"我现在还在开发中，还没有什么功能，您刚才说的是："+content)
                return self.render.reply_text(fromUser,toUser,int(time.time()),youdao(content))
                
        #关注后的欢迎语 TODO
        if msgType == 'event':
            if xml.find("Event").text == 'subscribe':#关注的时候的欢迎语
                return self.render.reply_text(fromUser, toUser, int(time.time()), u"谢谢你的关注，输入help看看如何正确的调戏我")


        
        #Nword=youdao(content)
    	#return self.render.reply_text(fromUser,toUser,int(time.time()),Nword)
    
def youdao(q):        
    appKey = '68288d01f74b3f01'
    secretKey ='zRKls8HP3j3jeTZgFCYE2SzO9Xhp8jfi'        
    myurl ='http://openapi.youdao.com/api'

    fromLang = 'auto'#auto  EN
    toLang = 'auto'#auto  zh-CHS
    
    salt = random.randint(1, 65536)

    sign = appKey+q+str(salt)+secretKey
    
    

    m1 = md5.new()
    m1.update(sign)
    sign = m1.hexdigest()
    
    myurl = myurl+r'?appKey='+appKey+r'&q='+q+r'&from='+fromLang+r'&to='+toLang+r'&salt='+str(salt)+r'&sign='+sign
    #return myurl
    
	

    resp = urllib2.urlopen(myurl)
    fanyi = json.loads(resp.read())
    
    
    if fanyi['errorCode'] == 0:    
        ##根据json是否返回一个叫“basic”的key来判断是否翻译成功
        if 'basic' in fanyi.keys():
            trans = u'%s:\n%s\n%s\n网络释义：\n%s'%(fanyi['query'],''.join(fanyi['translation']),' '.join(fanyi['basic']['explains']),''.join(fanyi['web'][0]['value']))
            return trans
        else:
            trans =u'%s:\n基本翻译:%s\n'%(fanyi['query'],''.join(fanyi['translation']))        
            return trans
    elif fanyi['errorCode'] == 20:
        return u'对不起，要翻译的文本过长'
    elif fanyi['errorCode'] == 30:
        return u'对不起，无法进行有效的翻译'
    elif fanyi['errorCode'] == 40:
        return u'对不起，不支持的语言类型'
    else:
        return u'对不起，您输入的单词%s无法翻译,请检查拼写'% q
    
    
    
    
    
    
    
    
#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import re
import urllib, urllib2
import requests
import pymongo
import time
import datetime
from bs4 import BeautifulSoup

import multiprocessing as mp


class MongoDBIO:
    # 申明相关的属性
    def __init__(self, host, port, name, password, database, collection):
        self.host = host
        self.port = port
        self.name = name
        self.password = password
        self.database = database
        self.collection = collection

    # 连接数据库，db和posts为数据库和集合的游标
    def Connection(self):
        # connection = pymongo.Connection() # 连接本地数据库
        connection = pymongo.MongoClient(host=self.host, port=self.port)
        # db = connection.datas
        db = connection[self.database]
        if self.name or self.password:
            db.authenticate(name=self.name, password=self.password)  # 验证用户名密码
        # print "Database:", db.name
        # posts = db.cn_live_news
        posts = db[self.collection]
        # print "Collection:", posts.name
        return posts


# # 保存操作
# def ResultSave(save_host, save_port, save_name, save_password, save_database, save_collection, save_contents):
#     posts = MongoDBIO(save_host, save_port, save_name, save_password, save_database, save_collection).Connection()
#
#     for save_content in save_contents:
#         posts.save(save_content)
# 保存操作
def ResultSave(save_host, save_port, save_name, save_password, save_database, save_collection, save_content):
    posts = MongoDBIO(save_host, save_port, save_name, save_password, save_database, save_collection).Connection()
    posts.save(save_content)


httpheader = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
              # "Cookie": "CXID=6F68E12B09D9E7AD554306FA7AA92414; SUID=C6000A703765860A5A6DACE10000F218; IPLOC=CN3301; SUV=00D31780700A32065ABEE6FFB6B00686; sw_uuid=2178910194; sg_uuid=2411859637; dt_ssuid=7533481900; pex=C864C03270DED3DD8A06887A372DA219231FFAC25A9D64AE09E82AED12E416AC; ssuid=6183521250; ld=AZllllllll2zsmb@lllllVrfU2tllllltlohxkllll9lllllRZlll5@@@@@@@@@@; ABTEST=2|1526440850|v1; weixinIndexVisited=1; JSESSIONID=aaalexYGOx3Urd7TZ_inw; PHPSESSID=bvtuj2iesn8n4bpoa2rg7hjdc5; SUIR=EAF9F78DFDF890CAF9F09947FD98FC0D; sct=3; SNUID=BEACA2D8A9ADC5F46ED2F830A90C8A0D; successCount=1|Thu, 17 May 2018 01:35:10 GMT",
              "Host": "weixin.sogou.com",
              # "Referer": "http://weixin.sogou.com/weixin?type=2&s_from=input&query=%E6%B8%85%E5%8D%8E&ie=utf8&_sug_=n&_sug_type_=",
              # "Upgrade-Insecure-Requests": "1",
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"}


def GetTitleUrl(session, url, data):
    session.headers.update(**httpheader)
    r=session.get(url=url, params=data)
    content = r.content  # GET请求发送
    if "用户您好，您的访问过于频繁" in content:
        print "访问被限制了"
        print  session.cookies
        print  session.headers
        print  r.cookies
        print  r.headers
        print  content

    soup = BeautifulSoup(content, "lxml")
    tags = soup.findAll("h3")
    titleurl = []
    for tag in tags:
        item = {"title": tag.text.strip(), "link": tag.find("a").get("href"), "content": ""}
        titleurl.append(item)
    return titleurl


def GetContent(url):
    soup = BeautifulSoup(requests.get(url=url).content, "lxml")
    a = soup.find("a", text="阅读全文")
    if a:
        GetContent(a.href)
    tag = soup.find("div", attrs={"class": "rich_media_content", "id": "js_content"})  # 提取第一个标签
    content_list = [tag_i.text for tag_i in tag.findAll("p")]
    content = "".join(content_list)
    return content


def ContentSave(item):
    # 保存配置
    save_host = "localhost"
    save_port = 27017
    save_name = ""
    save_password = ""
    save_database = "testwechat"
    save_collection = "result"

    save_content = {
        "title": item["title"],
        "link": item["link"],
        "content": item["content"]
    }

    ResultSave(save_host, save_port, save_name, save_password, save_database, save_collection, save_content)


count = 0


def func(tuple):
    querystring, type, page,session = tuple[0], tuple[1], tuple[2],tuple[3]
    url = "http://weixin.sogou.com/weixin"
    # get参数
    data = {
        "query": querystring,
        "type": type,
        "page": page
    }

    titleurl = GetTitleUrl(session, url, data)

    global count

    for item in titleurl:
        url = item["link"]
        count += 1
        print "count:", count, "url:", url
        content = GetContent(url)
        item["content"] = content
        ContentSave(item)


if __name__ == '__main__':
    start = datetime.datetime.now()

    querystring = u"Python"  # u"区块链" "清华"
    type = 2  # 2-文章，1-微信号

    # 多进程抓取
    # p = mp.Pool()
    # p.map_async(func, [(querystring, type, page) for page in range(1, 50, 1)])
    # p.close()
    # p.join()

    # 单进程抓取
    sess= requests.session()
    for page in range(1, 50, 1):
        time.sleep(2)
        tuple = (querystring, type, page,sess)
        func(tuple)

    end = datetime.datetime.now()
    print "last time: ", end - start

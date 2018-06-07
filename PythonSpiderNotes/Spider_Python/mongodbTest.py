#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import re
import urllib, urllib2
import requests
import pymongo
import datetime
import multiprocessing as mp
import pprint


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
        client = pymongo.MongoClient(host=self.host, port=self.port)
        # db = connection.datas
        db = client[self.database]
        if self.name or self.password:
            db.authenticate(name=self.name, password=self.password)  # 验证用户名密码
        # print "Database:", db.name
        # posts = db.cn_live_news
        posts = db[self.collection]
        # print "Collection:", posts.name
        return posts


# 保存操作
# def ResultSave(save_host, save_port, save_name, save_password, save_database, save_collection, save_contents):
#     posts = MongoDBIO(save_host, save_port, save_name, save_password, save_database, save_collection).Connection()
#     for save_content in save_contents:
#         posts.save(save_content)
def ResultSave(save_host, save_port, save_name, save_password, save_database, save_collection, save_content):
    posts = MongoDBIO(save_host, save_port, save_name, save_password, save_database, save_collection).Connection()
    # ret =  posts.save(save_content)
    # ret = posts.insert_one(save_content)
    # pprint.pprint(posts.find_one())
    # print (ret)

    c=0
    for post in posts.find():
        # pprint.pprint(post)
        for k,v in post.items():
            print "%s:%s" % (k,v)
        c+=1

    print "count:",posts.count()
    print  "c:",c



def ContentSave():
    # 保存配置
    save_host = "localhost"
    save_port = 27017
    save_name = ""
    save_password = ""
    save_database = "textclassify"
    save_collection = "WallstreetcnSave"
    save_content = {"test": 1}

    ResultSave(save_host, save_port, save_name, save_password, save_database, save_collection, save_content)


if __name__ == '__main__':
    ContentSave()

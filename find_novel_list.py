# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 10:27:17 2021

目标URL：http://www.xbiquge.la/xiaoshuodaquan/

完成内容：将 小说名称 与 对应url 以字典形式存入novel_list.json文件
完成时间：2021.3.25.11：00

@author: 靳佳
"""

from lxml import etree
import requests
from fake_useragent import UserAgent
import json,os
def FindNovelList():
    url = "http://www.xbiquge.la/xiaoshuodaquan/"

    headers = {
        "User-Agent": UserAgent().chrome
    }
    response = requests.get(url, headers=headers)
    e = etree.HTML(response.text)  #返回字符串
    #由网页源码而定
    names = e.xpath('//a/text()')
    urls = e.xpath('//a/@href')
    # #打印结果
    # for name,url in zip(names,urls):
    #     print(name+' '+url)
    novel_list =[]
    novel={}
    for name,url in zip(names,urls):
        novel[name]=url
        novel_list.append(novel)
        novel={}
    #print(novel_list)
    with open('novel_list.json','w',encoding='utf-8') as f:
        f.write(json.dumps(novel_list,ensure_ascii=False))
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 00:00:55 2021

    目标功能：小说名称输入页面，依据输入内容直接调用多线程爬虫

    bug:会导致子窗口退出引发主窗口退出（按键响应中）
            # app = QCoreApplication.instance()
            # # 退出应用程序
            # app.quit()
爬虫部分：
    缺陷：1、缺乏必要的异常处理
     2、缺乏代理ip，有IP被封的风险（实测还好，暂不考虑）
     3、直接解析保存为txt可节省47%的磁盘空间

实现功能：输入小说名称，自动搜索对应url，据此爬取该小说所有章节名称和url（键值对）
         存入以小说名同名问价夹下的chapter_list.json文件
         同时，遍历chapter_list.json，将每章源码下载，并存为章名.html放于文件夹chapters下
         规范所保存的章节序号，避免后期处理时循序紊乱
         支持多线程爬取（缺乏异常处理）

完成时间：2021.3.30.10:41

工作：加入多线程并避免章节顺序紊乱
开始时间：2021.4.18 0:15
完成时间：2021.4.1 14:35

@author: 靳佳
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtCore import QBasicTimer
from lxml import etree
import requests
from fake_useragent import UserAgent
import json,os,sys
from pathlib import Path
from threading import Thread # 多线程
from queue import PriorityQueue,Queue # 优先队列 普通队列
# 自定义库
try:
    from reminders import Qreminder
except:
    from modules.reminders import Qreminder

# 对应小说搜索框界面
class QinputNovel(QDialog):
    def __init__(self):
        super().__init__()
        self.newNovel = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('请输入小说名称')
        self.setWindowIcon(QIcon('./images/book.ico'))
        self.setFixedSize(280,160)
        nameLabel = QLabel('名称：',self)
        nameLabel.setFont(QFont("宋体",12))
        self.nameLineEdit = QLineEdit(self)  # 必须设为类属性才能由onClick_Ok访问输入内容

        btnOK = QPushButton('确定')
        btnCancel = QPushButton('取消')
        #栅格布局
        mainLayout = QGridLayout(self)
        mainLayout.addWidget(nameLabel,0,0,2,2)
        mainLayout.addWidget(self.nameLineEdit,0,1,2,2)

        mainLayout.addWidget(btnOK,2,1)
        mainLayout.addWidget(btnCancel,2,2)

        #事件绑定
        btnOK.clicked.connect(self.onClick_Ok)
        btnCancel.clicked.connect(self.onClick_Cancel)

    def onClick_Ok(self):
        self.newNovel = self.nameLineEdit.text()
        """
            此处为多线程爬虫模块的调用（必要的报错窗口必须有）
        """
        Runspyder(self.newNovel)  #调用
        self.close()

    def onClick_Cancel(self):
        self.close()

#================================================================================================================================
# 请求头

headers = {
    "User-Agent": UserAgent().chrome
}

#据小说名保存章节列表
def find_chapter_list(novel_name,url):
    response = requests.get(url, headers=headers)
    e = etree.HTML(response.content.decode('utf-8'))  # 返回字符串
    # 由网页源码而定
    chapter_names = e.xpath('//div[@class="box_con"]/div[@id="list"]/dl/dd/a/text()')
    urls = e.xpath('//div[@class="box_con"]/div[@id="list"]/dl/dd/a/@href')

    chapter_list = []
    chapter = {}
    for name,url in zip(chapter_names,urls):
        chapter[name] = 'http://www.xbiquge.la'+url
        chapter_list.append(chapter)
        chapter={}

    os.chdir(novel_name) # 切换目录
    with open('chapter_list.json','w',encoding='utf-8') as f:
        f.write(json.dumps(chapter_list,ensure_ascii=False))

#读取小说章节列表，规范处理后保存到优先队列里,将队列返回
def getChapterUrl():
    chapters_queue = PriorityQueue()
    # 为网页源码的保存建立文件夹
    my_file = Path('chapters')
    if not my_file.exists():  # 判断路径是否存在
        os.mkdir('chapters')
    with open("chapter_list.json", mode='r', encoding="utf-8") as f:
        chapters = json.loads(f.read())  # 注：read读取出来的时字符串，需要转为json对象

    os.chdir('./chapters')  # 切换目录
    i = 0  # 计数器，用以规范章节序号
    for chapter in chapters:  # 由于字典键值不可哈希，所以转为字符串处理
        c_name_f = (str(chapter).split(":", 1))[0][2:-1]
        c_url = (str(chapter).split(":", 1))[1][2:-2]

        try:
            c1, c2 = c_name_f.split(" ")  # 规范章节序号，很关键
        except ValueError:
            c2 = "无题(或违规标题)"  # 防止章节名称为空

        finally:
            if c2[-1] in ['?', '!','*']:  # 排除特殊字符
                c2 = c2[:-1]
            if c2[0] in ['?',"!",'*']:
                c2 = c2[1:]
            c_name = '第' + str(i + 1) + '章 ' + c2 + ".html"
            chapters_queue.put((i,c_name,c_url))  # 以i排序
        i += 1
    return chapters_queue


# downloadLog = PriorityQueue()  #下载日志（失败残留）

class GetHtml(Thread):
    def __init__(self,chapters_queue):
        Thread.__init__(self)
        self.chapters_queue = chapters_queue

    def run(self):
        while self.chapters_queue.empty() == False:
            this_chapter =self.chapters_queue.get()
            if this_chapter[1] not in os.listdir(): # 避免重复下载
                response = requests.get(this_chapter[2], headers=headers)
                if response.status_code == 200:
                    response = response.content.decode("utf-8")
                    with open(this_chapter[1], 'w', encoding="utf-8") as f:
                        f.write(response)
                        print('正在写入第' + str(this_chapter[0] + 1) + '章')
                        # downloadLog.put((this_chapter[0]+1,'正在写入第' + str(this_chapter[0] + 1) + '章'))
            else:
                print(this_chapter[1],"已存在")
                # downloadLog.put((this_chapter[0]+1,this_chapter[1]+"已存在"))
        print('下载完成')


def Runspyder(n_name):
    url = ''
    if __name__ =="__main__":
        with open("../novel_list.json", mode='r', encoding="utf-8") as f:
            novels = json.loads(f.read())  # 注：read读取出来的时字符串，需要转为json对象
    else:
        with open("novel_list.json", mode='r', encoding="utf-8") as f:
            novels = json.loads(f.read())  # 注：read读取出来的时字符串，需要转为json对象

    for novel in novels:
        if n_name in novel:
            url = novel[n_name]
            if __name__ == "__main__":
                os.chdir('../books')
            else:
                os.chdir('./books')
            my_file = Path(n_name)
            if not my_file.exists():  # 判断路径是否存在
                os.mkdir(n_name)
            break
        else: #不是当前小说
            continue
    else:
        main_rm = Qreminder('Sorry!您所搜索的小说不存在！')
        main_rm.exec()
    if url != '':
        find_chapter_list(n_name, url)
        print('小说目录加载完成！')
        chapters_queue = getChapterUrl()
        print('小说目录队列加载完成！')
        # print(chapters_queue.queue) #测试无误
        # print(chapters_queue.qsize())

        # 创建各个爬虫
        crawl_list = []

        for i in range(0, 20):
            crawl1 = GetHtml(chapters_queue)
            crawl_list.append(crawl1)
            crawl1.start()
        for crawl in crawl_list:
            crawl.join()  # 阻塞
        """
            下两行为初步设定的进度条窗口调用部分（出大问题）：
                如何做到窗口显示和多线程爬取并行进行？
                是否将窗口也作为一个线程开启？
                参数如何传递？
                当前bug出在哪里？？？
        """
        # qpb = QProgressBar(n_name,chapters_queue) # 进度条显示
        # qpb.exec()
        main_rm = Qreminder('全部下载结束！')
        print("下载完后的工作目录：",os.getcwd())
        os.chdir('..')
        os.chdir('..')
        os.chdir('..')  # 将工作目录改回去
        main_rm.exec()


""" 
此部分为：下载进度条界面（出大问题）：暂且放弃
"""
# class QprogressBar(QDialog):
#     def __init__(self,newNovel,chapter_queue):
#         super(ProgressBar, self).__init__()
#         self.newNovel = newNovel
#         self.novelSize = chapter_queue.qsize()
#         self.d_queue = downloadLog
#         self.step = 0
#         self.setFixedSize(500, 250)
#         self.setWindowIcon(QIcon('./images/book.ico'))
#         self.setWindowTitle('正在下载: '+self.newNovel)
#
#         # 标签1
#         dlabel1 = QLabel(self)
#         dlabel1.setGeometry(30,20,90,50)
#         dlabel1.setText("正在下载：")
#         dlabel1.setFont(QFont('宋体',12))
#
#         # 文本框：
#         self.dline = QLineEdit(self)
#         self.dline.setGeometry(60,80,350,30)
#         self.dline.setReadOnly(True)
#         # 标签2
#         dlabel2 = QLabel(self)
#         dlabel2.setGeometry(30,120,90,50)
#         dlabel2.setText("下载进度：")
#         dlabel2.setFont(QFont('宋体',12))
#
#         self.pbar = QProgressBar(self)   # 进度条
#         self.pbar.setGeometry(30, 200, 450, 25)
#
#
#         self.timer = QBasicTimer()  # 时钟控件
#         self.timer.start(500, self) # 500ms一刷新
#
#     def timerEvent(self, event):
#         if self.step >= 100:  # 最大值
#             self.timer.stop()
#             self.close()
#         self.step = (self.d_queue.qsize()/self.novelSize)*100
#         self.dline.setText(self.d_queue.get()[1])
#         self.pbar.setValue(self.step)
#===============================================================================================================================

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = QinputNovel()
    main.show()
    sys.exit(app.exec_())
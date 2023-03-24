# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 00:00:55 2021
    目标功能：使用pyqt5完成阅读器界面设计，此文件为主页面设计内容
            包括：小说文本显示，打开各子页面的按钮，及部分事件响应
@author: 靳佳
"""
import sys,os,json,re
from lxml import html
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtCore import Qt,QSize
# 自定义界面
import modules.inputNovel as inputNovel
import modules.showVersion as showVersion
import modules.chapterList as chapterList
import modules.bookList as bookList
import modules.reminders as reminders
from find_novel_list import FindNovelList

# 检测books文件夹是否存在
if not os.path.exists(os.path.join(os.getcwd(), "books")):
    try:
        os.makedirs(os.path.join(os.getcwd(), "books"))
    except Exception as err:
        print(f"创建books目录失败：\n{err}")
        sys.exit(-1)

#  阅读器主页面
class QinterFace(QMainWindow):
    def __init__(self):
        super().__init__()
        self.novelName = None
        self.chapterNum = None
        self.allNum_of_novel = None
        self.chapterNames = []
        self.root = os.getcwd()  # 获取主题程序的工作目录

        self.initUI()
        #初始化时需要首次选择 小说 和 章节 作为首次打开的依据
        """
            解决问题：1、初始化如果无书，添加后可刷新出新书选项
                    2、加入循环避免未选择条件下显示文本时参数未定义
        """
        main_bL_first = bookList.QbookList()
        main_bL_first.Signal_of_novelName.connect(self.get_nn_from_bl)
        main_bL_first.exec()
        while self.novelName == None:  #初次未选择小说,循环打开书架
            main_bL_second = bookList.QbookList()
            main_bL_second.Signal_of_novelName.connect(self.get_nn_from_bl)
            main_bL_second.exec()

        main_cL_first = chapterList.QchapterList(self.novelName)
        main_cL_first.Signal_of_c_num.connect(self.get_cn_from_cl)
        main_cL_first.Signal_of_chapterNames.connect(self.get_cnames_from_cl)
        main_cL_first.Signal_of_all_num.connect(self.get_allnum_from_cl)
        main_cL_first.exec()
        while self.chapterNum == None:
            main_cL_second = chapterList.QchapterList(self.novelName)
            main_cL_second.Signal_of_c_num.connect(self.get_cn_from_cl)
            main_cL_second.Signal_of_chapterNames.connect(self.get_cnames_from_cl)
            main_cL_second.Signal_of_all_num.connect(self.get_allnum_from_cl)
            main_cL_second.exec()

        # 为保证“章节名称”和内容随章节索引同步刷新，需要读取出章节列表
        self.showTheTxt(self.novelName, self.chapterNum) #刷新文本内容

    def initUI(self):
        self.setFixedSize(800, 975)  # 固定窗口大小
        self.setWindowTitle('小说阅读器')  # 设置窗口标题
        self.setWindowIcon(QIcon('./images/book.ico'))  # 图标设置
        # 居中
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,0)

        # 1、菜单栏及其功能设置
        bar = self.menuBar()  # 获取菜单栏
        chapterList = bar.addMenu("章节目录")
        novelList = bar.addMenu("我的书架")
        showMsg = bar.addMenu("显示/保存/读取")  # 5.6修改
        novelReaderhelp = bar.addMenu("帮助")

        inputNewNovel = QAction("添加新书",self)  # 必加self
        novelList.addAction(inputNewNovel)
        inputNewNovel.triggered.connect(self.inputNewBook)  # 事件绑定

        catalog = QAction('查看目录',self)
        chapterList.addAction(catalog)
        catalog.triggered.connect(self.chapterList)

        bookshelf = QAction("查看书架",self)
        novelList.addAction(bookshelf)
        bookshelf.triggered.connect(self.bookList)

        statusMsg = QAction("显示当前小说信息",self)
        saveChapter = QAction("保存当前进度",self)   # 5.6日修改
        readChapter = QAction("读取阅读进度",self)
        showMsg.addAction(statusMsg)
        showMsg.addAction(saveChapter)
        showMsg.addAction(readChapter)
        statusMsg.triggered.connect(self.showStatusbar)
        saveChapter.triggered.connect(self.saveChapterNum)  # 事件绑定
        readChapter.triggered.connect(self.readChapterNum)

        version = QAction("Version",self)
        novelReaderhelp.addAction(version)
        version.triggered.connect(self.version)

        # 2、界面主体的设置(章节名称+内容+前后章跳转按钮)
        self.cNamebutton = QPushButton(self)
        self.cNamebutton.setEnabled(False)
        self.cNamebutton.setGeometry(0,25,800,30)
        self.cNamebutton.setFont(QFont('微软雅黑',12))
        self.textEdit = QTextEdit(self)
        self.textEdit.setGeometry(0,55,800,870)
        self.textEdit.setFont(QFont('楷体',12))

        self.pre_button = QPushButton(self)
        self.pre_button.setGeometry(0,925,200,25)
        self.pre_button.setText("上一章")
        self.pre_button.clicked.connect(self.preChapter)   # 事件绑定，章节跳转

        self.next_button = QPushButton(self)
        self.next_button.setGeometry(600,925,200,25)
        self.next_button.setText("下一章")

        self.next_button.clicked.connect(self.nextChapter)  # 事件绑定，章节跳转

    # 自书架到主窗口的参数传递
    def get_nn_from_bl(self,datastr):
        self.novelName = datastr

    # 自目录到主窗口的参数传递
    def get_cn_from_cl(self,dataint):
        self.chapterNum = dataint

    # 自目录到主窗口的参数传递
    def get_cnames_from_cl(self,datalist):
        self.chapterNames = datalist

    # 自目录到主窗口的参数传递
    def get_allnum_from_cl(self,dataint):
        self.allNum_of_novel = dataint


    # 包括数据解析和主页面文本显示部分（待改动）

    def showTheTxt(self,novel_name,c_num):
        """"""
        """
        暂定：
            1、定位到指定章节.html，读取，解析，显示txt
        （扩展）2、如何保存上次阅读进度，如何提供用户选择①接着读②自选章节阅读
            3、注：c_num自0开始，为索引值
            4、若当前章节不存在，弹窗提醒，避免异常返回
        """
        # 1、获取小说内容的先
        if os.getcwd() == self.root:
            os.chdir('./books/' + novel_name + '/chapters')
        elif os.getcwd() == self.root+'./books/':
            os.chdir('./' + novel_name + '/chapters')
        elif os.getcwd() == self.root + './books/' + novel_name:  # 新增分支
            os.chdir("./chapters")
        elif os.getcwd() == self.root+'./books/'+ novel_name+'/chapters':
            pass
        """
        2021.4.15后工作：基于章节序号的精准定位（文件列表操作）
        """
        file_name = ""
        c_list = os.listdir()
        for item in c_list:
            num_str = ""
            for j in re.findall(r'\d',item):
                num_str += j
            if int(num_str) == c_num+1:
                file_name = item
        """
            4.22后：异常处理，添加未下载章节下载功能，暂时解决
        """
        if file_name == "":  # 注意工作目录的转换
            main_rm = Qreminder_of_download(novel_name)
            os.chdir(self.root)
            main_rm.exec()
        else:
            f = open(file_name, 'r', encoding='utf-8')  # 默认顺序尚有问题，暂且不处理
            chapter_html = f.read()

            # 后期处理
            selector = html.fromstring(chapter_html)
            txt_list = selector.xpath('//div[@id = "content"]/text()')

            txt = ''
            for i in txt_list:  # 先拼接
                if i != '\n':
                    i = repr(i).replace(r'\xa0', '').replace("'", '')
                    txt += i
            txt = repr(txt).replace("\\n", '\n').replace('\\', '')  # 最终处理
            # print(txt) # 测试打印
            os.chdir(self.root)  # 工作目录改回去

           # 2、界面文本显示
            self.cNamebutton.setText(self.chapterNames[self.chapterNum])  # 确保章节名称随索引同步刷新
            self.textEdit.setPlainText(txt)
            self.textEdit.setReadOnly(True)   # 只读设置


    def inputNewBook(self):
        main_iN = inputNovel.QinputNovel()
        main_iN.exec()  #以exec()代替show()，避免子窗口闪退

    def chapterList(self):
        main_cL = chapterList.QchapterList(self.novelName)
        main_cL.Signal_of_c_num.connect(self.get_cn_from_cl)
        main_cL.exec()

        self.showTheTxt(self.novelName, self.chapterNum)  # 小说切换并选定章节后，刷新文本
    def bookList(self):  # 基本搞定
        self.saveChapterNum() # 调用，先保存当前进度
        main_bL = bookList.QbookList()
        main_bL.Signal_of_novelName.connect(self.get_nn_from_bl)
        main_bL.exec()
        main_cL = chapterList.QchapterList(self.novelName)
        main_cL.Signal_of_c_num.connect(self.get_cn_from_cl)
        main_cL.Signal_of_chapterNames.connect(self.get_cnames_from_cl)
        main_cL.Signal_of_all_num.connect(self.get_allnum_from_cl)
        main_cL.exec()
        self.showTheTxt(self.novelName, self.chapterNum)  # 小说切换并选定章节后，刷新文本

    def showStatusbar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('《'+self.novelName+"》共有%d章" % self.allNum_of_novel)
        self.statusBar

    # 保存阅读进度：手动保存/切换小说 时被调用
    def saveChapterNum(self):
        os.chdir(self.root+'./books/' + self.novelName)
        with open('reading_progress.txt','w',encoding="utf-8") as f:
            f.write(str(self.chapterNum))
        main_rm = reminders.Qreminder("阅读进度已保存！")
        main_rm.exec()
        os.chdir(self.root)

    # 读取阅读进度（手动）
    def readChapterNum(self):
        os.chdir(self.root+'./books/' + self.novelName)
        if 'reading_progress.txt' in os.listdir():
            with open('reading_progress.txt', 'r', encoding="utf-8") as f:
                self.chapterNum = int(f.read())
        else:
            main_rm = reminders.Qreminder("未找到保存的进度！")
            main_rm.exec()
        os.chdir(self.root)
        self.showTheTxt(self.novelName, self.chapterNum)  # 刷新文本内容


    def version(self):
        main_sV = showVersion.Qversion()
        main_sV.exec()

    def preChapter(self):
        if self.chapterNum == 0:
            """
                弹窗提醒：已经是第一章了。
            """
            main_rm = reminders.Qreminder("已经是第一章了")
            main_rm.exec()
        else:
            self.chapterNum -= 1
            self.showTheTxt(self.novelName, self.chapterNum)

    def nextChapter(self):
        if self.chapterNum == self.allNum_of_novel-1:
            """
                弹窗提醒：已经是第一章了。
            """
            main_rm = reminders.Qreminder("已经是最后一章了")
            main_rm.exec()
        else:
            self.chapterNum += 1
            self.showTheTxt(self.novelName, self.chapterNum)

# 继续下载界面
class Qreminder_of_download(QDialog):
    def __init__(self,novelName):
        super().__init__()
        self.novelName = novelName
        self.initUI()

    def initUI(self):
        self.setWindowTitle('阅读提示')
        self.setWindowIcon(QIcon('./images/book.ico'))
        self.setFixedSize(300,180)
        vLabel1 = QLabel(self)
        vLabel1.setText("此章节尚未下载")
        vLabel1.setFont(QFont("宋体",10))
        vLabel1.setGeometry(90,30,120,20)

        vLabel2 = QLabel(self)
        vLabel2.setText("是否继续下载？")
        vLabel2.setFont(QFont("宋体", 10))
        vLabel2.setGeometry(90, 70, 120, 20)

        btn_OK = QPushButton('确定',self)
        btn_OK.setGeometry(50,110,60,30)
        btn_Cancel = QPushButton('取消',self)
        btn_Cancel.setGeometry(190, 110, 60, 30)

        # 事件绑定
        btn_OK.clicked.connect(self.onClick_Ok)
        btn_Cancel.clicked.connect(self.onClick_Cancel)

    def onClick_Ok(self):
        """
            此处为多线程爬虫模块的调用
        """
        inputNovel.Runspyder(self.novelName)
        self.close()

    def onClick_Cancel(self):
        self.close()

if __name__=="__main__":
    #检测novel_list.json是否存在
    if 'novel_list.json' not in os.listdir():
        FindNovelList()

    #创建QApplication类的实例
    app = QApplication(sys.argv)
    #创建一个窗口
    mainW = QinterFace()
    #显示窗口
    mainW.show()
    #进入程序的主循环、并通过exit函数确保主循环安全退出
    sys.exit(app.exec_())
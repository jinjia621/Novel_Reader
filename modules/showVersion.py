# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 00:00:55 2021
目标功能：显示版本和作者
@author: 靳佳
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtCore import Qt
import sys

#对应小说搜索框界面
class Qversion(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('关于阅读器')
        self.setWindowIcon(QIcon('./images/book.ico'))
        self.setFixedSize(280,120)
        vLabel = QLabel('当前版本：1.0',self)
        author = QLabel("@author: 昨非",self)
        vLabel.setAlignment(Qt.AlignCenter)
        author.setAlignment(Qt.AlignCenter)
        vLabel.setFont(QFont("宋体",12))
        author.setFont(QFont("宋体", 12))
        # 垂直布局
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(vLabel)
        mainLayout.addWidget(author)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Qversion()
    main.show()
    sys.exit(app.exec_())
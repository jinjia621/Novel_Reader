# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 00:00:55 2021

    目标功能：完成各种小弹窗的类,支持传参显示所要提示的内容

@author: 靳佳
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtCore import Qt
import sys,os

#对应各种小提示弹窗界面
class Qreminder(QDialog):
    def __init__(self,tips):
        super().__init__()
        self.tips = tips
        self.initUI()

    def initUI(self):
        self.setWindowTitle('阅读提示')
        self.setWindowIcon(QIcon('./images/book.ico'))
        self.setFixedSize(280,120)
        vLabel = QLabel(self.tips,self)
        vLabel.setAlignment(Qt.AlignCenter)
        vLabel.setFont(QFont("宋体",10))
        # 垂直布局
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(vLabel)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tips = "这是一条提示!"
    main = Qreminder(tips)
    main.show()
    sys.exit(app.exec_())
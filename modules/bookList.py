# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 00:00:55 2021
目标功能：
        选中新书后，通过参数novelName打开其对应的章节列表
        书架无书时：点击按钮添加新书：调用inputNovel.py
@author: 靳佳
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtCore import QStringListModel,Qt,pyqtSignal
import sys,os

# 自定义模块
if __name__=="__main__":
    import inputNovel
else:
    import modules.inputNovel as inputNovel

# 对应小说搜索框界面
class QbookList(QDialog):
    Signal_of_novelName = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.newNovel = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('我的书架')
        if __name__ == "__main__":
            self.setWindowIcon(QIcon('../images/book.ico'))
        else:
            self.setWindowIcon(QIcon("./images/book.ico"))
        self.setFixedSize(300, 600)

        layout = QVBoxLayout()

        # 创捷列表组件
        listview = QListView()
        listModel = QStringListModel()
        if __name__ == "__main__":
            os.chdir("../books")
        else:
            os.chdir("./books")

        # 小说数目显示标签
        bookNum = len(os.listdir())
        booknumLable = QLabel("共有%d本书" % bookNum)
        booknumLable.setFont(QFont("宋体", 12))
        self.b_list = os.listdir()
        listModel.setStringList(self.b_list)

        listview.setModel(listModel)
        listview.setFont(QFont('楷体',13))
        listview.clicked.connect(self.clicked)

        inputButton = QPushButton()
        inputButton.setText("添加新书")
        inputButton.clicked.connect(self.inputNewbook)  # 按钮事件绑定

        # 加入垂直布局
        booknumLable.setAlignment(Qt.AlignCenter)
        layout.addWidget(booknumLable)
        layout.addWidget(listview)
        layout.addWidget(inputButton)

        self.setLayout(layout)
        # 防止第二次及其以后打开目录出问题，工作路径必须要改回去
        os.chdir("..")

    def clicked(self,item):
        QMessageBox.information(self,"小说选择","是否跳转到：" + self.b_list[item.row()]) # 考虑修改（O/C）
        self.Signal_of_novelName.emit(self.b_list[item.row()])
        # print(self.b_list[item.row()])
        # print(os.getcwd()) # 测试用
        self.close()

    def inputNewbook(self):
        inputnew = inputNovel.QinputNovel()
        inputnew.exec()  # 以exec()代替show()，避免子窗口闪退
        self.close()  # 关闭窗口以更新 bookList

if __name__ == '__main__':
    # print(os.getcwd()) # 测试用
    app = QApplication(sys.argv)
    main = QbookList()
    main.show()
    sys.exit(app.exec_())
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
import os 
import sys

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(960, 500)


        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.receiveDataButton = QtWidgets.QPushButton(self.centralwidget)
        self.receiveDataButton.setGeometry(QtCore.QRect(70, 130, 75, 30))
        self.receiveDataButton.setObjectName("pushButton")
        self.sendDataButton = QtWidgets.QPushButton(self.centralwidget)
        self.sendDataButton.setGeometry(QtCore.QRect(70, 200, 75, 30))
        self.sendDataButton.setObjectName("pushButton_2")
        self.connectRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.connectRadioButton.setGeometry(QtCore.QRect(260, 160, 90, 16))
        self.connectRadioButton.setObjectName("radioButton")
        self.connectButton = QtWidgets.QPushButton(self.centralwidget)
        self.connectButton.setGeometry(QtCore.QRect(250, 60, 75, 30))
        self.connectButton.setObjectName("pushButton_3")
        self.disconnectButton = QtWidgets.QPushButton(self.centralwidget)
        self.disconnectButton.setGeometry(QtCore.QRect(250,110,75,30))
        self.disconnectButton.setObjectName("pushButton_4")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(70, 60, 150, 30))
        self.comboBox.setObjectName("comboBox")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(360, 20, 570, 420))
        self.graphicsView.setObjectName("graphicsView")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(70, 30, 91, 21))
        self.label.setObjectName("label")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(60, 280, 250, 160))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.instructionsLabel = QtWidgets.QLabel(self.centralwidget)
        self.instructionsLabel.setGeometry(QtCore.QRect(70, 450, 100, 30))
        self.instructionsLabel.setObjectName("instructionsLabel")
        self.instructionsLabel.setText("操作说明")
        self.instructionsLabel.setStyleSheet("color: blue; text-decoration: underline;")
        self.instructionsLabel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.instructionsLabel.mousePressEvent = self.show_instructions
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 960, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "电控手柄调整"))
        self.receiveDataButton.setText(_translate("MainWindow", "读取数据"))
        self.sendDataButton.setText(_translate("MainWindow", "写入数据"))
        self.connectRadioButton.setText(_translate("MainWindow", "未连接"))
        self.connectButton.setText(_translate("MainWindow", "连接"))
        self.label.setText(_translate("MainWindow", "选择串口"))
        self.disconnectButton.setText(_translate("MainWindow","断开"))


    # 获取图片的路径
    def resource_path(self,relative_path):
        try:
            # 打包后的路径
            base_path = sys._MEIPASS
        except Exception:
            # 开发时的路径
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def show_instructions(self, event):
        """显示操作说明图片"""
        img_path = self.resource_path("instruction.png")  # 图片路径
        pixmap = QtGui.QPixmap(img_path)  # 加载图片
        if pixmap.isNull():  # 检查图片是否加载成功
            QtWidgets.QMessageBox.warning(self, "错误", "无法加载操作说明图片！")
            return

        # 创建一个新的对话框来显示图片
        img_dialog = QtWidgets.QDialog(self)
        img_dialog.setWindowTitle("操作说明")
        img_dialog.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)  # 确保窗口在最上层

        img_label = QtWidgets.QLabel(img_dialog)  # 在对话框中创建标签
        img_label.setPixmap(pixmap)  # 设置标签的图片
        img_label.resize(pixmap.size())  # 调整标签大小以适应图片

        # 设置对话框的大小
        img_dialog.resize(pixmap.size())
        img_dialog.exec_()  # 显示对话框

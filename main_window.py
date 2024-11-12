# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


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

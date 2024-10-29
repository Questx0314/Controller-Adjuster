import sys
import serial.tools.list_ports
from PyQt5 import QtWidgets,QtGui,QtCore
from main_window import Ui_MainWindow  # 假设生成的文件名为 main_window_ui.py
from matplotlib import rcParams
from matplotlib.figure import Figure 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setFixedSize(960, 500)  # 设置固定大小

        # 初始化点的坐标
        self.points = [0, 0, 25, 25, 50, 50, 75, 75,100,100]

        # 设置 QGraphicsView 场景
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)

        # 显示点列表和初始化图表
        self.setup_table_widget()
        self.populate_table_widget()
        self.draw_plot()

        self.populate_com_ports()  # 自动填充串口
        self.pushButton_3.clicked.connect(self.populate_com_ports)  # 连接按钮点击时刷新串口列表

        # 连接表格项更改信号以更新图表
        self.tableWidget.itemChanged.connect(self.update_point_from_table)

    def setup_table_widget(self):
        """设置表格的行和列标题"""
        self.tableWidget.setRowCount(len(self.points) // 2)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["行程", "电流值"])
        
        # 设置行标题
        for i in range(len(self.points) // 2):
            self.tableWidget.setVerticalHeaderItem(i, QtWidgets.QTableWidgetItem(f"第{i + 1}点"))

        # 获取表格的宽度和高度
        table_width = self.tableWidget.width()-30
        table_height = self.tableWidget.height()-100

        # 获取标题的高度
        header_height = self.tableWidget.horizontalHeader().height()
        header_width = self.tableWidget.verticalHeader().width()
  
        # 计算可用高宽
        available_height = table_height - header_height
        available_width = table_width - header_width

        # 设置列宽（平均分配）
        self.tableWidget.setColumnWidth(0, available_width // 2)  # 行程列宽
        self.tableWidget.setColumnWidth(1, available_width // 2)  # 电流值列宽

        # 计算行高（根据可用高度和行数平均分配）
        row_height = available_height // self.tableWidget.rowCount()
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.setRowHeight(i, row_height)

        # 确保只自动调整已填充的行
        self.tableWidget.resizeRowsToContents()

    def populate_table_widget(self):
        """在 QTableWidget 中填充坐标点"""
        for i in range(0, len(self.points), 2):
            x = self.points[i]
            y = self.points[i + 1]
            row = i // 2
            # 填入 x 坐标
            x_item = QtWidgets.QTableWidgetItem(str(x))
            x_item.setTextAlignment(QtCore.Qt.AlignCenter)  # 设置居中
            self.tableWidget.setItem(row, 0, x_item)
            # 填入 y 坐标
            y_item = QtWidgets.QTableWidgetItem(str(y))
            y_item.setTextAlignment(QtCore.Qt.AlignCenter)  # 设置居中
            self.tableWidget.setItem(row, 1, y_item)

    def populate_com_ports(self):
        # 清空 comboBox 的内容
        self.comboBox.clear()
        
        # 获取所有可用的串口
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # 添加串口名称到 comboBox
            self.comboBox.addItem(port.device)

    def update_point_from_table(self, item):
        """当 QTableWidget 中的点被编辑后更新 self.points 列表"""
        row = item.row()
        col = item.column()
        
        try:
            # 读取更新后的值
            value = int(item.text())
            # 检查输入的值是否在 0 到 100 之间
            if 0 <= value <= 100:
                # 更新 points 列表
                self.points[2 * row + col] = value
                # 重新绘制图表
                self.draw_plot()
            else:
                QtWidgets.QMessageBox.warning(self, "输入错误", "坐标值必须在 0 到 100 之间")
                # 恢复到原值
                self.populate_table_widget()
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请输入有效的坐标")
            # 恢复到原值
            self.populate_table_widget()

    def draw_plot(self):
        """根据 points 绘制折线图"""
        # 创建 Matplotlib 图形
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        
        # 清除之前的绘图
        self.graphicsView.setScene(QtWidgets.QGraphicsScene(self))
        self.graphicsView.scene().addWidget(self.canvas)

        # 设置字体为支持中文的字体
        from matplotlib import rcParams
        rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
        rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        # 绘制折线图
        ax = self.figure.add_subplot(111)
        x_values = self.points[::2]  # x 坐标
        y_values = self.points[1::2]  # y 坐标

        ax.plot(x_values, y_values, marker='o')
        ax.set_xlabel("行程 (%)")  # x 轴标题
        ax.set_ylabel("电流值 (%)")  # y 轴标题
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)

        self.canvas.draw()

                                          
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
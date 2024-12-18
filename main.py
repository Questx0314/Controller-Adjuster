import sys
import serial.tools.list_ports
from PyQt5 import QtWidgets,QtCore
from main_window import Ui_MainWindow  # 假设生成的文件名为 main_window_ui.py
from matplotlib import rcParams
from matplotlib.figure import Figure 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 设置和串口之间的波特率
        self.baud_rate = 9600

        # 设置固定大小
        self.setFixedSize(960, 500)  

        # 初始化点的坐标
        self.points = [0, 0, 25, 25, 50, 50, 75, 75,100,100]
        self.serial_port = None

        # 设置 QGraphicsView 场景
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)

        # 显示点列表和初始化图表
        self.setup_table_widget()
        self.populate_table_widget()
        self.draw_plot()

        # 禁用按钮
        self.set_button_state(False)
        self.connectRadioButton.setEnabled(False)
        self.set_radioButton_state(0)

        self.populate_com_ports()  # 自动填充串口
        self.connectButton.clicked.connect(self.connect_to_serial_port)  # 连接按钮点击
        self.sendDataButton.clicked.connect(self.send_points_to_serial) # 发送消息按钮点击
        self.comboBox.currentIndexChanged.connect(self.on_combobox_change) # combobox内容控制
        self.receiveDataButton.clicked.connect(self.request_data_from_serial) # 点击读取数据
        self.disconnectButton.clicked.connect(self.disconnect) # 点击断开按钮

        # 连接表格项更改信号以更新图表
        self.tableWidget.itemChanged.connect(self.update_point_from_table)

    def on_combobox_change(self):
        if self.comboBox.currentText() == "刷新":
            self.populate_com_ports()  # 选择刷新时更新串口列表

    def populate_com_ports(self):
        """控制combobox状态"""
        self.comboBox.clear()         # 清空 comboBox 的内容
        ports = serial.tools.list_ports.comports()         # 获取所有可用的串口
        for port in ports:
            self.comboBox.addItem(port.device) # 添加串口名称到 comboBox
        self.comboBox.addItem("刷新")  # 添加刷新选项
    
    def set_button_state(self,state = False):
        """控制按钮的禁用状态"""
        self.receiveDataButton.setEnabled(state)
        self.sendDataButton.setEnabled(state)

    def set_radioButton_state(self,state=0):
        """控制radioButton的状态"""
        match state:
            case 0:#未连接状态
                self.connectRadioButton.setChecked(False)
                self.connectRadioButton.setText("未连接")
            case 1:#连接失败状态
                self.connectRadioButton.setChecked(False)
                self.connectRadioButton.setText("连接失败")
            case 2:#连接成功状态
                self.connectRadioButton.setChecked(True)
                self.connectRadioButton.setText("连接成功")

    def connect_to_serial_port(self):
        """点击连接按钮"""
        response = self.send_data("FS connect")
        if response == "connect success":
            self.set_radioButton_state(2)
            self.set_button_state(True)
            self.comboBox.setEnabled(False)
        else:
            self.set_radioButton_state(1)
            self.set_button_state(False)
            self.comboBox.setEnabled(True)

    def disconnect(self):
        """点击断开按钮"""
        self.set_radioButton_state(0)
        self.set_button_state(False)
        self.comboBox.setEnabled(True)

    def send_data(self,data):
        """发送数据"""
        selected_port = self.comboBox.currentText()
        if selected_port == "刷新" or selected_port == "":
            QtWidgets.QMessageBox.warning(self, "错误", "请选择有效的串口！")
            return "未选择串口"
        
        try:
            self.serial_port = serial.Serial(selected_port, baudrate=self.baud_rate, timeout=3)  # 3秒超时
            print(f"打开串口: {selected_port}")

            # 检查串口是否成功打开
            if not self.serial_port.is_open:
                QtWidgets.QMessageBox.warning(self, "错误", f"无法打开串口 {selected_port},请选择正确串口")
                return "串口无法打开"
            
            # 尝试发送数据
            try:
                self.serial_port.write(data.encode())
                print(f"发送数据: {data}")
            except serial.SerialTimeoutException:
                QtWidgets.QMessageBox.warning(self, "错误", "串口写入超时")
                self.serial_port.close()
                return "串口写入超时"
            except serial.SerialException as e:
                QtWidgets.QMessageBox.warning(self, "错误", f"串口写入失败: {str(e)}")
                self.serial_port.close()
                return f"串口写入失败: {str(e)}"       
            except Exception as e:
                # 捕获其他未知错误
                QtWidgets.QMessageBox.warning(self, "错误", f"发生未知错误: {str(e)}")
                print(f"发生未知错误: {str(e)}")
                return "未知错误"     

            # 等待回应
            response = self.wait_for_response()

            # 关闭串口
            if self.serial_port.is_open:
                self.serial_port.close()
                print("关闭串口")

            if response is None:
                response = "没有回应"

            return response 
        except serial.SerialException as e:
            QtWidgets.QMessageBox.warning(self, "错误", f"串口错误: {str(e)}")
            return "串口错误"
        except Exception as e:
            # 捕获其他未知错误
            QtWidgets.QMessageBox.warning(self, "错误", f"发生未知错误: {str(e)}")
            print(f"发生未知错误: {str(e)}")
            return "未知错误"
        finally:
            # 确保串口关闭
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                print("关闭串口")
        
    def wait_for_response(self):
        """等待回应并处理"""
        self.response = None

        # 设置计时器超时为3秒
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start(3000)  # 3秒等待时间

        while self.response is None:
            QtWidgets.QApplication.processEvents()  # 保持应用响应，等待接收数据
            if self.serial_port.in_waiting > 0:  # 检查是否有可用数据
                response_data = self.serial_port.readline().decode('utf-8').strip()  # 读取一行数据并解码
                if response_data:
                    self.response = response_data  # 存储收到的响应
                    print(f"收到数据: {response_data}")
                    break
        # 停止计时器
        self.timer.stop()
        
        return self.response
    
    def on_timeout(self):
        """超时处理"""
        if self.response is None:
            self.response = "超时"  # 设置回应为超时

    def request_data_from_serial(self):
        """发送读取数据的请求"""
        response = self.send_data("FS request points")
        self.check_data_format(response)

    def send_points_to_serial(self):
        """向选中的串口发送 points 数据"""
        data_to_send = "FS send points:" + ",".join(map(str, self.points)) + "\n"  # 格式化数据
        response = self.send_data(data_to_send)  # 发送数据并等待响应
        if response == "data send success":
            QtWidgets.QMessageBox.information(self, "成功", "数据写入成功！")
        else:
            QtWidgets.QMessageBox.warning(self, "失败", "数据写入失败！正在重新测试连接...")
            self.connect_to_serial_port()

    def check_data_format(self,data):
        if data is None:
            QtWidgets.QMessageBox.warning(self, "未接收到数据", "未能接收到数据，请检查连接。")
            return
        
        if data.startswith("Controller send points:"):
            # 提取坐标数据部分
            points_data = data[len("Controller send points:"):].strip()
            point_values = points_data.split(",")  # 按逗号分割坐标值

            # 检查数据格式是否正确并更新 points
            valid_data = True
            new_points = []
            for value in point_values:
                try:
                    point = float(value)
                    if 0 <= point <= 100:
                        new_points.append(point)
                    else:
                        valid_data = False
                        break
                except ValueError:
                    valid_data = False
                    break

            if valid_data and len(new_points) == 10:  # 确保有 5 对坐标
                self.points = new_points
                self.populate_table_widget()  # 更新表格
                self.draw_plot()  # 重绘图形
                QtWidgets.QMessageBox.information(self, "成功", "数据读取成功！")
            else:
                QtWidgets.QMessageBox.warning(self, "数据错误", "接收到的数据格式不正确或超出范围！")
        else:
            print("接收到的响应格式不正确")  # 打印调试信息
            QtWidgets.QMessageBox.warning(self, "数据错误", "接收到的响应格式不正确，请检查设备。")

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

    def update_point_from_table(self, item):
        """当 QTableWidget 中的点被编辑后更新 self.points 列表"""
        row = item.row()
        col = item.column()
        
        try:
            # 读取更新后的值
            value = float(item.text())
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
import tkinter as tk
from tkinter import scrolledtext, simpledialog, Listbox
from tkinter import ttk
import serial
import threading
import serial.tools.list_ports

class SerialDebugger:
    def __init__(self, master):
        self.master = master
        self.master.title("串口调试器")

        self.serial_port = None
        self.running = False
        self.points = [0,50,25,50,50,50,75,50,100,50]  # 初始五个点的XY坐标

        # 创建布局框架
        self.frame = tk.Frame(master)
        self.frame.pack(padx=10, pady=10)

        # 左列
        self.port_label = tk.Label(self.frame, text="串口号:")
        self.port_label.grid(row=0, column=0, pady=5)

        self.port_combobox = ttk.Combobox(self.frame, values=self.get_serial_ports())
        self.port_combobox.grid(row=0, column=1, pady=5)

        self.baudrate_label = tk.Label(self.frame, text="波特率:")
        self.baudrate_label.grid(row=1, column=0, pady=5)

        self.baudrate_entry = tk.Entry(self.frame, width=10)
        self.baudrate_entry.grid(row=1, column=1, pady=5)
        self.baudrate_entry.insert(0, "9600")  # 默认波特率

        self.connect_button = tk.Button(self.frame, text="连接", command=self.connect)
        self.connect_button.grid(row=2, column=0, pady=5)

        self.disconnect_button = tk.Button(self.frame, text="断开", command=self.disconnect)
        self.disconnect_button.grid(row=2, column=1, pady=5)

        # 右列
        self.send_text = tk.Entry(master, width=50)
        self.send_text.pack(pady=10)

        self.send_button = tk.Button(master, text="发送", command=self.send_data)
        self.send_button.pack(pady=5)

        self.recv_text = scrolledtext.ScrolledText(master, width=60, height=20)
        self.recv_text.pack(pady=10)

        # 坐标管理
        self.coord_label = tk.Label(master, text="坐标点:")
        self.coord_label.pack(pady=5)

        self.coord_listbox = Listbox(master, width=30, height=5)
        self.coord_listbox.pack(pady=5)

        self.add_point_button = tk.Button(master, text="添加点", command=self.add_point)
        self.add_point_button.pack(pady=5)

        self.send_points_button = tk.Button(master, text="发送点数据", command=self.send_points)
        self.send_points_button.pack(pady=5)

        self.update_coord_listbox()  # 初始化时更新坐标列表

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect(self):
        port = self.port_combobox.get()
        baudrate = int(self.baudrate_entry.get())
        self.serial_port = serial.Serial(port, baudrate)
        self.running = True
        self.recv_text.insert(tk.END, f"已连接到 {port}，波特率: {baudrate}\n")
        self.recv_text.see(tk.END)

        # 启动接收线程
        threading.Thread(target=self.receive_data, daemon=True).start()

    def disconnect(self):
        if self.serial_port:
            self.running = False
            self.serial_port.close()
            self.recv_text.insert(tk.END, "已断开连接\n")
            self.recv_text.see(tk.END)

    def send_data(self):
        if self.serial_port:
            data = self.send_text.get()
            self.serial_port.write(data.encode('utf-8'))
            self.recv_text.insert(tk.END, f"发送: {data}\n")
            self.recv_text.see(tk.END)
            self.send_text.delete(0, tk.END)

    def send_points(self):
        if self.serial_port:
            points_data = ",".join([f"({x},{y})" for x, y in self.points])
            message = f"FS points: {points_data}"
            self.serial_port.write(message.encode('utf-8'))
            self.recv_text.insert(tk.END, f"发送点数据: {message}\n")
            self.recv_text.see(tk.END)

    def receive_data(self):
        while self.running:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8').rstrip()
                self.recv_text.insert(tk.END, f"接收: {data}\n")
                self.recv_text.see(tk.END)

                # 检查接收到的消息
                if data == "FS connect":
                    self.serial_port.write("connect success".encode('utf-8'))  # 发送确认消息
                # 发送成功确认消息
                elif data.startswith("FS send points:"):
                    points_data = data[len("FS send points:"):].strip()
                    try:
                        # 解析点坐标
                        points_list = list(map(int, points_data.split(',')))  # 将字符串分割并转换为浮点数
                        self.points = points_list  # 更新点坐标
                        self.update_coord_listbox()  # 更新列表框
                        self.serial_port.write("data send success".encode('utf-8'))  # 发送成功确认
                    except Exception as e:
                        self.recv_text.insert(tk.END, f"解析点数据失败: {str(e)}\n")
                        self.recv_text.see(tk.END)
                        self.serial_port.write("data send failed".encode('utf-8'))  # 发送失败确认
                # 收到发送数据的请求，发送数据
                elif data == "FS request points":
                    data_to_send = "Controller send points:"+",".join(map(str, self.points)) + "\n"
                    self.serial_port.write(data_to_send.encode('utf-8'))
                    self.recv_text.insert(tk.END,f"发送: {data_to_send}\n")
                    self.recv_text.see(tk.END)
    def add_point(self):
        if len(self.points) < 5:
            x = float(simpledialog.askstring("输入X坐标", "请输入X坐标:"))
            y = float(simpledialog.askstring("输入Y坐标", "请输入Y坐标:"))
            self.points.append((x, y))
            self.update_coord_listbox()
        else:
            self.recv_text.insert(tk.END, "最多只能添加5个点\n")
            self.recv_text.see(tk.END)

    def update_coord_listbox(self):
        self.coord_listbox.delete(0, tk.END)  # 清空列表框
        for i in range(0, len(self.points), 2):  # 步长为2
            x = self.points[i]
            y = self.points[i + 1]
            self.coord_listbox.insert(tk.END, f"点{i // 2 + 1}: ({x}, {y})")

if __name__ == "__main__":
    root = tk.Tk()
    debugger = SerialDebugger(root)
    root.mainloop()

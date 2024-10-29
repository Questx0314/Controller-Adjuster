import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial.tools.list_ports
import random

# 定义数据点
points = [0, 0, 25, 0, 50, 0, 75, 0, 100, 0]
baud_rate = 115200

# 获取可用的 USB 接口
def get_usb_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# 刷新下拉菜单的端口列表
def refresh_ports():
    ports = get_usb_ports()
    combo['values'] = ports  # 更新下拉菜单的选项
    if ports:
        combo.current(0)  # 选择第一个可用端口
    else:
        combo.set("无可用端口")

# 按钮点击事件
def on_button_click():
    plot_data(points)  # 根据 points 数据绘制折线图

def plot_data(data_points):
    ax.clear()
    # 生成 X 坐标
    x_points = data_points[0::2]  # x1, x2, ...
    y_points = data_points[1::2]  # y1, y2, ...
    ax.plot(x_points, y_points, 'b-o')  # 画折线图
    ax.set_title("折线图")
    ax.set_xlabel("X 轴")
    ax.set_ylabel("Y 轴")
    canvas.draw()   

# 主窗口
root = tk.Tk()
root.title("电控手柄曲线调整对话框")
root.geometry("1280x600")  # 设置窗口尺寸为 1280x600
root.resizable(False, False)  # 禁止调整窗口大小

# 下拉菜单（Combobox）
label_combo = ttk.Label(root, text="选择 USB 接口:")
label_combo.grid(row=0, column=0, padx=10, pady=5, sticky='w')
combo = ttk.Combobox(root)
combo.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
refresh_ports()  # 初始化时加载端口列表

# 按钮
button1 = tk.Button(root, text="生成图表", command=on_button_click)
button1.grid(row=1, column=0, padx=10, pady=5, sticky='ew')

button2 = tk.Button(root, text="按钮2", command=lambda: print("按钮2被点击"))
button2.grid(row=2, column=0, padx=10, pady=5, sticky='ew')

button3 = tk.Button(root, text="按钮3", command=lambda: print("按钮3被点击"))
button3.grid(row=3, column=0, padx=10, pady=5, sticky='ew')

# 表格（Treeview）
tree = ttk.Treeview(root, columns=("col1", "col2"), show="headings")
tree.heading("col1", text="列1")
tree.heading("col2", text="列2")
tree.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')

# 折线图（使用 Matplotlib 嵌入 Tkinter）
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=2, rowspan=5, padx=10, pady=5, sticky='nsew')

# 配置列宽和权重
root.grid_columnconfigure(0, weight=1)  # 第一列自适应调整
root.grid_columnconfigure(1, weight=3)  # 第二列占更大比例

# 设置列最小宽度
root.columnconfigure(0, minsize=384)  # 第一列最小宽度（约占 30%）
root.columnconfigure(1, minsize=896)  # 第二列最小宽度（约占 70%）

# 添加一些示例数据到表格
for i in range(10):
    tree.insert("", "end", values=(f"数据 {i+1}", random.randint(1, 100)))

# 运行主循环
root.mainloop()

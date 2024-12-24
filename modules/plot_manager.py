# modules/plot_manager.py

import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import


class PlotManager:
    def __init__(self, parent_frame, plot_mode='2D'):
        """
        初始化绘图管理器。

        :param parent_frame: Tkinter父框架
        :param plot_mode: '2D' 或 '3D'
        """
        self.parent_frame = parent_frame
        self.plot_mode = plot_mode
        self.fig = plt.figure(figsize=(10, 6))
        if self.plot_mode == '3D':
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent_frame)
        self.canvas.get_tk_widget().pack(padx=10, pady=10, fill='both', expand=True)
        self.lines = {}
        self.labels = []

    def switch_mode(self, mode):
        """
        切换绘图模式。

        :param mode: '2D' 或 '3D'
        """
        if mode == self.plot_mode:
            return
        self.plot_mode = mode
        self.ax.clear()
        if self.plot_mode == '3D':
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax = self.fig.add_subplot(111)
        self.lines = {}
        self.labels = []
        self.canvas.draw()

    def plot_functions_2d(self, x_vals, y_vals, label, color='blue', linestyle='-'):
        line, = self.ax.plot(x_vals, y_vals, label=label, color=color, linestyle=linestyle)
        self.lines[label] = line
        self.labels.append(label)

    def plot_functions_3d(self, x_vals, y_vals, z_vals, label, color='blue'):
        # plot_surface 不支持 label 和 linestyle，因此需要用其他方式添加图例
        surface = self.ax.plot_surface(x_vals, y_vals, z_vals, color=color, alpha=0.7)
        self.lines[label] = surface
        self.labels.append(label)

    def clear_plot(self):
        self.ax.clear()
        self.lines = {}
        self.labels = []

    def update_plot(self):
        self.ax.grid(True)
        # 手动创建图例
        if self.labels:
            handles = []
            labels = []
            for label in self.labels:
                if self.plot_mode == '2D':
                    handles.append(self.lines[label])
                elif self.plot_mode == '3D':
                    # 为了图例，使用 Proxy Artist
                    from matplotlib.patches import Patch
                    handles.append(Patch(color=self.lines[label].get_facecolor()[0]))
                labels.append(label)
            self.ax.legend(handles, labels)
        self.canvas.draw()

    def save_plot(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"),
                                                                ("PDF files", "*.pdf"),
                                                                ("SVG files", "*.svg"),
                                                                ("All files", "*.*")])
            if file_path:
                self.fig.savefig(file_path)
                messagebox.showinfo("保存成功", f"图像已保存到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存图像时出错。\n错误信息: {e}")

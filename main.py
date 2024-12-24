# main.py

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from modules.function_parser import FunctionParser
from modules.plot_manager import PlotManager
from modules.parameter_controller import ParameterController
import sympy as sp

class FunctionPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("函数图像绘制器")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # 使用ttkbootstrap主题
        self.style = tb.Style("flatly")

        # 初始化
        self.parser = None
        self.plot_manager = None
        self.param_controller = None

        # 当前绘图模式： '2D' 或 '3D'
        self.plot_mode = '2D'

        # 创建UI组件
        self.create_widgets()

    def create_widgets(self):
        # 上部框架：函数输入和绘制按钮
        top_frame = ttk.Frame(self.root)
        top_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(top_frame, text="函数表达式 f(x):", font=("Helvetica", 12)).pack(side='left')
        self.func_entry = ttk.Entry(top_frame, width=50, font=("Helvetica", 12))
        self.func_entry.pack(side='left', padx=5)
        self.func_entry.insert(0, "sin(a * x) + b")

        plot_button = ttk.Button(top_frame, text="绘制", command=self.plot_function, bootstyle="success")
        plot_button.pack(side='left', padx=5)

        # 绘图模式选择
        mode_label = ttk.Label(top_frame, text="绘图模式:", font=("Helvetica", 12))
        mode_label.pack(side='left', padx=10)
        self.mode_var = tk.StringVar(value='2D')
        mode_combo = ttk.Combobox(top_frame, textvariable=self.mode_var, values=['2D', '3D'], state='readonly', width=5)
        mode_combo.pack(side='left', padx=5)
        mode_combo.bind("<<ComboboxSelected>>", lambda event: self.switch_plot_mode())

        # 增加导数和积分绘制选项
        options_frame = ttk.Frame(self.root)
        options_frame.pack(padx=10, pady=5, fill='x')

        self.derivative_var = tk.BooleanVar()
        derivative_check = ttk.Checkbutton(options_frame, text="绘制导数 f'(x)", variable=self.derivative_var,
                                           command=self.plot_function)
        derivative_check.pack(side='left', padx=10)

        self.integral_var = tk.BooleanVar()
        integral_check = ttk.Checkbutton(options_frame, text="绘制积分 ∫f(x)dx", variable=self.integral_var,
                                         command=self.plot_function)
        integral_check.pack(side='left', padx=10)

        # 参数调节区域
        self.params_frame = ttk.LabelFrame(self.root, text="参数调节")
        self.params_frame.pack(padx=10, pady=10, fill='x')

        # Matplotlib图形
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(padx=10, pady=10, fill='both', expand=True)
        self.plot_manager = PlotManager(plot_frame, plot_mode=self.plot_mode)

        # 底部按钮：保存图像
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(padx=10, pady=10, fill='x')

        save_button = ttk.Button(bottom_frame, text="保存图像", command=self.plot_manager.save_plot, bootstyle="info")
        save_button.pack(side='right')

    def switch_plot_mode(self):
        selected_mode = self.mode_var.get()
        if selected_mode != self.plot_mode:
            self.plot_mode = selected_mode
            self.plot_manager.switch_mode(self.plot_mode)
            # 重绘当前函数
            self.plot_function()

    def plot_function(self):
        func_str = self.func_entry.get()
        variables = ['x']
        if self.plot_mode == '3D':
            variables.append('y')  # 假设二维函数用于3D绘图

        self.parser = FunctionParser(func_str, variables=variables)
        success, msg = self.parser.parse_expression()
        if not success:
            messagebox.showerror("错误", f"无法解析函数表达式。\n错误信息: {msg}")
            return

        success, msg = self.parser.generate_functions()
        if not success:
            messagebox.showerror("错误", f"无法生成函数。\n错误信息: {msg}")
            return

        # 创建参数调节控件
        if self.parser.params:
            self.param_controller = ParameterController(self.params_frame, self.parser.params, self.update_plot)
        else:
            # 清除参数调节控件
            for widget in self.params_frame.winfo_children():
                widget.destroy()

        # 生成x（和y）值
        if self.plot_mode == '2D':
            self.x_vals = np.linspace(-10, 10, 400)
        else:
            self.x_vals = np.linspace(-10, 10, 100)
            self.y_vals = np.linspace(-10, 10, 100)
            self.X, self.Y = np.meshgrid(self.x_vals, self.y_vals)

        # 绘制
        self.draw_plot()

    def draw_plot(self):
        try:
            self.plot_manager.clear_plot()

            # 获取参数值
            if self.parser.params:
                param_values = self.param_controller.get_param_values()
                print(f"参数值: {param_values}")  # 调试信息
            else:
                param_values = []

            if self.plot_mode == '2D':
                # 2D绘图
                if self.parser.params:
                    args = [self.x_vals] + param_values
                else:
                    args = [self.x_vals]

                # 绘制原函数
                y_vals = self.parser.lambdified_func(*args)
                self.plot_manager.plot_functions_2d(self.x_vals, y_vals, label=f"f(x) = {sp.pretty(self.parser.expr)}",
                                                     color='blue', linestyle='-')

                # 绘制导数
                if self.derivative_var.get():
                    dy_vals = self.parser.lambdified_derivative(*args)
                    self.plot_manager.plot_functions_2d(self.x_vals, dy_vals, label=f"f'(x) = {sp.pretty(self.parser.derivative_expr)}",
                                                         color='green', linestyle='--')

                # 绘制积分
                if self.integral_var.get():
                    integral_vals = self.parser.lambdified_integral(*args)
                    self.plot_manager.plot_functions_2d(self.x_vals, integral_vals, label=f"∫f(x)dx = {sp.pretty(self.parser.integral_expr)}",
                                                         color='red', linestyle=':')

            else:
                # 3D绘图，假设函数为 f(x, y)
                if self.parser.params:
                    args = [self.X, self.Y] + param_values
                else:
                    args = [self.X, self.Y]

                print(f"3D绘图参数顺序: {args}")  # 调试信息

                # 绘制原函数
                z_vals = self.parser.lambdified_func(*args)
                self.plot_manager.plot_functions_3d(self.X, self.Y, z_vals, label=f"f(x, y) = {sp.pretty(self.parser.expr)}",
                                                     color='blue')

                # 绘制导数（偏导数）
                if self.derivative_var.get():
                    for var in self.parser.derivative_expr:
                        dz_vals = self.parser.lambdified_derivative[var](*args)
                        label = f"∂f/∂{var} = {sp.pretty(self.parser.derivative_expr[var])}"
                        self.plot_manager.plot_functions_3d(self.X, self.Y, dz_vals, label=label,
                                                           color='green')

                # 绘制积分（如果需要）
                if self.integral_var.get():
                    for var in self.parser.integral_expr:
                        integral_vals = self.parser.lambdified_integral[var](*args)
                        label = f"∫f d{var} = {sp.pretty(self.parser.integral_expr[var])}"
                        self.plot_manager.plot_functions_3d(self.X, self.Y, integral_vals, label=label,
                                                           color='red')

            # 设置标签和网格
            self.plot_manager.ax.set_xlabel('x', fontsize=12)
            if self.plot_mode == '3D':
                self.plot_manager.ax.set_ylabel('y', fontsize=12)
                self.plot_manager.ax.set_zlabel('z', fontsize=12)
            else:
                self.plot_manager.ax.set_ylabel('y', fontsize=12)
            self.plot_manager.ax.grid(True)
            self.plot_manager.ax.legend()
            self.plot_manager.update_plot()
        except Exception as e:
            messagebox.showerror("错误", f"无法绘制函数。\n错误信息: {e}")

    def update_plot(self):
        try:
            if not self.parser:
                return

            self.plot_manager.clear_plot()

            # 获取参数值
            if self.parser.params:
                param_values = self.param_controller.get_param_values()
                print(f"更新参数值: {param_values}")  # 调试信息
            else:
                param_values = []

            if self.plot_mode == '2D':
                # 2D绘图
                if self.parser.params:
                    args = [self.x_vals] + param_values
                else:
                    args = [self.x_vals]

                # 绘制原函数
                y_vals = self.parser.lambdified_func(*args)
                self.plot_manager.plot_functions_2d(self.x_vals, y_vals, label=f"f(x) = {sp.pretty(self.parser.expr)}",
                                                     color='blue', linestyle='-')

                # 绘制导数
                if self.derivative_var.get():
                    dy_vals = self.parser.lambdified_derivative(*args)
                    self.plot_manager.plot_functions_2d(self.x_vals, dy_vals, label=f"f'(x) = {sp.pretty(self.parser.derivative_expr)}",
                                                         color='green', linestyle='--')

                # 绘制积分
                if self.integral_var.get():
                    integral_vals = self.parser.lambdified_integral(*args)
                    self.plot_manager.plot_functions_2d(self.x_vals, integral_vals, label=f"∫f(x)dx = {sp.pretty(self.parser.integral_expr)}",
                                                         color='red', linestyle=':')

            else:
                # 3D绘图，假设函数为 f(x, y)
                if self.parser.params:
                    args = [self.X, self.Y] + param_values
                else:
                    args = [self.X, self.Y]

                print(f"3D绘图更新参数顺序: {args}")  # 调试信息

                # 绘制原函数
                z_vals = self.parser.lambdified_func(*args)
                self.plot_manager.plot_functions_3d(self.X, self.Y, z_vals, label=f"f(x, y) = {sp.pretty(self.parser.expr)}",
                                                     color='blue')

                # 绘制导数（偏导数）
                if self.derivative_var.get():
                    for var in self.parser.derivative_expr:
                        dz_vals = self.parser.lambdified_derivative[var](*args)
                        label = f"∂f/∂{var} = {sp.pretty(self.parser.derivative_expr[var])}"
                        self.plot_manager.plot_functions_3d(self.X, self.Y, dz_vals, label=label,
                                                           color='green')

                # 绘制积分（如果需要）
                if self.integral_var.get():
                    for var in self.parser.integral_expr:
                        integral_vals = self.parser.lambdified_integral[var](*args)
                        label = f"∫f d{var} = {sp.pretty(self.parser.integral_expr[var])}"
                        self.plot_manager.plot_functions_3d(self.X, self.Y, integral_vals, label=label,
                                                           color='red')

            # 设置标签和网格
            self.plot_manager.ax.set_xlabel('x', fontsize=12)
            if self.plot_mode == '3D':
                self.plot_manager.ax.set_ylabel('y', fontsize=12)
                self.plot_manager.ax.set_zlabel('z', fontsize=12)
            else:
                self.plot_manager.ax.set_ylabel('y', fontsize=12)
            self.plot_manager.ax.grid(True)
            self.plot_manager.ax.legend()
            self.plot_manager.update_plot()
        except Exception as e:
            messagebox.showerror("错误", f"更新函数时出错。\n错误信息: {e}")

def main():
    root = tb.Window()
    app = FunctionPlotterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

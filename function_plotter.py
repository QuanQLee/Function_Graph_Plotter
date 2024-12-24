import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy as sp


class FunctionPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("函数图像绘制器")
        self.root.geometry("1000x800")
        self.root.resizable(False, False)

        # 初始化变量
        self.params = []
        self.param_values = {}
        self.lambdified_func = None
        self.lambdified_derivative = None
        self.lambdified_integral = None
        self.x_vals = np.linspace(-10, 10, 400)

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

        plot_button = ttk.Button(top_frame, text="绘制", command=self.plot_function)
        plot_button.pack(side='left', padx=5)

        # 导数和积分选项
        options_frame = ttk.Frame(self.root)
        options_frame.pack(padx=10, pady=5, fill='x')

        self.derivative_var = tk.BooleanVar()
        derivative_check = ttk.Checkbutton(options_frame, text="绘制导数 f'(x)", variable=self.derivative_var)
        derivative_check.pack(side='left', padx=10)

        self.integral_var = tk.BooleanVar()
        integral_check = ttk.Checkbutton(options_frame, text="绘制积分 ∫f(x)dx", variable=self.integral_var)
        integral_check.pack(side='left', padx=10)

        # 参数调节区域
        self.params_frame = ttk.LabelFrame(self.root, text="参数调节")
        self.params_frame.pack(padx=10, pady=10, fill='x')

        # Matplotlib图形
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(padx=10, pady=10, fill='both', expand=True)
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # 保存图像按钮
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(padx=10, pady=10, fill='x')

        save_button = ttk.Button(bottom_frame, text="保存图像", command=self.save_plot)
        save_button.pack(side='right')

    def plot_function(self):
        func_str = self.func_entry.get()
        x = sp.symbols('x')
        try:
            expr = sp.sympify(func_str)
            print(f"解析的函数表达式: {expr}")
        except Exception as e:
            messagebox.showerror("错误", f"无法解析函数表达式。\n错误信息: {e}")
            return

        # 提取参数
        symbols = sorted(expr.free_symbols, key=lambda s: s.name)
        self.params = [str(s) for s in symbols if str(s) != 'x']
        self.params.sort()

        # 打印调试信息
        print(f"识别的参数: {self.params}")

        # 清除之前的参数调节控件
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        self.param_values = {}

        # 创建参数调节滑动条和输入框
        for param in self.params:
            frame = ttk.Frame(self.params_frame)
            frame.pack(fill='x', padx=5, pady=2)

            ttk.Label(frame, text=param, font=("Helvetica", 11)).pack(side='left', padx=5)

            slider = ttk.Scale(frame, from_=-10, to=10, orient='horizontal',
                               command=lambda val, p=param: self.update_plot())
            slider.set(1.0)  # 默认值
            slider.pack(side='left', fill='x', expand=True, padx=5)

            entry = ttk.Entry(frame, width=5)
            entry.pack(side='left', padx=5)
            entry.insert(0, "1.0")
            entry.bind("<Return>", lambda event, p=param, e=entry: self.set_param(p, e.get()))

            self.param_values[param] = slider

        # 生成可调用的函数
        try:
            all_symbols = [x] + [sp.symbols(p) for p in self.params]
            self.lambdified_func = sp.lambdify(all_symbols, expr, modules=['numpy'])
            print(f"生成的原函数: {self.lambdified_func}")

            if self.derivative_var.get():
                derivative_expr = sp.diff(expr, x)
                self.lambdified_derivative = sp.lambdify(all_symbols, derivative_expr, modules=['numpy'])
                print(f"生成的导数函数: {self.lambdified_derivative}")
            else:
                self.lambdified_derivative = None

            if self.integral_var.get():
                integral_expr = sp.integrate(expr, x)
                self.lambdified_integral = sp.lambdify(all_symbols, integral_expr, modules=['numpy'])
                print(f"生成的积分函数: {self.lambdified_integral}")
            else:
                self.lambdified_integral = None
        except Exception as e:
            messagebox.showerror("错误", f"无法生成函数。\n错误信息: {e}")
            return

        # 绘制初始图形
        self.draw_plot()

    def set_param(self, param, value):
        try:
            value = float(value)
            self.param_values[param].set(value)
            self.update_plot()
        except ValueError:
            messagebox.showerror("错误", f"参数 {param} 的值必须是数字。")

    def draw_plot(self):
        self.ax.clear()
        try:
            if self.params:
                param_vals = [self.param_values[p].get() for p in self.params]
                args = [self.x_vals] + param_vals
                print(f"绘制 f(x) 时传递的参数: {args}")
            else:
                args = [self.x_vals]
                print(f"绘制 f(x) 时传递的参数: {args}")

            # 绘制原函数
            y = self.lambdified_func(*args)
            self.ax.plot(self.x_vals, y, label="f(x)", color='blue')
            print(f"f(x) 计算结果: {y[:5]}...")  # 只打印前5个值

            # 绘制导数
            if self.lambdified_derivative:
                dy = self.lambdified_derivative(*args)
                self.ax.plot(self.x_vals, dy, label="f'(x)", color='green', linestyle='--')
                print(f"f'(x) 计算结果: {dy[:5]}...")

            # 绘制积分
            if self.lambdified_integral:
                integral = self.lambdified_integral(*args)
                self.ax.plot(self.x_vals, integral, label="∫f(x)dx", color='red', linestyle=':')
                print(f"∫f(x)dx 计算结果: {integral[:5]}...")

            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
            self.ax.grid(True)
            self.ax.legend()
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("错误", f"无法绘制函数。\n错误信息: {e}")

    def update_plot(self):
        self.draw_plot()

    def save_plot(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                self.fig.savefig(file_path)
                messagebox.showinfo("保存成功", f"图像已保存到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存图像时出错。\n错误信息: {e}")


def main():
    root = tk.Tk()
    app = FunctionPlotterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

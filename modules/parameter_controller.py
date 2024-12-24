# modules/parameter_controller.py

import tkinter as tk
from tkinter import ttk


class ParameterController:
    def __init__(self, parent_frame, params, update_callback):
        """
        初始化参数控制器。

        :param parent_frame: Tkinter父框架
        :param params: 参数名称列表
        :param update_callback: 参数变化时的回调函数
        """
        self.parent_frame = parent_frame
        self.params = params
        self.update_callback = update_callback
        self.sliders = {}
        self.entries = {}
        self.create_sliders()

    def create_sliders(self):
        # 清除之前的控件
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        self.sliders = {}
        self.entries = {}

        for param in sorted(self.params):
            frame = ttk.Frame(self.parent_frame)
            frame.pack(fill='x', padx=5, pady=2)

            ttk.Label(frame, text=param, font=("Helvetica", 11)).pack(side='left', padx=5)

            slider = ttk.Scale(frame, from_=-10, to=10, orient='horizontal',
                               command=lambda val, p=param: self.on_slider_change(p, val))
            slider.set(1.0)  # 默认值
            slider.pack(side='left', fill='x', expand=True, padx=5)
            self.sliders[param] = slider

            entry = ttk.Entry(frame, width=5, font=("Helvetica", 11))
            entry.pack(side='left', padx=5)
            entry.insert(0, "1.0")
            entry.bind("<Return>", lambda event, p=param: self.on_entry_change(p, event))
            self.entries[param] = entry

    def on_slider_change(self, param, value):
        # 更新Entry值
        self.entries[param].delete(0, tk.END)
        self.entries[param].insert(0, f"{float(value):.2f}")
        self.update_callback()

    def on_entry_change(self, param, event):
        try:
            value = float(self.entries[param].get())
            if value < -10:
                value = -10
            elif value > 10:
                value = 10
            self.sliders[param].set(value)
            self.update_callback()
        except ValueError:
            # 恢复滑动条到当前值
            current_val = self.sliders[param].get()
            self.entries[param].delete(0, tk.END)
            self.entries[param].insert(0, f"{float(current_val):.2f}")

    def get_param_values(self):
        values = []
        for param in sorted(self.params):
            try:
                value = float(self.entries[param].get())
                values.append(value)
            except ValueError:
                values.append(self.sliders[param].get())
        return values

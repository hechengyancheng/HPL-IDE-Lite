#!/usr/bin/env python3
"""
HPL-IDE-Lite
轻量级 HPL 集成开发环境
"""

import sys
import os

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
import customtkinter as ctk


def main():
    """程序入口"""
    # 设置 CustomTkinter 外观
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # 创建主窗口
    app = MainWindow()
    
    # 启动应用
    app.run()


if __name__ == "__main__":
    main()

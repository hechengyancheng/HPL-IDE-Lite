"""
主窗口实现
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .editor import CodeEditor
from .console import Console
from .file_tree import FileTree
from utils.logger import logger, LogLevel



class MainWindow:
    """HPL IDE 主窗口"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("HPL IDE Lite")
        self.root.geometry("1200x800")
        
        self.current_file = None
        self.current_project_dir = None
        
        self._setup_menu()
        self._setup_layout()
        self._bind_shortcuts()
    
    def _setup_menu(self):
        """设置菜单栏"""
        # 创建菜单栏框架
        menubar = ctk.CTkFrame(self.root, height=30, corner_radius=0)
        menubar.pack(fill="x", side="top")
        menubar.pack_propagate(False)
        
        # 文件菜单
        file_btn = ctk.CTkButton(
            menubar, text="文件", width=60, height=25,
            command=self._show_file_menu
        )
        file_btn.pack(side="left", padx=5, pady=2)
        
        # 编辑菜单
        edit_btn = ctk.CTkButton(
            menubar, text="编辑", width=60, height=25,
            command=self._show_edit_menu
        )
        edit_btn.pack(side="left", padx=5, pady=2)
        
        # 运行菜单
        run_btn = ctk.CTkButton(
            menubar, text="运行", width=60, height=25,
            command=self._show_run_menu
        )
        run_btn.pack(side="left", padx=5, pady=2)
        
        # 帮助菜单
        help_btn = ctk.CTkButton(
            menubar, text="帮助", width=60, height=25,
            command=self._show_help_menu
        )
        help_btn.pack(side="left", padx=5, pady=2)
        
        # 查看菜单（日志）
        view_btn = ctk.CTkButton(
            menubar, text="查看", width=60, height=25,
            command=self._show_view_menu
        )
        view_btn.pack(side="left", padx=5, pady=2)

    
    def _setup_layout(self):
        """设置主布局"""
        # 主分割窗口（水平：左文件树，右编辑区）
        self.main_paned = ctk.CTkFrame(self.root)
        self.main_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 使用 grid 布局
        self.main_paned.grid_columnconfigure(1, weight=1)
        self.main_paned.grid_rowconfigure(0, weight=1)
        
        # 左侧：文件树
        self.file_tree = FileTree(self.main_paned, on_select=self._on_file_select)
        self.file_tree.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # 右侧：编辑器和控制台（垂直分割）
        right_frame = ctk.CTkFrame(self.main_paned)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=3)
        right_frame.grid_rowconfigure(1, weight=1)
        
        # 代码编辑器
        self.editor = CodeEditor(right_frame)
        self.editor.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        
        # 控制台
        self.console = Console(right_frame)
        self.console.grid(row=1, column=0, sticky="nsew")
        
        # 状态栏
        self.statusbar = ctk.CTkFrame(self.root, height=25, corner_radius=0)
        self.statusbar.pack(fill="x", side="bottom")
        self.statusbar.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.statusbar, text="就绪", anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=2)
        
        self.file_info_label = ctk.CTkLabel(
            self.statusbar, text="", anchor="e"
        )
        self.file_info_label.pack(side="right", padx=10, pady=2)
        
        # 设置日志系统
        self._setup_logging()

    def _bind_shortcuts(self):

        """绑定快捷键"""
        self.root.bind("<Control-o>", lambda e: self._open_file())
        self.root.bind("<Control-s>", lambda e: self._save_file())
        self.root.bind("<Control-n>", lambda e: self._new_file())
        self.root.bind("<F5>", lambda e: self._run_code())
        self.root.bind("<F9>", lambda e: self._debug_code())
    
    def _setup_logging(self):
        """设置日志系统"""
        # 设置控制台回调
        logger.set_console_callback(
            lambda msg, level: self.console.log_with_level(msg, level)
        )
        logger.info("IDE 日志系统已启动")

    
    def _show_file_menu(self):
        """显示文件菜单"""
        menu = ctk.CTkToplevel(self.root)
        menu.title("文件")
        menu.geometry("200x250")
        menu.transient(self.root)
        menu.grab_set()
        
        buttons = [
            ("新建文件 (Ctrl+N)", self._new_file),
            ("打开文件 (Ctrl+O)", self._open_file),
            ("保存文件 (Ctrl+S)", self._save_file),
            ("另存为...", self._save_as_file),
            ("打开文件夹...", self._open_folder),
            ("", None),
            ("退出", self.root.quit),
        ]
        
        for text, command in buttons:
            if text:
                btn = ctk.CTkButton(menu, text=text, command=command)
                btn.pack(fill="x", padx=10, pady=2)
            else:
                ctk.CTkFrame(menu, height=2).pack(fill="x", padx=10, pady=5)
    
    def _show_edit_menu(self):
        """显示编辑菜单"""
        menu = ctk.CTkToplevel(self.root)
        menu.title("编辑")
        menu.geometry("200x200")
        menu.transient(self.root)
        menu.grab_set()
        
        buttons = [
            ("撤销 (Ctrl+Z)", self.editor.undo),
            ("重做 (Ctrl+Y)", self.editor.redo),
            ("", None),
            ("剪切 (Ctrl+X)", self.editor.cut),
            ("复制 (Ctrl+C)", self.editor.copy),
            ("粘贴 (Ctrl+V)", self.editor.paste),
            ("", None),
            ("查找 (Ctrl+F)", self.editor.show_find),
        ]
        
        for text, command in buttons:
            if text:
                btn = ctk.CTkButton(menu, text=text, command=command)
                btn.pack(fill="x", padx=10, pady=2)
            else:
                ctk.CTkFrame(menu, height=2).pack(fill="x", padx=10, pady=5)
    
    def _show_run_menu(self):
        """显示运行菜单"""
        menu = ctk.CTkToplevel(self.root)
        menu.title("运行")
        menu.geometry("200x150")
        menu.transient(self.root)
        menu.grab_set()
        
        buttons = [
            ("运行 (F5)", self._run_code),
            ("调试 (F9)", self._debug_code),
            ("", None),
            ("停止", self._stop_code),
        ]
        
        for text, command in buttons:
            if text:
                btn = ctk.CTkButton(menu, text=text, command=command)
                btn.pack(fill="x", padx=10, pady=2)
            else:
                ctk.CTkFrame(menu, height=2).pack(fill="x", padx=10, pady=5)
    
    def _show_help_menu(self):
        """显示帮助菜单"""
        menu = ctk.CTkToplevel(self.root)
        menu.title("帮助")
        menu.geometry("200x150")
        menu.transient(self.root)
        menu.grab_set()
        
        buttons = [
            ("HPL 语法手册", self._show_syntax_help),
            ("快捷键参考", self._show_shortcuts_help),
            ("", None),
            ("关于", self._show_about),
        ]
        
        for text, command in buttons:
            if text:
                btn = ctk.CTkButton(menu, text=text, command=command)
                btn.pack(fill="x", padx=10, pady=2)
            else:
                ctk.CTkFrame(menu, height=2).pack(fill="x", padx=10, pady=5)
    
    def _show_view_menu(self):
        """显示查看菜单（日志相关）"""
        menu = ctk.CTkToplevel(self.root)
        menu.title("查看")
        menu.geometry("250x300")
        menu.transient(self.root)
        menu.grab_set()
        
        buttons = [
            ("显示日志窗口", self._show_log_window),
            ("清除日志", self._clear_logs),
            ("", None),
            ("日志级别: 调试", lambda: self._set_log_level(LogLevel.DEBUG)),
            ("日志级别: 信息", lambda: self._set_log_level(LogLevel.INFO)),
            ("日志级别: 警告", lambda: self._set_log_level(LogLevel.WARNING)),
            ("日志级别: 错误", lambda: self._set_log_level(LogLevel.ERROR)),
            ("", None),
            ("启用文件日志", self._enable_file_logging),
            ("打开日志文件", self._open_log_file),
        ]
        
        for text, command in buttons:
            if text:
                btn = ctk.CTkButton(menu, text=text, command=command)
                btn.pack(fill="x", padx=10, pady=2)
            else:
                ctk.CTkFrame(menu, height=2).pack(fill="x", padx=10, pady=5)
    
    def _show_log_window(self):
        """显示日志窗口"""
        log_window = ctk.CTkToplevel(self.root)
        log_window.title("日志窗口")
        log_window.geometry("600x400")
        log_window.transient(self.root)
        
        # 日志文本区域
        import tkinter as tk
        log_text = tk.Text(
            log_window,
            wrap="word",
            font=("Consolas", 10),
            bg="#2b2b2b",
            fg="#d4d4d4",
            state="disabled"
        )
        log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 配置标签颜色
        log_text.tag_config("debug", foreground="#858585")
        log_text.tag_config("info", foreground="#75beff")
        log_text.tag_config("warning", foreground="#dcdcaa")
        log_text.tag_config("error", foreground="#f48771")
        
        # 加载历史日志
        history = logger.get_log_history(limit=100)
        log_text.configure(state="normal")
        for entry in history:
            level = entry['level'].lower()
            message = entry['message']
            log_text.insert("end", message + "\n", level)
        log_text.see("end")
        log_text.configure(state="disabled")
        
        # 设置日志回调，实时更新
        def log_callback(message, level):
            log_text.configure(state="normal")
            log_text.insert("end", message + "\n", level)
            log_text.see("end")
            log_text.configure(state="disabled")
        
        # 临时设置回调（这里简化处理，实际应该管理回调）
        logger.set_console_callback(lambda msg, lvl: self.console.log_with_level(msg, lvl))
    
    def _clear_logs(self):
        """清除日志"""
        logger.clear_history()
        self.console.log_info("日志已清除")
    
    def _set_log_level(self, level):
        """设置日志级别"""
        logger.set_log_level(level)
        self.console.log_info(f"日志级别已设置为: {level.value}")
    
    def _enable_file_logging(self):
        """启用文件日志"""
        logger.enable_file_logging(True)
        self.console.log_info(f"文件日志已启用: {logger.get_current_log_file()}")
    
    def _open_log_file(self):
        """打开日志文件"""
        logger.open_log_file()

    
    def _new_file(self):
        """新建文件"""
        logger.info("创建新文件")
        self.current_file = None
        self.editor.clear()
        self._update_title()
        self._set_status("新建文件")

    
    def _open_file(self, file_path=None):
        """打开文件"""
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="打开 HPL 文件",
                filetypes=[("HPL 文件", "*.hpl"), ("所有文件", "*.*")]
            )
        
        if file_path:
            try:
                logger.info(f"打开文件: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.set_content(content)
                self.current_file = file_path
                self._update_title()
                self._set_status(f"已打开: {file_path}")
                logger.info(f"文件打开成功: {file_path}")
            except Exception as e:
                logger.error(f"打开文件失败: {file_path}, 错误: {str(e)}")
                messagebox.showerror("错误", f"无法打开文件: {str(e)}")

    
    def _save_file(self):
        """保存文件"""
        if not self.current_file:
            return self._save_as_file()
        
        try:
            logger.info(f"保存文件: {self.current_file}")
            content = self.editor.get_content()
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self._set_status(f"已保存: {self.current_file}")
            logger.info(f"文件保存成功: {self.current_file}")
            return True
        except Exception as e:
            logger.error(f"保存文件失败: {self.current_file}, 错误: {str(e)}")
            messagebox.showerror("错误", f"无法保存文件: {str(e)}")
            return False

    
    def _save_as_file(self):
        """另存为"""
        file_path = filedialog.asksaveasfilename(
            title="保存 HPL 文件",
            defaultextension=".hpl",
            filetypes=[("HPL 文件", "*.hpl"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.current_file = file_path
            return self._save_file()
        return False
    
    def _open_folder(self):
        """打开文件夹"""
        folder = filedialog.askdirectory(title="选择项目文件夹")
        if folder:
            logger.info(f"打开文件夹: {folder}")
            self.current_project_dir = folder
            self.file_tree.load_directory(folder)
            self._set_status(f"已打开文件夹: {folder}")
            logger.info(f"文件夹加载完成: {folder}")

    
    def _on_file_select(self, file_path):
        """文件树选择回调"""
        if file_path.endswith('.hpl'):
            # 先保存当前文件
            if self.current_file:
                self._save_file()
            self._open_file(file_path)
    
    def _run_code(self):
        """运行代码"""
        import time
        start_time = time.time()
        
        if not self.current_file:
            # 先保存为临时文件
            if not self._save_as_file():
                return
        
        # 保存文件
        if not self._save_file():
            return
        
        logger.info(f"开始运行: {self.current_file}")
        self._set_status(f"正在运行: {self.current_file}")
        self.console.clear()
        self.console.log(f"运行: {self.current_file}")
        self.console.log("-" * 50)
        
        # 导入并运行
        from runner.hpl_runner import HPLRunner
        runner = HPLRunner()
        result = runner.run(self.current_file)
        
        elapsed_time = time.time() - start_time
        
        if result['success']:
            logger.info(f"代码执行成功，耗时: {elapsed_time:.2f}秒")
            if result['output']:
                self.console.log(result['output'])
            self.console.log("-" * 50)
            self.console.log(f"执行完成 (耗时: {elapsed_time:.2f}秒)")
            self._set_status(f"执行完成 ({elapsed_time:.2f}秒)")
        else:
            logger.error(f"代码执行失败: {result['error']}, 类型: {result['error_type']}")
            self.console.log("-" * 50)
            self.console.log(f"错误: {result['error']}")
            if result.get('line'):
                self.editor.highlight_error_line(result['line'])
            self._set_status(f"执行失败: {result['error_type']}")

    
    def _debug_code(self):
        """调试代码"""
        import time
        start_time = time.time()
        
        if not self.current_file:
            if not self._save_as_file():
                return
        
        if not self._save_file():
            return
        
        logger.info(f"开始调试: {self.current_file}")
        self._set_status(f"调试模式: {self.current_file}")
        self.console.clear()
        self.console.log(f"调试: {self.current_file}")
        self.console.log("-" * 50)
        
        from runner.hpl_runner import HPLRunner
        runner = HPLRunner()
        result = runner.debug(self.current_file)
        
        elapsed_time = time.time() - start_time
        
        if result['success']:
            logger.info(f"调试完成，耗时: {elapsed_time:.2f}秒")
            self.console.log("调试信息:")
            if result.get('trace'):
                for entry in result['trace']:
                    self.console.log(f"  {entry}")
            if result.get('variables'):
                self.console.log("\n变量状态:")
                for snapshot in result['variables']:
                    self.console.log(f"  行 {snapshot['line']}: {snapshot}")
            self.console.log("-" * 50)
            self.console.log(f"调试完成 (耗时: {elapsed_time:.2f}秒)")
            self._set_status(f"调试完成 ({elapsed_time:.2f}秒)")
        else:
            logger.error(f"调试失败: {result['error']}")
            self.console.log("-" * 50)
            self.console.log(f"调试错误: {result['error']}")
            self._set_status(f"调试失败")

    
    def _stop_code(self):
        """停止运行"""
        self._set_status("已停止")
        self.console.log("执行已停止")
    
    def _show_syntax_help(self):
        """显示语法帮助"""
        help_text = """
HPL 语法要点:
- 基于 YAML 格式
- 使用缩进表示代码块
- 支持类、对象、函数定义
- 控制流: if-else, for-in, while
- 异常处理: try-catch
- 标准库: math, io, json, os, time 等

详见 docs/HPL语法手册.md
        """
        messagebox.showinfo("HPL 语法手册", help_text)
    
    def _show_shortcuts_help(self):
        """显示快捷键帮助"""
        shortcuts = """
快捷键:
Ctrl+N - 新建文件
Ctrl+O - 打开文件
Ctrl+S - 保存文件
F5     - 运行代码
F9     - 调试代码
Ctrl+Z - 撤销
Ctrl+Y - 重做
Ctrl+F - 查找
        """
        messagebox.showinfo("快捷键", shortcuts)
    
    def _show_about(self):
        """显示关于信息"""
        messagebox.showinfo(
            "关于 HPL IDE Lite",
            "HPL IDE Lite v1.0\n\n轻量级 HPL 集成开发环境\n基于 hpl_runtime 模块"
        )
    
    def _update_title(self):
        """更新窗口标题"""
        if self.current_file:
            self.root.title(f"HPL IDE Lite - {os.path.basename(self.current_file)}")
        else:
            self.root.title("HPL IDE Lite - 未命名")
    
    def _set_status(self, message):
        """设置状态栏信息"""
        self.status_label.configure(text=message)
        if self.current_file:
            line, col = self.editor.get_cursor_position()
            self.file_info_label.configure(text=f"行 {line}, 列 {col} | {self.current_file or '未保存'}")
    
    def _cleanup(self):
        """清理资源（应用关闭时调用）"""
        logger.clear_console_callback()
    
    def run(self):
        """启动应用"""
        logger.info("HPL IDE 启动")
        
        # 设置窗口关闭处理
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.root.mainloop()
    
    def _on_close(self):
        """窗口关闭处理"""
        logger.info("HPL IDE 关闭")
        self._cleanup()
        self.root.destroy()

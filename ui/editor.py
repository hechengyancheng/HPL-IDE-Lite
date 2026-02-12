"""
代码编辑器组件
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import font

from .autocomplete import AutocompleteManager
from .syntax_checker import SyntaxChecker


class CodeEditor(ctk.CTkFrame):
    """HPL 代码编辑器"""
    
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self._setup_ui()
        self._setup_syntax_highlighting()
        self._bind_events()
        
        self.error_line = None
        
        # 初始化自动补全和语法检查
        self.autocomplete = AutocompleteManager(self.text_widget)
        self.syntax_checker = SyntaxChecker(self.text_widget, self._on_syntax_errors)
        self.syntax_errors = []
    
    def _setup_ui(self):
        """设置界面"""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 行号显示
        self.line_numbers = tk.Canvas(
            self, width=50, bg="#2b2b2b", highlightthickness=0
        )
        self.line_numbers.grid(row=0, column=0, sticky="nsew")
        
        # 代码编辑区
        self.text_widget = tk.Text(
            self,
            wrap=tk.NONE,
            undo=True,
            font=("Consolas", 12),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#d4d4d4",
            selectbackground="#264f78",
            selectforeground="#d4d4d4",
            highlightthickness=0,
            borderwidth=0,
            padx=5,
            pady=5
        )
        self.text_widget.grid(row=0, column=1, sticky="nsew")
        
        # 滚动条
        self.scrollbar = ctk.CTkScrollbar(self, command=self._on_scroll)
        self.scrollbar.grid(row=0, column=2, sticky="nsew")
        
        self.text_widget.config(yscrollcommand=self._on_textscroll)
        
        # 水平滚动条
        self.h_scrollbar = ctk.CTkScrollbar(
            self, orientation="horizontal", command=self.text_widget.xview
        )
        self.h_scrollbar.grid(row=1, column=1, sticky="ew")
        self.text_widget.config(xscrollcommand=self.h_scrollbar.set)
    
    def _setup_syntax_highlighting(self):
        """设置语法高亮标签"""
        # YAML 键（蓝色）
        self.text_widget.tag_config("keyword", foreground="#569cd6")
        # 字符串（绿色）
        self.text_widget.tag_config("string", foreground="#ce9178")
        # 注释（灰色）
        self.text_widget.tag_config("comment", foreground="#6a9955")
        # 函数（黄色）
        self.text_widget.tag_config("function", foreground="#dcdcaa")
        # 数字（浅绿）
        self.text_widget.tag_config("number", foreground="#b5cea8")
        # 类名（青色）
        self.text_widget.tag_config("class", foreground="#4ec9b0")
        # 错误行（红色背景）
        self.text_widget.tag_config("error", background="#5a1d1d")
        # 当前行高亮
        self.text_widget.tag_config("current_line", background="#2a2d2e")
    
    def _bind_events(self):
        """绑定事件"""
        self.text_widget.bind("<KeyRelease>", self._on_key_release)
        self.text_widget.bind("<ButtonRelease-1>", self._update_line_numbers)
        self.text_widget.bind("<MouseWheel>", self._on_mousewheel)
        self.text_widget.bind("<Configure>", self._update_line_numbers)
        self.text_widget.bind("<FocusIn>", self._on_focus_in)
        self.text_widget.bind("<FocusOut>", self._on_focus_out)
        
        # 缩进支持
        self.text_widget.bind("<Return>", self._on_return)
        self.text_widget.bind("<Tab>", self._on_tab)
        self.text_widget.bind("<BackSpace>", self._on_backspace)
    
    def _on_scroll(self, *args):
        """滚动条回调"""
        self.text_widget.yview(*args)
        self._update_line_numbers()
    
    def _on_textscroll(self, first, last):
        """文本滚动回调"""
        self.scrollbar.set(first, last)
        self._update_line_numbers()
    
    def _on_mousewheel(self, event):
        """鼠标滚轮"""
        self.text_widget.yview_scroll(int(-1*(event.delta/120)), "units")
        self._update_line_numbers()
        return "break"
    
    def _update_line_numbers(self, event=None):
        """更新行号"""
        self.line_numbers.delete("all")
        
        # 获取可见区域
        first, last = self.text_widget.yview()
        first_line = int(float(first) * float(self.text_widget.index("end-1c").split(".")[0]))
        last_line = int(float(last) * float(self.text_widget.index("end-1c").split(".")[0]))
        
        # 绘制行号
        for i in range(first_line, last_line + 1):
            if i > 0:
                y = self.text_widget.dlineinfo(f"{i}.0")
                if y:
                    self.line_numbers.create_text(
                        45, y[1] + y[3]//2,
                        text=str(i),
                        anchor="e",
                        fill="#858585",
                        font=("Consolas", 10)
                    )
        
        # 高亮当前行
        self._highlight_current_line()
    
    def _highlight_current_line(self):
        """高亮当前行"""
        self.text_widget.tag_remove("current_line", "1.0", "end")
        cursor_line = self.text_widget.index("insert").split(".")[0]
        self.text_widget.tag_add("current_line", f"{cursor_line}.0", f"{cursor_line}.end")
    
    def _on_key_release(self, event=None):
        """按键释放时更新"""
        self._update_line_numbers()
        self._apply_syntax_highlighting()
        # 语法检查由 SyntaxChecker 自动处理
    
    def _on_syntax_errors(self, errors):
        """语法错误回调"""
        self.syntax_errors = errors
        
        # 清除之前的错误标记
        self.text_widget.tag_remove("error", "1.0", "end")
        
        # 标记所有错误行
        for error in errors:
            self.text_widget.tag_add("error", f"{error.line}.0", f"{error.line}.end")
        
        # 通知父窗口显示错误
        if hasattr(self.master, 'on_syntax_errors'):
            self.master.on_syntax_errors(errors)
    
    def get_syntax_errors(self):
        """获取当前语法错误"""
        return self.syntax_errors
    
    def check_syntax_now(self):
        """立即执行语法检查"""
        return self.syntax_checker.check_now()
    
    def _apply_syntax_highlighting(self):
        """应用语法高亮"""
        # 清除所有标签
        for tag in ["keyword", "string", "comment", "function", "number", "class"]:
            self.text_widget.tag_remove(tag, "1.0", "end")
        
        content = self.text_widget.get("1.0", "end-1c")
        lines = content.split("\n")
        
        import re
        
        for i, line in enumerate(lines, 1):
            # 注释高亮
            if "#" in line:
                comment_start = line.index("#")
                self.text_widget.tag_add("comment", f"{i}.{comment_start}", f"{i}.end")
                line = line[:comment_start]  # 注释后的内容不再处理
            
            # YAML 键高亮（行首的键名）
            key_match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', line)
            if key_match:
                start = len(key_match.group(1))
                end = start + len(key_match.group(2))
                self.text_widget.tag_add("keyword", f"{i}.{start}", f"{i}.{end}")
            
            # 函数定义高亮
            func_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*=>', line)
            if func_match:
                start = func_match.start(1)
                end = func_match.end(1)
                self.text_widget.tag_add("function", f"{i}.{start}", f"{i}.{end}")
            
            # 字符串高亮
            for match in re.finditer(r'"[^"]*"', line):
                self.text_widget.tag_add("string", f"{i}.{match.start()}", f"{i}.{match.end()}")
            
            # 数字高亮
            for match in re.finditer(r'\b\d+(\.\d+)?\b', line):
                self.text_widget.tag_add("number", f"{i}.{match.start()}", f"{i}.{match.end()}")
            
            # 类名高亮（大写字母开头）
            for match in re.finditer(r'\b[A-Z][a-zA-Z0-9_]*\b', line):
                word = match.group()
                if word not in ["True", "False", "None"]:
                    self.text_widget.tag_add("class", f"{i}.{match.start()}", f"{i}.{match.end()}")
    
    def _on_return(self, event):
        """处理回车键 - 自动缩进"""
        cursor = self.text_widget.index("insert")
        line, col = map(int, cursor.split("."))
        
        # 获取当前行的缩进
        current_line = self.text_widget.get(f"{line}.0", f"{line}.end")
        indent = len(current_line) - len(current_line.lstrip())
        
        # 检查是否需要额外缩进（以 : 或 { 结尾）
        extra_indent = 2 if current_line.rstrip().endswith((":", "{")) else 0
        
        # 插入新行和缩进
        new_indent = " " * (indent + extra_indent)
        self.text_widget.insert("insert", f"\n{new_indent}")
        
        self._update_line_numbers()
        return "break"
    
    def _on_tab(self, event):
        """处理 Tab 键"""
        self.text_widget.insert("insert", "  ")
        return "break"
    
    def _on_backspace(self, event):
        """处理退格键 - 智能删除缩进"""
        cursor = self.text_widget.index("insert")
        line, col = map(int, cursor.split("."))
        
        if col > 0:
            line_content = self.text_widget.get(f"{line}.0", f"{line}.{col}")
            if line_content.endswith("  "):
                # 删除两个空格
                self.text_widget.delete(f"{line}.{col-2}", f"{line}.{col}")
                return "break"
        
        return None  # 使用默认行为
    
    def _on_focus_in(self, event):
        """获得焦点"""
        self._highlight_current_line()
    
    def _on_focus_out(self, event):
        """失去焦点"""
        self.text_widget.tag_remove("current_line", "1.0", "end")
    
    def get_content(self):
        """获取内容"""
        return self.text_widget.get("1.0", "end-1c")
    
    def set_content(self, content):
        """设置内容"""
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", content)
        self._update_line_numbers()
        self._apply_syntax_highlighting()
        self.error_line = None
        # 触发语法检查
        self.syntax_checker.check_now()
    
    def clear(self):
        """清空"""
        self.text_widget.delete("1.0", "end")
        self._update_line_numbers()
        self.error_line = None
    
    def get_cursor_position(self):
        """获取光标位置"""
        cursor = self.text_widget.index("insert")
        line, col = map(int, cursor.split("."))
        return line, col
    
    def highlight_error_line(self, line):
        """高亮错误行"""
        # 清除之前的错误标记
        self.text_widget.tag_remove("error", "1.0", "end")
        
        # 标记错误行
        self.text_widget.tag_add("error", f"{line}.0", f"{line}.end")
        self.error_line = line
        
        # 滚动到错误行
        self.text_widget.see(f"{line}.0")
    
    def clear_error_highlight(self):
        """清除错误高亮"""
        self.text_widget.tag_remove("error", "1.0", "end")
        self.error_line = None
    
    def undo(self):
        """撤销"""
        try:
            self.text_widget.edit_undo()
        except tk.TclError:
            pass
    
    def redo(self):
        """重做"""
        try:
            self.text_widget.edit_redo()
        except tk.TclError:
            pass
    
    def cut(self):
        """剪切"""
        self.text_widget.event_generate("<<Cut>>")
    
    def copy(self):
        """复制"""
        self.text_widget.event_generate("<<Copy>>")
    
    def paste(self):
        """粘贴"""
        self.text_widget.event_generate("<<Paste>>")
        self._update_line_numbers()
        self._apply_syntax_highlighting()
        # 触发语法检查
        self.syntax_checker.check_now()
    
    def show_find(self):
        """显示查找对话框"""
        # 简单实现，可以扩展为完整的查找替换
        dialog = ctk.CTkToplevel(self)
        dialog.title("查找")
        dialog.geometry("300x100")
        dialog.transient(self)
        dialog.grab_set()
        
        entry = ctk.CTkEntry(dialog, placeholder_text="输入查找内容")
        entry.pack(fill="x", padx=10, pady=10)
        entry.focus()
        
        def find_next():
            search_text = entry.get()
            if search_text:
                start = self.text_widget.index("insert")
                pos = self.text_widget.search(search_text, start, stopindex="end")
                if pos:
                    self.text_widget.see(pos)
                    self.text_widget.mark_set("insert", f"{pos}+{len(search_text)}c")
                    self.text_widget.focus()
        
        btn = ctk.CTkButton(dialog, text="查找下一个", command=find_next)
        btn.pack(pady=5)
        
        entry.bind("<Return>", lambda e: find_next())

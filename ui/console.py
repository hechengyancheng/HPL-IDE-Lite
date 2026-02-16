"""
控制台组件
"""

import customtkinter as ctk


class Console(ctk.CTkFrame):
    """输出控制台"""
    
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置界面"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 标题栏
        header = ctk.CTkFrame(self, height=25, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        header.grid_propagate(False)
        
        title = ctk.CTkLabel(header, text="控制台", font=("Arial", 12, "bold"))
        title.pack(side="left", padx=10, pady=2)
        
        # 清除按钮
        clear_btn = ctk.CTkButton(
            header, text="清除", width=60, height=20,
            command=self.clear
        )
        clear_btn.pack(side="right", padx=5, pady=2)
        
        # 输出区域 - 使用 tkinter.Text 直接以支持标签
        import tkinter as tk
        self.output = tk.Text(
            self,
            wrap="word",
            font=("Consolas", 10),
            state="disabled",
            bg="#2b2b2b",
            fg="#d4d4d4",
            highlightthickness=0,
            borderwidth=0
        )
        self.output.grid(row=1, column=0, sticky="nsew")
        
        # 配置标签
        self.output.tag_config("normal", foreground="#d4d4d4")
        self.output.tag_config("error", foreground="#f48771")
        self.output.tag_config("success", foreground="#89d185")
        self.output.tag_config("info", foreground="#75beff")
        self.output.tag_config("debug", foreground="#858585")  # 灰色
        self.output.tag_config("warning", foreground="#dcdcaa")  # 黄色



    
    def log(self, message, tag="normal"):
        """输出日志"""
        self.output.configure(state="normal")
        self.output.insert("end", str(message) + "\n", tag)
        self.output.see("end")
        self.output.configure(state="disabled")
    
    def log_error(self, message):
        """输出错误"""
        self.log(message, "error")
    
    def log_success(self, message):
        """输出成功信息"""
        self.log(message, "success")
    
    def log_info(self, message):
        """输出信息"""
        self.log(message, "info")
    
    def log_debug(self, message):
        """输出调试信息"""
        self.log(message, "debug")
    
    def log_warning(self, message):
        """输出警告信息"""
        self.log(message, "warning")
    
    def log_with_level(self, message, level="info"):
        """
        根据级别输出日志
        
        Args:
            message: 日志消息
            level: 日志级别 (debug, info, warning, error, success)
        """
        level_map = {
            "debug": "debug",
            "info": "info",
            "warning": "warning",
            "error": "error",
            "success": "success",
            "critical": "error"
        }
        tag = level_map.get(level.lower(), "normal")
        self.log(message, tag)

    
    def clear(self):
        """清除控制台"""
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
    
    def get_content(self):
        """获取内容"""
        return self.output.get("1.0", "end-1c")

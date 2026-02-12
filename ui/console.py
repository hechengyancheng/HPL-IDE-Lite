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
        
        # 输出区域
        self.output = ctk.CTkTextbox(
            self,
            wrap="word",
            font=("Consolas", 10),
            state="disabled"
        )
        self.output.grid(row=1, column=0, sticky="nsew")
        
        # 配置标签
        self.output.tag_config("normal", text_color="#d4d4d4")
        self.output.tag_config("error", text_color="#f48771")
        self.output.tag_config("success", text_color="#89d185")
        self.output.tag_config("info", text_color="#75beff")
    
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
    
    def clear(self):
        """清除控制台"""
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
    
    def get_content(self):
        """获取内容"""
        return self.output.get("1.0", "end-1c")

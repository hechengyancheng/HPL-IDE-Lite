"""
文件树组件
"""

import customtkinter as ctk
from tkinter import ttk
import os


class FileTree(ctk.CTkFrame):
    """文件树浏览器"""
    
    def __init__(self, master=None, on_select=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_select = on_select
        self.current_path = None
        self.expanded_dirs = set()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置界面"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 标题栏
        header = ctk.CTkFrame(self, height=25, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        header.grid_propagate(False)
        
        title = ctk.CTkLabel(header, text="项目", font=("Arial", 12, "bold"))
        title.pack(side="left", padx=10, pady=2)
        
        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            header, text="↻", width=30, height=20,
            command=self._refresh
        )
        refresh_btn.pack(side="right", padx=5, pady=2)
        
        # 文件树
        self.tree = ttk.Treeview(self, selectmode="browse")
        self.tree.grid(row=1, column=0, sticky="nsew")
        
        # 滚动条
        scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 配置样式
        style = ttk.Style()
        style.configure("Treeview", 
            background="#2b2b2b",
            foreground="#d4d4d4",
            fieldbackground="#2b2b2b",
            font=("Arial", 10)
        )
        style.configure("Treeview.Heading",
            background="#3c3c3c",
            foreground="#d4d4d4",
            font=("Arial", 10, "bold")
        )
        
        # 隐藏表头
        self.tree["show"] = "tree"
        
        # 绑定事件
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)
    
    def load_directory(self, path):
        """加载目录"""
        self.current_path = path
        self._refresh()
    
    def _refresh(self):
        """刷新文件树"""
        # 清除现有内容
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.current_path or not os.path.exists(self.current_path):
            return
        
        # 添加根节点
        root_name = os.path.basename(self.current_path) or self.current_path
        root_node = self.tree.insert("", "end", text=root_name, open=True)
        self.tree.item(root_node, values=(self.current_path,))
        
        # 递归添加子项
        self._add_directory_contents(root_node, self.current_path)
    
    def _add_directory_contents(self, parent_node, path):
        """添加目录内容"""
        try:
            items = os.listdir(path)
        except PermissionError:
            return
        
        # 分离文件夹和文件
        dirs = []
        files = []
        
        for item in sorted(items):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                dirs.append((item, item_path))
            elif item.endswith('.hpl'):
                files.append((item, item_path))
        
        # 先添加文件夹
        for name, item_path in dirs:
            node = self.tree.insert(parent_node, "end", text=name, open=False)
            self.tree.item(node, values=(item_path,))
            
            # 递归添加子目录内容
            if item_path in self.expanded_dirs:
                self.tree.item(node, open=True)
                self._add_directory_contents(node, item_path)
        
        # 再添加 HPL 文件
        for name, item_path in files:
            node = self.tree.insert(parent_node, "end", text=name)
            self.tree.item(node, values=(item_path,))
    
    def _on_select(self, event):
        """选择事件"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        item_path = self.tree.item(item, "values")[0] if self.tree.item(item, "values") else None
        
        if item_path and os.path.isfile(item_path):
            if self.on_select:
                self.on_select(item_path)
    
    def _on_double_click(self, event):
        """双击事件 - 展开/折叠目录"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        item_path = self.tree.item(item, "values")[0] if self.tree.item(item, "values") else None
        if not item_path or not os.path.isdir(item_path):
            return
        
        # 切换展开状态
        is_open = self.tree.item(item, "open")
        if is_open:
            self.tree.item(item, open=False)
            self.expanded_dirs.discard(item_path)
        else:
            self.tree.item(item, open=True)
            self.expanded_dirs.add(item_path)
            # 刷新子项
            for child in self.tree.get_children(item):
                self.tree.delete(child)
            self._add_directory_contents(item, item_path)
    
    def get_selected_path(self):
        """获取选中项的路径"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        values = self.tree.item(item, "values")
        return values[0] if values else None
    
    def select_file(self, file_path):
        """选中指定文件"""
        def find_and_select(parent, target):
            for child in self.tree.get_children(parent):
                child_path = self.tree.item(child, "values")[0] if self.tree.item(child, "values") else None
                if child_path == target:
                    self.tree.selection_set(child)
                    self.tree.see(child)
                    return True
                
                # 递归搜索
                if self.tree.get_children(child):
                    if find_and_select(child, target):
                        return True
            
            return False
        
        find_and_select("", file_path)

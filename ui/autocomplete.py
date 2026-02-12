"""
代码自动补全组件
"""

import tkinter as tk


class AutocompleteManager:
    """HPL 代码自动补全管理器"""
    
    # HPL 关键字
    HPL_KEYWORDS = [
        'includes', 'imports', 'classes', 'objects', 'main', 'call',
        'if', 'else', 'for', 'while', 'in', 'range', 'try', 'catch', 'throw',
        'break', 'continue', 'return', 'true', 'false', 'null', 'this', 'parent',
        'init', '__init__'
    ]
    
    # 内置函数
    BUILTIN_FUNCTIONS = [
        'echo', 'len', 'int', 'str', 'type', 'abs', 'max', 'min', 'input'
    ]
    
    # 标准库模块
    STDLIB_MODULES = [
        'math', 'io', 'json', 'os', 'time', 'crypto', 'random', 'string', 're', 'net'
    ]
    
    # math 模块函数和常量
    MATH_ITEMS = [
        'PI', 'E', 'TAU', 'INF', 'NAN',
        'sqrt', 'pow', 'abs', 'max', 'min',
        'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
        'log', 'log10', 'exp',
        'floor', 'ceil', 'round', 'trunc', 'factorial', 'gcd',
        'degrees', 'radians',
        'is_nan', 'is_inf'
    ]
    
    # io 模块函数
    IO_ITEMS = [
        'read_file', 'write_file', 'append_file',
        'file_exists', 'get_file_size', 'is_file', 'is_dir',
        'delete_file', 'create_dir', 'list_dir'
    ]
    
    # json 模块函数
    JSON_ITEMS = [
        'parse', 'stringify', 'read', 'write', 'is_valid'
    ]
    
    # os 模块函数
    OS_ITEMS = [
        'get_env', 'set_env', 'get_cwd', 'change_dir',
        'get_platform', 'get_python_version', 'get_hpl_version', 'cpu_count',
        'get_path_sep', 'get_line_sep', 'path_join', 'path_abs',
        'path_dir', 'path_base', 'path_ext', 'path_norm',
        'execute', 'get_args', 'exit'
    ]
    
    # time 模块函数
    TIME_ITEMS = [
        'now', 'now_ms', 'utc_now', 'sleep', 'sleep_ms',
        'format', 'parse', 'get_year', 'get_month', 'get_day',
        'get_hour', 'get_minute', 'get_second', 'get_weekday',
        'get_iso_date', 'get_iso_time', 'add_days', 'diff_days', 'local_timezone'
    ]
    
    # crypto 模块函数
    CRYPTO_ITEMS = [
        'md5', 'sha1', 'sha256', 'sha512', 'sha3_256', 'sha3_512',
        'blake2b', 'blake2s', 'hash', 'hmac',
        'base64_encode', 'base64_decode', 'base64_urlsafe_encode', 'base64_urlsafe_decode',
        'url_encode', 'url_decode', 'url_encode_plus', 'url_decode_plus',
        'secure_random_bytes', 'secure_random_hex', 'secure_random_urlsafe',
        'secure_choice', 'compare_digest',
        'pbkdf2_hmac', 'scrypt'
    ]
    
    # random 模块函数
    RANDOM_ITEMS = [
        'random', 'random_int', 'random_float', 'choice', 'shuffle', 'sample', 'seed', 'random_bool',
        'uuid', 'uuid1', 'uuid3', 'uuid5',
        'random_bytes', 'random_hex',
        'gauss', 'triangular', 'expovariate', 'betavariate', 'gammavariate',
        'lognormvariate', 'vonmisesvariate', 'paretovariate', 'weibullvariate',
        'getstate', 'setstate'
    ]
    
    # string 模块函数
    STRING_ITEMS = [
        'length', 'split', 'join', 'replace', 'substring',
        'trim', 'trim_start', 'trim_end', 'is_empty', 'is_blank',
        'to_upper', 'to_lower', 'capitalize', 'title_case', 'swap_case',
        'index_of', 'last_index_of', 'starts_with', 'ends_with', 'contains', 'count',
        'reverse', 'repeat', 'pad_start', 'pad_end'
    ]
    
    # re 模块函数
    RE_ITEMS = [
        'match', 'search', 'test', 'find_all', 'find_iter',
        'replace', 'split', 'escape', 'compile', 'validate',
        'PATTERN_EMAIL', 'PATTERN_URL', 'PATTERN_IP', 'PATTERN_PHONE', 'PATTERN_ID_CARD',
        'PATTERN_CHINESE', 'PATTERN_ENGLISH', 'PATTERN_NUMBER', 'PATTERN_WHITESPACE', 'PATTERN_WORD'
    ]
    
    # net 模块函数
    NET_ITEMS = [
        'get', 'post', 'put', 'delete', 'head', 'request',
        'encode_url', 'decode_url', 'parse_url', 'build_url',
        'is_success', 'is_redirect', 'is_client_error', 'is_server_error',
        'STATUS_OK', 'STATUS_CREATED', 'STATUS_ACCEPTED', 'STATUS_NO_CONTENT',
        'STATUS_MOVED_PERMANENTLY', 'STATUS_FOUND', 'STATUS_NOT_MODIFIED',
        'STATUS_BAD_REQUEST', 'STATUS_UNAUTHORIZED', 'STATUS_FORBIDDEN', 'STATUS_NOT_FOUND',
        'STATUS_METHOD_NOT_ALLOWED', 'STATUS_INTERNAL_ERROR', 'STATUS_NOT_IMPLEMENTED',
        'STATUS_BAD_GATEWAY', 'STATUS_SERVICE_UNAVAILABLE'
    ]
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.popup = None
        self.suggestions = []
        self.current_index = 0
        self.user_defined = {
            'classes': set(),
            'methods': {},  # class_name -> set of methods
            'objects': set(),
            'functions': set()
        }
        
        self._setup_bindings()
    
    def _setup_bindings(self):
        """设置键盘绑定"""
        self.text_widget.bind('<Control-space>', self.show_completions)
        self.text_widget.bind('<KeyRelease>', self._on_key_release)
    
    def _on_key_release(self, event):
        """按键释放时检查是否触发自动补全"""
        # 忽略控制键
        if event.keysym in ('Control_L', 'Control_R', 'Shift_L', 'Shift_R', 
                           'Alt_L', 'Alt_R', 'Up', 'Down', 'Left', 'Right',
                           'Return', 'Escape', 'Tab'):
            return
        
        # 检查是否输入了触发字符（如点号或字母）
        char = event.char
        if char and (char.isalnum() or char in '._'):
            # 延迟一点执行，让字符先输入到文本框
            self.text_widget.after(100, self._check_auto_trigger)
    
    def _check_auto_trigger(self):
        """检查是否自动触发补全"""
        # 获取当前光标位置
        cursor = self.text_widget.index('insert')
        line, col = map(int, cursor.split('.'))
        
        # 获取当前行内容
        line_content = self.text_widget.get(f'{line}.0', f'{line}.end')
        
        # 检查是否在输入模块名后输入了点号
        if col > 0 and line_content[col-1] == '.':
            # 检查点号前是否是模块名
            prefix = line_content[:col-1].strip()
            # 获取最后一个词
            words = prefix.replace('(', ' ').replace(')', ' ').split()
            if words:
                last_word = words[-1]
                if last_word in self.STDLIB_MODULES:
                    self._show_module_completions(last_word)
                    return
        
        # 检查是否输入了至少2个字符
        word = self._get_current_word()
        if len(word) >= 2:
            self._show_word_completions(word)
    
    def _get_current_word(self):
        """获取光标前的当前单词"""
        cursor = self.text_widget.index('insert')
        line, col = map(int, cursor.split('.'))
        line_content = self.text_widget.get(f'{line}.0', f'{line}.end')
        
        # 从光标位置向前查找单词
        start = col
        while start > 0 and (line_content[start-1].isalnum() or line_content[start-1] == '_'):
            start -= 1
        
        return line_content[start:col]
    
    def _get_module_items(self, module_name):
        """获取模块的补全项"""
        module_map = {
            'math': self.MATH_ITEMS,
            'io': self.IO_ITEMS,
            'json': self.JSON_ITEMS,
            'os': self.OS_ITEMS,
            'time': self.TIME_ITEMS,
            'crypto': self.CRYPTO_ITEMS,
            'random': self.RANDOM_ITEMS,
            'string': self.STRING_ITEMS,
            're': self.RE_ITEMS,
            'net': self.NET_ITEMS
        }
        return module_map.get(module_name, [])
    
    def _show_module_completions(self, module_name):
        """显示模块的补全列表"""
        items = self._get_module_items(module_name)
        if items:
            self.suggestions = items
            self._show_popup(items)
    
    def _show_word_completions(self, word):
        """显示基于当前单词的补全列表"""
        suggestions = []
        word_lower = word.lower()
        
        # 添加关键字
        for kw in self.HPL_KEYWORDS:
            if kw.lower().startswith(word_lower) and kw not in suggestions:
                suggestions.append(kw)
        
        # 添加内置函数
        for func in self.BUILTIN_FUNCTIONS:
            if func.lower().startswith(word_lower) and func not in suggestions:
                suggestions.append(func)
        
        # 添加模块名
        for mod in self.STDLIB_MODULES:
            if mod.lower().startswith(word_lower) and mod not in suggestions:
                suggestions.append(mod)
        
        # 添加用户定义的类
        for cls in self.user_defined['classes']:
            if cls.lower().startswith(word_lower) and cls not in suggestions:
                suggestions.append(cls)
        
        # 添加用户定义的函数
        for func in self.user_defined['functions']:
            if func.lower().startswith(word_lower) and func not in suggestions:
                suggestions.append(func)
        
        # 添加用户定义的对象
        for obj in self.user_defined['objects']:
            if obj.lower().startswith(word_lower) and obj not in suggestions:
                suggestions.append(obj)
        
        if suggestions:
            self.suggestions = suggestions
            self._show_popup(suggestions)
        else:
            self.hide_popup()
    
    def show_completions(self, event=None):
        """显示补全列表（Ctrl+Space触发）"""
        # 解析当前文件，更新用户定义
        self._parse_user_definitions()
        
        # 检查是否在点号后
        cursor = self.text_widget.index('insert')
        line, col = map(int, cursor.split('.'))
        line_content = self.text_widget.get(f'{line}.0', f'{line}.end')
        
        if col > 0 and line_content[col-1] == '.':
            # 获取点号前的单词
            prefix = line_content[:col-1].strip()
            words = prefix.replace('(', ' ').replace(')', ' ').split()
            if words:
                last_word = words[-1]
                if last_word in self.STDLIB_MODULES:
                    self._show_module_completions(last_word)
                    return
                elif last_word in self.user_defined['objects']:
                    # 获取对象的类
                    obj_class = self._get_object_class(last_word)
                    if obj_class and obj_class in self.user_defined['methods']:
                        methods = self.user_defined['methods'][obj_class]
                        self.suggestions = list(methods)
                        self._show_popup(self.suggestions)
                        return
        
        # 显示所有可能的补全
        all_suggestions = (
            self.HPL_KEYWORDS + 
            self.BUILTIN_FUNCTIONS + 
            self.STDLIB_MODULES +
            list(self.user_defined['classes']) +
            list(self.user_defined['functions']) +
            list(self.user_defined['objects'])
        )
        
        # 去重并保持顺序
        seen = set()
        unique_suggestions = []
        for s in all_suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)
        
        if unique_suggestions:
            self.suggestions = unique_suggestions
            self._show_popup(unique_suggestions)
        
        return 'break'
    
    def _parse_user_definitions(self):
        """解析用户定义的类、方法和对象"""
        content = self.text_widget.get('1.0', 'end-1c')
        lines = content.split('\n')
        
        current_class = None
        in_classes = False
        in_objects = False
        
        for line in lines:
            stripped = line.strip()
            
            # 检测 sections
            if stripped == 'classes:':
                in_classes = True
                in_objects = False
                continue
            elif stripped == 'objects:':
                in_classes = False
                in_objects = True
                continue
            elif stripped in ['includes:', 'imports:', 'main:', 'call:']:
                in_classes = False
                in_objects = False
                continue
            
            # 解析类定义
            if in_classes and stripped:
                # 检查是否是类定义（缩进后跟着冒号）
                if line.startswith('  ') and ':' in stripped:
                    # 可能是类名或方法名
                    key = stripped.split(':')[0].strip()
                    if not key.startswith('-') and not key.startswith('#'):
                        # 检查缩进级别
                        indent = len(line) - len(line.lstrip())
                        if indent == 2:
                            # 类名
                            current_class = key
                            self.user_defined['classes'].add(key)
                            if key not in self.user_defined['methods']:
                                self.user_defined['methods'][key] = set()
                        elif indent == 4 and current_class:
                            # 方法名
                            self.user_defined['methods'][current_class].add(key)
            
            # 解析对象定义
            if in_objects and stripped:
                if ':' in stripped and not stripped.startswith('#'):
                    key = stripped.split(':')[0].strip()
                    if key and not key.startswith('-'):
                        self.user_defined['objects'].add(key)
            
            # 解析顶层函数（在 main 之前定义的函数）
            if not in_classes and not in_objects and stripped:
                if '=>' in stripped and not stripped.startswith('#'):
                    # 可能是函数定义
                    func_match = stripped.split('=>')[0].strip()
                    if ':' in func_match:
                        func_name = func_match.split(':')[0].strip()
                        if func_name and func_name not in ['main', 'call']:
                            self.user_defined['functions'].add(func_name)
    
    def _get_object_class(self, obj_name):
        """获取对象的类名"""
        content = self.text_widget.get('1.0', 'end-1c')
        lines = content.split('\n')
        in_objects = False
        
        for line in lines:
            stripped = line.strip()
            if stripped == 'objects:':
                in_objects = True
                continue
            elif stripped in ['classes:', 'includes:', 'imports:', 'main:', 'call:']:
                in_objects = False
                continue
            
            if in_objects and stripped.startswith(obj_name + ':'):
                # 提取类名
                value = stripped.split(':', 1)[1].strip()
                # 移除括号及其内容
                class_name = value.split('(')[0].strip()
                return class_name
        
        return None
    
    def _show_popup(self, suggestions):
        """显示补全弹出窗口"""
        self.hide_popup()
        
        if not suggestions:
            return
        
        self.suggestions = suggestions
        self.current_index = 0
        
        # 创建弹出窗口
        self.popup = tk.Toplevel(self.text_widget)
        self.popup.wm_overrideredirect(True)
        self.popup.wm_attributes('-topmost', True)
        
        # 创建列表框
        self.listbox = tk.Listbox(
            self.popup,
            bg='#2b2b2b',
            fg='#d4d4d4',
            selectbackground='#264f78',
            selectforeground='#d4d4d4',
            font=('Consolas', 11),
            width=30,
            height=min(10, len(suggestions)),
            borderwidth=1,
            highlightthickness=0
        )
        self.listbox.pack(fill='both', expand=True)
        
        # 添加建议项
        for suggestion in suggestions:
            self.listbox.insert('end', suggestion)
        
        # 选中第一项
        if suggestions:
            self.listbox.selection_set(0)
        
        # 绑定事件
        self.listbox.bind('<Button-1>', self._on_listbox_click)
        self.listbox.bind('<Double-Button-1>', self._on_listbox_double_click)
        
        # 绑定键盘事件到文本框
        self.text_widget.bind('<Up>', self._on_up)
        self.text_widget.bind('<Down>', self._on_down)
        self.text_widget.bind('<Return>', self._on_return)
        self.text_widget.bind('<Escape>', self._on_escape)
        self.text_widget.bind('<Tab>', self._on_tab)
        
        # 定位弹出窗口
        self._position_popup()
    
    def _position_popup(self):
        """定位弹出窗口到光标位置"""
        # 获取光标位置（像素坐标）
        cursor = self.text_widget.index('insert')
        bbox = self.text_widget.bbox(cursor)
        
        if bbox:
            x, y, width, height = bbox
            # 转换为屏幕坐标
            root_x = self.text_widget.winfo_rootx() + x
            root_y = self.text_widget.winfo_rooty() + y + height
            
            self.popup.geometry(f'+{root_x}+{root_y}')
    
    def hide_popup(self):
        """隐藏补全弹出窗口"""
        if self.popup:
            self.popup.destroy()
            self.popup = None
        
        # 解绑键盘事件
        self.text_widget.unbind('<Up>')
        self.text_widget.unbind('<Down>')
        self.text_widget.unbind('<Return>')
        self.text_widget.unbind('<Escape>')
        self.text_widget.unbind('<Tab>')
    
    def _on_up(self, event):
        """向上选择"""
        if self.popup and self.suggestions:
            self.current_index = (self.current_index - 1) % len(self.suggestions)
            self.listbox.selection_clear(0, 'end')
            self.listbox.selection_set(self.current_index)
            self.listbox.see(self.current_index)
            return 'break'
    
    def _on_down(self, event):
        """向下选择"""
        if self.popup and self.suggestions:
            self.current_index = (self.current_index + 1) % len(self.suggestions)
            self.listbox.selection_clear(0, 'end')
            self.listbox.selection_set(self.current_index)
            self.listbox.see(self.current_index)
            return 'break'
    
    def _on_return(self, event):
        """确认选择"""
        if self.popup and self.suggestions:
            self._insert_completion(self.suggestions[self.current_index])
            return 'break'
    
    def _on_escape(self, event):
        """取消补全"""
        self.hide_popup()
        return 'break'
    
    def _on_tab(self, event):
        """Tab键选择"""
        if self.popup and self.suggestions:
            self._insert_completion(self.suggestions[self.current_index])
            return 'break'
    
    def _on_listbox_click(self, event):
        """鼠标点击列表项"""
        if self.popup:
            index = self.listbox.nearest(event.y)
            self.current_index = index
            self.listbox.selection_clear(0, 'end')
            self.listbox.selection_set(index)
    
    def _on_listbox_double_click(self, event):
        """鼠标双击列表项"""
        if self.popup:
            index = self.listbox.nearest(event.y)
            if index < len(self.suggestions):
                self._insert_completion(self.suggestions[index])
    
    def _insert_completion(self, completion):
        """插入选中的补全内容"""
        # 获取当前单词
        word = self._get_current_word()
        
        # 删除当前单词
        if word:
            cursor = self.text_widget.index('insert')
            line, col = map(int, cursor.split('.'))
            start_pos = f'{line}.{col - len(word)}'
            self.text_widget.delete(start_pos, 'insert')
        
        # 插入补全内容
        self.text_widget.insert('insert', completion)
        
        # 隐藏弹出窗口
        self.hide_popup()

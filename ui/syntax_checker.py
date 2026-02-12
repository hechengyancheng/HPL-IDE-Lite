"""
实时语法检查组件
"""

import re
import threading
import yaml


class SyntaxError:
    """语法错误信息"""
    
    def __init__(self, line, message, error_type='Syntax'):
        self.line = line
        self.message = message
        self.error_type = error_type
    
    def __str__(self):
        return f"Line {self.line}: [{self.error_type}] {self.message}"


class SyntaxChecker:
    """HPL 实时语法检查器"""
    
    def __init__(self, text_widget, error_callback=None):
        self.text_widget = text_widget
        self.error_callback = error_callback
        self.check_timer = None
        self.check_delay = 500  # 延迟500ms后检查
        self.last_errors = []
        
        self._setup_bindings()
    
    def _setup_bindings(self):
        """设置事件绑定"""
        self.text_widget.bind('<KeyRelease>', self._on_key_release)
    
    def _on_key_release(self, event):
        """按键释放时触发检查"""
        # 忽略导航键
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return', 
                           'Escape', 'Tab', 'Control_L', 'Control_R'):
            return
        
        # 取消之前的定时器
        if self.check_timer:
            self.text_widget.after_cancel(self.check_timer)
        
        # 设置新的定时器
        self.check_timer = self.text_widget.after(
            self.check_delay, 
            self._perform_check
        )
    
    def _perform_check(self):
        """执行语法检查"""
        content = self.text_widget.get('1.0', 'end-1c')
        errors = []
        
        # 执行各种检查
        errors.extend(self._check_yaml_structure(content))
        errors.extend(self._check_indentation(content))
        errors.extend(self._check_braces_and_parens(content))
        errors.extend(self._check_control_flow_syntax(content))
        errors.extend(self._check_class_syntax(content))
        errors.extend(self._check_function_syntax(content))
        
        # 更新错误列表
        self.last_errors = errors
        
        # 调用回调函数
        if self.error_callback:
            self.error_callback(errors)
        
        return errors
    
    def _check_yaml_structure(self, content):
        """检查 YAML 结构"""
        errors = []
        lines = content.split('\n')
        
        # 检查顶级键
        valid_top_keys = ['includes', 'imports', 'classes', 'objects', 'main', 'call']
        found_top_keys = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # 检查是否是顶级键
            if not line.startswith(' ') and ':' in stripped:
                key = stripped.split(':')[0].strip()
                if key and key not in valid_top_keys:
                    # 可能是函数定义，检查是否是函数
                    if '=>' not in stripped:
                        errors.append(SyntaxError(
                            i, 
                            f"Unknown top-level key '{key}'. Valid keys: {', '.join(valid_top_keys)}",
                            'Structure'
                        ))
                elif key:
                    found_top_keys.append(key)
        
        # 检查 call 是否存在（可选，但推荐）
        if 'main' in found_top_keys and 'call' not in found_top_keys:
            # 这只是警告，不是错误
            pass
        
        # 检查 YAML 基本语法
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            # 解析 YAML 错误位置
            error_str = str(e)
            if 'line' in error_str.lower():
                # 尝试提取行号
                match = re.search(r'line\s+(\d+)', error_str, re.IGNORECASE)
                if match:
                    line_num = int(match.group(1))
                    errors.append(SyntaxError(
                        line_num,
                        f"YAML syntax error: {error_str}",
                        'YAML'
                    ))
        
        return errors
    
    def _check_indentation(self, content):
        """检查缩进"""
        errors = []
        lines = content.split('\n')
        
        expected_indent = 0
        in_code_block = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            actual_indent = len(line) - len(line.lstrip())
            
            # 检查顶级键
            if not line.startswith(' ') and ':' in stripped:
                expected_indent = 0
                in_code_block = False
                
                # 检查是否在代码块中
                if '=>' in stripped or stripped.endswith(':'):
                    in_code_block = True
                    expected_indent = 2
            
            # 检查缩进级别
            elif in_code_block:
                if actual_indent % 2 != 0:
                    errors.append(SyntaxError(
                        i,
                        f"Invalid indentation: {actual_indent} spaces. Use 2-space indentation.",
                        'Indentation'
                    ))
                
                # 检查是否退出代码块
                if actual_indent < expected_indent and stripped:
                    in_code_block = False
                    expected_indent = 0
            
            # 检查混合使用制表符和空格
            if '\t' in line:
                errors.append(SyntaxError(
                    i,
                    "Use spaces instead of tabs for indentation",
                    'Indentation'
                ))
        
        return errors
    
    def _check_braces_and_parens(self, content):
        """检查大括号和括号匹配"""
        errors = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # 检查大括号
            open_braces = stripped.count('{')
            close_braces = stripped.count('}')
            
            # 检查括号
            open_parens = stripped.count('(')
            close_parens = stripped.count(')')
            
            # 检查方括号
            open_brackets = stripped.count('[')
            close_brackets = stripped.count(']')
            
            # 检查字符串中的括号（简单处理）
            in_string = False
            string_char = None
            cleaned = ''
            for char in stripped:
                if char in '"\'':
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                elif not in_string:
                    cleaned += char
            
            # 重新计算（排除字符串内）
            open_braces = cleaned.count('{')
            close_braces = cleaned.count('}')
            open_parens = cleaned.count('(')
            close_parens = cleaned.count(')')
            open_brackets = cleaned.count('[')
            close_brackets = cleaned.count(']')
            
            # 检查箭头函数语法
            if '=>' in stripped:
                # 检查是否有匹配的括号
                if open_parens != close_parens:
                    errors.append(SyntaxError(
                        i,
                        f"Mismatched parentheses in function definition: {open_parens} opening, {close_parens} closing",
                        'Syntax'
                    ))
                
                # 检查箭头函数的大括号
                if open_braces != close_braces:
                    errors.append(SyntaxError(
                        i,
                        f"Mismatched braces in function definition: {open_braces} opening, {close_braces} closing",
                        'Syntax'
                    ))
            
            # 检查数组和字典
            if open_brackets != close_brackets:
                errors.append(SyntaxError(
                    i,
                    f"Mismatched brackets: {open_brackets} opening, {close_brackets} closing",
                    'Syntax'
                ))
        
        return errors
    
    def _check_control_flow_syntax(self, content):
        """检查控制流语法"""
        errors = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # 检查 if 语句
            if stripped.startswith('if '):
                if not stripped.endswith(':'):
                    errors.append(SyntaxError(
                        i,
                        "If statement must end with ':'",
                        'ControlFlow'
                    ))
                if '(' not in stripped or ')' not in stripped:
                    errors.append(SyntaxError(
                        i,
                        "If condition must be enclosed in parentheses",
                        'ControlFlow'
                    ))
            
            # 检查 else 语句
            elif stripped == 'else':
                errors.append(SyntaxError(
                    i,
                    "Else must be followed by ':'",
                    'ControlFlow'
                ))
            
            # 检查 for 语句
            elif stripped.startswith('for '):
                if not stripped.endswith(':'):
                    errors.append(SyntaxError(
                        i,
                        "For statement must end with ':'",
                        'ControlFlow'
                    ))
                if ' in ' not in stripped:
                    errors.append(SyntaxError(
                        i,
                        "For statement must use 'in' keyword (e.g., for (i in range(5)) :)",
                        'ControlFlow'
                    ))
                if '(' not in stripped or ')' not in stripped:
                    errors.append(SyntaxError(
                        i,
                        "For loop must be enclosed in parentheses",
                        'ControlFlow'
                    ))
            
            # 检查 while 语句
            elif stripped.startswith('while '):
                if not stripped.endswith(':'):
                    errors.append(SyntaxError(
                        i,
                        "While statement must end with ':'",
                        'ControlFlow'
                    ))
                if '(' not in stripped or ')' not in stripped:
                    errors.append(SyntaxError(
                        i,
                        "While condition must be enclosed in parentheses",
                        'ControlFlow'
                    ))
            
            # 检查 try-catch
            elif stripped == 'try':
                errors.append(SyntaxError(
                    i,
                    "Try must be followed by ':'",
                    'ControlFlow'
                ))
            elif stripped.startswith('catch '):
                if not stripped.endswith(':'):
                    errors.append(SyntaxError(
                        i,
                        "Catch must end with ':'",
                        'ControlFlow'
                    ))
                if '(' not in stripped or ')' not in stripped:
                    errors.append(SyntaxError(
                        i,
                        "Catch must specify error variable in parentheses",
                        'ControlFlow'
                    ))
        
        return errors
    
    def _check_class_syntax(self, content):
        """检查类定义语法"""
        errors = []
        lines = content.split('\n')
        
        in_classes = False
        current_class = None
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # 检测 classes 部分
            if stripped == 'classes:':
                in_classes = True
                continue
            elif not line.startswith(' ') and ':' in stripped:
                in_classes = False
                current_class = None
                continue
            
            if in_classes:
                indent = len(line) - len(line.lstrip())
                
                # 类名（缩进2个空格）
                if indent == 2 and ':' in stripped:
                    class_name = stripped.split(':')[0].strip()
                    
                    # 检查类名是否有效
                    if not re.match(r'^[A-Z][a-zA-Z0-9_]*$', class_name):
                        if class_name != 'parent':  # parent 是特殊键
                            errors.append(SyntaxError(
                                i,
                                f"Class name '{class_name}' should start with uppercase letter",
                                'Naming'
                            ))
                    
                    current_class = class_name
                    if class_name != 'parent':
                        # 检查类定义是否为空
                        next_line_idx = i
                        if next_line_idx < len(lines):
                            next_line = lines[next_line_idx]
                            next_indent = len(next_line) - len(next_line.lstrip())
                            if next_indent <= 2 and next_line.strip():
                                errors.append(SyntaxError(
                                    i,
                                    f"Class '{class_name}' appears to be empty or not properly indented",
                                    'Class'
                                ))
                
                # 方法定义（缩进4个空格）
                elif indent == 4 and current_class and '=>' in stripped:
                    # 提取方法名
                    method_part = stripped.split('=>')[0].strip()
                    if ':' in method_part:
                        method_name = method_part.split(':')[0].strip()
                        
                        # 检查方法名
                        if not re.match(r'^[a-z_][a-zA-Z0-9_]*$', method_name):
                            errors.append(SyntaxError(
                                i,
                                f"Method name '{method_name}' should start with lowercase letter or underscore",
                                'Naming'
                            ))
                        
                        # 检查参数列表
                        if '(' in method_part and ')' in method_part:
                            params_str = method_part[method_part.find('(')+1:method_part.find(')')]
                            params = [p.strip() for p in params_str.split(',') if p.strip()]
                            
                            for param in params:
                                if not re.match(r'^[a-z_][a-zA-Z0-9_]*$', param):
                                    errors.append(SyntaxError(
                                        i,
                                        f"Parameter name '{param}' should start with lowercase letter or underscore",
                                        'Naming'
                                    ))
        
        return errors
    
    def _check_function_syntax(self, content):
        """检查函数定义语法"""
        errors = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # 检查顶层函数定义（不在 classes 中）
            if '=>' in stripped and not line.startswith('  '):
                # 检查是否是有效的函数定义
                if ':' not in stripped:
                    errors.append(SyntaxError(
                        i,
                        "Function definition must have ':' before '=>'",
                        'Function'
                    ))
                    continue
                
                # 提取函数名和参数
                func_part = stripped.split('=>')[0].strip()
                func_name = func_part.split(':')[0].strip()
                
                # 检查函数名
                if not re.match(r'^[a-z_][a-zA-Z0-9_]*$', func_name):
                    if func_name not in ['main', 'call', 'includes', 'imports', 'classes', 'objects']:
                        errors.append(SyntaxError(
                            i,
                            f"Function name '{func_name}' should start with lowercase letter or underscore",
                            'Naming'
                        ))
                
                # 检查参数
                if '(' in func_part and ')' in func_part:
                    params_str = func_part[func_part.find('(')+1:func_part.find(')')]
                    params = [p.strip() for p in params_str.split(',') if p.strip()]
                    
                    for param in params:
                        if not re.match(r'^[a-z_][a-zA-Z0-9_]*$', param):
                            errors.append(SyntaxError(
                                i,
                                f"Parameter name '{param}' should start with lowercase letter or underscore",
                                'Naming'
                            ))
                
                # 检查大括号
                if '{' not in stripped or '}' not in stripped:
                    # 可能是多行函数，检查下一行
                    pass
        
        return errors
    
    def check_now(self):
        """立即执行语法检查"""
        if self.check_timer:
            self.text_widget.after_cancel(self.check_timer)
        return self._perform_check()
    
    def get_errors(self):
        """获取最后一次检查的错误"""
        return self.last_errors
    
    def clear_errors(self):
        """清除错误"""
        self.last_errors = []
        if self.error_callback:
            self.error_callback([])

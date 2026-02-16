"""
实时语法检查组件
集成 hpl_runtime 进行准确的语法检查
"""

import sys
import os
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from hpl_runtime import HPLParser, HPLSyntaxError
    HPL_AVAILABLE = True
except ImportError:
    HPL_AVAILABLE = False

from utils.logger import logger


class SyntaxErrorInfo:
    """语法错误信息"""
    
    def __init__(self, line, message, error_type='Syntax', column=None, error_key=None):
        self.line = line
        self.message = message
        self.error_type = error_type
        self.column = column
        self.error_key = error_key
    
    def __str__(self):
        if self.column:
            return f"Line {self.line}, Col {self.column}: [{self.error_type}] {self.message}"
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
        """执行语法检查 - 使用 hpl_runtime.HPLParser"""
        content = self.text_widget.get('1.0', 'end-1c')
        errors = []
        
        if not HPL_AVAILABLE:
            logger.warning("hpl_runtime 不可用，跳过语法检查")
            self.last_errors = errors
            if self.error_callback:
                self.error_callback(errors)
            return errors
        
        # 使用 HPLParser 进行准确的语法检查
        try:
            # 创建临时文件供 HPLParser 使用
            with tempfile.NamedTemporaryFile(mode='w', suffix='.hpl', delete=False, encoding='utf-8') as f:
                f.write(content)
                temp_file = f.name
            
            try:
                parser = HPLParser(temp_file)
                parser.parse()  # 如果解析成功，无语法错误
                logger.debug("语法检查通过")
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
                    
        except HPLSyntaxError as e:
            # 转换 HPLSyntaxError 为 SyntaxErrorInfo
            error_info = SyntaxErrorInfo(
                line=e.line if e.line else 1,
                message=str(e),
                error_type='SyntaxError',
                column=e.column,
                error_key=getattr(e, 'error_key', None)
            )
            errors.append(error_info)
            logger.debug(f"发现语法错误: {error_info}")
        except Exception as e:
            # 其他错误（如文件问题）
            error_info = SyntaxErrorInfo(
                line=1,
                message=f"检查失败: {str(e)}",
                error_type='CheckError'
            )
            errors.append(error_info)
            logger.error(f"语法检查异常: {e}")
        
        # 更新错误列表
        self.last_errors = errors
        
        # 调用回调函数
        if self.error_callback:
            self.error_callback(errors)
        
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

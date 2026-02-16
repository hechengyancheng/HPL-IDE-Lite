"""
日志系统模块
提供统一的日志记录功能
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional, Callable
from enum import Enum


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class IDELogger:
    """
    IDE 日志记录器
    支持控制台输出、文件输出和回调通知
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._log_file = None
        self._console_callback = None
        self._log_level = LogLevel.INFO
        self._log_to_file = False
        self._log_to_console = True
        self._show_timestamp = True
        self._log_history = []
        self._max_history = 1000
        
        # 创建日志目录
        self._log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        os.makedirs(self._log_dir, exist_ok=True)
        
        # 设置默认日志文件
        self._setup_log_file()
    
    def _setup_log_file(self):
        """设置日志文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._log_file = os.path.join(self._log_dir, f"ide_{timestamp}.log")
    
    def set_console_callback(self, callback: Callable[[str, str], None]):
        """
        设置控制台回调函数
        
        Args:
            callback: 回调函数，接收 (message, level) 参数
        """
        self._console_callback = callback
    
    def set_log_level(self, level: LogLevel):
        """
        设置日志级别
        
        Args:
            level: 日志级别
        """
        self._log_level = level
        self.info(f"日志级别设置为: {level.value}")
    
    def enable_file_logging(self, enable: bool = True):
        """
        启用/禁用文件日志
        
        Args:
            enable: 是否启用
        """
        self._log_to_file = enable
        if enable:
            self.info(f"文件日志已启用: {self._log_file}")
        else:
            self.info("文件日志已禁用")
    
    def enable_console_logging(self, enable: bool = True):
        """
        启用/禁用控制台日志
        
        Args:
            enable: 是否启用
        """
        self._log_to_console = enable
    
    def set_show_timestamp(self, show: bool):
        """
        设置是否显示时间戳
        
        Args:
            show: 是否显示
        """
        self._show_timestamp = show
    
    def _should_log(self, level: LogLevel) -> bool:
        """检查是否应该记录该级别的日志"""
        levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
        current_index = levels.index(self._log_level)
        message_index = levels.index(level)
        return message_index >= current_index
    
    def _format_message(self, message: str, level: LogLevel) -> str:
        """格式化日志消息"""
        if self._show_timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S")
            return f"[{timestamp}] [{level.value}] {message}"
        else:
            return f"[{level.value}] {message}"
    
    def _write_to_file(self, formatted_message: str):
        """写入日志文件"""
        if self._log_to_file and self._log_file:
            try:
                with open(self._log_file, 'a', encoding='utf-8') as f:
                    f.write(formatted_message + "\n")
            except Exception as e:
                print(f"写入日志文件失败: {e}", file=sys.stderr)
    
    def _notify_console(self, formatted_message: str, level: LogLevel):
        """通知控制台回调"""
        if self._log_to_console and self._console_callback:
            try:
                self._console_callback(formatted_message, level.value.lower())
            except Exception as e:
                # 忽略Tkinter widget销毁后的回调错误
                error_msg = str(e)
                if "invalid command name" in error_msg:
                    # Widget已被销毁，静默忽略
                    pass
                else:
                    print(f"控制台回调失败: {e}", file=sys.stderr)
    
    def clear_console_callback(self):
        """清除控制台回调（用于应用关闭时）"""
        self._console_callback = None

    
    def _add_to_history(self, formatted_message: str, level: LogLevel):
        """添加到历史记录"""
        self._log_history.append({
            'timestamp': datetime.now(),
            'level': level.value,
            'message': formatted_message
        })
        
        # 限制历史记录大小
        if len(self._log_history) > self._max_history:
            self._log_history = self._log_history[-self._max_history:]
    
    def log(self, message: str, level: LogLevel = LogLevel.INFO):
        """
        记录日志
        
        Args:
            message: 日志消息
            level: 日志级别
        """
        if not self._should_log(level):
            return
        
        formatted = self._format_message(message, level)
        
        # 添加到历史
        self._add_to_history(formatted, level)
        
        # 写入文件
        self._write_to_file(formatted)
        
        # 通知控制台
        self._notify_console(formatted, level)
        
        # 同时输出到标准错误（用于调试）
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            print(formatted, file=sys.stderr)
    
    def debug(self, message: str):
        """记录调试日志"""
        self.log(message, LogLevel.DEBUG)
    
    def info(self, message: str):
        """记录信息日志"""
        self.log(message, LogLevel.INFO)
    
    def warning(self, message: str):
        """记录警告日志"""
        self.log(message, LogLevel.WARNING)
    
    def error(self, message: str):
        """记录错误日志"""
        self.log(message, LogLevel.ERROR)
    
    def critical(self, message: str):
        """记录严重错误日志"""
        self.log(message, LogLevel.CRITICAL)
    
    def get_log_history(self, level: Optional[LogLevel] = None, limit: int = 100) -> list:
        """
        获取日志历史
        
        Args:
            level: 过滤级别（可选）
            limit: 返回条数限制
            
        Returns:
            日志历史列表
        """
        if level:
            filtered = [entry for entry in self._log_history if entry['level'] == level.value]
        else:
            filtered = self._log_history
        
        return filtered[-limit:]
    
    def clear_history(self):
        """清除日志历史"""
        self._log_history.clear()
        self.info("日志历史已清除")
    
    def get_current_log_file(self) -> str:
        """获取当前日志文件路径"""
        return self._log_file
    
    def open_log_file(self):
        """打开日志文件（用于查看）"""
        if self._log_file and os.path.exists(self._log_file):
            try:
                if sys.platform == 'win32':
                    os.startfile(self._log_file)
                elif sys.platform == 'darwin':
                    import subprocess
                    subprocess.call(['open', self._log_file])
                else:
                    import subprocess
                    subprocess.call(['xdg-open', self._log_file])
            except Exception as e:
                self.error(f"打开日志文件失败: {e}")


# 全局日志记录器实例
logger = IDELogger()


def get_logger() -> IDELogger:
    """获取全局日志记录器"""
    return logger


# 便捷函数
def debug(message: str):
    """记录调试日志"""
    logger.debug(message)

def info(message: str):
    """记录信息日志"""
    logger.info(message)

def warning(message: str):
    """记录警告日志"""
    logger.warning(message)

def error(message: str):
    """记录错误日志"""
    logger.error(message)

def critical(message: str):
    """记录严重错误日志"""
    logger.critical(message)

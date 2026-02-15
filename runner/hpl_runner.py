"""
HPL 执行器封装
集成 hpl_runtime 模块
"""

import sys
import io
import traceback
import time
import os
from typing import Dict, Any, Optional

# 导入日志模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logger

# 导入 hpl_runtime
try:
    from hpl_runtime import (
        HPLParser, HPLEvaluator, DebugInterpreter,
        HPLSyntaxError, HPLRuntimeError, HPLImportError, HPLNameError
    )
    HPL_AVAILABLE = True
except ImportError:
    HPL_AVAILABLE = False
    print("警告: hpl_runtime 模块未安装，运行功能将不可用")
    logger.warning("hpl_runtime 模块未安装，运行功能将不可用")



class HPLRunner:
    """HPL 代码执行器"""
    
    def __init__(self):
        self.last_result = None
    
    def run(self, file_path: str) -> Dict[str, Any]:
        """
        运行 HPL 文件
        
        Returns:
            {
                'success': bool,
                'output': str,  # 标准输出
                'error': str,   # 错误信息
                'error_type': str,  # 错误类型
                'line': int,    # 错误行号
                'column': int,  # 错误列号
                'call_stack': list  # 调用栈
            }
        """
        start_time = time.time()
        logger.info(f"开始解析和运行 HPL 文件: {file_path}")
        
        if not HPL_AVAILABLE:
            logger.error("hpl_runtime 模块未安装")
            return {
                'success': False,
                'output': '',
                'error': 'hpl_runtime 模块未安装',
                'error_type': 'ImportError',
                'line': None,
                'column': None,
                'call_stack': []
            }
        
        # 重定向标准输出
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        try:
            sys.stdout = stdout_buffer
            sys.stderr = stderr_buffer
            
            # 解析文件
            logger.debug(f"解析文件: {file_path}")
            parser = HPLParser(file_path)
            classes, objects, functions, main_func, call_target, call_args, imports, user_data = parser.parse()

            logger.debug(f"解析完成: 发现 {len(classes)} 个类, {len(objects)} 个对象, {len(functions)} 个函数")
            
            # 创建执行器
            evaluator = HPLEvaluator(
                classes=classes,
                objects=objects,
                functions=functions,
                main_func=main_func,
                call_target=call_target,
                call_args=call_args
            )
            
            # 执行
            logger.debug("开始执行 HPL 代码")
            evaluator.run()
            
            # 获取输出
            output = stdout_buffer.getvalue()
            elapsed_time = time.time() - start_time
            logger.info(f"HPL 代码执行成功，耗时: {elapsed_time:.3f}秒")
            
            self.last_result = {
                'success': True,
                'output': output,
                'error': None,
                'error_type': None,
                'line': None,
                'column': None,
                'call_stack': []
            }
            
        except HPLSyntaxError as e:
            elapsed_time = time.time() - start_time
            error_msg = f"语法错误 [行 {e.line}, 列 {e.column}]: {str(e)}"
            logger.error(f"语法错误 (耗时: {elapsed_time:.3f}秒): {error_msg}")

            self.last_result = {
                'success': False,
                'output': stdout_buffer.getvalue(),
                'error': error_msg,
                'error_type': 'SyntaxError',
                'line': e.line,
                'column': e.column,
                'call_stack': []
            }
            
        except HPLNameError as e:
            elapsed_time = time.time() - start_time
            error_msg = f"名称错误: {str(e)}"
            logger.error(f"名称错误 (耗时: {elapsed_time:.3f}秒): {error_msg}")
            self.last_result = {
                'success': False,
                'output': stdout_buffer.getvalue(),
                'error': error_msg,
                'error_type': 'NameError',
                'line': getattr(e, 'line', None),
                'column': getattr(e, 'column', None),
                'call_stack': getattr(e, 'call_stack', [])
            }
            
        except HPLRuntimeError as e:
            elapsed_time = time.time() - start_time
            error_msg = f"运行时错误: {str(e)}"
            if hasattr(e, 'call_stack') and e.call_stack:
                error_msg += f"\n调用栈: {e.call_stack}"
            logger.error(f"运行时错误 (耗时: {elapsed_time:.3f}秒): {error_msg}")
            
            self.last_result = {
                'success': False,
                'output': stdout_buffer.getvalue(),
                'error': error_msg,
                'error_type': 'RuntimeError',
                'line': getattr(e, 'line', None),
                'column': getattr(e, 'column', None),
                'call_stack': getattr(e, 'call_stack', [])
            }
            
        except HPLImportError as e:
            elapsed_time = time.time() - start_time
            error_msg = f"导入错误: {str(e)}"
            logger.error(f"导入错误 (耗时: {elapsed_time:.3f}秒): {error_msg}")
            self.last_result = {
                'success': False,
                'output': stdout_buffer.getvalue(),
                'error': error_msg,
                'error_type': 'ImportError',
                'line': None,
                'column': None,
                'call_stack': []
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = f"内部错误: {str(e)}"
            logger.error(f"内部错误 (耗时: {elapsed_time:.3f}秒): {error_msg}")
            logger.debug(f"错误详情: {traceback.format_exc()}")
            self.last_result = {
                'success': False,
                'output': stdout_buffer.getvalue(),
                'error': error_msg,
                'error_type': type(e).__name__,
                'line': None,
                'column': None,
                'call_stack': traceback.format_exc().split('\n')
            }
            
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        return self.last_result

    
    def debug(self, file_path: str) -> Dict[str, Any]:
        """
        调试 HPL 文件
        
        Returns:
            {
                'success': bool,
                'output': str,
                'error': str,
                'trace': list,  # 执行跟踪
                'variables': list,  # 变量快照
                'call_stack': list  # 调用栈历史
            }
        """
        start_time = time.time()
        logger.info(f"开始调试 HPL 文件: {file_path}")
        
        if not HPL_AVAILABLE:
            logger.error("hpl_runtime 模块未安装，无法调试")
            return {
                'success': False,
                'output': '',
                'error': 'hpl_runtime 模块未安装',
                'trace': [],
                'variables': [],
                'call_stack': []
            }
        
        # 重定向输出
        old_stdout = sys.stdout
        stdout_buffer = io.StringIO()
        
        try:
            sys.stdout = stdout_buffer
            
            # 使用调试解释器
            logger.debug("初始化调试解释器")
            interpreter = DebugInterpreter(debug_mode=True, verbose=False)
            result = interpreter.run(file_path)
            
            debug_info = result.get('debug_info', {})
            elapsed_time = time.time() - start_time
            
            trace_count = len(debug_info.get('execution_trace', []))
            var_count = len(debug_info.get('variable_snapshots', []))
            logger.info(f"调试完成，耗时: {elapsed_time:.3f}秒，跟踪 {trace_count} 步，{var_count} 个变量快照")
            
            return {
                'success': result.get('success', False),
                'output': stdout_buffer.getvalue(),
                'error': str(result.get('error')) if result.get('error') else None,
                'trace': debug_info.get('execution_trace', []),
                'variables': debug_info.get('variable_snapshots', []),
                'call_stack': debug_info.get('call_stack_history', [])
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = f"调试错误: {str(e)}"
            logger.error(f"调试异常 (耗时: {elapsed_time:.3f}秒): {error_msg}")
            logger.debug(f"错误详情: {traceback.format_exc()}")
            return {
                'success': False,
                'output': stdout_buffer.getvalue(),
                'error': f"{error_msg}\n{traceback.format_exc()}",
                'trace': [],
                'variables': [],
                'call_stack': []
            }
            
        finally:
            sys.stdout = old_stdout

    
    def check_syntax(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        检查语法
        
        Returns:
            None - 语法正确
            Dict - 错误信息
        """
        logger.debug(f"检查语法: {file_path}")
        
        if not HPL_AVAILABLE:
            logger.warning("hpl_runtime 模块未安装，无法检查语法")
            return {
                'line': 1,
                'column': 1,
                'message': 'hpl_runtime 模块未安装',
                'error_code': 'IMPORT_ERROR'
            }
        
        try:
            parser = HPLParser(file_path)
            parser.parse()
            logger.debug(f"语法检查通过: {file_path}")
            return None  # 无错误
            
        except HPLSyntaxError as e:
            logger.warning(f"语法错误 [行 {e.line}, 列 {e.column}]: {str(e)}")
            return {
                'line': e.line,
                'column': e.column,
                'message': str(e),
                'error_code': getattr(e, 'error_code', 'SYNTAX_ERROR')
            }

        except Exception as e:
            logger.error(f"语法检查异常: {str(e)}")
            return {
                'line': 1,
                'column': 1,
                'message': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }

    
    def get_completions(self, file_path: str, prefix: str = "") -> list:
        """
        获取代码补全项
        
        Returns:
            list of dict: [{'label': str, 'kind': str, 'detail': str}]
        """
        logger.debug(f"获取代码补全: {file_path}, 前缀: '{prefix}'")
        
        if not HPL_AVAILABLE:
            logger.warning("hpl_runtime 模块未安装，无法获取补全")
            return []
        
        try:
            parser = HPLParser(file_path)
            classes, objects, functions, _, _, _, _ = parser.parse()
            
            items = []
            
            # 类补全
            for name in classes.keys():
                if name.startswith(prefix):
                    items.append({
                        'label': name,
                        'kind': 'Class',
                        'detail': f'Class {name}'
                    })
            
            # 对象补全
            for name in objects.keys():
                if name.startswith(prefix):
                    obj = objects[name]
                    class_name = obj.hpl_class.name if hasattr(obj, 'hpl_class') else 'Unknown'
                    items.append({
                        'label': name,
                        'kind': 'Object',
                        'detail': f'Object {name} ({class_name})'
                    })
            
            # 函数补全
            for name, func in functions.items():
                if name.startswith(prefix):
                    params = getattr(func, 'params', [])
                    items.append({
                        'label': name,
                        'kind': 'Function',
                        'detail': f'Function {name}({", ".join(params)})'
                    })
            
            logger.debug(f"找到 {len(items)} 个补全项")
            return items
            
        except Exception as e:
            logger.warning(f"获取补全失败: {str(e)}")
            return []

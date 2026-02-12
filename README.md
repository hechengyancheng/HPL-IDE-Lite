# HPL-IDE-Lite

轻量级的 HPL (H Programming Language) 集成开发环境，基于 Python 和 CustomTkinter 构建。

## 功能特性

- 📝 **代码编辑器**：支持语法高亮、行号显示、自动缩进
- 🖥️ **集成控制台**：实时显示程序输出
- 📁 **文件浏览器**：项目文件树浏览
- ▶️ **一键运行**：F5 快速执行 HPL 程序
- 🐛 **调试支持**：F9 调试模式，查看执行跟踪和变量状态
- 🎨 **现代界面**：暗色主题，美观易用

## 安装要求

- Python 3.8+
- hpl_runtime 模块（HPL 运行时）
- customtkinter（现代 UI 组件）

## 安装步骤

1. 克隆或下载本项目
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 确保已安装 hpl_runtime 模块（根据你的 HPL 运行时安装方式）

## 使用方法

### 启动 IDE
```bash
python main.py
```

### 基本操作

| 快捷键 | 功能 |
|--------|------|
| Ctrl+N | 新建文件 |
| Ctrl+O | 打开文件 |
| Ctrl+S | 保存文件 |
| F5 | 运行代码 |
| F9 | 调试代码 |
| Ctrl+Z | 撤销 |
| Ctrl+Y | 重做 |
| Ctrl+F | 查找 |

### 创建 HPL 程序

1. 点击"文件" → "新建文件" 或按 Ctrl+N
2. 在编辑器中编写 HPL 代码
3. 按 Ctrl+S 保存为 `.hpl` 文件
4. 按 F5 运行程序

### 示例代码

```yaml
# Hello World 示例
classes:
  Greeter:
    init: (name) => {
        this.name = name
      }
    greet: () => {
        echo "Hello, " + this.name + "!"
      }

objects:
  greeter: Greeter("World")

main: () => {
    greeter.greet()
  }

call: main()
```

## 项目结构

```
HPL-IDE-Lite/
├── main.py              # 程序入口
├── ui/                  # UI 组件
│   ├── main_window.py   # 主窗口
│   ├── editor.py        # 代码编辑器
│   ├── console.py       # 控制台
│   └── file_tree.py     # 文件树
├── runner/              # HPL 执行器
│   └── hpl_runner.py    # hpl_runtime 封装
├── examples/            # 示例程序
│   ├── hello.hpl        # Hello World
│   └── features.hpl     # 特性演示
├── docs/                # 文档
├── requirements.txt     # 依赖列表
└── README.md           # 本文件
```

## HPL 语言简介

HPL (H Programming Language) 是一种基于 YAML 格式的面向对象编程语言：

- 使用 YAML 结构组织代码
- 支持类、对象、继承
- 支持函数、控制流（if/for/while）
- 支持异常处理（try-catch）
- 丰富的标准库（math, io, json, os, time 等）

详见 `docs/HPL语法手册.md`

## 调试功能

在调试模式下（F9），IDE 会显示：
- 执行跟踪（每步执行的函数和语句）
- 变量状态快照（各执行点的变量值）
- 调用栈历史

## 错误处理

IDE 会自动捕获并显示：
- 语法错误（显示行号和列号）
- 运行时错误（显示错误信息和调用栈）
- 导入错误

错误行会在编辑器中高亮显示。

## 许可证

MIT License

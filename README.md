# SRE 制造工具

这是一个桌面应用程序，用于根据设备信息生成配置二维码和对应的JSON字符串。

## 功能特性

- **数据输入**: 提供用于输入设备SN、密钥、服务器地址等信息的表单。
- **JSON生成**: 根据输入动态生成层级结构的JSON配置。
- **二维码生成**: 实时生成包含JSON内容的二维码。
- **结果展示**: 同时展示二维码图像和格式化的JSON文本。
- **操作便捷**: 支持一键下载二维码、一键清空所有输入。
- **自适应布局**: 窗口大小可调，所有控件将自动适应。

## 架构与技术

- **语言**: Python 3
- **UI框架**: PySide6
- **核心库**:
    - `qrcode`: 用于生成二维码图像。
    - `Pillow`: `qrcode`的依赖，用于处理图像。
    - `pyinstaller`: 用于将Python脚本打包成独立的可执行文件。
- **代码结构**:
    - `main.py`: 单文件应用，包含所有UI和逻辑。
        - `MainWindow` 类: 继承自 `QMainWindow`，负责构建和管理整个UI及所有功能。
        - **可扩展性**: 输入字段被存储在一个字典 `self.inputs` 中，使得未来添加新的输入框或选择框变得非常简单，只需修改初始化部分即可，核心逻辑无需大改。

---

## 安装与运行

### 1. 环境准备

确保你的系统已经安装了 Python 3 (建议 3.8+)。

### 2. 克隆或下载项目

将项目文件下载到本地。

### 3. 创建并激活虚拟环境

在项目根目录下打开终端，执行以下命令：

```bash
# 创建虚拟环境 (venv是虚拟环境的名称)
python3 -m venv venv

# 激活虚拟环境
# macOS / Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

### 4. 安装依赖

激活虚拟环境后，安装所有必需的库：

```bash
pip install -r requirements.txt
```

### 5. 运行程序

执行主程序脚本：

```bash
python main.py
```

---

## 使用说明

1.  **填写信息**: 根据标签提示，在对应的输入框中填入信息。
2.  **选择配置**: 从下拉框中选择 `serverType`。
3.  **生成**: 点击“生成”按钮。右侧将立即显示二维码和其包含的JSON内容。
    - *注意*: 只有填写了内容的字段才会被包含在JSON中。
4.  **下载**: 点击“下载二维码”按钮，选择本地路径即可将当前二维码保存为 `.png` 文件。
5.  **清空**: 点击“清空”按钮，所有输入将被重置为初始状态。

---

## 打包为独立应用

你可以使用 `pyinstaller` 将此工具打包成一个无需Python环境即可运行的独立应用程序。

**重要前提：** `PyInstaller` **不支持交叉编译**。这意味着你必须在目标操作系统和架构上运行打包命令。
- 要想打包成 Windows 应用，你必须在 Windows 系统上执行命令。
- 要想打包成 macOS 应用，你必须在 macOS 系统上执行命令。

---

### 在 Windows 上打包 (64位 .exe)

1.  **环境要求**: 一台64位 Windows 电脑，并已安装64位版本的 Python。
2.  按照“安装与运行”部分的说明，在 Windows 上准备好虚拟环境并安装依赖。
3.  在激活了虚拟环境的终端 (CMD 或 PowerShell) 中，执行打包命令：
    ```bash
    pyinstaller --name SRE-QR-Generator --onefile --windowed main.py
    ```
4.  打包完成后，在项目目录下的 `dist` 文件夹中找到 `SRE-QR-Generator.exe` 文件。

---

### 在 macOS 上打包 (ARM .app)

1.  **环境要求**: 一台使用 Apple Silicon (M1, M2, M3 等) 的 Mac 电脑，并已安装 ARM 架构的 Python 版本。
    - 你可以通过以下命令检查你的 Python 架构，结果应为 `arm64`：
      ```bash
      python -c "import platform; print(platform.machine())"
      ```
2.  按照“安装与运行”部分的说明，在 macOS 上准备好虚拟环境并安装依赖。
3.  在激活了虚拟环境的终端中，执行打包命令：
    ```bash
    pyinstaller --name SRE-QR-Generator --onefile --windowed main.py
    ```
4.  打包完成后，在项目目录下的 `dist` 文件夹中找到 `SRE-QR-Generator.app`。
    - **macOS 图标 (可选)**: 如果你想为 `.app` 添加自定义图标，可以准备一个 `.icns` 格式的图标文件，然后使用 `--icon` 参数：
      ```bash
      pyinstaller --name SRE-QR-Generator --onefile --windowed --icon=YourIcon.icns main.py
      ```

# 局域网聊天室

本项目为使用 Python 3 + Flask + WebSocket + HTML5 + CSS3 + JS (jQuery) 实现的 Web 在线聊天室，集成智能助手功能。

参考项目：[deyugong/GAME](https://github.com/deyugong/GAME)

## 功能特性

### 1. 基础聊天
- **多人实时群聊**：采用 WebSocket 技术，支持多人同房间即时通讯。
- **UI 设计**：仿微信/QQ 气泡样式，支持 Emoji 表情。

### 2. 智能指令
支持以下快捷指令（点击聊天框上方按钮或直接输入）：
- **@新闻**：获取最新的实时新闻热点（Top 10），以卡片形式展示。
- **@天气 [城市名]**：查询指定城市的实时天气信息（如：`@天气 北京`）。
- **@音乐**：随机推荐一首热歌，支持直接在聊天卡片中播放。

### 3. 客户端支持
- **Web 端**：浏览器直接访问。
- **Windows 客户端**：提供打包脚本，可生成 `.exe` 独立可执行文件。

## 快速开始

### 1. 环境准备
确保已安装 Python 3.8+。

```bash
# 克隆仓库
git clone https://github.com/159hv/ChatBoot.git
cd ChatBoot

# 创建虚拟环境 (推荐)
python -m venv venv

# 激活虚拟环境
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行项目

**开发模式启动：**

```bash
python app.py
```
启动后访问：`http://localhost:5000`

**打包为 EXE (Windows)：**

```bash
python build_exe.py
```
打包完成后，可执行文件位于 `dist/ChatBoot.exe`。

## 项目结构

```
ChatBoot/
├── app.py              # 主程序入口 (Flask + SocketIO)
├── build_exe.py        # PyInstaller 打包脚本
├── config.py           # 配置文件
├── hook-dns.py         # PyInstaller 钩子文件 (修复 dns 模块问题)
├── requirements.txt    # 项目依赖
├── static/             # 静态资源 (JS/CSS)
└── templates/          # HTML 模板
    ├── chat.html       # 聊天室主页
    └── login.html      # 登录页
```

## API 说明

本项目集成了以下第三方 API：
- **新闻/音乐**：QQSUU API
- **天气**：Open-Meteo & Geopy

## 许可证

MIT License

# Gomoku 项目完整打包和部署指南

## 项目概述

本项目是一个基于Python Flask的五子棋游戏，支持人机对战，包含多种AI难度。本文档详细说明了如何将项目打包为Windows EXE文件和Android APK文件，以及相关的部署和发布步骤。

## 技术栈

### 前端
- HTML5
- CSS3
- Canvas API
- JavaScript (ES6+)

### 后端
- Python 3.8+（推荐3.13.12）
- Flask Web框架
- Flask-CORS (跨域支持)

### AI算法
- 随机算法（简单难度）
- 贪心算法（普通难度）
- Minimax α-β 剪枝（困难难度，搜索深度4层）
简单难度在随机落子的基础上，增加了对玩家三连子（两边为空）和四连子的拦截，保证AI具备基本防守能力。

## 项目结构

```
Gomoku/
├── main.py                     # 程序入口
├── frontend/                   # 前端页面
│   ├── index.html             # 首页
│   ├── aiBattle.html          # 人机对战
│   ├── FriendBattle.html      # 好友对战
│   ├── ChessManual.html       # 棋谱导出
│   └── quweiAuthor/           # 趣味登录模块
│       ├── index.html         # 登录注册主页
│       ├── login.html        # 登录页面
│       ├── register.html     # 注册页面
│       ├── css/             # 样式文件
│       └── js/              # JavaScript文件
├── backend/                    # 后端代码
│   ├── app.py                # Flask接口
│   ├── game.py               # 游戏逻辑
│   ├── ai_1.py              # 简单/普通AI
│   ├── ai_2.py              # 困难AI
│   └── game_utils.py        # 工具函数
└── static/                     # 静态资源
    └── sounds/                 # 音效文件
        └── luozi.mp3         # 落子音效
```

## 环境配置

### 系统要求
- 操作系统：Windows/Linux/macOS
- Python版本：3.8或更高（推荐3.13.12）
- 浏览器：现代浏览器（Chrome/Firefox/Safari/Edge）

### 安装Python

#### Windows
1. 访问 https://www.python.org/downloads/
2. 下载Python 3.8或更高版本（推荐3.13.12）
3. 运行安装程序，勾选"Add Python to PATH"
4. 验证安装：打开命令行输入 `python --version`

#### Linux
```bash
sudo apt-get update
sudo apt-get install python3.13 python3-pip
```

#### macOS
```bash
brew install python@3.13
```

### 安装依赖

创建虚拟环境（推荐）：
```bash
python -m venv .venv
```

激活虚拟环境：
- Windows:.\.venv\Scripts\Activate.ps1
- Linux/macOS: `source venv/bin/activate`

安装项目依赖：
```bash
pip install flask flask-cors
```

## 服务器启动

### 基本启动

```bash
python main.py
```

### 端口配置

**重要说明**：服务器默认使用80端口，需要管理员权限运行。

#### Windows
- 右键点击命令提示符或PowerShell
- 选择"以管理员身份运行"
- 执行 `python main.py`

#### Linux/macOS
```bash
sudo python main.py
```

### 修改端口

如果需要使用其他端口，修改 `main.py` 文件：
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # 修改为8080端口
```

### 访问应用

启动成功后，可以通过以下方式访问：

1. **本地访问**
   - http://localhost
   - http://127.0.0.1

2. **局域网访问**
   - 查看本机IP地址：
     - Windows: `ipconfig`
     - Linux/macOS: `ifconfig` 或 `ip addr`
   - 访问：http://[你的IP地址]

3. **直接打开文件**
   - 浏览器打开 `frontend/index.html`

## 响应式设计

项目采用响应式设计，支持多种设备：

### 桌面端 (>768px)
- 完整的游戏界面
- 大尺寸棋盘
- 水平布局的控制按钮

### 平板端 (≤768px)
- 适中的界面尺寸
- 调整后的棋盘大小
- 优化的按钮尺寸

### 移动端 (≤480px)
- 小尺寸界面
- 垂直布局的控制按钮
- 优化的触摸目标

## Windows EXE 打包

### 准备工作

1. **安装PyInstaller**
```bash
pip install pyinstaller
```

2. **测试项目运行**
```bash
python main.py
```
访问 http://localhost 确保功能正常

### 执行打包

```bash
pyinstaller --onefile --add-data "frontend;frontend" --add-data "backend;backend" --add-data "static;static" --name Gomoku main.py
```

### 打包后处理

1. **测试EXE文件**
   - 进入 `dist` 目录
   - 双击运行 `Gomoku.exe`
   - 测试所有功能

2. **文件分发**
   - 直接分发EXE文件
   - 或创建ZIP压缩包

## 常见问题解决

### 启动问题

**问题1：端口被占用**
```
OSError: [WinError 10048] 通常每个套接字地址
```
**解决方案**：
- 检查80端口是否被其他程序占用
- 修改 `main.py` 使用其他端口
- 或以管理员身份运行程序

**问题2：权限不足**
```
PermissionError: [WinError 5] 拒绝访问
```
**解决方案**：
- 以管理员身份运行程序
- 检查防火墙设置

**问题3：依赖缺失**
```
ModuleNotFoundError: No module named 'flask'
```
**解决方案**：
```bash
pip install flask flask-cors
```

### 游戏问题

**问题1：落子音效无法播放**
**解决方案**：
- 确保浏览器允许自动播放音效
- 检查音效文件路径是否正确
- 确认音效文件存在于 `static/sounds/luozi.mp3`

**问题2：AI响应很慢**
**解决方案**：
- 困难难度AI需要较多计算时间，这是正常现象
- 可以降低难度或等待计算完成
- 检查系统资源使用情况

**问题3：棋谱导出失败**
**解决方案**：
- 确保浏览器支持Canvas导出
- 检查是否有足够的存储空间
- 尝试使用不同的浏览器

### 兼容性问题

**问题1：移动端显示异常**
**解决方案**：
- 刷新页面
- 更换浏览器
- 清除浏览器缓存

**问题2：跨域请求失败**
**解决方案**：
- 确保后端已启动
- 检查CORS配置
- 使用相同协议访问（http或https）

## 性能优化

### 服务器优化

1. **使用生产环境**
```python
app.run(host='0.0.0.0', port=80, debug=False)
```

2. **使用Gunicorn（Linux/macOS）**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:80 main:app
```

3. **使用Nginx反向代理**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 前端优化

1. **压缩静态资源**
2. **使用CDN加速**
3. **启用浏览器缓存**
4. **优化图片加载**

### AI优化

1. **调整搜索深度**
   - 简单难度：无需优化
   - 普通难度：贪心算法已优化
   - 困难难度：可调整搜索深度为3层以提升速度

2. **使用多线程**
   - 将AI计算放到后台线程
   - 避免阻塞主线程

## 安全建议

1. **输入验证**
   - 验证所有用户输入
   - 防止SQL注入和XSS攻击

2. **HTTPS部署**
   - 使用SSL证书
   - 强制HTTPS访问

3. **访问控制**
   - 限制访问IP
   - 实现用户认证

4. **日志记录**
   - 记录访问日志
   - 监控异常行为

## 测试清单

### 功能测试
- [ ] 游戏启动正常
- [ ] 人机对战功能
- [ ] 三种AI难度
- [ ] 好友对战功能
- [ ] 悔棋功能
- [ ] 重新开始功能
- [ ] 认输功能
- [ ] 棋谱导出功能
- [ ] 落子音效播放
- [ ] 胜负判断准确

### 兼容性测试
- [ ] Windows 7/8/10/11
- [ ] Linux (Ubuntu/CentOS)
- [ ] macOS
- [ ] Chrome浏览器
- [ ] Firefox浏览器
- [ ] Safari浏览器
- [ ] Edge浏览器
- [ ] 移动端浏览器

### 性能测试
- [ ] 启动速度 < 5秒
- [ ] 简单AI响应 < 1秒
- [ ] 普通AI响应 < 2秒
- [ ] 困难AI响应 < 10秒
- [ ] 内存使用 < 500MB
- [ ] CPU使用率合理

### 安全测试
- [ ] 输入验证
- [ ] 跨站脚本攻击(XSS)防护
- [ ] 跨站请求伪造(CSRF)防护
- [ ] SQL注入防护（如适用）

## 维护和更新

### 日志管理

1. **启用日志**
```python
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)
```

2. **日志轮转**
```python
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
```

### 错误监控

1. **捕获异常**
```python
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({'error': str(e)}), 500
```

2. **记录错误**
```python
import traceback
traceback.print_exc()
```

### 版本更新

1. **版本管理**
   - 使用语义化版本号（如1.0.0）
   - 维护更新日志（CHANGELOG.md）
   - 提供版本升级说明

2. **数据备份**
   - 定期备份用户数据
   - 备份配置文件
   - 测试恢复流程

## 总结

通过本指南，你可以：

1. **配置开发环境**：安装Python和必要的依赖
2. **启动服务器**：运行Flask应用
3. **访问应用**：通过浏览器访问游戏
4. **打包应用**：创建Windows EXE文件
5. **解决问题**：处理常见问题和错误
6. **优化性能**：提升应用性能和用户体验
7. **确保安全**：实施安全措施

如有其他问题，请参考项目README.md或提交Issue。

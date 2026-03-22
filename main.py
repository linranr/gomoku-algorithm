# main.py
# 项目入口文件 - 启动 Flask 服务器
import webbrowser
import time
from backend.app import app


def open_browser():
    # 延迟 1 秒，等服务器启动后再打开浏览器
    time.sleep(1)
    # 本地开发环境配置（已注释）
    # webbrowser.open("http://127.0.0.1:5000")
    # webbrowser.open("http://localhost:5000")
    
    # 公网生产环境配置
    webbrowser.open("https://gomoku-algorithm-production.up.railway.app/")


if __name__ == '__main__':
    # 启动前先打开浏览器
    open_browser()

    print("正在启动服务器，监听端口 80...")
    print("提示：如果启动失败，请以管理员身份运行此程序")
    # 本地开发环境配置（已注释）
    # app.run(debug=True, host='0.0.0.0', port=5000)
    
    # 公网生产环境配置
    app.run(debug=False, host='0.0.0.0', port=80)

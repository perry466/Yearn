"""Yearn 单服务启动入口。

直接运行即可拉起整个项目（API + 调度器 + 前端 dist），无需命令行参数、
无需手动设置 PYTHONPATH（脚本会自动把 backend 目录加入模块搜索路径）。
关闭终端 / 窗口即停止服务。

用法：
    cd D:/project/yearn/backend
    python run.py
（也可以直接双击本文件运行，前提是 .py 已关联 python）
"""
import sys
from pathlib import Path

# 确保能 import app 包（无论从哪个目录启动本脚本）
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import uvicorn
from app.main import app

HOST = "0.0.0.0"
PORT = 8000


if __name__ == "__main__":
    print("=" * 50)
    print(" Starting Yearn (single service)")
    print(" API + Scheduler + Frontend")
    print(f" Home:     http://localhost:{PORT}")
    print(f" Settings: http://localhost:{PORT}/settings")
    print(" (Ctrl+C or close window to stop)")
    print("=" * 50)
    uvicorn.run(app, host=HOST, port=PORT)

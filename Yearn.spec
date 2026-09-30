# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置（Yearn → Windows 绿色目录版）。

用法（项目根目录执行）：
    npm run build            # 先确保 frontend/dist 存在
    pyinstaller Yearn.spec   # 产物在 dist/Yearn/ 目录

目录模式（onedir）产出结构：
    dist/Yearn/
    ├── Yearn.exe   启动入口，双击它（无控制台，右下角托盘常驻）
    ├── data/       你的数据与日志，首次运行自动创建
    ├── lib/        依赖与前端资源，不用动它
    └── 使用说明.txt

用 spec 而不是命令行参数的好处：datas 用元组写法，不需要区分
Windows 的 `;` 和 Linux/macOS 的 `:`，本地与 CI 行为完全一致。
"""
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []

# 前端构建产物（必须已执行 npm run build）
# 目标路径保持 frontend/dist，与 app/main.py 中 _resource_dir() 的约定一致
datas += [("frontend/dist", "frontend/dist")]

# 随包分发的使用说明，目标写 "." 表示放在绿色版根目录，而不是被塞进 lib/
# （由 spec 统一处理，CI 里就不需要再 cp 了，也绕开中文文件名的编码问题）
datas += [("packaging/使用说明.txt", ".")]

# 以下包必须整包收集，否则运行时报错：
# - pydantic  : v2 含二进制扩展 pydantic_core
# - apscheduler: 通过 entry points 动态加载 executors/jobstores，
#                缺少 dist-info 会报找不到插件
# - uvicorn   : protocols / loops 在运行时按名字动态 import
# - pystray   : 在 Windows 上动态选择 _win32 后端
# - PIL       : Pillow 含二进制扩展且字体/插件动态加载
for _pkg in ("pydantic", "apscheduler", "uvicorn", "pystray", "PIL"):
    _d, _b, _h = collect_all(_pkg)
    datas += _d
    binaries += _b
    hiddenimports += _h

hiddenimports += [
    "sqlalchemy.dialects.sqlite",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan.on",
    "uvicorn.logging",
    "app.scheduler",
]

a = Analysis(
    ["backend/launcher.py"],
    pathex=["backend"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Yearn",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,     # 无控制台窗口：程序在右下角托盘常驻，右键退出
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # 需要图标时改成 icon="docs/icon.ico"
    contents_directory="lib",   # 依赖目录名，默认是 _internal
)

# 目录模式（onedir）：exe、依赖、前端资源放在同一个目录下
# 相比单文件模式，启动更快（不必每次把几十 MB 解压到临时目录），
# 数据也能规整地放在目录内的 data/ 子目录，用户备份时拷走整个文件夹即可
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Yearn",
)

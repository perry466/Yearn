"""把 dist/Yearn 压成用于发布的 zip。

单独抽成脚本而不是塞在 workflow 的 `python -c "..."` 里，原因有三个：
1. 避开 YAML + shell + Python 三层引号转义，减少隐性出错
2. 出错时能输出明确的诊断信息（比如 dist/Yearn 到底存不存在）
3. 可以在本地先跑一遍验证，不必每次都推到 CI 上试

用法：
    python scripts/make_release_zip.py v1.0.0
产物：
    ./Yearn-v1.0.0-windows-x64.zip
    （zip 内顶层是单个 Yearn/ 目录，用户解压后得到一个整洁的文件夹）
"""
import os
import sys
from pathlib import Path

import shutil

# 与 COLLECT(..., name="Yearn") 保持一致
APP_NAME = "Yearn"
DIST_DIR = Path("dist")


def main(tag: str) -> int:
    app_dir = DIST_DIR / APP_NAME

    if not app_dir.is_dir():
        print(f"[make_zip] 错误：找不到目录 {app_dir}", file=sys.stderr)
        if DIST_DIR.is_dir():
            contents = sorted(p.name for p in DIST_DIR.iterdir())
            print(f"[make_zip] dist/ 下实际存在：{contents}", file=sys.stderr)
        else:
            print("[make_zip] dist/ 不存在 —— 上一步打包很可能失败了", file=sys.stderr)
        return 1

    files = sorted(p.name for p in app_dir.iterdir())
    print(f"[make_zip] {app_dir}/ 内容：{files}")

    missing = [name for name in (f"{APP_NAME}.exe", "lib") if not (app_dir / name).exists()]
    if missing:
        print(f"[make_zip] 警告：缺少预期内容 {missing}", file=sys.stderr)

    archive_base = f"{APP_NAME}-{tag}-windows-x64"
    dest = shutil.make_archive(archive_base, "zip", root_dir=DIST_DIR, base_dir=APP_NAME)
    size_mb = os.path.getsize(dest) / 1048576
    print(f"[make_zip] 打包完成：{dest}（{size_mb:.1f} MB）")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python scripts/make_release_zip.py <tag>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))

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


def _move_readme_to_root(app_dir: Path) -> None:
    """把随包说明文件放到绿色版根目录。

    坑：虽然 spec 里写的是 datas=[("packaging/使用说明.txt", ".")]，但 onedir 模式下
    COLLECT 会把 a.datas 全部塞进 contents_directory（这里是 lib/），
    所以文件实际落在 dist/Yearn/lib/使用说明.txt，而不是用户一眼能看到的地方。
    好在 PyInstaller 确实把它打进去了，这里只是把它挪回根目录。
    """
    lib_dir = app_dir / "lib"
    for name in ("使用说明.txt", "README.txt"):
        src = lib_dir / name
        if src.is_file():
            shutil.copy2(src, app_dir / name)
            print(f"[make_zip] 已归位说明文件：lib/{name} → {name}")
            return
    print("[make_zip] 提示：未找到随包说明文件（不影响运行）", file=sys.stderr)


def _locate_app_dir() -> Path | None:
    """定位实际的产物目录。

    正常情况下就是 dist/Yearn。但如果 PyInstaller 大版本升级改变了 COLLECT 的输出
    目录命名，这里做一层兜底：直接在 dist 下找含 Yearn.exe 的目录，
    避免整个发布流程因为目录名差异而中断。
    """
    primary = DIST_DIR / APP_NAME
    if primary.is_dir():
        return primary

    if DIST_DIR.is_dir():
        print(f"[make_zip] 未找到 {primary}，dist/ 下实际有："
              f"{sorted(p.name for p in DIST_DIR.iterdir())}", file=sys.stderr)
        candidates = sorted(
            p for p in DIST_DIR.iterdir()
            if p.is_dir() and (p / f"{APP_NAME}.exe").exists()
        )
        if candidates:
            print(f"[make_zip] 回退到实际产物目录：{candidates[0].name}", file=sys.stderr)
            return candidates[0]

    print("[make_zip] dist/ 不存在 —— 上一步打包很可能失败了", file=sys.stderr)
    return None


def main(tag: str) -> int:
    app_dir = _locate_app_dir()
    if app_dir is None:
        return 1

    files = sorted(p.name for p in app_dir.iterdir())
    print(f"[make_zip] {app_dir}/ 内容：{files}")

    missing = [name for name in (f"{APP_NAME}.exe", "lib") if not (app_dir / name).exists()]
    if missing:
        print(f"[make_zip] 警告：缺少预期内容 {missing}", file=sys.stderr)

    _move_readme_to_root(app_dir)

    archive_base = f"{APP_NAME}-{tag}-windows-x64"
    # base_dir 必须用实际目录名，否则兜底场景下会因找不到固定名字而抛 FileNotFoundError
    dest = shutil.make_archive(archive_base, "zip", root_dir=app_dir.parent, base_dir=app_dir.name)
    size_mb = os.path.getsize(dest) / 1048576
    print(f"[make_zip] 打包完成：{dest}（{size_mb:.1f} MB），顶层目录 {app_dir.name}/")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python scripts/make_release_zip.py <tag>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))

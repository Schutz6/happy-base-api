from pathlib import Path
import os
import shutil
import compileall


def build_package(version):
    """构建新版本"""

    root_path = os.path.join(os.path.dirname(__file__))
    root = Path(root_path)

    # 先删除根目录下的pyc文件和__pycache__文件夹
    for src_file in root.rglob("*.pyc"):
        os.remove(src_file)
    for src_file in root.rglob("__pycache__"):
        os.rmdir(src_file)

    # 编译目录
    build_dist = Path(root.parent / f"{root.name}-v{version}")

    # 删除编译目录
    if os.path.exists(build_dist):
        shutil.rmtree(build_dist)

    # 复制代码到编译目录
    shutil.copytree(root, build_dist)

    # 将项目下的py都编译成pyc文件
    compileall.compile_dir(root, force=True)

    # 遍历所有pyc文件
    for src_file in root.glob("**/*.pyc"):
        # pyc文件对应模块文件夹名称
        relative_path = src_file.relative_to(root)
        # 在目标文件夹下创建同名模块文件夹
        dist_folder = build_dist / str(relative_path.parent.parent)
        os.makedirs(dist_folder, exist_ok=True)
        # 创建同名文件
        dist_file = dist_folder / (src_file.stem.rsplit(".", 1)[0] + src_file.suffix)
        print(f"install {relative_path}")
        # 将pyc文件复制到同名文件
        shutil.copyfile(src_file, dist_file)

    # 删除不要到文件
    for src_file in build_dist.rglob("*"):
        if src_file.is_file():
            # 文件
            if src_file.name.endswith(".pyc"):
                if src_file.name in ['setup.pyc', 'config.pyc', 'test.pyc']:
                    os.remove(src_file)
            else:
                if src_file.name != "config.py":
                    os.remove(src_file)
        else:
            # 目录
            if src_file.name in ['venv', '.git', '.idea']:
                shutil.rmtree(src_file)


if __name__ == '__main__':
    build_package("1.0")

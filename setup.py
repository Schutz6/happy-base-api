from pathlib import Path
import os
import shutil
import compileall


def package(version):
    """
    编译根目录下的包括子目录里的所有py文件成pyc文件到新的文件夹下
    :return:
    """

    root_path = os.path.join(os.path.dirname(__file__))
    root = Path(root_path)

    # 先删除根目录下的pyc文件和__pycache__文件夹
    for src_file in root.rglob("*.pyc"):
        os.remove(src_file)
    for src_file in root.rglob("__pycache__"):
        os.rmdir(src_file)

    # 目标文件夹名称
    dest = Path(root.parent / f"{root.name}-v{version}")

    if os.path.exists(dest):
        shutil.rmtree(dest)

    shutil.copytree(root, dest)

    # 将项目下的py都编译成pyc文件
    compileall.compile_dir(root, force=True)

    # 遍历所有pyc文件
    for src_file in root.glob("**/*.pyc"):
        # pyc文件对应模块文件夹名称
        relative_path = src_file.relative_to(root)
        # 在目标文件夹下创建同名模块文件夹
        dest_folder = dest / str(relative_path.parent.parent)
        os.makedirs(dest_folder, exist_ok=True)
        # 创建同名文件
        dest_file = dest_folder / (src_file.stem.rsplit(".", 1)[0] + src_file.suffix)
        print(f"install {relative_path}")
        # 将pyc文件复制到同名文件
        shutil.copyfile(src_file, dest_file)

    # 清除源py文件
    for src_file in dest.rglob("*.py"):
        if src_file.name == "config.py":
            # 排除设置文件
            pass
        else:
            # 删除其他的源文件
            os.remove(src_file)


if __name__ == '__main__':
    package("1.0")

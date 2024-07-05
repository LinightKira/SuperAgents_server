from pathlib import Path


# 同步写入文件
def write_file(root_path: str, filename: str, content: bytes):
    """
    异步写入文件内容到指定路径

    Args:
        root_path: 文件根路径,如 "/data"
        filename: 文件名,如 "test.txt"
        content: 文件二进制内容

    Returns:
        完整的文件路径,如 "/data/test.txt"
    """
    # 将root_path转换为Path对象
    root_path = Path(root_path)

    # 创建目录(如果不存在)
    root_path.mkdir(parents=True, exist_ok=True)

    # 替换文件名中的双引号
    filename = filename.replace('"', '')
    # 构造完整文件路径
    full_path = root_path / filename
    full_path = full_path.as_posix()  # 将路径转换为字符串,避免特殊字符问题

    try:
        # 同步写入文件
        with open(full_path, mode="wb") as f:
            f.write(content)

        print(f"Successfully wrote file: {full_path}")
        return full_path
    except Exception as e:
        print(f"Error writing file: {e}")
        raise


def delete_file(file_path):
    """
    删除指定路径下的文件，如果文件不存在则不进行操作

    Args:
        file_path: 文件路径
    """
    try:
        path = Path(file_path)
        if path.is_file():
            path.unlink()
            print(f"Successfully deleted file: {file_path}")
        else:
            print(f"File does not exist: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")
        raise

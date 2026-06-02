from pathlib import Path


IGNORE_DIRS = [
    "node_modules",
    ".git",
    "dist",
    ".idea",
    "__pycache__",
]

def get_vue_files(project_root: str) -> list[str]:
    root = Path(project_root)

    files: list[str] = []

    for file in root.rglob("*.vue"):
        if not file.is_file():
            continue

        if any(path in IGNORE_DIRS for path in file.parts):
             continue
        files.append(str(file))

    return files


def get_js_files(project_root: str) -> list[str]:
    root = Path(project_root)
    files: list[str] = []
    for file in root.rglob("*.js"):
        if not file.is_file():
            continue

        if any(path in IGNORE_DIRS for path in file.parts):
            continue
        files.append(str(file))

    return files


def classify_files(files: list[str]) -> dict:
    """根据文件路径特征对前端项目文件进行分类

    Args:
        files (list[str]): 文件路径列表

    Returns:
        dict: 分类后的文件字典，包含 views、routers、stores、apis 四个类别
    """
    result = {
        "views": [],
        "routers": [],
        "stores": [],
        "apis": [],
    }

    for file in files:
        file = file.strip()

        if not file:
            continue

        # 分类逻辑：根据路径中的关键词判断文件类型
        if "/views/" in file or file.startswith("src/views/"):
            result["views"].append(file)
        elif "/router/" in file or file.startswith("src/router/"):
            result["routers"].append(file)
        elif "/store/" in file or file.startswith("src/store/") or "/stores/" in file or file.startswith("src/stores/"):
            result["stores"].append(file)
        elif "/api/" in file or file.startswith("src/api/") or "/apis/" in file or file.startswith("src/apis/"):
            result["apis"].append(file)

    return result



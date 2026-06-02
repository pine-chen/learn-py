from app.services.project_scanner import get_vue_files, classify_files
from app.services.project_scanner import get_js_files


def test_get_vue_project() -> None:
    vue_files = get_vue_files("/Users/chen/zyk/yunwei-client")

    print(f"\n扫描到的 Vue 文件数量: {len(vue_files)}")
    print("Vue 文件列表（前10个）:")
    for file in vue_files[:10]:
        print(f"  - {file}")

    assert isinstance(vue_files, list)

def test_get_js_project() -> None:
    js_files = get_js_files("/Users/chen/zyk/yunwei-client")

    print(f"\n扫描到的 JS 文件数量: {len(js_files)}")
    print("JS 文件列表（前10个）:")
    for file in js_files[:10]:
        print(f"  - {file}")

    assert isinstance(js_files, list)


def test_classify_files() -> None:
    """测试文件分类功能"""
    test_files = [
        "src/views/order/index.vue",
        "src/views/user/profile.vue",
        "src/router/index.js",
        "src/store/user.js",
        "src/api/order.js",
        "src/components/Button.vue",
        "src/utils/format.jsx",
    ]

    result = classify_files(test_files)

    print(f"\n分类结果:")
    print(f"  Views: {len(result['views'])} 个")
    for file in result["views"]:
        print(f"    - {file}")

    print(f"  Routers: {len(result['routers'])} 个")
    for file in result["routers"]:
        print(f"    - {file}")

    print(f"  Stores: {len(result['stores'])} 个")
    for file in result["stores"]:
        print(f"    - {file}")

    print(f"  APIs: {len(result['apis'])} 个")
    for file in result["apis"]:
        print(f"    - {file}")

    # 验证返回类型
    assert isinstance(result, dict)

    # 验证包含所有分类键
    assert "views" in result
    assert "routers" in result
    assert "stores" in result
    assert "apis" in result

    # 验证分类结果
    assert len(result["views"]) == 2
    assert "src/views/order/index.vue" in result["views"]
    assert "src/views/user/profile.vue" in result["views"]

    assert len(result["routers"]) == 1
    assert "src/router/index.js" in result["routers"]

    assert len(result["stores"]) == 1
    assert "src/store/user.js" in result["stores"]

    assert len(result["apis"]) == 1
    assert "src/api/order.js" in result["apis"]


def test_classify_files_empty() -> None:
    """测试空列表分类"""
    result = classify_files([])

    assert isinstance(result, dict)
    assert len(result["views"]) == 0
    assert len(result["routers"]) == 0
    assert len(result["stores"]) == 0
    assert len(result["apis"]) == 0


def test_classify_files_with_real_project() -> None:
    """测试真实项目的文件分类"""
    vue_files = get_vue_files("/Users/chen/zyk/yunwei-client")
    js_files = get_js_files("/Users/chen/zyk/yunwei-client")

    all_files = vue_files + js_files
    result = classify_files(all_files)

    print(f"\n真实项目分类结果:")
    print(f"  Views: {len(result['views'])} 个")
    print(f"  Routers: {len(result['routers'])} 个")
    print(f"  Stores: {len(result['stores'])} 个")
    print(f"  APIs: {len(result['apis'])} 个")

    assert isinstance(result, dict)

    # 验证至少有一些文件被分类
    total_classified = (
            len(result["views"]) +
            len(result["routers"]) +
            len(result["stores"]) +
            len(result["apis"])
    )
    assert total_classified > 0
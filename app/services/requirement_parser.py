from app.schemas.requirement import RequirementSpec

def parse_requirement(text: str) -> RequirementSpec:
    lines = text.split("\n")

    result = {
        "title": "",
        "background": "",
        "requirements": [],
        "acceptance": [],
    }

    # 当前正在解析的章节类型，用于判断文本行应该归类到哪个部分
    current_section = None

    # 逐行解析文本，根据章节标识和内容将文本归类到相应字段
    for line in lines:
        line = line.strip()

        # 跳过空行，不进行处理
        if not line:
            continue

        # 识别章节标识并更新当前解析的章节类型
        if line.startswith("背景"):
            current_section = "background"
            continue
        if line.startswith("需求"):
            current_section = "requirements"
            continue
        if line.startswith("验收"):
            current_section = "acceptance"
            continue

        # 如果标题尚未设置，则将当前行作为标题
        if result["title"] == "":
            result["title"] = line
            continue

        # 根据当前章节类型，将文本行添加到对应的字段中
        if current_section == "background":
            result["background"] += line
        elif current_section == "requirements":
            result["requirements"].append(line)
        elif current_section == "acceptance":
            result["acceptance"].append(line)

    return RequirementSpec(**result)
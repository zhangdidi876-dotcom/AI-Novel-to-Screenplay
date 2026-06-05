"""剧本 YAML 序列化工具"""

from datetime import datetime

import yaml


def screenplay_to_yaml(screenplay: dict) -> str:
    """将 screenplay dict 转为符合 Schema 的 YAML 字符串"""
    data = _clean(screenplay)
    return yaml.dump(
        {"screenplay": data},
        allow_unicode=True,
        default_flow_style=False,
        indent=2,
        sort_keys=False,
        width=120,
    )


def yaml_to_screenplay(yaml_str: str) -> dict:
    """从 YAML 字符串解析 screenplay dict"""
    data = yaml.safe_load(yaml_str)
    return data.get("screenplay", data)


def _clean(data: dict) -> dict:
    """补全缺失字段，确保输出完整"""
    meta = data.get("meta", {})
    meta.setdefault("title", "")
    meta.setdefault("original_novel", "")
    meta.setdefault("original_author", "")
    meta.setdefault("adapted_by", "AI 辅助改编")
    meta.setdefault("version", "1.0.0")
    if not meta.get("created_at"):
        meta["created_at"] = datetime.now().isoformat()
    meta.setdefault("description", "")
    meta.setdefault("source_chapters", [])
    meta.setdefault("notes", "")

    for c in data.get("characters", []):
        c.setdefault("aliases", [])
        c.setdefault("role", "supporting")
        c.setdefault("age", "")
        c.setdefault("gender", "")
        c.setdefault("occupation", "")
        c.setdefault("traits", [])
        c.setdefault("relationships", [])
        c.setdefault("arc_summary", "")
        c.setdefault("notes", "")

    for s in data.get("scenes", []):
        sl = s.setdefault("slug_line", {})
        sl.setdefault("location", "")
        sl.setdefault("time", "day")
        sl.setdefault("set_details", "")
        s.setdefault("characters_present", [])
        s.setdefault("summary", "")
        s.setdefault("transition", "")
        s.setdefault("notes", "")
        for elem in s.get("content", []):
            elem.setdefault("element_type", "action")
            elem.setdefault("text", "")
            elem.setdefault("character_id", "")
            elem.setdefault("parenthetical", "")

    return data

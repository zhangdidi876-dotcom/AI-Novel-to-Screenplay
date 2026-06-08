"""三合一转换服务 — 一次 API 调用完成角色+场景+剧本"""

from .ai_client import AIClient, default_client

COMBINED_PROMPT = """你是一位专业的编剧。请根据以上小说完成以下三项任务，按顺序输出 JSON。

## 任务1: 提取角色
{{
  "characters": [
    {{
      "id": "char_001", "name": "姓名", "aliases": [], "role": "protagonist",
      "age": "", "gender": "", "occupation": "", "description": "", "traits": [],
      "relationships": [{{"target": "char_002", "relation": "师徒"}}],
      "arc_summary": "", "notes": ""
    }}
  ]
}}
role可选: protagonist/antagonist/supporting/minor/extra

## 任务2: 拆分场景
slug_line格式: "INT./EXT. 地点 - 时间"
{{
  "scenes": [
    {{
      "id": "scene_001", "scene_number": 1,
      "slug_line": "INT. 酒楼 - 大厅 - 日",
      "characters_present": ["char_001"], "summary": "概要",
      "content": [], "transition": "",
      "source_reference": {{"chapter": 1, "paragraphs": "1-5"}}, "notes": ""
    }}
  ]
}}

## 任务3: 生成剧本内容
元素: action(动作描写)/dialogue(对白,需character_id)/parenthetical(仅表演指示: 冷笑/低声/愤怒/耳语)/transition(转场)/shot(镜头)
每个场景content至少3-6个元素
{{
  "script_scenes": [
    {{
      "id": "scene_001",
      "content": [
        {{"element_type": "action", "text": "...", "character_id": "", "parenthetical": ""}},
        {{"element_type": "dialogue", "text": "...", "character_id": "char_001", "parenthetical": "低声"}}
      ]
    }}
  ]
}}

规则: 短信/语音内容为发送者新建角色(如char_007 "陌生号码"), 读信人反应写action
只输出JSON, 包含characters、scenes、script_scenes三个顶层字段
"""


async def convert_combined(
    chapters: str,
    client: AIClient | None = None,
) -> dict:
    """一次 API 调用完成全部转换"""
    if client is None:
        client = default_client

    response = await client.chat(
        messages=[
            {"role": "user", "content": f"小说原文：\n\n{chapters}"},
            {"role": "user", "content": COMBINED_PROMPT},
        ],
        temperature=0.5,
        max_tokens=65536,
        json_mode=True,
    )
    data = client.parse_json(response)
    # 合并 script_scenes 内容到 scenes
    script_map = {}
    for ss in data.get("script_scenes", []):
        script_map[ss.get("id", "")] = ss.get("content", [])
    for scene in data.get("scenes", []):
        if scene.get("id") in script_map:
            scene["content"] = script_map[scene["id"]]
    return {
        "characters": data.get("characters", []),
        "scenes": data.get("scenes", []),
    }

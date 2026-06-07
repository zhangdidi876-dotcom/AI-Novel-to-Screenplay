"""场景拆分服务 — 将小说章节拆分为剧本场景"""

import json

from .ai_client import AIClient, default_client

SCENE_PROMPT = """你是一位专业的剧本分析师。请将以下小说章节拆分为剧本场景，输出 JSON。

## 要求
1. 按叙事顺序拆分场景，每个场景是一个相对完整的情节单元
2. 每个场景需识别：地点、时间、出场角色、1-2句概要
3. 标注每个场景改编自原文的哪些段落（paragraphs字段填大致段落序号范围）
4. content 留空数组，后续步骤会填充

## 时间枚举值
day(白天) / night(夜晚) / dawn(清晨) / dusk(黄昏) / morning(上午) / afternoon(下午) / evening(傍晚) / continuous(连续) / later(稍后) / same(同时)

## 已识别的角色
{characters}

## 输出格式
{{
  "scenes": [
    {{
      "id": "scene_001",
      "scene_number": 1,
      "slug_line": "地点描述 - 时间，场景补充",
      "characters_present": ["char_001"],
      "summary": "本场1-2句概要",
      "content": [],
      "transition": "",
      "source_reference": {{"chapter": 1, "paragraphs": "1-5"}},
      "notes": ""
    }}
  ]
}}

## 关键规则
- slug_line 必须是单一字符串，格式: "地点 - 时间"，如 "林家宅院 - 前厅 - 日"
- 如有场景细节(set_details)直接追加，如 "城西仓库 - 夜，窗外大雨滂沱"
- source_reference.paragraphs 用 "1-5" 格式表示第1到5段
- id 格式为 scene_001、scene_002...按顺序编号
- characters_present 引用已识别角色的 id
- 只输出 JSON，不要额外文字

## 小说章节
{chapters}
"""


async def extract_scenes(
    chapters: str,
    characters: list[dict],
    client: AIClient | None = None,
) -> list[dict]:
    """从章节文本中拆分场景"""
    if client is None:
        client = default_client

    # 简化角色信息传给 AI
    chars_summary = [
        {"id": c.get("id"), "name": c.get("name"), "role": c.get("role")}
        for c in characters
    ]
    prompt = SCENE_PROMPT.format(
        characters=json.dumps(chars_summary, ensure_ascii=False, indent=2),
        chapters=chapters,
    )
    response = await client.chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=16384,
        json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("scenes", [])

"""场景拆分服务"""

import json
from .ai_client import AIClient, default_client

SCENE_PROMPT = """将以上小说拆分为剧本场景，输出 JSON。

输出格式示例：
{{
  "scenes": [
    {{
      "id": "scene_001",
      "scene_number": 1,
      "slug_line": "INT. 酒楼 - 大厅 - 日",
      "characters_present": ["char_001"],
      "summary": "1-2句概要",
      "content": [],
      "transition": "",
      "source_reference": {{"chapter": 1, "paragraphs": "1-5"}},
      "notes": ""
    }}
  ]
}}

slug_line 必须: INT.(内景) / EXT.(外景) + 地点 - 时间
paragraphs 格式: "1-5" 表示第1至第5段
只输出 JSON

已识别角色:
{characters}"""


async def extract_scenes(
    chapters: str,
    characters: list[dict],
    client: AIClient | None = None,
) -> list[dict]:
    if client is None:
        client = default_client
    chars_summary = [
        {"id": c.get("id"), "name": c.get("name"), "role": c.get("role")}
        for c in characters
    ]
    prompt = SCENE_PROMPT.format(
        characters=json.dumps(chars_summary, ensure_ascii=False, indent=2),
    )
    response = await client.chat(
        messages=[
            {"role": "user", "content": f"小说原文：\n\n{chapters}"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=16384,
        json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("scenes", [])

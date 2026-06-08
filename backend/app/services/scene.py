"""场景拆分服务 — 将小说章节拆分为剧本场景"""

import json
from .ai_client import AIClient, default_client

SCENE_PROMPT = """将以上小说拆分为剧本场景，输出 JSON。

场景字段: id(scene_001格式), scene_number, slug_line("INT./EXT. 地点 - 时间"), characters_present[角色id], summary, content[](留空), transition, source_reference{chapter, paragraphs("1-5"格式)}, notes。
slug_line 必须标 INT.(内景) 或 EXT.(外景)。
只输出JSON。

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
        max_tokens=8192,
        json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("scenes", [])

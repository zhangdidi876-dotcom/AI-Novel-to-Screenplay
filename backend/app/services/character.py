"""角色提取服务"""

from .ai_client import AIClient, default_client

CHARACTER_PROMPT = """提取以上小说的所有角色，输出 JSON。

输出格式示例：
{
  "characters": [
    {
      "id": "char_001",
      "name": "角色姓名",
      "aliases": [],
      "role": "protagonist",
      "age": "",
      "gender": "",
      "occupation": "",
      "description": "",
      "traits": [],
      "relationships": [{"target": "char_002", "relation": "师徒"}],
      "arc_summary": "",
      "notes": ""
    }
  ]
}

role 取值: protagonist / antagonist / supporting / minor / extra
id 格式: char_001, char_002...按出场顺序
未知字段用 "" 或 []
只输出 JSON，不要其他文字
"""


async def extract_characters(
    chapters: str,
    client: AIClient | None = None,
) -> list[dict]:
    if client is None:
        client = default_client
    response = await client.chat(
        messages=[
            {"role": "user", "content": f"小说原文：\n\n{chapters}"},
            {"role": "user", "content": CHARACTER_PROMPT},
        ],
        temperature=0.3,
        max_tokens=8192,
        json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("characters", [])

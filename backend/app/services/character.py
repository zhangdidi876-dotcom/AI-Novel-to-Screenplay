"""角色提取服务 — 从小说章节中识别所有角色"""

from .ai_client import AIClient, default_client

CHARACTER_PROMPT = """提取以上小说的所有角色，输出 JSON。

角色字段: id(char_001格式), name, aliases[], role(protagonist/antagonist/supporting/minor/extra), age, gender, occupation, description, traits[], relationships[{target,relation}], arc_summary, notes。
未知字段用""或[]。只输出JSON。"""


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
        max_tokens=4096,
        json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("characters", [])

"""角色提取服务"""
from .ai_client import AIClient, default_client
from .prompts import CHARACTER_PROMPT


async def extract_characters(chapters: str, client: AIClient | None = None) -> list[dict]:
    if client is None:
        client = default_client
    response = await client.chat(
        messages=[
            {"role": "user", "content": f"小说原文：\n\n{chapters}"},
            {"role": "user", "content": CHARACTER_PROMPT},
        ],
        temperature=0.3, max_tokens=8192, json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("characters", [])

"""场景拆分服务"""
import json
from .ai_client import AIClient, default_client
from .prompts import SCENE_PROMPT


async def extract_scenes(chapters: str, characters: list[dict], client: AIClient | None = None) -> list[dict]:
    if client is None:
        client = default_client
    chars_summary = [{"id": c.get("id"), "name": c.get("name"), "role": c.get("role")} for c in characters]
    prompt = SCENE_PROMPT.format(characters=json.dumps(chars_summary, ensure_ascii=False, indent=2))
    response = await client.chat(
        messages=[
            {"role": "user", "content": f"小说原文：\n\n{chapters}"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3, max_tokens=16384, json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("scenes", [])

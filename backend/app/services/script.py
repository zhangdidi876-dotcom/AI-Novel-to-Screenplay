"""剧本生成服务"""
import json
from .ai_client import AIClient, default_client
from .prompts import SCRIPT_PROMPT


async def generate_script(chapters: str, characters: list[dict], scenes: list[dict], client: AIClient | None = None) -> list[dict]:
    if client is None:
        client = default_client
    chars_json = json.dumps(characters, ensure_ascii=False, indent=2)
    scenes_outline = [{k: v for k, v in s.items() if k != "content"} for s in scenes]
    scenes_json = json.dumps(scenes_outline, ensure_ascii=False, indent=2)
    prompt = SCRIPT_PROMPT.format(characters=chars_json, scenes=scenes_json)
    response = await client.chat(
        messages=[
            {"role": "user", "content": f"小说原文：\n\n{chapters}"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7, max_tokens=32768, json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("scenes", [])

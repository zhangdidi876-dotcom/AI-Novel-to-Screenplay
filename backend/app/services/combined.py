"""三合一转换服务"""
from .ai_client import AIClient, default_client
from .prompts import COMBINED_PROMPT


async def convert_combined(chapters: str, client: AIClient | None = None) -> dict:
    if client is None:
        client = default_client
    response = await client.chat(
        messages=[
            {"role": "user", "content": f"小说原文：\n\n{chapters}"},
            {"role": "user", "content": COMBINED_PROMPT},
        ],
        temperature=0.5, max_tokens=65536, json_mode=True,
    )
    data = client.parse_json(response)
    script_map = {}
    for ss in data.get("script_scenes", []):
        script_map[ss.get("id", "")] = ss.get("content", [])
    for scene in data.get("scenes", []):
        if scene.get("id") in script_map:
            scene["content"] = script_map[scene["id"]]
    return {"characters": data.get("characters", []), "scenes": data.get("scenes", [])}

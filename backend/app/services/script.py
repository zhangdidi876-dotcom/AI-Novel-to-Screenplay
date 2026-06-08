"""剧本生成服务 — 为每个场景生成对白和动作描写"""

import json
from .ai_client import AIClient, default_client

SCRIPT_PROMPT = """为以上场景生成剧本内容，输出 JSON。

元素类型: action(动作描写,可见可拍), dialogue(对白,必须填character_id), parenthetical(仅限表演指示: 冷笑/低声/愤怒/耳语等, 禁止读短信/站起来等动作描述), transition(转场), shot(镜头)。
短信/语音内容: 为发送者新建临时角色, 内容归dialogue, 读信人反应写action。
每个场景至少3-6个content元素。

已识别角色: {characters}
场景大纲: {scenes}

输出格式: {{"scenes": [{{"id": "scene_001", "content": [{{"element_type": "action", "text": "...", "character_id": "", "parenthetical": ""}}]}}]}}
只输出JSON。"""


async def generate_script(
    chapters: str,
    characters: list[dict],
    scenes: list[dict],
    client: AIClient | None = None,
) -> list[dict]:
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
        temperature=0.7,
        max_tokens=16384,
        json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("scenes", [])

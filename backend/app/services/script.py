"""剧本生成服务"""

import json
from .ai_client import AIClient, default_client

SCRIPT_PROMPT = """为以上场景生成完整剧本内容，输出 JSON。

输出格式示例：
{{
  "scenes": [
    {{
      "id": "scene_001",
      "content": [
        {{"element_type": "action", "text": "张远推门而入。", "character_id": "", "parenthetical": ""}},
        {{"element_type": "dialogue", "text": "你好。", "character_id": "char_001", "parenthetical": "低声"}},
        {{"element_type": "parenthetical", "text": "冷笑", "character_id": "", "parenthetical": ""}},
        {{"element_type": "transition", "text": "CUT TO:", "character_id": "", "parenthetical": ""}}
      ]
    }}
  ]
}}

规则:
- action: 动作描写, 只写可见可拍的内容
- dialogue: 对白, 必须填 character_id
- parenthetical: 仅限表演指示(冷笑/低声/愤怒/耳语), 禁止读短信/站起来
- transition: 转场(CUT TO:/FADE OUT:)
- element_type 只能是 action/dialogue/parenthetical/transition/shot
- 读短信/语音: 为发送者新建临时角色如 char_007 name:"陌生号码", 内容归dialogue
- 保留原文关键对白, 每个场景至少3-6个元素

已识别角色: {characters}
场景大纲: {scenes}
只输出 JSON"""


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
        max_tokens=32768,
        json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("scenes", [])

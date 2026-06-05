"""剧本生成服务 — 为每个场景生成对白和动作描写"""

import json

from .ai_client import AIClient, default_client

SCRIPT_PROMPT = """你是一位专业的编剧。请根据小说原文和场景大纲，为每个场景生成完整的剧本内容，输出 JSON。

## 剧本元素类型
- action: 动作/场景描写，只写能拍出来的内容，避免心理描写
- dialogue: 角色对白，必须指定 character_id
- parenthetical: 对白中的情绪/动作指示，如（冷笑）（低声）
- transition: 转场效果，如 CUT TO:、FADE OUT.
- shot: 特殊镜头指示

## 创作要求
1. 保留原文关键对白和情节节点
2. 对白符合角色性格特征
3. 动作描写客观、可视化
4. 每个场景至少 3-6 个 content 元素
5. 对白数量合理，不要所有行都是对话

## 已识别角色
{characters}

## 场景大纲
{scenes}

## 输出格式
{{
  "scenes": [
    {{
      "id": "scene_001",
      "content": [
        {{"element_type": "action", "text": "场景描写内容", "character_id": "", "parenthetical": ""}},
        {{"element_type": "dialogue", "text": "对白内容", "character_id": "char_001", "parenthetical": ""}},
        {{"element_type": "parenthetical", "text": "(低声)", "character_id": "", "parenthetical": ""}}
      ]
    }}
  ]
}}

## 注意
- element_type 只能是 action/dialogue/parenthetical/transition/shot
- dialogue 必须指定 character_id
- 只输出 JSON，不要额外文字

## 小说原文
{chapters}
"""


async def generate_script(
    chapters: str,
    characters: list[dict],
    scenes: list[dict],
    client: AIClient | None = None,
) -> list[dict]:
    """为每个场景生成完整剧本内容"""
    if client is None:
        client = default_client

    chars_json = json.dumps(characters, ensure_ascii=False, indent=2)
    # 移出已生成的 content，减少冗余
    scenes_outline = [{k: v for k, v in s.items() if k != "content"} for s in scenes]
    scenes_json = json.dumps(scenes_outline, ensure_ascii=False, indent=2)

    prompt = SCRIPT_PROMPT.format(
        characters=chars_json, scenes=scenes_json, chapters=chapters
    )
    response = await client.chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=32768,
        json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("scenes", [])

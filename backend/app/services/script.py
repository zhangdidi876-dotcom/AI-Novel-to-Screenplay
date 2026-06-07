"""剧本生成服务 — 为每个场景生成对白和动作描写"""

import json

from .ai_client import AIClient, default_client

SCRIPT_PROMPT = """你是一位专业的编剧。请根据上面提供的小说原文、角色列表和场景大纲，为每个场景生成完整的剧本内容，输出 JSON。

## 剧本元素类型
- action: 动作/场景描写，只写能拍出来的内容，避免心理描写
- dialogue: 角色对白，必须指定 character_id
- parenthetical: ⚠️ 仅限表演指示！（冷笑/低声/愤怒/颤抖/耳语/激动/哽咽）
- transition: 转场效果，如 CUT TO:、FADE OUT.
- shot: 特殊镜头指示

## ⚠️ parenthetical 使用铁律
- ✅ 允许: (冷笑) (低声) (愤怒) (颤抖) (耳语) (激动) (哽咽) (叹气)
- ❌ 禁止: (读短信) (听语音) (看向窗外) (站起来) — 这些是动作，必须写成 action

## ⚠️ 短信/语音/信件内容的归属
当原文中角色读取短信、语音、信件时：
- 为发信人新建临时角色，如 char_007, name: "陌生号码"
- 内容归为该临时角色的 dialogue
- 读信人的反应写成 action

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

## 创作要求
1. 保留原文关键对白和情节节点
2. 对白符合角色性格特征
3. 动作描写客观、可视化
4. 每个场景至少 3-6 个 content 元素
5. 读短信/语音/信件时，将内容归属给发送者角色而非读者

## 注意
- element_type 只能是 action/dialogue/parenthetical/transition/shot
- dialogue 必须指定 character_id
- 只输出 JSON，不要额外文字
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
    scenes_outline = [{k: v for k, v in s.items() if k != "content"} for s in scenes]
    scenes_json = json.dumps(scenes_outline, ensure_ascii=False, indent=2)

    prompt = SCRIPT_PROMPT.format(
        characters=chars_json, scenes=scenes_json,
    )
    # 章节文本放第一条消息 → 与前两步共享缓存前缀
    response = await client.chat(
        messages=[
            {"role": "user", "content": f"以下是要改编的小说原文：\n\n{chapters}"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=65536,
        json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("scenes", [])

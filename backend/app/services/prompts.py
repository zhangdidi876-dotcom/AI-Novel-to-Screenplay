"""AI Prompt 模板 — 集中管理所有提示词，便于调优和版本管理"""

# ── 角色提取 ─────────────────────────────────────────────

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

# ── 场景拆分 ─────────────────────────────────────────────

SCENE_PROMPT = """将以上小说拆分为剧本场景，输出 JSON。

输出格式示例：
{{
  "scenes": [
    {{
      "id": "scene_001",
      "scene_number": 1,
      "slug_line": "INT. 酒楼 - 大厅 - 日",
      "characters_present": ["char_001"],
      "summary": "1-2句概要",
      "content": [],
      "transition": "",
      "source_reference": {{"chapter": 1, "paragraphs": "1-5"}},
      "notes": ""
    }}
  ]
}}

slug_line 必须: INT.(内景) / EXT.(外景) + 地点 - 时间
paragraphs 格式: "1-5" 表示第1至第5段
只输出 JSON

已识别角色:
{characters}"""

# ── 剧本生成 ─────────────────────────────────────────────

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

# ── 三合一转换 ───────────────────────────────────────────

COMBINED_PROMPT = """你是一位专业的编剧。请根据以上小说完成以下三项任务，按顺序输出 JSON。

## 任务1: 提取角色
{{
  "characters": [
    {{
      "id": "char_001", "name": "姓名", "aliases": [], "role": "protagonist",
      "age": "", "gender": "", "occupation": "", "description": "", "traits": [],
      "relationships": [{{"target": "char_002", "relation": "师徒"}}],
      "arc_summary": "", "notes": ""
    }}
  ]
}}
role可选: protagonist/antagonist/supporting/minor/extra

## 任务2: 拆分场景
slug_line格式: "INT./EXT. 地点 - 时间"
{{
  "scenes": [
    {{
      "id": "scene_001", "scene_number": 1,
      "slug_line": "INT. 酒楼 - 大厅 - 日",
      "characters_present": ["char_001"], "summary": "概要",
      "content": [], "transition": "",
      "source_reference": {{"chapter": 1, "paragraphs": "1-5"}}, "notes": ""
    }}
  ]
}}

## 任务3: 生成剧本内容
元素: action(动作描写)/dialogue(对白,需character_id)/parenthetical(仅表演指示: 冷笑/低声/愤怒/耳语)/transition(转场)/shot(镜头)
每个场景content至少3-6个元素
{{
  "script_scenes": [
    {{
      "id": "scene_001",
      "content": [
        {{"element_type": "action", "text": "...", "character_id": "", "parenthetical": ""}},
        {{"element_type": "dialogue", "text": "...", "character_id": "char_001", "parenthetical": "低声"}}
      ]
    }}
  ]
}}

规则: 短信/语音内容为发送者新建角色(如char_007 "陌生号码"), 读信人反应写action
只输出JSON, 包含characters、scenes、script_scenes三个顶层字段
"""

# ── AI 章节检测（用于智能分段）─────────────────────────

CHAPTER_DETECT_PROMPT = """分析以下小说文本，找出所有章节边界位置。

返回 JSON 格式：
{{"breaks": [100, 520, 980]}}

其中 breaks 数组是每章开始位置的字符索引（从0开始计数）。

常见章节标记：
- "第X章"、"第X回"、"Chapter X"
- 大段空行（3行以上）
- 序号标题（一、/ 1. / (1)）
- 明显的场景切换

如果没有明显章节边界，返回 breaks: []。

文本：
{sample}
"""

"""角色提取服务 — 从小说章节中识别所有角色"""

from .ai_client import AIClient, default_client

CHARACTER_PROMPT = """你是一位专业的剧本分析师。请从以下小说章节中提取所有角色信息，输出 JSON。

## 要求
1. 识别所有有名有姓或有重要戏份的角色
2. 为每个角色推断：姓名、别名、角色定位、大致年龄、性别、职业、外貌性格描述、性格特征列表
3. 分析角色之间的关系（如亲友、敌对、师徒等）
4. 如果原文没有明确信息，用空字符串或空数组，不要编造

## 角色定位说明
- protagonist: 主角
- antagonist: 反派/对立面
- supporting: 重要配角
- minor: 次要角色
- extra: 龙套/背景角色

## 输出格式
{
  "characters": [
    {
      "id": "char_001",
      "name": "角色姓名",
      "aliases": ["别名1", "别名2"],
      "role": "protagonist",
      "age": "约25岁",
      "gender": "男",
      "occupation": "剑客",
      "description": "外貌与性格的简洁描述",
      "traits": ["勇敢", "冲动"],
      "relationships": [{"target": "char_002", "relation": "挚友"}],
      "arc_summary": "",
      "notes": "补充说明"
    }
  ]
}

## 注意
- id 格式为 char_001、char_002...按出场顺序编号
- role 只能从 protagonist/antagonist/supporting/minor/extra 中选
- relationships 中的 target 必须指向其他角色的 id
- 只输出 JSON，不要额外文字

## 小说章节
{chapters}
"""


async def extract_characters(
    chapters: str,
    client: AIClient | None = None,
) -> list[dict]:
    """从章节文本中提取角色列表"""
    if client is None:
        client = default_client

    prompt = CHARACTER_PROMPT.format(chapters=chapters)
    response = await client.chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=16384,
        json_mode=True,
    )
    data = client.parse_json(response)
    return data.get("characters", [])

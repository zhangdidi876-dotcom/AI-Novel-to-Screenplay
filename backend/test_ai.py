"""测试：用真实章节文本验证"""
import asyncio, sys, os
sys.path.insert(0, ".")

from app.services.ai_client import AIClient

# 你之前输入的章节文本，直接粘贴到下面三引号中间
CHAPTERS = """
第1章 初入江湖

张三是一个年轻的剑客，他从小在华山学艺。这一天，师父把他叫到跟前。

"三儿，你下山去吧。"师父叹了口气，"江湖险恶，但你必须去。"

张三跪地磕了三个响头，背上长剑，独自一人走下山去。山脚下的小镇热闹非凡，他第一次见到这么多人。

在一家酒馆里，他遇到了一个神秘的女子。女子自称李四娘，是峨眉派的弟子。李四娘穿着一身青色长裙，面容清秀，但眉宇间带着一股英气。

"小兄弟，一个人？"李四娘端着酒杯走过来，在张三对面坐下。

张三点点头，不知如何回答。他从小在山上长大，很少和女子说话。

"看你背着剑，是华山派的？"李四娘打量着他。

第2章 狭路相逢

离开小镇后，张三在树林里遭遇了一群山贼。为首的是一个独眼大汉，名叫王五。

"此路是我开，此树是我栽！"王五挥舞着大刀，身后的十几个喽啰跟着起哄。

张三握紧剑柄，心跳加速。这是他第一次真正面对敌人。

"小子，把值钱的东西都交出来，饶你不死！"

就在这时，一道青色身影从树上落下。李四娘不知何时已经站在了张三身前。

"这么多人欺负一个少年，也不害臊？"李四娘冷笑一声，手中已经多了一把短剑。

第3章 不打不相识

王五看到李四娘，眼中闪过一丝忌惮。但他仗着人多，还是挥刀冲了上来。

张三和李四娘并肩作战。华山的剑法讲究灵动飘逸，峨眉的短剑则是快准狠。

不到半盏茶的时间，十几个山贼倒了一地。王五的一条胳膊被李四娘卸了关节，疼得哇哇大叫。

"姑奶奶饶命！姑奶奶饶命！"

"滚！"李四娘一脚把王五踹开。

张三看着李四娘，心中涌起一股敬佩。这个看似柔弱的女子，武功竟然如此高强。
"""


async def main():
    client = AIClient()
    print(f"章节长度: {len(CHAPTERS)} 字符")
    print(f"模型: {client.model_name}")
    print(f"API: {client.base_url}")
    print("发送角色提取请求...")
    print("-" * 50)

    # 使用和 character.py 中一样的 prompt
    from app.services.character import CHARACTER_PROMPT
    prompt = CHARACTER_PROMPT.format(chapters=CHAPTERS)

    response = await client.chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=16384,
        json_mode=True,
    )

    # 保存完整返回
    os.makedirs("test_output", exist_ok=True)
    with open("test_output/ai_response.txt", "w", encoding="utf-8") as f:
        f.write(response)

    print(f"返回长度: {len(response)} 字符")
    print(f"完整返回已保存到: test_output/ai_response.txt")
    print()
    print("=== 前 300 字符 ===")
    print(repr(response[:300]))
    print()
    print("=== 后 200 字符 ===")
    print(repr(response[-200:] if len(response) > 200 else response))
    print()
    print("=== 以 { 开头?", response.strip().startswith("{"))

    # 尝试解析
    try:
        data = client.parse_json(response)
        print(f"=== 解析成功! 角色数: {len(data.get('characters', []))} ===")
    except Exception as e:
        print(f"=== 解析失败 ===")
        print(f"错误: {e}")

asyncio.run(main())

# 剧本 YAML Schema 设计文档

## 概述

本文档定义了 AI 辅助剧本创作工具所使用的 YAML 剧本格式。该 Schema 旨在将小说文本转换为结构化剧本，既保留剧本行业的专业规范，又兼顾 YAML 格式的可读性与可编辑性。

## 设计原则

### 1. 行业标准对齐

Schema 遵循影视行业剧本格式惯例：
- **场景标头**（Slug Line）：包含场号、地点、时间（日/夜）
- **动作描写**（Action）：客观描述可见的动作和场景
- **对白**（Dialogue）：角色名称 + 括号备注（parenthetical）+ 台词
- **转场**（Transition）：CUT TO / FADE IN / FADE OUT 等

### 2. 结构化与可读性的平衡

选择 YAML 而非 JSON 的原因：
- **可读性优先**：YAML 的缩进层次结构更接近剧本的自然格式，非技术作者也能直观阅读和编辑
- **支持注释**：YAML 原生支持 `#` 注释，方便作者添加修改备注
- **多行字符串**：YAML 的 `|` / `>` 语法天然适合处理长篇对白和动作描写
- **无需转义**：相比 JSON，对白中的引号不需要大量转义

### 3. 扩展性

- 每个实体均设有 `notes` 字段，承载 AI 无法完美处理的边缘信息
- `metadata` 块预留自定义字段，方便后续扩展
- `extras` 字段用于存储 AI 分析中间产物（置信度、原文依据等）

### 4. AI 友好的结构

- 每个实体有唯一 `id`，便于跨引用（角色↔场景）
- 使用枚举值约束 `type` 字段（action / dialogue / transition），降低 AI 输出歧义
- `source_reference` 字段记录 AI 判断依据（原文段落），方便作者回溯验证

---

## Schema 定义

### 顶层结构

```yaml
screenplay:
  meta: Meta          # 剧本元信息
  characters:         # 角色列表
    - Character
  scenes:             # 场景列表
    - Scene
```

### Meta — 剧本元信息

```yaml
meta:
  title: string                # 剧本标题
  original_novel: string       # 原著名称
  original_author: string      # 原著作者
  adapted_by: string           # 改编者（可选）
  version: string              # 版本号，如 "1.0.0"
  created_at: string           # 创建时间，ISO 8601 格式
  description: string          # 剧本简介（可选）
  source_chapters:             # 改编来源章节
    - number: 1
      title: "第一章标题"
  notes: string                # 备注（可选）
```

**设计考量：**
- `original_novel` 和 `original_author` 保留版权溯源
- `source_chapters` 记录改编范围，支持部分章节改编的场景
- `version` 支持迭代打磨的版本管理
- `description` 提供快速了解剧情的入口

### Character — 角色

```yaml
characters:
  - id: string                 # 唯一标识，如 "char_001"
    name: string               # 角色姓名
    aliases:                   # 别名/称呼列表
      - string
    role: string               # 角色定位：protagonist / antagonist / supporting / minor / extra
    age: string                # 年龄（可为范围或描述，如"25"、"三十岁左右"）
    gender: string             # 性别
    occupation: string         # 职业（可选）
    description: string        # 外貌与性格描述
    traits:                    # 性格特征
      - string
    relationships:             # 与其他角色的关系
      - target: string         # 目标角色 id
        relation: string       # 关系描述，如 "挚友"、"死敌"、"师徒"
    arc_summary: string        # 角色弧线简述（可选）
    notes: string              # 补充说明（可选）
```

**设计考量：**
- `id` 使用 `char_001` 格式，人可读且方便在场景中引用
- `role` 枚举值覆盖主要角色类型，帮助 AI 正确归类
- `relationships` 使用 `target` 引用其他角色 id，而非嵌套对象，避免循环引用，方便增量编辑
- `aliases` 解决小说中同一人物有多种称呼的问题（如"林黛玉"又称"颦儿"、"林妹妹"）
- `arc_summary` 面向长篇小说，帮助把握角色发展脉络
- `age` 使用字符串而非数字，因为小说中年龄常以模糊描述出现

### Scene — 场景

```yaml
scenes:
  - id: string                 # 唯一标识，如 "scene_001"
    scene_number: integer      # 场号，从 1 开始
    slug_line:                 # 场景标头
      location: string         # 地点，如 "林家宅院 — 前厅"
      time: string             # 时间：day / night / dawn / dusk / morning / afternoon / evening / continuous / later / same
      set_details: string      # 场景补充描述（可选）
    characters_present:        # 出场角色 id 列表
      - string
    summary: string            # 本场概要（1-2 句）
    content:                   # 本场内容，按顺序排列
      - element_type: action   # action | dialogue | parenthetical | transition | shot
        text: string           # 内容文本
        character_id: string   # 对白角色 id（仅 dialogue 类型）
        parenthetical: string  # 对白括号备注（仅 dialogue 类型，可选）
    transition: string         # 转场效果，如 "CUT TO:"（可选）
    source_reference:          # AI 提取依据（可选）
      chapter: integer         # 原文章节号
      paragraphs:              # 原文段落范围
        - integer
    notes: string              # 备注（可选）
```

**设计考量：**

- **`content` 使用类型数组而非扁平文本：**
  - 结构化使得前端可以区分渲染动作描写、对白、转场
  - 方便统计对白占比、动作描写占比等分析功能
  - AI 生成时按类型输出，准确性高于自由文本

- **`element_type` 枚举说明：**

  | 类型 | 用途 | 示例 |
  |------|------|------|
  | `action` | 动作/场景描写 | "林黛玉推门而入，手中捧着一卷诗稿。" |
  | `dialogue` | 角色对白 | "你可知道，这诗稿写了多久？" |
  | `parenthetical` | 对白中的情绪/动作指示 | (冷笑) |
  | `transition` | 转场 | "FADE OUT." |
  | `shot` | 特殊镜头指示 | "CLOSE UP — 手中的诗稿" |

- **`slug_line.time` 使用标准术语：**
  - `continuous` — 连续时间（同一场景跨时间）
  - `later` — 稍后
  - `same` — 同一时间（并行蒙太奇）

- **`source_reference` 不参与渲染，仅供作者验证 AI 判断是否正确。**

### 完整示例

```yaml
screenplay:
  meta:
    title: "红楼梦·黛玉初入荣国府"
    original_novel: "红楼梦"
    original_author: "曹雪芹"
    adapted_by: "AI 辅助改编"
    version: "1.0.0"
    created_at: "2026-06-05T10:00:00+08:00"
    description: "改编自红楼梦第三回，林黛玉初入荣国府，众人相见。"
    source_chapters:
      - number: 3
        title: "贾雨村夤缘复旧职 林黛玉抛父进京都"
    notes: "初稿，待打磨"

  characters:
    - id: "char_001"
      name: "林黛玉"
      aliases: ["黛玉", "林妹妹", "颦儿"]
      role: "protagonist"
      age: "约十岁"
      gender: "女"
      occupation: ""
      description: "体弱多病，心思细腻，才情出众。眉如远山，目含秋水。"
      traits: ["敏感", "聪慧", "多愁善感", "才华横溢"]
      relationships:
        - target: "char_002"
          relation: "外祖母"
        - target: "char_003"
          relation: "表哥"
      arc_summary: ""
      notes: ""

    - id: "char_002"
      name: "贾母"
      aliases: ["史太君", "老太太", "老祖宗"]
      role: "supporting"
      age: "约七十岁"
      gender: "女"
      description: "荣国府最高辈分，慈祥威严。疼惜外孙女黛玉。"
      traits: ["慈爱", "威严", "精明"]
      relationships:
        - target: "char_001"
          relation: "外孙女"
      notes: ""

  scenes:
    - id: "scene_001"
      scene_number: 1
      slug_line:
        location: "荣国府 — 贾母房中"
        time: "day"
        set_details: "陈设华贵，丫鬟环伺"
      characters_present: ["char_001", "char_002"]
      summary: "林黛玉拜见贾母，祖孙相见，悲喜交加。"
      content:
        - element_type: "action"
          text: "林黛玉在丫鬟引路下，步入贾母房中。只见满室珠围翠绕，榻上端坐一位鬓发如银的老太太。"
        - element_type: "dialogue"
          text: "外祖母在上，黛玉给您磕头了。"
          character_id: "char_001"
        - element_type: "parenthetical"
          text: "（声音微颤）"
        - element_type: "action"
          text: "贾母早已泪流满面，一把将黛玉搂入怀中。"
        - element_type: "dialogue"
          text: "我的儿！你可来了……你母亲……我苦命的女儿啊！"
          character_id: "char_002"
          parenthetical: "（泣不成声）"
        - element_type: "action"
          text: "满屋丫鬟婆子无不落泪。"
      transition: "CUT TO:"
      source_reference:
        chapter: 3
        paragraphs: [12, 15, 16, 17]
      notes: ""

    - id: "scene_002"
      scene_number: 2
      slug_line:
        location: "荣国府 — 贾母房外回廊"
        time: "same"
        set_details: ""
      characters_present: ["char_001"]
      summary: "黛玉稍整仪容，丫鬟引去见贾府诸人。"
      content:
        - element_type: "action"
          text: "黛玉拭去泪水，深吸一口气。丫鬟鸳鸯上前搀扶。"
        - element_type: "dialogue"
          text: "林姑娘，老太太吩咐了，先歇一歇再去见太太奶奶们也不迟。"
          character_id: ""
          parenthetical: ""
        - element_type: "dialogue"
          text: "不必了。既来了，自当一一拜见，不敢失了礼数。"
          character_id: "char_001"
      transition: ""
      source_reference:
        chapter: 3
        paragraphs: [18, 19]
      notes: ""
```

---

## 版本兼容性

- 当前版本：`1.0.0`
- Schema 遵循 [语义化版本](https://semver.org/lang/zh-CN/)
- `MAJOR` 变更：不兼容的结构修改
- `MINOR` 变更：新增可选字段
- `PATCH` 变更：文档修正、字段说明更新

---

## 与行业标准的关系

| 本标准 | 好莱坞标准格式 | Final Draft (.fdx) | Fountain |
|--------|:--:|:--:|:--:|
| 结构化程度 | 高 | 高 | 中 |
| 可读性（纯文本） | 高 | 低（XML） | 高 |
| 可编程处理 | 原生（YAML） | 需 XML 解析 | 需专用解析器 |
| AI 生成友好度 | 高 | 中 | 低 |

本 Schema 不能替代专业的 `.fdx` 格式，但作为 **AI 辅助初稿创作格式**，在可读性、可编程性和 AI 适配性之间取得了最优平衡。作者在此 YAML 基础上打磨后，可通过转换脚本输出为 Final Draft 兼容格式。

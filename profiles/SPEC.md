# Profile 格式规范

Profile 是从 wiki 编译的、给 writing agent 使用的**可执行写作约束**。
它不是分析文档的压缩版，而是按写作任务组织的规则集。

## 设计原则

1. **约束优于结论**：不是"风月做了 X"，而是"你应该做 X → [实例: 天启预报 ch67]"
2. **按写作任务组织**：不是按分析维度（pacing/syntax/...），而是按 agent 的实际写作阶段
3. **规则必须可验证**：每条约束应该能明确判断"agent 遵守了还是违反了"
4. **反例与正例同等重要**：告诉 agent "不要做什么" 和 "要做什么"

## 三层架构

```
profiles/
├── base/          ← 网文通用手艺（跨作者跨作品可复用）
├── authors/<slug>/ ← 作者特定风格（仅在该作者的作品中加载）
└── works/<slug>/    ← 作品特定约束（仅在该作品中加载，包含连续性状态）
```

**加载规则**：`works/ > authors/ > base/` —— 具体覆盖通用。
**适用范围**：base/ 写入所有 agent session，authors/ 写入风格模仿 session，works/ 写入特定同人/续写 session。

---

## 一、base/ — 网文通用手艺

### base/padding-catalog.yml
注水手法分类。每个条目描述一种注水模式、适用场景、使用限制。

```yaml
# 格式
patterns:
  - id: description_padding_long_sentence
    name: "长句描写注水"
    category: description
    when_to_use: "战斗高潮后需要拉长过渡章时"
    constraint: "长句描写单章占比不超过70%，超过则为'失败注水'"
    technique: "利用3-4个比喻句链延长一个动作或场景的描写时间"
    examples: []
    anti_examples: []
    source_study: ""
```

### base/chapter-anatomy.yml
章节结构解剖。定义一节网文章的标准骨架和变体。

```yaml
# 格式
chapter_types:
  - id: action_chapter
    name: "动作章"
    structure: [预热(500字), 战斗(2000字), 收束(500字)]
    required_elements: [章末钩子]
    pacing_constraint: "战斗段句长<15字，描写段句长>20字"
```

### base/hook-patterns.yml
章末钩子类型库。A/B/C/D/E 五种类型的定义、适用场景和使用间距。

```yaml
# 格式
hook_types:
  - id: A_suspense_cut
    name: "悬念切割"
    technique: "在关键信息揭露前突然换章"
    best_used_when: "每10-15章一次大悬念"
    overuse_risk: "连续A型会疲劳"
```

### base/reader-curve.yml
微快感曲线。读者情绪波动的节奏约束——每N段需要一个小刺激。

```yaml
# 格式
curve_rules:
  - rule: "每800-1200字需要一次情绪波动（笑/紧张/好奇/感动）"
  - rule: "连续3000字以上无情绪波动 = 读者开始跳章"
  - rule: "章末200字内必须有一个钩子或情绪落地"
```

---

## 二、authors/<slug>/ — 作者特定风格

### authors/<slug>/voice.yml
作者声音指纹。句法偏好、词汇指纹、语气模式。

```yaml
# 格式
voice:
  syntax_modes:
    - name: "长描写句"
      avg_length: "26-41字"
      when_to_use: "环境渲染、氛围建立"
    - name: "中叙事句"  
      avg_length: "15-25字"
      when_to_use: "情节推进、角色互动"
    - name: "短吐槽句"
      avg_length: "5-14字"
      when_to_use: "喜剧打断、情绪强调"
  vocab_fingerprint: []
  tone_profile: ""
```

### authors/<slug>/scene-rhythm.yml
场景节奏特征。高潮间距、过渡处理、日常比重。

```yaml
# 格式
rhythm:
  micro_cycle: ""
  macro_cycle: ""
  comedy_density: ""
  climax_spacing: ""
```

### authors/<slug>/character-speech.yml
角色话术指纹。每个主要角色的口语特征。

```yaml
# 格式
characters:
  - id: protagonist
    name: ""
    speech_fingerprint:
      - trait: "自嘲式吐槽"
        frequency: "每章2-3次"
        examples: []
      - trait: "骚话打趣"
        frequency: "互动场景专用"
        examples: []
```

### authors/<slug>/trope-preferences.yml
这个作者爱用的爽点模式和套路偏好。

```yaml
# 格式
preferred_modes:
  - id: M6_ritual_execution
    name: "仪式化处决"
    description: "复仇高潮不是暴力打脸，而是通过叙事框架（童话/自白）执行处决"
    when_to_use: "大复仇弧线的高潮章"
    source_instances: []
```

---

## 三、works/<slug>/ — 作品特定约束

### works/<slug>/continuity.yml
当前写作状态。角色位置、情节线进度、未回收伏笔清单。
这是"agent 写下一章前必须读取的文件"。

```yaml
# 格式
state:
  last_chapter: 0
  characters:
    - id: ""
      status: ""
      location: ""
  active_threads: []
  pending_chekhovs: []
```

### works/<slug>/world-rules.yml
世界观规则清单。力量体系、组织关系、不能打破的规则。

```yaml
# 格式
rules:
  - rule: ""
    category: power_system | organization | geography | history
    cannot_violate: true/false
```

### works/<slug>/chapter-template.yml
这一部作品的章节写作骨架。

```yaml
# 格式
template:
  opening: ""
  middle: ""
  ending: ""
  hook_position: ""
```

---

## 编译流程

profile 通过 `sub-skills/tasks/style-profile.md` 从 wiki 编译生成。

前提条件（7 项门控）：
1. wiki/novels/<slug>/source-map.md 存在且所有 high priority 章节 status: complete
2. characters/_index.md 存在且 >= 5 个主要角色
3. plot-threads/_index.md 存在且 >= 3 条主线/支线
4. scenes/_index.md 存在且 >= 3 种场景类型
5. excerpts.md 存在且 >= 20 条带章号锚点的摘录
6. style-dimensions/ 中 >= 6/8 维度页已完成
7. 每条声明有来源锚点

编译原则：
- 从 wiki 提取规则，而非复制分析文本
- 每条规则附带至少一个来源实例
- 不满足门控条件时拒绝编译（给出具体缺失项）
- 编译结果写入 data repo 的 profiles/ 对应位置

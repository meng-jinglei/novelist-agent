"""写作 Pipeline: 加载状态 → 写一章。"""

import yaml
from core.llm import call
from core.state import (
    load_prompt, load_project_state, load_project_file, load_rule,
    load_strengths, load_library_index,
    save_chapter, save_project_state, get_data_root,
)

AGENT_DIR = __import__('pathlib').Path(__file__).parent.parent


def _build_context(project_name: str) -> str:
    """组装写作上下文。"""
    state = load_project_state(project_name)
    outline = load_project_file(project_name, "outline.md") or ""

    ctx = f"""## 写作状态

- 章节: 第{state.get('current_chapter', 1)}章
- 上一章结尾: {state.get('last_chapter_ending', '无')[:300]}
- 上一章钩子: {state.get('last_hook_type', '未知')}
- 本章目标: {state.get('chapter_goal', '推进主线')}

## 角色状态
"""
    for name, info in state.get("character_states", {}).items():
        ctx += f"- {name}: {info}\n"

    ctx += f"\n## 活跃情节线\n{chr(10).join(state.get('active_threads', []))}\n"
    ctx += f"\n## 未回收伏笔\n{chr(10).join(state.get('pending_chekhovs', []))}\n"

    # 加载编译后的规则
    for rule_name in ["action_scene", "dialogue_pacing", "chapter_ending"]:
        rule = load_rule(rule_name)
        if rule:
            ctx += f"\n## 写作规则: {rule_name}\n{rule[:1500]}\n"

    return ctx


def run(project_name: str, model: str = "deepseek-v4-pro"):
    """写一章。"""
    state = load_project_state(project_name)
    if not state:
        raise RuntimeError(f"项目 {project_name} 未初始化。先创建 state.json")

    ch = state.get("current_chapter", 1)

    system = load_prompt("write_chapter.md")

    # 注入 voice profile（如果有）
    data_root = get_data_root()
    profile_path = data_root / "profiles" / "authors" / "fengyue" / "voice.yml"
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = yaml.dump(yaml.safe_load(f), allow_unicode=True)
        system += f"\n\n## 风格指纹（必须遵守）\n```yaml\n{profile}\n```"

    user = _build_context(project_name)

    print(f"   ✍️  写第{ch}章...")
    chapter = call(system=system, user=user, model=model, temperature=0.8, max_tokens=8192)

    # 解析章节标题
    lines = chapter.strip().split("\n")
    title = "未命名"
    for line in lines[:3]:
        line = line.strip()
        if line.startswith("第") and "章" in line:
            title = line
            chapter = "\n".join(lines[1:]).strip()
            break

    word_count = len(chapter)
    print(f"   ✅ 完成 ({word_count} 字)")

    return chapter, word_count

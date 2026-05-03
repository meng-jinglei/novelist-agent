"""定向学习 Pipeline: 读素材 → 提取技法 → 写入 craft/rules/。"""

from core.llm import call_with_yaml_output
from core.state import (
    load_prompt, load_library_index, save_library_index,
    save_rule, load_strengths, save_strengths,
)


def run(
    target_technique: str,
    source_name: str,
    source_text: str,
    chapter_label: str = "",
    model: str = "deepseek-v4-pro",
) -> dict:
    """读素材，定向提取技法。"""
    system = load_prompt("targeted_ingest.md")

    user = f"""## 目标技法
{target_technique}

## 素材
来源: {source_name}
{f"章节: {chapter_label}" if chapter_label else ""}

{source_text[:12000]}
"""

    print(f"   📚 定向学习: {target_technique} ← {source_name}")
    report = call_with_yaml_output(system=system, user=user, model=model, temperature=0.3, max_tokens=8192)

    # 保存编译后的规则
    rules = report.get("compiled_rules", [])
    if rules:
        rule_name = target_technique.replace(" ", "_").replace("/", "_")
        rule_text = f"# {target_technique}\n\n来源: {source_name}\n\n"
        for i, r in enumerate(rules):
            rule_text += f"## 规则{i+1}: {r.get('rule', '')}\n"
            rule_text += f"- 正例: {r.get('example', '')}\n"
            rule_text += f"- 反例: {r.get('anti_example', '')}\n\n"
        save_rule(rule_name, rule_text)
        print(f"   📄 规则已保存: craft/rules/{rule_name}.md")

    # 更新 library_index
    lib = load_library_index()
    owned = lib.setdefault("owned", {})

    if source_name not in owned:
        owned[source_name] = {"learned": []}
    if "learned" not in owned[source_name]:
        owned[source_name]["learned"] = []

    learned = owned[source_name]["learned"]
    if target_technique not in learned:
        learned.append(target_technique)

    # 从 want 列表中移除已学习的
    lib["want"] = [w for w in lib.get("want", [])
                   if w.get("target", "") != target_technique]
    save_library_index(lib)

    # 更新 strengths
    strengths = load_strengths()
    caps = strengths.setdefault("capabilities", {})
    if target_technique in caps:
        caps[target_technique]["level"] = "learning"

    # 如果学习队列中有对应项，标记为完成
    queue = strengths.get("learning_queue", [])
    strengths["learning_queue"] = [
        q for q in queue if q.get("dimension") != target_technique
    ]
    save_strengths(strengths)

    return report

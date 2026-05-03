"""自审 Pipeline: 检查章节 → 评估能力。"""

from core.llm import call_with_yaml_output
from core.state import load_prompt, load_project_state, load_strengths, save_strengths


def _build_review_context(project_name: str, chapter_text: str) -> str:
    """组装自审上下文。"""
    state = load_project_state(project_name)
    strengths = load_strengths()

    return f"""## 上一章信息
- 上一章结尾: {state.get('last_chapter_ending', '无')[:300]}
- 上一章钩子类型: {state.get('last_hook_type', '未知')}

## 当前能力状态
```yaml
{str(strengths.get('capabilities', {}))[:1500]}
```

## 要检查的章节

{chapter_text[:8000]}
"""


def run(project_name: str, chapter_text: str, model: str = "deepseek-v4-pro") -> dict:
    """自审章节，返回报告。"""
    system = load_prompt("self_review.md")
    user = _build_review_context(project_name, chapter_text)

    print("   🔍 自审中...")
    report = call_with_yaml_output(system=system, user=user, model=model, temperature=0.3, max_tokens=4096)

    # 更新能力状态
    _update_strengths(report)

    return report


def _update_strengths(report: dict):
    """根据自审报告更新 strengths.yml。"""
    cap_feedback = report.get("capability_feedback", {})
    if not cap_feedback:
        return

    strengths = load_strengths()
    caps = strengths.setdefault("capabilities", {})
    queue = strengths.setdefault("learning_queue", [])

    # 标记改进
    for dim in cap_feedback.get("improved", []):
        if dim in caps:
            caps[dim]["level"] = "competent"

    # 新增弱项
    for dim in cap_feedback.get("new_weakness", []):
        caps[dim] = {"level": "weak", "evidence": []}
        target = cap_feedback.get("learning_target", "")
        if target and not any(q.get("dimension") == dim for q in queue):
            queue.append({
                "dimension": dim,
                "reason": "自审发现",
                "priority": "high" if cap_feedback.get("is_critical") else "medium",
            })

    save_strengths(strengths)

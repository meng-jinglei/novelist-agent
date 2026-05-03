"""缺口分析 Pipeline: 评估能力 → 确定学习优先级。"""

from core.llm import call_with_yaml_output
from core.state import (
    load_prompt, load_strengths, load_library_index,
    load_project_state, load_project_file, save_strengths,
)


def _build_gap_context(project_name: str) -> str:
    import yaml
    strengths = load_strengths()
    lib = load_library_index()
    state = load_project_state(project_name)
    outline = load_project_file(project_name, "outline.md") or "未设置"

    return f"""## 当前能力
```yaml
{yaml.dump(strengths.get('capabilities', {}), allow_unicode=True)}
```

## 学习队列
```yaml
{yaml.dump(strengths.get('learning_queue', []), allow_unicode=True)}
```

## 素材地图
已有素材: {list(lib.get('owned', {}).keys())}
想找的素材: {lib.get('want', [])}

## 项目进度
当前章节: {state.get('current_chapter', 1)}
本章目标: {state.get('chapter_goal', '未知')}

## 项目大纲
{outline[:2000]}
"""


def run(project_name: str, model: str = "deepseek-v4-pro") -> dict:
    """分析能力缺口，返回学习计划。"""
    system = load_prompt("gap_analysis.md")
    user = _build_gap_context(project_name)

    print("   🧠 缺口分析中...")
    report = call_with_yaml_output(system=system, user=user, model=model, temperature=0.5, max_tokens=4096)

    # 更新 strengths 学习队列
    plan = report.get("learning_plan", [])
    if plan:
        strengths = load_strengths()
        queue = strengths.setdefault("learning_queue", [])
        for item in plan:
            target = item.get("target", "")
            if not any(q.get("dimension") == target for q in queue):
                queue.append({
                    "dimension": target,
                    "reason": item.get("source_candidates", []),
                    "priority": item.get("urgency", "medium"),
                })
        save_strengths(strengths)

    return report

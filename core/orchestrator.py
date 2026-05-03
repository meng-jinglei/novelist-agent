"""主循环编排器 — 评估 → 学习 → 写作 → 自审 → 保存。"""

import sys
from pathlib import Path

AGENT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(AGENT_DIR))

from core.state import (
    load_project_state, save_project_state, save_chapter,
    load_strengths,
)
from pipelines.write_chapter import run as write
from pipelines.self_review import run as review
from pipelines.gap_analysis import run as gap_analysis
try:
    from pipelines.targeted_ingest import run as targeted_ingest
except ImportError:
    targeted_ingest = None


def _fix_chapter(chapter: str, issues: list, model: str) -> str:
    """根据 critical issues 修正章节。"""
    from core.llm import call

    issue_text = "\n".join(
        f"- [{i['category']}] {i['description']} → {i.get('fix', '请修正')}"
        for i in issues if i.get("severity") in ("critical", "high")
    )

    system = "你是严格的文字编辑。修正以下章节中列出的问题，保持其他内容不变。只输出修正后的完整章节。"
    user = f"## 需要修正的问题\n{issue_text}\n\n## 原章节\n{chapter}"

    print("   🔄 修正中...")
    return call(system=system, user=user, model=model, temperature=0.4, max_tokens=8192)


def run_loop(
    project_name: str,
    model: str = "deepseek-v4-pro",
    gap_interval: int = 3,
    auto_fix: bool = True,
):
    """
    主循环。
    gap_interval: 每 N 章跑一次缺口分析
    auto_fix: 是否自动修复 critical 问题
    """
    state = load_project_state(project_name)
    if not state:
        print(f"❌ 项目 '{project_name}' 未找到。请先在 projects/{project_name}/ 创建 state.json")
        return

    start_ch = state.get("current_chapter", 1)
    target_ch = state.get("target_chapter", start_ch + 4)
    print(f"🎭 Novelist Agent — {project_name}")
    print(f"   章节 {start_ch} → {target_ch}  |  模型 {model}")
    print(f"   缺口分析间隔: 每 {gap_interval} 章")
    print()

    ch = start_ch

    while ch <= target_ch:
        print(f"── 第 {ch} 章 ──")

        # Phase 0: 缺口分析（间隔）
        if (ch - start_ch) % gap_interval == 0 and ch > start_ch:
            gap = gap_analysis(project_name, model=model)
            can = gap.get("can_proceed", {}).get("value", True)
            blockers = gap.get("can_proceed", {}).get("blockers", [])
            if not can and blockers:
                print(f"   ⛔ 阻塞: {blockers}")
                strengths = load_strengths()
                queue = strengths.get("learning_queue", [])
                if queue:
                    print(f"   📋 学习队列: {[q['dimension'] for q in queue]}")
                # 不强制停止——继续写但记录警告

        # Phase 1: 写作
        chapter, wc = write(project_name, model=model)

        # Phase 2: 自审
        report = review(project_name, chapter, model=model)

        critical_issues = [
            i for i in report.get("issues", [])
            if i.get("severity") == "critical"
        ]
        passed = report.get("passed", True) and len(critical_issues) == 0

        # Phase 3: 修正（如果需要）
        if not passed and auto_fix and critical_issues:
            print(f"   ⚠️  {len(critical_issues)} 个 critical 问题:")
            for ci in critical_issues:
                print(f"      [{ci.get('category', '?')}] {ci.get('description', '?')[:80]}")
            chapter = _fix_chapter(chapter, critical_issues, model)
            report2 = review(project_name, chapter, model=model)
            critical2 = [i for i in report2.get("issues", []) if i.get("severity") == "critical"]
            passed = report2.get("passed", True) and len(critical2) == 0
            report = report2

        # Phase 4: 保存
        filename = save_chapter(project_name, ch, chapter, passed)

        # 更新状态
        state["current_chapter"] = ch + 1
        state["last_chapter_ending"] = chapter[-200:]
        state["last_hook_type"] = report.get("chapter_summary", {}).get("hook_type",
                                       state.get("last_hook_type", "?"))
        # 更新角色状态（从章节内容推断 —— 简化版：保持不变，自审可以标注变化）
        save_project_state(project_name, state)

        status = "✅" if passed else "⚠️"
        print(f"   {status} 保存: {filename}")
        print()

        ch += 1

    print(f"🎉 完成。章节已写入 projects/{project_name}/output/")
    print(f"   strengths.yml 已更新——可以在下次 session 前看看学习建议")


# ── CLI ──

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Novelist Agent")
    p.add_argument("--project", required=True, help="项目名称")
    p.add_argument("--model", default="deepseek-v4-pro")
    p.add_argument("--gap-interval", type=int, default=3)
    p.add_argument("--no-fix", action="store_true")
    args = p.parse_args()
    run_loop(args.project, model=args.model, gap_interval=args.gap_interval, auto_fix=not args.no_fix)

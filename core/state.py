"""状态管理 — 读写 craft/ 和 projects/ 的持久化状态。"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Any

AGENT_DIR = Path(__file__).parent.parent
CRAFT_DIR = AGENT_DIR / "craft"
PROJECTS_DIR = AGENT_DIR / "projects"

# data_root: 从 config.yml 加载，指向数据仓库
_data_root: Path | None = None


def get_data_root() -> Path:
    global _data_root
    if _data_root is None:
        cfg_path = AGENT_DIR / "config.yml"
        if cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            dr = cfg.get("data_root", "")
            if dr:
                _data_root = Path(dr)
    return _data_root or AGENT_DIR.parent  # fallback


# ── Craft 层 ──

def load_strengths() -> dict:
    path = CRAFT_DIR / "strengths.yml"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {"capabilities": {}, "learning_queue": []}


def save_strengths(data: dict):
    CRAFT_DIR.mkdir(parents=True, exist_ok=True)
    data["updated"] = datetime.now().isoformat()
    with open(CRAFT_DIR / "strengths.yml", "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def load_library_index() -> dict:
    path = CRAFT_DIR / "library_index.yml"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {"owned": {}, "want": []}


def save_library_index(data: dict):
    CRAFT_DIR.mkdir(parents=True, exist_ok=True)
    data["updated"] = datetime.now().isoformat()
    with open(CRAFT_DIR / "library_index.yml", "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def load_rule(rule_name: str) -> str | None:
    """加载编译后的写作规则。"""
    path = CRAFT_DIR / "rules" / f"{rule_name}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def save_rule(rule_name: str, content: str):
    rules_dir = CRAFT_DIR / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / f"{rule_name}.md").write_text(content, encoding="utf-8")


# ── Project 层 ──

def load_project_state(project_name: str) -> dict:
    path = PROJECTS_DIR / project_name / "state.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_project_state(project_name: str, state: dict):
    proj_dir = PROJECTS_DIR / project_name
    proj_dir.mkdir(parents=True, exist_ok=True)
    state["saved_at"] = datetime.now().isoformat()
    with open(proj_dir / "state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_project_file(project_name: str, filename: str) -> str | None:
    path = PROJECTS_DIR / project_name / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def save_project_file(project_name: str, filename: str, content: str):
    proj_dir = PROJECTS_DIR / project_name
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / filename).write_text(content, encoding="utf-8")


def save_chapter(project_name: str, chapter_num: int, text: str, passed: bool = True):
    proj_dir = PROJECTS_DIR / project_name / "output"
    proj_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    status = "ok" if passed else "needs_fix"
    filename = f"ch{chapter_num:04d}_{status}_{ts}.md"
    (proj_dir / filename).write_text(text, encoding="utf-8")
    return filename


def load_prompt(name: str) -> str:
    path = AGENT_DIR / "prompts" / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

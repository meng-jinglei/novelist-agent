"""LLM 客户端 — DeepSeek V4 via Anthropic compatible API."""

import os
import json
import yaml
import time
from pathlib import Path
from anthropic import Anthropic

AGENT_DIR = Path(__file__).parent.parent


def _get_api_key() -> str:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("请设置环境变量 DEEPSEEK_API_KEY")
    return key


_client: Anthropic | None = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(
            base_url="https://api.deepseek.com/anthropic",
            api_key=_get_api_key(),
            timeout=600.0,
        )
    return _client


def call(
    system: str,
    user: str,
    model: str = "deepseek-v4-pro",
    temperature: float = 0.7,
    max_tokens: int = 8192,
    retries: int = 2,
) -> str:
    """调用 LLM，自动重试。"""
    client = get_client()
    last_err = None

    for attempt in range(retries + 1):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return resp.content[0].text
        except Exception as e:
            last_err = e
            if attempt < retries:
                wait = 2 ** attempt
                print(f"   ⚠️  LLM 调用失败 (尝试 {attempt+1}/{retries+1}), {wait}s 后重试: {e}")
                time.sleep(wait)

    raise RuntimeError(f"LLM 调用失败: {last_err}")


def call_with_yaml_output(
    system: str, user: str, **kwargs
) -> dict:
    """调用 LLM 并解析 YAML 输出。"""
    text = call(system=system, user=user, **kwargs)

    # 尝试提取 YAML 块
    if "```yaml" in text:
        yaml_str = text.split("```yaml")[1].split("```")[0]
    elif "```" in text:
        yaml_str = text.split("```")[1].split("```")[0]
    else:
        yaml_str = text

    try:
        return yaml.safe_load(yaml_str) or {}
    except Exception:
        return {"_raw": text, "_parse_error": str(yaml.YAMLError) if hasattr(yaml, 'YAMLError') else "parse failed"}

"""LiteLLM pre-call hook that injects each model's system_prompt.md.

The prompt is looked up by the model's public name, so any client
(Open WebUI, curl, other apps) gets the same behavior.
If the client already sent a system message, the server prompt goes first
and the client's text is appended, so there is never a duplicated system role.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from litellm.integrations.custom_logger import CustomLogger

MODELS_DIR = Path(os.environ.get("MODELS_DIR", "/app/models"))


class SystemPromptHook(CustomLogger):
    def __init__(self) -> None:
        super().__init__()
        self._index: dict[str, Path] = {}
        self._cache: dict[Path, tuple[float, str]] = {}
        self._build_index()

    def _build_index(self) -> None:
        """Map public model names to their system prompt files."""
        for model_file in MODELS_DIR.glob("*/model.yaml"):
            spec = yaml.safe_load(model_file.read_text(encoding="utf-8")) or {}
            prompt_name = (spec.get("files") or {}).get("system_prompt")
            public_name = (spec.get("model") or {}).get("public_name")
            if prompt_name and public_name:
                self._index[public_name] = model_file.parent / prompt_name

    def _read_prompt(self, path: Path) -> str:
        """Read the prompt, reloading only when the file changes."""
        if not path.exists():
            return ""
        mtime = path.stat().st_mtime
        cached = self._cache.get(path)
        if cached is None or cached[0] != mtime:
            cached = (mtime, path.read_text(encoding="utf-8").strip())
            self._cache[path] = cached
        return cached[1]

    async def async_pre_call_hook(self, user_api_key_dict, cache, data: dict, call_type):
        if call_type not in ("completion", "acompletion"):
            return data

        path = self._index.get(data.get("model", ""))
        messages = data.get("messages")
        if path is None or not isinstance(messages, list):
            return data

        prompt = self._read_prompt(path)
        if not prompt:
            return data

        first = messages[0] if messages else None
        if isinstance(first, dict) and first.get("role") == "system":
            content = first.get("content")
            if isinstance(content, str):
                if prompt not in content:  # already injected
                    first["content"] = f"{prompt}\n\n{content}"
            elif isinstance(content, list):
                content.insert(0, {"type": "text", "text": prompt})
        else:
            messages.insert(0, {"role": "system", "content": prompt})

        return data


system_prompt_handler = SystemPromptHook()

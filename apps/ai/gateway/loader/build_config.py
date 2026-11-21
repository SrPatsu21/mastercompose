#!/usr/bin/env python3
"""Build the final LiteLLM config from per-model YAML files.

For every models/<name>/model.yaml this script:
  1. creates/updates the model in Ollama from the Modelfile (POST /api/create);
  2. appends a matching entry to LiteLLM's `model_list`;
  3. writes the merged configuration (global config.yaml + model_list).

The system prompt is NOT handled here; see system_prompt_hook.py.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

# Ollama runtime options baked into the model at creation time.
# `think`, `format` and `keep_alive` are request-level, so they go to LiteLLM.
REQUEST_LEVEL_OLLAMA_KEYS = {"think", "format", "keep_alive"}

# Values that mean "use Ollama's default" and must not be forwarded.
DEFAULT_SENTINELS = {"num_thread": 0, "num_gpu": -1}


def log(message: str) -> None:
    print(f"[build_config] {message}", flush=True)


def is_empty(value) -> bool:
    """Return True for values that should not be forwarded."""
    return value is None or value == "" or value == [] or value == {}


def clean(mapping: dict) -> dict:
    """Drop empty values from a dict."""
    return {k: v for k, v in mapping.items() if not is_empty(v)}


# ---------------------------------------------------------------------------
# Modelfile parsing
# ---------------------------------------------------------------------------

def _convert(value: str):
    """Convert a PARAMETER value to int/float when possible."""
    value = value.strip().strip('"')
    for cast in (int, float):
        try:
            return cast(value)
        except ValueError:
            continue
    return value


def parse_modelfile(text: str) -> dict:
    """Parse the subset of the Modelfile syntax needed by /api/create.

    Supported: FROM, TEMPLATE (single or triple quoted), PARAMETER.
    SYSTEM is intentionally ignored: the system prompt is injected by the
    LiteLLM hook so every client gets the same behavior.
    """
    result = {"from": None, "template": None, "parameters": {}}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("#"):
            continue

        keyword, _, rest = line.partition(" ")
        keyword, rest = keyword.upper(), rest.strip()

        if keyword == "FROM":
            result["from"] = rest
        elif keyword in ("TEMPLATE", "SYSTEM"):
            if rest.startswith('"""'):
                body = rest[3:]
                if body.endswith('"""'):
                    value = body[:-3]
                else:
                    chunks = [body]
                    while i < len(lines):
                        current = lines[i]
                        i += 1
                        if current.rstrip().endswith('"""'):
                            chunks.append(current.rstrip()[:-3])
                            break
                        chunks.append(current)
                    value = "\n".join(chunks)
                value = value.removeprefix("\n")
            else:
                value = rest.strip('"')
            if keyword == "TEMPLATE":
                result["template"] = value
        elif keyword == "PARAMETER":
            name, _, raw = rest.partition(" ")
            parsed = _convert(raw)
            if name == "stop":
                result["parameters"].setdefault("stop", []).append(parsed)
            else:
                result["parameters"][name] = parsed
    return result


# ---------------------------------------------------------------------------
# Ollama
# ---------------------------------------------------------------------------

def ollama_request(api_base: str, path: str, payload: dict | None = None,
                   timeout: int = 600) -> dict:
    url = api_base.rstrip("/") + path
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode() or "{}"
        return json.loads(body)


def wait_for_ollama(api_base: str, attempts: int = 30, delay: int = 2) -> bool:
    for _ in range(attempts):
        try:
            ollama_request(api_base, "/api/tags", timeout=5)
            return True
        except (urllib.error.URLError, OSError):
            time.sleep(delay)
    return False


def sync_ollama_model(spec: dict, model_dir: Path, ollama_name: str) -> None:
    """Create or update the Ollama model from the Modelfile."""
    api_base = spec["model"]["api_base"]
    modelfile = parse_modelfile(
        (model_dir / spec["files"]["template"]).read_text(encoding="utf-8")
    )
    if not modelfile["from"]:
        raise ValueError("Modelfile has no FROM instruction")

    # Runtime options from model.yaml, merged with PARAMETER lines
    options = clean({
        k: v for k, v in spec.get("ollama", {}).items()
        if k not in REQUEST_LEVEL_OLLAMA_KEYS and DEFAULT_SENTINELS.get(k) != v
    })
    options.update(modelfile["parameters"])

    payload = {
        "model": ollama_name,
        "from": modelfile["from"],
        "parameters": options,
        "stream": False,
    }
    if modelfile["template"]:
        payload["template"] = modelfile["template"]

    log(f"Syncing Ollama model '{ollama_name}' (from '{modelfile['from']}')")
    try:
        ollama_request(api_base, "/api/create", payload)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        log(f"WARNING: /api/create failed ({exc.code}): {detail}")
        log(f"Hint: run 'ollama pull {modelfile['from']}' and restart the gateway.")


# ---------------------------------------------------------------------------
# LiteLLM
# ---------------------------------------------------------------------------

def build_model_entry(spec: dict, ollama_name: str) -> dict:
    model, gen = spec["model"], spec.get("generation", {})
    reasoning = spec.get("reasoning", {})
    function_calling = spec.get("function_calling", {})
    ollama = spec.get("ollama", {})
    meta = spec.get("metadata", {})

    params = {
        "model": f"{model['provider']}/{ollama_name}",
        "api_base": model["api_base"],
        # Sampling / generation defaults
        "temperature": gen.get("temperature"),
        "max_tokens": gen.get("max_tokens"),
        "top_p": gen.get("top_p"),
        "top_k": gen.get("top_k"),
        "min_p": gen.get("min_p") or None,
        "frequency_penalty": gen.get("frequency_penalty") or None,
        "presence_penalty": gen.get("presence_penalty") or None,
        "seed": gen.get("seed"),
        "stop": gen.get("stop"),
        "logit_bias": gen.get("logit_bias"),
        # Request-level Ollama options
        "think": ollama.get("think"),
        "format": ollama.get("format"),
        "keep_alive": ollama.get("keep_alive"),
    }
    if function_calling.get("enabled"):
        params["parallel_tool_calls"] = function_calling.get("parallel_tool_calls", False)
    if reasoning.get("enabled"):
        params["reasoning_effort"] = reasoning.get("effort")

    # `think: false` is a meaningful value, so keep booleans
    params = {k: v for k, v in params.items() if v is False or not is_empty(v)}

    model_info = {
        "supports_function_calling": bool(function_calling.get("enabled")),
    }
    if meta.get("description"):
        model_info["description"] = meta["description"]
    if meta.get("category"):
        model_info["category"] = meta["category"]

    return {
        "model_name": model["public_name"],
        "litellm_params": params,
        "model_info": model_info,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="Global LiteLLM config.yaml")
    parser.add_argument("--models-dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    base = yaml.safe_load(Path(args.base).read_text(encoding="utf-8")) or {}
    model_list = []

    for model_file in sorted(Path(args.models_dir).glob("*/model.yaml")):
        spec = yaml.safe_load(model_file.read_text(encoding="utf-8"))
        if not spec.get("metadata", {}).get("enabled", True):
            log(f"Skipping disabled model: {model_file.parent.name}")
            continue

        model_dir = model_file.parent
        template_name = spec.get("files", {}).get("template")
        has_modelfile = bool(template_name) and (model_dir / template_name).exists()

        ollama_name = spec["model"]["name"]
        if has_modelfile:
            # Custom model so the base model is never overwritten
            ollama_name = spec["model"].get("ollama_name") or f"mastercompose-{ollama_name}"
            if wait_for_ollama(spec["model"]["api_base"]):
                sync_ollama_model(spec, model_dir, ollama_name)
            else:
                log("WARNING: Ollama is unreachable, skipping model sync")

        model_list.append(build_model_entry(spec, ollama_name))
        log(f"Registered '{spec['model']['public_name']}' -> {ollama_name}")

    base["model_list"] = model_list
    Path(args.out).write_text(
        yaml.safe_dump(base, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    log(f"Config written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

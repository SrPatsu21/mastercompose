#!/bin/sh

set -eu

# Fail early if the Docker secret is missing
if [ ! -s /run/secrets/ai_gateway_key ]; then
    echo "ERROR: LiteLLM master key secret not found."
    exit 1
fi

# Expose the secret to LiteLLM
export LITELLM_MASTER_KEY="$(cat /run/secrets/ai_gateway_key)"

PYTHON="$(command -v python3 || command -v python)"
RUNTIME_DIR=/tmp/gateway
export MODELS_DIR=/app/models

# LiteLLM resolves `callbacks` modules relative to the config file directory,
# so the generated config and the hook must live side by side.
mkdir -p "$RUNTIME_DIR"
cp /app/loader/system_prompt_hook.py "$RUNTIME_DIR/"

# Generate model_list from models/*/model.yaml and sync Modelfiles to Ollama
"$PYTHON" /app/loader/build_config.py \
    --base /app/config.yaml \
    --models-dir "$MODELS_DIR" \
    --out "$RUNTIME_DIR/config.yaml"

exec litellm \
    --config "$RUNTIME_DIR/config.yaml" \
    --port "${AI_GATEWAY_PORT}"

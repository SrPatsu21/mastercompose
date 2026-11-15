# Image for the AI review job.
# Build context: .forgejo/docker/ai_review
# No certificates here: the job receives the trusted certificate at runtime.
# Pin the versions you tested; the unpinned installs below are placeholders.
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir semgrep detect-secrets

# The review script is baked into the image, so a pull request can never
# change what reviews it. Rebuild and push the image when the script changes.
COPY ai_review.py /opt/ai-review/ai_review.py
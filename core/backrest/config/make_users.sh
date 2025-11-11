#!/bin/sh
set -e

if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

CONFIG_PATH="./core/backrest/config/users.yaml"

cat > "$CONFIG_PATH" <<EOF
users:
  - username: ${BACKREST_USERNAME:-admin}
    password: ${BACKREST_PASSWORD:-changeme}
    permissions:
      - backup
      - restore
      - manage
EOF

echo "File created at: $CONFIG_PATH"
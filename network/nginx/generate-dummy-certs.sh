#!/usr/bin/env bash
set -euo pipefail

# Load .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Output folder directly mapped to Nginx
SSL_PATH=${NGINX_SSL:-./network/nginx/ssl}
DAYS_VALID=${DAYS_VALID:-365}
SSL_SIZE=${SSL_SIZE:-2048}

DOMAINS=(
    "dummy"
    "${CF_ZONE}"
)

echo "🔧 Checking and generating dummy certificates if missing..."
for domain in "${DOMAINS[@]}"; do
    CERT_FILE="${SSL_PATH}/${domain}-fullchain.pem"
    KEY_FILE="${SSL_PATH}/${domain}-privkey.pem"

    if [[ -f "$CERT_FILE" && -f "$KEY_FILE" ]]; then
        echo "✅ Certificate already exists for ${domain}"
        continue
    fi

    echo "🚧 Creating dummy cert for ${domain}..."
    mkdir -p "$SSL_PATH"

    openssl req -x509 -nodes -newkey rsa:${SSL_SIZE} \
        -days ${DAYS_VALID} \
        -keyout "${KEY_FILE}" \
        -out "${CERT_FILE}" \
        -subj "/CN=${domain}" \
        -addext "subjectAltName=DNS:${domain}" >/dev/null 2>&1

    chmod 644 "${CERT_FILE}" || true
    chmod 600 "${KEY_FILE}" || true

    echo "   ➜ Created dummy certs for ${domain}"
done

echo "✅ All dummy certs ready."
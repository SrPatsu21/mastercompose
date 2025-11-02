#!/usr/bin/env bash
# ======================================================
# Auto-generate dummy self-signed certificates
# for all domains used by nginx-proxy before Let's Encrypt is ready
# ======================================================

DOMAINS=(
    "backrest.mc.localhost"
    "gitlab.mc.localhost"
)

CERT_BASE="./network/nginx/letsencrypt/live"
DAYS_VALID=365
SSL_SIZE=2048

echo "🔧 Generating dummy certificates if missing..."
for domain in "${DOMAINS[@]}"; do
    DOMAIN_PATH="${CERT_BASE}/${domain}"
    CERT_FILE="${DOMAIN_PATH}/fullchain.pem"
    KEY_FILE="${DOMAIN_PATH}/privkey.pem"

    # skip if already exists
    if [[ -f "$CERT_FILE" && -f "$KEY_FILE" ]]; then
        echo "✅ Certificate already exists for ${domain}"
        continue
    fi

    echo "🚧 Creating dummy cert for ${domain}..."
    mkdir -p "$DOMAIN_PATH"

    openssl req -x509 -nodes -newkey rsa:${SSL_SIZE} \
        -days ${DAYS_VALID} \
        -keyout "${KEY_FILE}" \
        -out "${CERT_FILE}" \
        -subj "/CN=${domain}" >/dev/null 2>&1

    # optional chain copy
    cp "${CERT_FILE}" "${DOMAIN_PATH}/cert.pem" >/dev/null 2>&1 || true

    echo "   ➜ Created: ${DOMAIN_PATH}"
done

echo "✅ Done. Dummy certs ready."

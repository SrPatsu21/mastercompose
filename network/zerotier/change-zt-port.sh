#!/bin/sh
# change-zt-port.sh
# Loads .env and updates /var/lib/zerotier-one.port

# Load .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Ensure the directory exists
if [ ! -d "$(dirname "$PORT_FILE")" ]; then
    echo "Directory $(dirname "$PORT_FILE") does not exist!"
    exit 1
fi

# Write the port
echo -n "{ \"settings\": { \"primaryPort\": ${ZT_PORT:-30000} } }" > ./network/zerotier/local.conf
echo "ZeroTier port set to ${ZT_PORT:-30000}"

#!/usr/bin/env bash
# tf-start.sh — Start TrueFit containers
#
# Usage:
#   sudo ./tf-start.sh

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "Starting TrueFit..."
docker compose up -d

for name in truefit-api truefit-web; do
    if docker ps --format '{{.Names}}' | grep -q "^${name}$"; then
        echo "  ✓ ${name}: running"
    else
        echo "  ✗ ${name}: failed to start"
        docker compose logs --tail=10 "${name}"
        exit 1
    fi
done

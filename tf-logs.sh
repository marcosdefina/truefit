#!/usr/bin/env bash
# tf-logs.sh — Tail TrueFit container logs
#
# Usage:
#   sudo ./tf-logs.sh          # all containers
#   sudo ./tf-logs.sh api      # API only
#   sudo ./tf-logs.sh web      # web only

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

SERVICE="${1:-}"

if [[ -n "$SERVICE" ]]; then
    docker compose logs -f "truefit-${SERVICE}"
else
    docker compose logs -f
fi

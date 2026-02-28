#!/usr/bin/env bash
# tf-down.sh — Stop TrueFit containers
#
# Usage:
#   sudo ./tf-down.sh

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "Stopping TrueFit..."
docker compose down
echo "  ✓ TrueFit stopped"

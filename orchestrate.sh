#!/usr/bin/env bash
# orchestrate.sh — Rebuild and restart TrueFit after config changes
#
# Usage (on mainframe):
#   sudo ./orchestrate.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo "  TrueFit Orchestrate"
echo "============================================"

echo ""
echo "[1/3] Stopping existing containers..."
docker compose down --remove-orphans

echo ""
echo "[2/3] Rebuilding images..."
docker compose build --no-cache

echo ""
echo "[3/3] Starting stack..."
docker compose up -d

echo ""
echo "Verifying..."
docker ps --filter 'name=truefit' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo ""
echo "  ✓ TrueFit orchestrated"

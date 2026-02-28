#!/usr/bin/env bash
# deploy.sh — Deploy TrueFit to the mainframe
#
# Copies project files via SCP, builds Docker images, and starts the stack.
#
# Usage (from Mac):
#   ./deploy.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SERVER="192.168.0.245"
REMOTE_DIR="/opt/truefit"
SSH_USER="marcosdefina"

echo "============================================"
echo "  TrueFit Deploy"
echo "  Target: ${SSH_USER}@${SERVER}:${REMOTE_DIR}"
echo "============================================"

# ---------------------------------------------------------------------------
# [1/4] Create remote directory
# ---------------------------------------------------------------------------
echo ""
echo "[1/4] Preparing remote directory..."
ssh -t "$SERVER" "echo 'Creating ${REMOTE_DIR}...' && sudo mkdir -p ${REMOTE_DIR} && sudo chown ${SSH_USER}:${SSH_USER} ${REMOTE_DIR}"

# ---------------------------------------------------------------------------
# [2/4] Copy project files
# ---------------------------------------------------------------------------
echo ""
echo "[2/4] Copying project files..."
scp -r \
    "${SCRIPT_DIR}/api" \
    "${SCRIPT_DIR}/web" \
    "${SCRIPT_DIR}/docker-compose.yml" \
    "${SCRIPT_DIR}/Dockerfile.api" \
    "${SCRIPT_DIR}/Dockerfile.web" \
    "${SSH_USER}@${SERVER}:${REMOTE_DIR}/"

echo "  ✓ Files copied"

# ---------------------------------------------------------------------------
# [3/4] Build and start containers
# ---------------------------------------------------------------------------
echo ""
echo "[3/4] Building and starting containers..."
ssh -t "$SERVER" "cd ${REMOTE_DIR} && sudo docker compose up -d --build"

# ---------------------------------------------------------------------------
# [4/4] Verify
# ---------------------------------------------------------------------------
echo ""
echo "[4/4] Verifying..."
ssh "$SERVER" "docker ps --filter 'name=truefit' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo "============================================"
echo "  Deploy complete!"
echo "  API:  http://${SERVER}:8100/health"
echo "  Web:  http://${SERVER}:8101"
echo "============================================"

#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# start.sh — One-click launcher for Ozkan Gateway (backend + Streamlit UI)
#
# Usage:
#   ./start.sh              # uses default ports (backend 8080, UI 8501)
#   ./start.sh 8080 8501    # explicit: ./start.sh <backend_port> <ui_port>
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

BACKEND_PORT="${1:-8080}"
UI_PORT="${2:-8502}"

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Ozkan AI Security Gateway — Launcher       ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# ── 1. Clean Python cache ─────────────────────────────────────────────────────
info "Cleaning Python __pycache__ and .pyc files..."
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -not -path "./venv/*" -delete 2>/dev/null || true
success "Python cache cleared."

# ── 2. Clean Streamlit cache ──────────────────────────────────────────────────
info "Clearing Streamlit cache..."
STREAMLIT_CACHE_DIR="${HOME}/.streamlit/cache"
if [ -d "$STREAMLIT_CACHE_DIR" ]; then
    rm -rf "$STREAMLIT_CACHE_DIR"
    success "Streamlit cache cleared."
else
    warn "No Streamlit cache directory found — skipping."
fi

# ── 3. Kill anything on the target ports ─────────────────────────────────────
kill_port() {
    local port="$1"
    local pids
    pids=$(lsof -ti tcp:"$port" 2>/dev/null || true)
    if [ -n "$pids" ]; then
        warn "Port $port in use — killing PID(s): $pids"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 1
        success "Port $port freed."
    else
        info "Port $port is free."
    fi
}

kill_port "$BACKEND_PORT"
kill_port "$UI_PORT"

# ── 4. Activate venv if present ───────────────────────────────────────────────
if [ -f "venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
    success "Virtual environment activated."
elif [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
    success "Virtual environment (.venv) activated."
else
    warn "No venv found — using system Python. Consider: python -m venv venv && pip install -r requirements.txt"
fi

# ── 5. Start FastAPI backend ──────────────────────────────────────────────────
info "Starting FastAPI backend on port ${BACKEND_PORT}..."
uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload &
BACKEND_PID=$!
success "Backend started (PID $BACKEND_PID)."

# Give the backend a moment to bind
sleep 2

# ── 6. Start Streamlit UI ─────────────────────────────────────────────────────
info "Starting Streamlit UI on port ${UI_PORT}..."
streamlit run ui.py \
    --server.port "$UI_PORT" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false &
UI_PID=$!
success "Streamlit started (PID $UI_PID)."

echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Backend API : http://localhost:${BACKEND_PORT}${NC}"
echo -e "${GREEN}  API Docs    : http://localhost:${BACKEND_PORT}/docs${NC}"
echo -e "${GREEN}  UI Console  : http://localhost:${UI_PORT}${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "Press ${RED}Ctrl+C${NC} to stop both services."
echo ""

# ── 7. Wait and handle shutdown ───────────────────────────────────────────────
trap 'echo ""; warn "Shutting down..."; kill $BACKEND_PID $UI_PID 2>/dev/null; success "Done."; exit 0' INT TERM

wait

#!/usr/bin/env bash
# ===================================================
# UniEnroll: FFCS Management Platform Startup Script
# ===================================================

set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$PROJECT_ROOT/.toolchain/bin:$PATH"

echo "🎓 Starting UniEnroll: FFCS Management Platform..."

# 1. Check Neo4j connection
echo "📡 Checking Neo4j connection..."
/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -c "
from backend.database import Neo4jManager
try:
    h = Neo4jManager.check_connection()
    print('✅ Neo4j Connected successfully!')
    print(f'   Nodes: {h[\"node_counts\"]}')
    print(f'   Relationships: {h[\"total_relationships\"]}')
    Neo4jManager.close()
except Exception as e:
    print('⚠️ Neo4j Warning:', e)
"

# 2. Start FastAPI Backend in background
echo "🚀 Launching FastAPI backend on http://127.0.0.1:8000 ..."
/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Trap signals to kill child processes on exit
trap "echo 'Stopping UniEnroll...'; kill $BACKEND_PID 2>/dev/null || true; exit" SIGINT SIGTERM

echo "✨ UniEnroll Full-Stack Platform is LIVE!"
echo "   • Application URL: http://localhost:8000 (Single-Page App + REST API)"
echo "   • Interactive Swagger Docs: http://localhost:8000/docs"
echo "   • Vite Dev Server (Optional): cd frontend && npm run dev"
echo ""
echo "Press Ctrl+C to stop the server."

wait $BACKEND_PID

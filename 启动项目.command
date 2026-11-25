#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$PROJECT_DIR/.run"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_PID_FILE="$RUN_DIR/backend.pid"
FRONTEND_PID_FILE="$RUN_DIR/frontend.pid"

mkdir -p "$RUN_DIR"

# Finder 双击启动时可能不会加载交互式 PATH，这里主动补齐常见路径
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"
if [ -s "$HOME/.nvm/nvm.sh" ]; then
  # shellcheck disable=SC1090
  source "$HOME/.nvm/nvm.sh" >/dev/null 2>&1 || true
fi

echo "============================================================"
echo "  启动：基于ENA与聚类的师范生教学反思分析系统设计与实现"
echo "============================================================"

# -------------------- 1. 启动 Django 后端 --------------------
echo ""
echo "[1/2] 正在检查并启动 Django 后端服务 (端口 8000)..."

if [ -f "$BACKEND_PID_FILE" ] && kill -0 "$(cat "$BACKEND_PID_FILE")" 2>/dev/null; then
  echo "  -> 后端服务已在运行 (PID: $(cat "$BACKEND_PID_FILE"))"
else
  if [ ! -x "$BACKEND_DIR/.venv/bin/python" ]; then
    echo "  -> 未检测到 Python 虚拟环境，正在初始化 .venv 并安装依赖..."
    python3 -m venv "$BACKEND_DIR/.venv"
    "$BACKEND_DIR/.venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
  fi

  if [ ! -f "$BACKEND_DIR/db.sqlite3" ] && [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "  -> 正在初始化数据库与演示数据..."
    "$BACKEND_DIR/.venv/bin/python" "$BACKEND_DIR/manage.py" migrate
    "$BACKEND_DIR/.venv/bin/python" "$BACKEND_DIR/manage.py" seed_demo_data
  fi

  cd "$BACKEND_DIR"
  nohup "$BACKEND_DIR/.venv/bin/python" "$BACKEND_DIR/manage.py" runserver 0.0.0.0:8000 --noreload \
    > "$RUN_DIR/backend.log" 2>&1 &
  BACKEND_PID=$!
  echo "$BACKEND_PID" > "$BACKEND_PID_FILE"

  sleep 2
  if kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "  -> 后端启动成功 (PID: $BACKEND_PID) | 地址: http://127.0.0.1:8000"
  else
    echo "  -> [错误] 后端启动失败，请查看日志: $RUN_DIR/backend.log"
    rm -f "$BACKEND_PID_FILE"
  fi
fi

# -------------------- 2. 启动 Vue 3 前端 --------------------
echo ""
echo "[2/2] 正在检查并启动 Vue 3 前端服务 (端口 5173)..."

if ! command -v npm >/dev/null 2>&1; then
  echo "  -> [提示] 未检测到 Node.js / npm，前端暂无法自动启动。"
  echo "     请先安装 Node.js（推荐执行: brew install node 或访问 https://nodejs.org），"
  echo "     安装完成后再次双击「启动项目.command」即可一键启动前后端。"
else
  if [ -f "$FRONTEND_PID_FILE" ] && kill -0 "$(cat "$FRONTEND_PID_FILE")" 2>/dev/null; then
    echo "  -> 前端服务已在运行 (PID: $(cat "$FRONTEND_PID_FILE"))"
  else
    cd "$FRONTEND_DIR"
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
      echo "  -> 首次启动，正在安装前端依赖 (npm install)..."
      npm install
    fi

    nohup npm run dev -- --host 0.0.0.0 --port 5173 \
      > "$RUN_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo "$FRONTEND_PID" > "$FRONTEND_PID_FILE"

    sleep 2
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
      echo "  -> 前端启动成功 (PID: $FRONTEND_PID) | 地址: http://localhost:5173"
      open "http://localhost:5173" >/dev/null 2>&1 || true
    else
      echo "  -> [错误] 前端启动失败，请查看日志: $RUN_DIR/frontend.log"
      rm -f "$FRONTEND_PID_FILE"
    fi
  fi
fi

echo ""
echo "------------------------------------------------------------"
echo "  访问地址: http://localhost:5173 (前端) / http://127.0.0.1:8000 (后端)"
echo "  日志目录: $RUN_DIR"
echo "  默认账号: 管理员 admin/admin123 | 教师 111/123456 | 学生 010/123456"
echo "  停止服务请双击根目录下的「停止项目.command」"
echo "------------------------------------------------------------"

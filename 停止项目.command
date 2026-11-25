#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$PROJECT_DIR/.run"
BACKEND_PID_FILE="$RUN_DIR/backend.pid"
FRONTEND_PID_FILE="$RUN_DIR/frontend.pid"

echo "============================================================"
echo "  停止：基于ENA与聚类的师范生教学反思分析系统设计与实现"
echo "============================================================"

stop_by_pid_file() {
  local name="$1"
  local pid_file="$2"

  if [ -f "$pid_file" ]; then
    local pid
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      # 先停止该进程及其子进程（兼容 npm -> vite 子进程树）
      pkill -TERM -P "$pid" 2>/dev/null || true
      kill -TERM "$pid" 2>/dev/null || true
      sleep 1
      if kill -0 "$pid" 2>/dev/null; then
        pkill -KILL -P "$pid" 2>/dev/null || true
        kill -KILL "$pid" 2>/dev/null || true
      fi
      echo "  -> ${name}已停止 (PID: $pid)"
    else
      echo "  -> ${name}未在运行"
    fi
    rm -f "$pid_file"
  else
    echo "  -> 未找到${name}运行记录"
  fi
}

# 1. 通过 PID 文件停止前后端
stop_by_pid_file "Django 后端服务" "$BACKEND_PID_FILE"
stop_by_pid_file "Vue 3 前端服务" "$FRONTEND_PID_FILE"

# 2. 兜底清理本项目中可能残留的 runserver / vite 进程
pkill -f "$PROJECT_DIR/backend/manage.py runserver" 2>/dev/null || true
pkill -f "$PROJECT_DIR/frontend/node_modules/.bin/vite" 2>/dev/null || true

echo ""
echo "所有项目服务已停止。"
echo "------------------------------------------------------------"

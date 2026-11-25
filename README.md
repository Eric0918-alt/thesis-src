# 基于ENA与聚类的师范生教学反思分析系统设计与实现

本仓库为毕业设计《基于ENA与聚类的师范生教学反思分析系统设计与实现》的前后端分离工程代码。

## 技术栈
- **前端**：Vue 3 + TypeScript + Vite + Element Plus + Pinia + Vue Router + Axios
- **后端**：Python + Django 4.2 + Django REST Framework + SimpleJWT + Pandas + openpyxl
- **数据库**：MySQL 8.x（默认提供 `.env` 配置切换，未配置 MySQL 时自动降级 SQLite 便于本地快速开发调试）
- **后续扩展预留**：`rENA`（Rscript 桥接）、Scikit-learn 聚类（K-means / DBSCAN）、ECharts 可视化看板、大模型辅助诊断与人工核对模块

## 当前已实现模块
1. **认证与注册**：学生 / 教师 / 管理员三角色登录；学生注册、教师注册（支持头像上传）。
2. **三角色权限隔离**：
   - **学生端**：系统首页、个人编码结果查看（严格隔离仅看本人记录）、个人中心（修改密码、个人信息）。
   - **教师端**：系统首页、学生信息查看（只读）、全部编码结果检索查看（只读）、个人中心（修改密码、个人信息）。
   - **管理员端**：系统首页、学生管理、教师管理、届别管理、编码结果管理（含开题报告要求的严格批量导入校验、模板下载与导出）、系统日志、个人中心。

## 快速启动

### 方式一：一键双击启动 / 停止（macOS 推荐）
在项目根目录直接双击以下两个可执行按钮脚本：
- `启动项目.command`：自动检查环境、启动 Django 后端（`8000` 端口）与 Vue 3 前端（`5173` 端口），并自动打开浏览器。
- `停止项目.command`：一键安全停止前后端全部服务并清理 PID 记录。

### 方式二：命令行手动启动

#### 1. 后端启动
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 可选：复制 .env.example 为 .env 并填入 MySQL 8 连接参数（也可执行 init_mysql.sql 建库）
# cp .env.example .env

python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver 0.0.0.0:8000
```

### 2. 前端启动
```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`。

## 默认演示账号（由 `seed_demo_data` 生成）
- **管理员**：账号 `admin`，密码 `admin123`
- **教师**：工号 `111`（李四），密码 `123456`
- **学生**：学号 `010`（张三，2023届），密码 `123456`

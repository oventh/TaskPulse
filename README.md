# TaskPulse — AI Agent Task Monitor

统一看板，监控 AI Agent 定时任务的运行状态、执行历史，并在任务超时未执行时发送告警通知。

**线上地址**: https://task.pags.cn

---

## 核心功能

- **AI 原生接入** — AI Agent 通过 API 一次性注册自己 + 所有定时任务，无需手动填写表单
- **统一状态看板** — 所有定时任务的运行状态、最近运行时间、结果一目了然
- **执行汇报** — Agent 执行完任务后主动汇报结果，含详细日志
- **超时告警** — 任务未按时执行时自动告警
- **多渠道通知** — 支持飞书 Webhook、邮件、通用 Webhook
- **Base URL 可配置** — 系统设置页面可配置公网访问地址，所有接入指令自动更新

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python FastAPI (异步) + Gunicorn (生产) |
| 前端 | Vue3 + Element Plus (暗色主题) |
| 数据库 | MySQL 8.0 |
| 部署 | 单体应用（FastAPI serve Vue3 构建产物） |

## 快速开始

### 本地开发

```bash
# 1. 克隆项目
git clone https://gitea.tatta.cn/Tatta/TaskPulse.git
cd TaskPulse

# 2. 后端 - 创建虚拟环境并安装依赖
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux:   source .venv/bin/activate
pip install -r requirements.txt

# 3. 复制环境变量并修改数据库配置
cp .env.example .env
# 编辑 .env，配置 MySQL 连接信息

# 4. 启动后端开发服务器
uvicorn app.main:app --reload --port 8000

# 5. 前端（新开终端）
cd frontend
npm install
npm run dev   # 访问 http://localhost:3000
```

> 前端 dev server 自动代理 `/api` 请求到 `localhost:8000`

### 生产部署

```bash
# 1. 构建前端
cd frontend
npm install && npm run build

# 2. 部署到服务器
# 将整个项目复制到服务器（排除 .venv 和 node_modules）
rsync -avz --exclude='.venv' --exclude='node_modules' --exclude='.git' \
  ./ user@server:/home/openclaw/app/taskpulse/

# 3. 在服务器上创建虚拟环境并安装依赖
cd /home/openclaw/app/taskpulse/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 4. 使用 Gunicorn 启动
.venv/bin/gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  -w 2 \
  --access-logfile /var/log/taskpulse/access.log \
  --error-logfile /var/log/taskpulse/error.log \
  --daemon
```

## 环境变量

复制 `backend/.env.example` 为 `backend/.env` 并按需修改：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| TASKPULSE_DB_HOST | localhost | MySQL 主机 |
| TASKPULSE_DB_PORT | 3306 | MySQL 端口 |
| TASKPULSE_DB_USER | dbuser | 数据库用户 |
| TASKPULSE_DB_PASSWORD | - | 数据库密码 |
| TASKPULSE_DB_NAME | taskpulse | 数据库名 |
| TASKPULSE_DEBUG | true | 调试模式（生产环境设为 false） |
| TASKPULSE_FEISHU_WEBHOOK_URL | (空) | 飞书 Webhook 地址 |
| TASKPULSE_SMTP_HOST | (空) | SMTP 服务器 |
| TASKPULSE_SMTP_PORT | 587 | SMTP 端口 |
| TASKPULSE_SMTP_USER | (空) | SMTP 用户 |
| TASKPULSE_SMTP_PASSWORD | (空) | SMTP 密码 |

## Agent 接入

详细接入说明见 [AGENT_GUIDE.md](./AGENT_GUIDE.md)。

### 最小接入示例

```python
import requests

BASE = "https://task.pags.cn"  # 替换为你的实际地址

# 1. AI Agent 注册自己 + 所有定时任务（一次性）
resp = requests.post(f"{BASE}/api/agents/register-with-tasks", json={
    "name": "my-agent",
    "description": "我的 AI Agent",
    "tasks": [
        {"name": "sync-data", "cron_expression": "*/5 * * * *"},
        {"name": "daily-report", "cron_expression": "0 9 * * *"}
    ]
})
agent = resp.json()
API_KEY = agent["api_key"]   # 保存此 Key
AGENT_ID = agent["agent"]["id"]

# 2. 每次执行后汇报结果
requests.post(f"{BASE}/api/tasks/{TASK_ID}/executions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"status": "success", "duration_ms": 1200, "log": "done"})
```

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/agents | 注册 Agent |
| POST | /api/agents/register-with-tasks | **AI Agent 一次性注册自己 + 所有任务** |
| GET | /api/agents | 列出所有 Agent |
| POST | /api/tasks?agent_id=X | 注册定时任务 |
| GET | /api/tasks | 列出所有任务 |
| DELETE | /api/tasks/{id} | 删除任务 |
| POST | /api/tasks/{id}/executions | 汇报执行结果 |
| GET | /api/tasks/{id}/executions | 查看执行历史 |
| GET | /api/dashboard/summary | 看板概览 |
| GET | /api/dashboard/tasks | 看板任务视图 |
| GET | /api/system/config | 读取系统配置（Base URL） |
| PUT | /api/system/config | 更新系统配置 |
| GET | /api/alerts | 告警列表 |
| POST | /api/alerts/{id}/acknowledge | 确认告警 |
| POST | /api/notification-channels | 添加通知渠道 |
| GET | /api/notification-channels | 列出通知渠道 |

完整 API 文档见 `/docs`（Swagger UI）。

## 项目结构

```
taskpulse/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口 + SPA 静态文件服务
│   │   ├── config.py            # 环境变量配置
│   │   ├── database.py          # 异步数据库连接
│   │   ├── models/              # SQLAlchemy 数据模型
│   │   │   ├── agent.py         # Agent（含 API Key 自动生成）
│   │   │   ├── task.py          # 定时任务（cron、宽容窗口）
│   │   │   ├── execution.py     # 执行记录（日志、结果、耗时）
│   │   │   ├── notification.py  # 通知渠道、告警规则、告警历史
│   │   │   └── system_config.py # 系统配置（key-value）
│   │   ├── schemas/             # Pydantic 数据校验
│   │   ├── api/                 # API 路由
│   │   │   ├── agents.py        # Agent CRUD + 批量注册
│   │   │   ├── tasks.py         # 任务 CRUD
│   │   │   ├── executions.py    # 执行汇报 + 历史查询
│   │   │   ├── notifications.py # 通知渠道 + 告警规则 + 告警确认
│   │   │   ├── dashboard.py     # 看板概览统计
│   │   │   └── system.py        # 系统配置
│   │   └── services/            # 业务逻辑
│   │       ├── agent.py / task.py / execution.py
│   │       ├── scheduler.py     # 后台扫描：检测超时任务→生成告警→通知
│   │       └── notification.py  # 飞书 / 邮件 / Webhook 通知发送
│   ├── alembic/                 # 数据库迁移
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/               # 页面组件（暗色主题）
│   │   ├── router/              # 路由
│   │   └── api/                 # Axios API 客户端
│   └── package.json
├── AGENT_GUIDE.md               # Agent 接入指南
└── README.md
```

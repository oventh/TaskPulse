<picture src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python" /><picture src="https://img.shields.io/badge/vue-3.4%2B-4FC08D" alt="Vue" /><picture src="https://img.shields.io/badge/license-MIT-green" alt="License" />

# TaskPulse — AI Agent 定时任务监控系统

> **让 AI Agent 自己汇报工作，你只需要打开看板看一眼。**

TaskPulse 是一个面向 AI Agent 的定时任务跟踪与监控平台。它不是传统的"你去填表创建任务"的后台管理系统，而是**给 AI Agent 一份 API 说明书，让 Agent 自主注册、自动汇报**——你只需要在统一的 Dashboard 上看全局状态。
## 系统截图
<img src="https://pub-44c5bd2a850e4bc7aab6f5f8701493fd.r2.dev/images/111.png"></img>

---

## 设计理念

```
                         ┌─────────────────────┐
                         │   TaskPulse Dashboard│
                         │   统一状态看板       │
                         └──────┬──────────┬───┘
                                │          │
              ┌─────────────────┘          └─────────────────┐
              ▼                                               ▼
     ┌─────────────────┐                          ┌──────────────────────┐
     │  AI Agent A     │  注册任务 → 定时执行       │   AI Agent B         │
     │  └─ 数据同步     │  ← 汇报结果 + 日志         │   └─ 订单采集        │
     │  └─ 报表生成     │                          │   └─ 库存同步        │
     └─────────────────┘                          └──────────────────────┘
```

**核心理念：AI 原生接入**

传统定时任务管理需要用户手动填写 cron 表达式、配置参数。但 AI Agent 本身就具备理解和执行能力——只需给 Agent 一份 API 文档，它就能：

1. **自主注册** — 通过一条 API 把自己和所有定时任务登记到系统
2. **按时汇报** — 每次任务执行完毕，主动 POST 结果（含日志、耗时、状态）
3. **自动纠错** — 如果某个任务到点没执行，系统自动告警

人类要做的只有一件事：**打开看板，看一眼全局状态。**

---

## 核心功能

### 🤖 AI 原生接入
- **一次性批量注册**：`POST /api/agents/register-with-tasks` — Agent 在一分钟内完成注册 + 所有任务登记
- **API Key 鉴权**：每个 Agent 独立密钥，汇报时自动校验
- **无缝重注册**：删除后可重新注册，获取新 Key 继续工作
- **Agent 头像**：名称首字 + 确定性色彩头像，多 Agent 一目了然

### 📊 统一状态看板
- **概览卡片**：Agent 数量、任务总数、24h 执行量、待处理告警
- **全任务视图**：所有 Agent 的任务集中展示，状态、最近运行、结果一目了然
- **任务标签**：可对任务打标签（如"数据同步"、"重要"），按标签筛选
- **Cron 人类可读**：`*/5 * * * *` 自动显示为 "每5分钟"
- **时间本地化**：所有时间自动从 UTC 转为浏览器本地时区

### ⏱ 执行汇报与追踪
- **实时汇报**：Agent 执行完任务后 POST 结果，系统记录执行日志
- **执行历史**：每个任务都有完整的时间线，支持分页查看
- **日志查看器**：暗色终端风格，方便排查问题
- **搜索过滤**：按任务名称、标签、状态快速筛选

### 🚨 超时告警与通知
- **自动检测**：后台调度器每 60 秒扫描未按时执行的任务
- **宽容窗口**：每个任务可单独配置容忍时间，避免误报
- **多渠道通知**：飞书 Webhook、邮件 SMTP、通用 Webhook
- **告警确认**：已处理的告警可标记确认，闭环管理

### 🎨 现代化界面
- **暗色主题**：深色渐变背景 + 霓虹色点缀，降低视觉疲劳
- **全宽布局**：充分利用屏幕空间
- **响应式**：适配不同分辨率

---

## 技术栈

| 层 | 技术 |
|---|---|
| 后端框架 | Python FastAPI (异步) |
| 生产服务 | Gunicorn + Uvicorn Worker |
| 前端框架 | Vue 3 + Element Plus |
| 构建工具 | Vite |
| 数据库 | MySQL 8.0 |
| 数据校验 | Pydantic v2 |
| ORM | SQLAlchemy 2.0 (异步) |
| 认证 | JWT (python-jose) + bcrypt |
| 定时检测 | APScheduler (异步) |
| 部署形态 | 单体应用 (FastAPI serve 前端静态文件) |

---

## 快速开始

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/oventh/TaskPulse.git
cd TaskPulse

# 2. 后端
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # 编辑 .env 配置数据库
uvicorn app.main:app --reload --port 8000

# 3. 前端（新终端）
cd frontend
npm install
npm run dev                 # http://localhost:3000
```

> 前端 `npm run dev` 会代理 `/api` 到 `localhost:8000`

### 生产部署

```bash
# 1. 构建前端
cd frontend && npm install && npm run build

# 2. 部署到服务器
rsync -avz --exclude='.venv' --exclude='node_modules' --exclude='.git' \
  ./ user@server:/home/app/taskpulse/

# 3. 安装依赖 + Gunicorn 启动
cd /home/app/taskpulse/backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 -w 2 --preload --daemon
```

---

## Agent 接入指南

让 AI Agent 自动接入只需 3 步：

```python
import requests

BASE = "https://your-domain.com"  # 替换为你的实际地址

# 1. Agent 一次性注册自己 + 所有定时任务
resp = requests.post(f"{BASE}/api/agents/register-with-tasks", json={
    "name": "my-agent",
    "description": "我的 AI Agent",
    "tasks": [
        {"name": "sync-data",     "cron_expression": "*/5 * * * *"},
        {"name": "daily-report",  "cron_expression": "0 9 * * *"}
    ]
})
data = resp.json()
API_KEY = data["agent"]["api_key"]   # ← 保存此 Key
AGENT_ID = data["agent"]["id"]

# 2. 每次执行完任务后，汇报结果
requests.post(f"{BASE}/api/tasks/{TASK_ID}/executions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"status": "success", "duration_ms": 1500, "log": "执行完毕"})
```

> 完整接入说明见 [AGENT_GUIDE.md](./AGENT_GUIDE.md)，含 curl / Python / 批量注册示例。

---

## 系统配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TASKPULSE_DB_HOST` | localhost | MySQL 主机 |
| `TASKPULSE_DB_PORT` | 3306 | MySQL 端口 |
| `TASKPULSE_DB_USER` | dbuser | 数据库用户 |
| `TASKPULSE_DB_PASSWORD` | - | 数据库密码 |
| `TASKPULSE_DB_NAME` | taskpulse | 数据库名 |
| `TASKPULSE_DEBUG` | true | 调试模式（生产 false） |
| `TASKPULSE_SECRET_KEY` | - | JWT 签名密钥 |
| `TASKPULSE_SMTP_*` | - | 邮件通知配置 |

完整变量列表见 `backend/.env.example`。

---

## API 概览

### Agent 管理
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/agents` | 注册 Agent（返回 API Key） |
| **POST** | **`/api/agents/register-with-tasks`** | **🌟 Agent + 任务一次性批量注册** |
| GET | `/api/agents` | 列出所有 Agent |
| PUT | `/api/agents/{id}` | 修改 Agent 名称/描述 |
| DELETE | `/api/agents/{id}` | 删除 Agent（关联任务一并删除） |

### 定时任务
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/tasks?agent_id=X` | 注册定时任务 |
| GET | `/api/tasks` | 任务列表（支持 `?q=&tags=&status=` 搜索） |
| PUT | `/api/tasks/{id}` | 修改任务名称/标签/描述 |
| DELETE | `/api/tasks/{id}` | 删除任务 |

### 执行汇报
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/tasks/{id}/executions` | Agent 汇报执行结果 |
| GET | `/api/tasks/{id}/executions` | 查看执行历史（分页） |
| GET | `/api/tasks/{id}/executions/{eid}` | 查看单次执行详情 |

### 看板与配置
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard/summary` | 看板概览统计数据 |
| GET | `/api/dashboard/tasks` | 看板全任务视图 |
| GET | `/api/system/config` | 获取系统配置 |
| PUT | `/api/system/config` | 更新系统配置（Base URL） |

### 告警与通知
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/alerts` | 告警列表 |
| POST | `/api/alerts/{id}/acknowledge` | 确认告警 |
| POST | `/api/notification-channels` | 添加通知渠道（飞书/邮件/Webhook） |

完整 OpenAPI 文档在 `/docs`（Swagger UI）查看。

---

## 项目结构

```
taskpulse/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口 + SPA 静态文件 + 生命周期
│   │   ├── config.py            # 环境变量配置 (pydantic-settings)
│   │   ├── database.py          # 异步 MySQL 连接
│   │   ├── models/              # SQLAlchemy 数据模型（6 张表）
│   │   │   ├── agent.py         # Agent + API Key
│   │   │   ├── task.py          # 定时任务 + cron + tags
│   │   │   ├── execution.py     # 执行记录 + 日志
│   │   │   ├── notification.py  # 通知渠道 + 告警规则 + 告警
│   │   │   ├── system_config.py # 系统配置 (key-value)
│   │   │   └── user.py          # 看板登录用户
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   ├── api/                 # REST API 路由（7 个模块）
│   │   └── services/            # 业务逻辑层
│   │       ├── scheduler.py     # ⏰ 后台调度器（超时检测）
│   │       └── notification.py  # 📢 飞书/邮件/Webhook 发送
│   ├── alembic/                 # 数据库迁移
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/               # 6 个页面（暗色主题）
│   │   ├── router/              # 路由守卫 + 登录跳转
│   │   ├── api/                 # Axios 客户端 + 401 拦截
│   │   └── assets/              # 全局样式 + Element Plus 覆盖
│   └── package.json
├── AGENT_GUIDE.md               # Agent API 接入说明
└── README.md
```

---

## 许可证

MIT License © 2026

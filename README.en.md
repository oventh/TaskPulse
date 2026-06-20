<picture src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python" /><picture src="https://img.shields.io/badge/vue-3.4%2B-4FC08D" alt="Vue" /><picture src="https://img.shields.io/badge/license-MIT-green" alt="License" />

# TaskPulse — AI Agent Scheduled Task Monitor

> **Let your AI agents self-report. You just glance at the dashboard.**

TaskPulse is a tracking and monitoring platform designed for AI agents' scheduled tasks. Unlike traditional CRUD-heavy admin panels, TaskPulse is **AI-native**: give your agents an API spec, and they autonomously register themselves, report execution results, and update their status — no manual form-filling required.


[📖 中文文档](./README.md)

---

## Philosophy

```
                         ┌─────────────────────┐
                         │   TaskPulse Dashboard│
                         │   Unified Status View│
                         └──────┬──────────┬───┘
                                │          │
              ┌─────────────────┘          └─────────────────┐
              ▼                                               ▼
     ┌─────────────────┐                          ┌──────────────────────┐
     │  AI Agent A     │  register tasks → execute │   AI Agent B         │
     │  ├─ data sync   │  ← report result + log    │   ├─ order fetch     │
     │  └─ report gen  │                           │   └─ inventory sync  │
     └─────────────────┘                          └──────────────────────┘
```

**AI-Native by Design**

Traditional schedulers require humans to fill forms and manage cron expressions. But AI agents can read API docs and act autonomously:

1. **Self-Register** — One API call to register both the agent and all its tasks
2. **Report Results** — After each execution, POST back the result with logs and duration
3. **Auto-Alert** — If a task misses its window, the system alerts automatically

The only thing humans need to do: **open the dashboard and see the big picture.**

---

## Features

### 🤖 AI-Native Onboarding
- **Batch Registration**: `POST /api/agents/register-with-tasks` — agent + tasks in one shot
- **API Key Auth**: Each agent gets its own key for reporting
- **Re-registration**: Deleted agents can re-register anytime
- **Agent Avatars**: First-letter + deterministic color avatars for quick visual identification

### 📊 Unified Dashboard
- **Summary Cards**: agent count, task count, 24h executions, pending alerts
- **Global Task View**: all tasks from all agents in one place
- **Task Tags**: label tasks (e.g. "data-sync", "critical"), filter by tags
- **Human-Readable Cron**: `*/5 * * * *` → "Every 5 minutes"
- **Localized Time**: all timestamps auto-converted from UTC to browser timezone

### ⏱ Execution Tracking
- **Live Reporting**: agents POST results immediately after execution
- **Execution History**: full timeline per task, paginated
- **Log Viewer**: dark terminal-style viewer for debugging
- **Search & Filter**: by task name, tags, and status

### 🚨 Timeout Alerts & Notifications
- **Auto-Scan**: background scheduler checks overdue tasks every 60s
- **Grace Window**: per-task tolerance to avoid false alerts
- **Multi-Channel**: Feishu (Lark) webhook, email SMTP, generic webhook
- **Alert Acknowledgment**: mark alerts as handled for closed-loop management

### 🎨 Modern UI
- **Dark Theme**: gradient backgrounds + neon accents
- **Full-Width Layout**: maximizes screen usage
- **Responsive**: adapts to different screen sizes

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python FastAPI (async) |
| Production Server | Gunicorn + Uvicorn Worker |
| Frontend | Vue 3 + Element Plus |
| Build Tool | Vite |
| Database | MySQL 8.0 |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.0 (async) |
| Auth | JWT (python-jose) + bcrypt |
| Scheduler | APScheduler (async loop) |
| Deployment | Monolithic (FastAPI serves SPA) |

---

## Quick Start

### Local Development

```bash
# 1. Clone
git clone https://github.com/oventh/TaskPulse.git
cd TaskPulse

# 2. Backend
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # edit .env with your DB config
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev                         # http://localhost:3000
```

> Frontend dev server proxies `/api` to `localhost:8000`.

### Production Deployment

```bash
# 1. Build frontend
cd frontend && npm install && npm run build

# 2. Deploy to server
rsync -avz --exclude='.venv' --exclude='node_modules' --exclude='.git' \
  ./ user@server:/home/app/taskpulse/

# 3. Install deps + start with Gunicorn
cd /home/app/taskpulse/backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 -w 2 --preload --daemon
```

---

## Agent Integration

Let your AI agent self-register in 3 steps:

```python
import requests

BASE = "https://your-domain.com"

# 1. Register agent + all its tasks (one API call)
resp = requests.post(f"{BASE}/api/agents/register-with-tasks", json={
    "name": "my-agent",
    "description": "My AI Agent",
    "tasks": [
        {"name": "sync-data",     "cron_expression": "*/5 * * * *"},
        {"name": "daily-report",  "cron_expression": "0 9 * * *"}
    ]
})
data = resp.json()
API_KEY = data["agent"]["api_key"]   # ← save this
AGENT_ID = data["agent"]["id"]

# 2. Report execution result after each run
requests.post(f"{BASE}/api/tasks/{TASK_ID}/executions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"status": "success", "duration_ms": 1500, "log": "Task completed"})
```

> For curl, batch registration, and more examples, see the Chinese doc [AGENT_GUIDE.md](./AGENT_GUIDE.md).

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `TASKPULSE_DB_HOST` | localhost | MySQL host |
| `TASKPULSE_DB_PORT` | 3306 | MySQL port |
| `TASKPULSE_DB_USER` | dbuser | Database user |
| `TASKPULSE_DB_PASSWORD` | - | Database password |
| `TASKPULSE_DB_NAME` | taskpulse | Database name |
| `TASKPULSE_DEBUG` | true | Debug mode (false in production) |
| `TASKPULSE_SECRET_KEY` | - | JWT signing key |
| `TASKPULSE_SMTP_*` | - | Email notification config |

See `backend/.env.example` for the full list.

---

## API Overview

### Agents
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/agents` | Register an agent (returns API Key) |
| **POST** | **`/api/agents/register-with-tasks`** | **🌟 Batch register agent + tasks** |
| GET | `/api/agents` | List all agents |
| PUT | `/api/agents/{id}` | Update agent name/description |
| DELETE | `/api/agents/{id}` | Delete agent (cascades to tasks) |

### Tasks
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/tasks?agent_id=X` | Create a scheduled task |
| GET | `/api/tasks` | List tasks (`?q=&tags=&status=` filters) |
| PUT | `/api/tasks/{id}` | Update task name/tags/description |
| DELETE | `/api/tasks/{id}` | Delete a task |

### Execution Reporting
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/tasks/{id}/executions` | **Agent reports execution result** |
| GET | `/api/tasks/{id}/executions` | View execution history (paginated) |
| GET | `/api/tasks/{id}/executions/{eid}` | View single execution detail |

### Dashboard & Config
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dashboard/summary` | Dashboard summary stats |
| GET | `/api/dashboard/tasks` | Dashboard full task view |
| GET | `/api/system/config` | Get system config |
| PUT | `/api/system/config` | Update system config (Base URL) |

### Alerts & Notifications
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/alerts` | List alerts |
| POST | `/api/alerts/{id}/acknowledge` | Acknowledge an alert |
| POST | `/api/notification-channels` | Add notification channel |

Full OpenAPI docs at `/docs` (Swagger UI).

---

## Project Structure

```
taskpulse/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry + SPA static files + lifecycle
│   │   ├── config.py            # Environment variables (pydantic-settings)
│   │   ├── database.py          # Async MySQL connection
│   │   ├── models/              # SQLAlchemy models (6 tables)
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── api/                 # REST API routes (7 modules)
│   │   └── services/            # Business logic layer
│   │       ├── scheduler.py     # ⏰ Background scheduler (timeout detection)
│   │       └── notification.py  # 📢 Feishu/Email/Webhook sender
│   ├── alembic/                 # DB migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/               # 6 pages (dark theme)
│   │   ├── router/              # Route guards + login redirect
│   │   ├── api/                 # Axios client + 401 interceptor
│   │   └── assets/              # Global styles + Element Plus overrides
│   └── package.json
├── AGENT_GUIDE.md               # Agent API guide (Chinese)
├── README.md                    # Documentation (Chinese)
└── README.en.md                 # Documentation (English)
```

---

## License

MIT License © 2026

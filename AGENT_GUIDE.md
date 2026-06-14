# Agent 接入指南

本文档说明 AI Agent 如何接入 TaskPulse 系统。

## 一、注册 Agent

首先向 TaskPulse 注册你的 Agent，获取 API Key：

```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent", "description": "我的第一个 Agent"}'
```

返回示例：
```json
{
  "id": 1,
  "name": "my-agent",
  "api_key": "tp_a1b2c3d4e5f6...",
  "status": "active",
  "task_count": 0,
  ...
}
```

**请妥善保存 `api_key`**，后续所有操作都需要通过这个 Key 鉴权。

## 二、注册定时任务

Agent 注册成功后，注册它所管理的定时任务：

```bash
curl -X POST "http://localhost:8000/api/tasks?agent_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "data-sync",
    "cron_expression": "0 */1 * * *",
    "description": "每小时同步数据",
    "grace_period": 300
  }'
```

| 参数 | 说明 |
|------|------|
| `name` | 任务名称 |
| `cron_expression` | Cron 表达式（分 时 日 月 周） |
| `grace_period` | 容忍窗口（秒），超过预定时间N秒未执行则触发告警 |
| `description` | 任务描述（可选） |

## 三、执行后汇报结果

每次任务执行完成后，向 TaskPulse 汇报执行结果：

```bash
curl -X POST http://localhost:8000/api/tasks/1/executions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tp_a1b2c3d4e5f6..." \
  -d '{
    "status": "success",
    "duration_ms": 1523,
    "result": "{\"records_synced\": 100}",
    "log": "[2025-01-01 10:00:00] Starting sync...\n[2025-01-01 10:00:01] Synced 100 records",
    "error_message": null
  }'
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `status` | 是 | `success` 或 `failed` |
| `finished_at` | 否 | 结束时间（ISO 格式），默认当前时间 |
| `duration_ms` | 否 | 执行耗时（毫秒） |
| `result` | 否 | 执行结果摘要（JSON 字符串） |
| `log` | 否 | 执行日志文本 |
| `error_message` | 否 | 错误信息（仅失败时填写） |

## 四、Python SDK 示例

```python
import requests

BASE_URL = "http://localhost:8000"
API_KEY = "tp_a1b2c3d4e5f6..."

headers = {"Authorization": f"Bearer {API_KEY}"}

# 1. 注册 Agent
def register_agent(name: str, description: str = "") -> dict:
    resp = requests.post(f"{BASE_URL}/api/agents", json={
        "name": name, "description": description
    })
    resp.raise_for_status()
    return resp.json()

# 2. 注册定时任务
def register_task(agent_id: int, name: str, cron: str) -> dict:
    resp = requests.post(f"{BASE_URL}/api/tasks", params={"agent_id": agent_id}, json={
        "name": name, "cron_expression": cron
    })
    resp.raise_for_status()
    return resp.json()

# 3. 汇报执行结果
def report_execution(task_id: int, status: str, log: str = "", duration_ms: int = 0):
    resp = requests.post(
        f"{BASE_URL}/api/tasks/{task_id}/executions",
        headers=headers,
        json={
            "status": status,
            "duration_ms": duration_ms,
            "log": log,
            "result": "{}",
        }
    )
    resp.raise_for_status()
    return resp.json()

# 使用示例
agent = register_agent("data-agent", "数据同步 Agent")
task = register_task(agent["id"], "hourly-sync", "0 * * * *")
report_execution(task["id"], "success", log="Sync completed", duration_ms=2500)
```

## 五、查看看板

打开浏览器访问 `http://localhost:8000` 即可查看统一的 Dashboard。

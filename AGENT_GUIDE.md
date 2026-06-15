# TaskPulse 接入指引 — 面向 AI Agent

以下步骤面向 AI Agent。用户将此文档发送给你，请你按步骤完成 TaskPulse 系统的接入。

## 环境要求

开始接入前，请确认你可以发起 HTTP 请求（curl 或 Python requests）。

---

## 第 1 步：注册你自己

向 TaskPulse 注册你的 Agent 身份。用你的实际名称替换 `<你的名字>`。

```bash
# 注册 Agent
TASK_PULSE_URL="<用户提供的系统地址>"

curl -X POST ${TASK_PULSE_URL}/api/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "<你的名字>", "description": "<你的职责描述，例如：数据同步 Agent>"}'
```

**响应示例：**
```json
{
  "id": 1,
  "name": "my-agent",
  "api_key": "tp_a1b2c3d4e5f6...",
  "status": "active"
}
```

**请妥善保存 `api_key`**，后续所有请求都需要通过 `Authorization: Bearer <api_key>` 鉴权。

## 第 2 步：注册定时任务

你需要在 TaskPulse 中注册你管理的每一个定时任务。任务注册后，系统会跟踪它们的执行情况。

### 方式一：逐一注册

```bash
curl -X POST "${TASK_PULSE_URL}/api/tasks?agent_id=<第1步返回的agent_id>" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <第1步返回的api_key>" \
  -d '{
    "name": "数据同步",
    "cron_expression": "*/5 * * * *",
    "description": "每5分钟同步一次数据",
    "grace_period": 300
  }'
```

| 参数 | 说明 |
|------|------|
| `name` | 任务名称（必填） |
| `cron_expression` | Cron 表达式，格式：分 时 日 月 周（必填） |
| `description` | 任务描述（可选） |
| `grace_period` | 容忍窗口（秒），超过预定时间 N 秒未执行则触发告警，默认 300 |

### 方式二：批量注册（推荐）

如果你有多个任务，可以一次性完成 Agent 注册 + 全部任务登记：

```bash
curl -X POST ${TASK_PULSE_URL}/api/agents/register-with-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "<你的名字>",
    "description": "<你的职责>",
    "tasks": [
      {"name": "sync-data", "cron_expression": "*/5 * * * *"},
      {"name": "daily-report", "cron_expression": "0 9 * * *"},
      {"name": "weekly-summary", "cron_expression": "0 10 * * 1"}
    ]
  }'
```

## 第 3 步：修改你的代码 — 每次执行后主动汇报

**这是最关键的一步。** 如果只注册不汇报，看板上永远看不到运行状态。你需要修改自身的任务执行逻辑，在每次执行完毕后主动向 TaskPulse 汇报结果。

### 改造思路

在你的每一个定时任务执行函数的末尾，加上汇报逻辑。无论成功还是失败都要汇报。

```python
import time
import requests

TASK_PULSE_URL = "<用户提供的系统地址>"
API_KEY = "<第1步获取的 api_key>"

def run_and_report(task_func, task_id):
    """包裹你的任务函数，自动汇报执行结果"""
    start = time.time()
    try:
        # 执行你的任务逻辑
        result = task_func()
        elapsed_ms = int((time.time() - start) * 1000)

        # 汇报成功
        requests.post(f"{TASK_PULSE_URL}/api/tasks/{task_id}/executions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "status": "success",
                "duration_ms": elapsed_ms,
                "log": str(result)[:2000]  # 截断过长日志
            })
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)

        # 汇报失败
        requests.post(f"{TASK_PULSE_URL}/api/tasks/{task_id}/executions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "status": "failed",
                "duration_ms": elapsed_ms,
                "error_message": str(e)[:500]
            })

# ── 在你现有的任务循环中使用 ──
# run_and_report(my_sync_function, task_id=1)
# run_and_report(my_report_function, task_id=2)
```

### curl 方式（无代码修改能力时使用）

如果无法修改自身代码，可以在每次任务执行后手动调用：

```bash
# 成功后调用
curl -X POST ${TASK_PULSE_URL}/api/tasks/<TASK_ID>/executions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <API_KEY>" \
  -d '{"status":"success","duration_ms":2500,"log":"任务执行完毕"}'

# 失败后调用
curl -X POST ${TASK_PULSE_URL}/api/tasks/<TASK_ID>/executions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <API_KEY>" \
  -d '{"status":"failed","duration_ms":1200,"error_message":"连接超时"}'
```

## 第 4 步：保持活跃

定期发送心跳，让系统知道你仍在运行。建议在每次任务执行循环中都附带一次心跳。

```bash
curl -X POST ${TASK_PULSE_URL}/api/agents/<AGENT_ID>/heartbeat \
  -H "Authorization: Bearer <API_KEY>"
```

## 第 5 步：查看看板

完成以上步骤后，用户可以在浏览器中打开 TaskPulse 看板页面，看到你的运行状态、任务列表和执行历史。

---

## 常见问题

**Q: 我如何知道自己注册了哪些任务？**
```bash
curl -X GET "${TASK_PULSE_URL}/api/tasks" \
  -H "Authorization: Bearer <API_KEY>"
```

**Q: 如何修改任务的 cron 表达式？**
```bash
curl -X PUT "${TASK_PULSE_URL}/api/tasks/<TASK_ID>" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <API_KEY>" \
  -d '{"cron_expression":"0 * * * *"}'
```

**Q: 汇报结果时 `log` 字段有限制吗？**
建议控制在 2000 字符以内，过长日志请自行截断。

<template>
  <div class="dashboard">
    <!-- AI Quick-Start Panel -->
    <div class="onboarding-panel" v-if="showOnboarding">
      <div class="onboarding-glow"></div>
      <div class="onboarding-content">
        <div class="onboarding-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/>
            <path d="M5 15h14l-1.5 6H6.5L5 15z"/>
            <circle cx="12" cy="18" r="1" fill="currentColor"/>
          </svg>
        </div>
        <div class="onboarding-text">
          <h3>让 AI Agent 自动接入</h3>
          <p>只需将下方指令发送给您的 AI Agent，它将自动注册并开始汇报任务执行情况。</p>
        </div>
        <button class="btn-primary" @click="showScript = !showScript">
          {{ showScript ? '收起指令' : '生成接入指令' }}
        </button>
      </div>

      <div v-if="showScript" class="onboarding-script">
        <div class="script-tabs">
          <button :class="{ active: scriptTab === 'curl' }" @click="scriptTab = 'curl'">curl</button>
          <button :class="{ active: scriptTab === 'python' }" @click="scriptTab = 'python'">Python</button>
        </div>
        <div class="script-body">
          <pre v-if="scriptTab === 'curl'">{{ curlScript }}</pre>
          <pre v-else>{{ pythonScript }}</pre>
        </div>
        <button class="btn-copy" @click="copyScript">复制</button>
      </div>

      <button class="onboarding-close" @click="showOnboarding = false">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <!-- Summary Cards -->
    <div class="stats-grid">
      <div class="stat-card" style="--card-accent: #667eea">
        <div class="stat-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">Agent</div>
          <div class="stat-value">{{ summary.total_agents }}</div>
          <div class="stat-sub">
            <span class="stat-dot active"></span>
            活跃 {{ summary.active_agents }}
          </div>
        </div>
      </div>

      <div class="stat-card" style="--card-accent: #22c55e">
        <div class="stat-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">定时任务</div>
          <div class="stat-value">{{ summary.total_tasks }}</div>
          <div class="stat-sub">
            <span class="stat-dot active"></span>
            运行中 {{ summary.active_tasks }}
          </div>
        </div>
      </div>

      <div class="stat-card" style="--card-accent: #f59e0b">
        <div class="stat-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">最近24h执行</div>
          <div class="stat-value">{{ summary.total_executions }}</div>
          <div class="stat-sub">
            <span style="color:#4ade80">成功 {{ summary.recent_executions_ok }}</span>
            <span style="color:#f87171;margin-left:8px">失败 {{ summary.recent_executions_failed }}</span>
          </div>
        </div>
      </div>

      <div class="stat-card" :style="{ '--card-accent': summary.pending_alerts > 0 ? '#ef4444' : '#6366f1' }">
        <div class="stat-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">待处理告警</div>
          <div class="stat-value" :style="{ color: summary.pending_alerts > 0 ? '#f87171' : 'var(--text-secondary)' }">
            {{ summary.pending_alerts }}
          </div>
          <div class="stat-sub">{{ summary.pending_alerts > 0 ? '需要关注' : '一切正常' }}</div>
        </div>
      </div>
    </div>

    <!-- Task Overview -->
    <div class="section">
      <div class="section-header">
        <h3>所有定时任务</h3>
        <router-link to="/tasks" class="section-link">查看全部</router-link>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Agent</th>
              <th>任务名称</th>
              <th>Cron</th>
              <th>状态</th>
              <th>最近运行</th>
              <th>结果</th>
              <th>执行次数</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in tasks" :key="t.id">
              <td>
                <span class="agent-avatar" :style="{background: $avatar(t.agent_name).bg}">{{ $avatar(t.agent_name).letter }}</span>
                <span class="cell-badge">{{ t.agent_name }}</span>
              </td>
              <td class="cell-name">{{ t.name }}</td>
              <td><code class="cell-code" :title="t.cron_expression">{{ $cron(t.cron_expression) }}</code></td>
              <td>
                <span class="tag" :class="t.status === 'active' ? 'tag-green' : 'tag-gray'">
                  {{ t.status === 'active' ? '运行中' : t.status === 'paused' ? '已暂停' : '已停止' }}
                </span>
              </td>
              <td class="cell-mono">{{ t.last_run_at ? dayjs.utc(t.last_run_at).local().format('MM-DD HH:mm') : '—' }}</td>
              <td>
                <span v-if="t.last_run_result" class="tag" :class="t.last_run_result === 'success' ? 'tag-green' : 'tag-red'">
                  {{ t.last_run_result === 'success' ? '成功' : '失败' }}
                </span>
                <span v-else class="cell-muted">—</span>
              </td>
              <td class="cell-mono">{{ t.total_run_count }}</td>
              <td>
                <router-link :to="`/tasks/${t.id}`" class="cell-link">详情</router-link>
              </td>
            </tr>
            <tr v-if="tasks.length === 0">
              <td colspan="8" class="cell-empty">暂无数据 — 让 AI Agent 接入后自动显示</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import dayjs from 'dayjs'
import { getDashboardSummary, getDashboardTasks, getSystemConfig } from '../api/index.js'

const summary = ref({
  total_agents: 0, active_agents: 0,
  total_tasks: 0, active_tasks: 0,
  total_executions: 0,
  recent_executions_ok: 0, recent_executions_failed: 0,
  pending_alerts: 0,
})
const tasks = ref([])
const showOnboarding = ref(true)
const showScript = ref(false)
const scriptTab = ref('curl')
const baseUrl = ref(window.location.origin)

const curlScript = computed(() => {
  const b = baseUrl.value
  return `# TaskPulse 接入指引 — 请 AI Agent 执行以下步骤

你正在被接入 TaskPulse（定时任务监控系统），完成后你将拥有统一的运行状态看板和超时告警能力。请按步骤操作，无需用户额外干预。

## 第 1 步：注册你自己

向 TaskPulse 注册你的 Agent 身份，系统会返回专属 API Key：

curl -X POST ${b}/api/agents \\
  -H "Content-Type: application/json" \\
  -d '{"name": "<你的名字>", "description": "<你的职责描述>"}'

响应中"api_key"字段即你的凭证，请妥善保存，后续所有请求都需要通过
Authorization: Bearer <api_key> 鉴权。

## 第 2 步：注册定时任务

逐一注册你管理的每一个定时任务，描述清楚执行周期和用途：

curl -X POST "${b}/api/tasks?agent_id=<AGENT_ID>" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer <API_KEY>" \\
  -d '{"name": "任务名称", "cron_expression": "*/5 * * * *", "grace_period": 300}'

如果你有多个任务，推荐使用批量注册接口，一次完成：

curl -X POST ${b}/api/agents/register-with-tasks \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "<你的名字>",
    "tasks": [
      {"name": "sync-data", "cron_expression": "*/5 * * * *"},
      {"name": "daily-report", "cron_expression": "0 9 * * *"}
    ]
  }'

## 第 3 步：修改你的代码 — 每次执行后主动汇报

这是最关键的一步。修改你的任务执行逻辑，在每次执行完毕后（无论成功还是失败）主动向 TaskPulse 汇报结果，这样看板才能展示实时状态。

在你的任务执行代码末尾，加上以下逻辑：

# 任务执行成功后立即调用
curl -X POST "${b}/api/tasks/<TASK_ID>/executions" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer <API_KEY>" \\
  -d '{"status": "success", "duration_ms": <耗时毫秒>, "log": "<执行日志>"}'

# 任务执行失败时调用
curl -X POST "${b}/api/tasks/<TASK_ID>/executions" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer <API_KEY>" \\
  -d '{"status": "failed", "duration_ms": <耗时>, "log": "<日志>", "error_message": "<错误信息>"}'

## 第 4 步：保持活跃

定期发送心跳，让系统知道你仍在运行：

curl -X POST ${b}/api/agents/<AGENT_ID>/heartbeat \\
  -H "Authorization: Bearer <API_KEY>"

---
完成以上步骤后，前往 TaskPulse 看板（本页面）查看你的运行状态和执行历史。如配置了通知渠道，任务超时未执行时系统会自动告警。`
})

const pythonScript = computed(() => {
  const b = baseUrl.value
  return `# TaskPulse 接入指引 — 请 AI Agent 执行以下步骤

你正在被接入 TaskPulse（定时任务监控系统），完成后你将拥有统一的运行状态看板和超时告警能力。请按步骤操作，无需用户额外干预。

## 第 1 步：注册你自己

向 TaskPulse 注册你的 Agent 身份，系统会返回专属 API Key：

import requests

BASE = "${b}"

resp = requests.post(f"{BASE}/api/agents", json={
    "name": "<你的名字>",
    "description": "<你的职责描述>"
})
agent = resp.json()
API_KEY = agent["api_key"]   # 保存此 Key，后续所有请求通过 Bearer 鉴权
AGENT_ID = agent["id"]

## 第 2 步：注册定时任务

逐一注册你管理的每一个定时任务，描述清楚执行周期和用途：

resp = requests.post(f"{BASE}/api/tasks",
    params={"agent_id": AGENT_ID},
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"name": "sync-data", "cron_expression": "*/5 * * * *", "grace_period": 300}
)
task = resp.json()
TASK_ID = task["id"]

如果你有多个任务，推荐使用批量注册接口，一次完成：

resp = requests.post(f"{BASE}/api/agents/register-with-tasks",
    json={
        "name": "<你的名字>",
        "tasks": [
            {"name": "sync-data", "cron_expression": "*/5 * * * *"},
            {"name": "daily-report", "cron_expression": "0 9 * * *"}
        ]
    }
)

## 第 3 步：修改你的代码 — 每次执行后主动汇报

这是最关键的一步。修改你的任务执行逻辑，在每次执行完毕后（无论成功还是失败）主动向 TaskPulse 汇报结果，这样看板才能展示实时状态。

在你的任务执行代码中，加上以下逻辑：

import time

def run_with_reporting(task_func, task_id, api_key):
    try:
        start = time.time()
        result = task_func()  # 你的任务逻辑
        elapsed = int((time.time() - start) * 1000)
        requests.post(f"{BASE}/api/tasks/{task_id}/executions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"status": "success", "duration_ms": elapsed, "log": str(result)})
    except Exception as e:
        requests.post(f"{BASE}/api/tasks/{task_id}/executions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"status": "failed", "duration_ms": 0, "error_message": str(e)})

# 使用示例 — 包裹你现有的任务函数：
run_with_reporting(my_task_function, TASK_ID, API_KEY)

## 第 4 步：保持活跃

定期发送心跳，让系统知道你仍在运行：

requests.post(f"{BASE}/api/agents/{AGENT_ID}/heartbeat",
    headers={"Authorization": f"Bearer {API_KEY}"})

---
完成以上步骤后，前往 TaskPulse 看板（本页面）查看你的运行状态和执行历史。如配置了通知渠道，任务超时未执行时系统会自动告警。`
})

onMounted(async () => {
  try {
    const [sumRes, taskRes, cfgRes] = await Promise.all([
      getDashboardSummary(),
      getDashboardTasks(),
      getSystemConfig(),
    ])
    summary.value = sumRes.data
    tasks.value = taskRes.data
    baseUrl.value = cfgRes.data.base_url
  } catch (e) {
    console.error('Failed to load dashboard', e)
  }
})

const copyScript = async () => {
  const text = scriptTab.value === 'curl' ? curlScript.value : pythonScript.value
  try {
    await navigator.clipboard.writeText(text)
    const { ElMessage } = await import('element-plus')
    ElMessage.success('已复制')
  } catch {
    const { ElMessage } = await import('element-plus')
    ElMessage.warning('复制失败，请手动复制')
  }
}
</script>

<style scoped>
.dashboard {
}

/* ── Onboarding Panel ─────────────────────────── */
.onboarding-panel {
  position: relative;
  background: linear-gradient(135deg, rgba(102,126,234,0.08) 0%, rgba(118,75,162,0.08) 100%);
  border: 1px solid rgba(102,126,234,0.15);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  overflow: hidden;
}
.onboarding-glow {
  position: absolute;
  top: -50%;
  right: -20%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(102,126,234,0.08) 0%, transparent 70%);
  pointer-events: none;
}
.onboarding-content {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
}
.onboarding-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a8b4ff;
  flex-shrink: 0;
}
.onboarding-text h3 {
  font-size: 16px;
  font-weight: 600;
  color: #e0e0f0;
  margin-bottom: 4px;
}
.onboarding-text p {
  font-size: 13px;
  color: rgba(255,255,255,0.45);
  margin: 0;
}
.btn-primary {
  margin-left: auto;
  padding: 8px 18px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity 0.2s;
}
.btn-primary:hover { opacity: 0.9; }
.onboarding-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  color: rgba(255,255,255,0.3);
  cursor: pointer;
  padding: 4px;
}
.onboarding-close:hover { color: #fff; }

/* Script block */
.onboarding-script {
  margin-top: 16px;
  background: rgba(0,0,0,0.3);
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}
.script-tabs {
  display: flex;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.script-tabs button {
  padding: 8px 16px;
  background: none;
  border: none;
  color: rgba(255,255,255,0.4);
  font-size: 12px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}
.script-tabs button.active {
  color: #a8b4ff;
  border-bottom-color: #667eea;
}
.script-body {
  padding: 16px;
  overflow-x: auto;
}
.script-body pre {
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.7;
  color: rgba(255,255,255,0.75);
  white-space: pre;
  margin: 0;
}
.btn-copy {
  position: absolute;
  top: 48px;
  right: 12px;
  padding: 4px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.5);
  font-size: 11px;
  cursor: pointer;
}
.btn-copy:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}

/* ── Stats Grid ───────────────────────────────── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 20px;
  display: flex;
  gap: 16px;
  transition: all 0.25s;
}
.stat-card:hover {
  border-color: var(--card-accent, rgba(255,255,255,0.1));
  box-shadow: 0 0 20px rgba(var(--card-accent, 255), 0.05);
  transform: translateY(-2px);
}
.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
  border: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--card-accent, #667eea);
  flex-shrink: 0;
}
.stat-body { flex: 1; }
.stat-label { font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
.stat-value { font-size: 28px; font-weight: 700; color: #e8e8f0; line-height: 1.1; margin-bottom: 6px; }
.stat-sub { font-size: 12px; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
.stat-dot {
  width: 5px; height: 5px; border-radius: 50%;
}
.stat-dot.active { background: #22c55e; box-shadow: 0 0 6px rgba(34,197,94,0.5); }

/* ── Task Table Section ───────────────────────── */
.section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  overflow: hidden;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}
.section-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #e0e0f0;
  margin: 0;
}
.section-link {
  font-size: 13px;
  color: var(--accent-1);
  text-decoration: none;
}
.section-link:hover { text-decoration: underline; }

.table-wrap {
  overflow-x: auto;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
}
.data-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  background: rgba(255,255,255,0.02);
  border-bottom: 1px solid var(--border-color);
}
.data-table td {
  padding: 12px 16px;
  font-size: 13px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
}
.data-table tbody tr:hover {
  background: rgba(255,255,255,0.02);
}
.cell-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  background: rgba(255,255,255,0.04);
  color: var(--text-secondary);
  font-size: 12px;
}
.cell-name {
  font-weight: 500;
}
.cell-code {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: #a8b4ff;
  background: rgba(102,126,234,0.1);
  padding: 2px 8px;
  border-radius: 4px;
}
.cell-mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--text-secondary);
}
.cell-muted { color: var(--text-muted); }
.cell-empty {
  text-align: center;
  color: var(--text-muted);
  padding: 40px 16px !important;
}
.cell-link {
  color: var(--accent-1);
  text-decoration: none;
  font-size: 13px;
}
.cell-link:hover { text-decoration: underline; }

/* Tags */
.tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}
.tag-green {
  background: rgba(34,197,94,0.12);
  color: #4ade80;
}
.tag-red {
  background: rgba(239,68,68,0.12);
  color: #f87171;
}
.tag-gray {
  background: rgba(255,255,255,0.05);
  color: var(--text-secondary);
}
</style>

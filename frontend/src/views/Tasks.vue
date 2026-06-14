<template>
  <div class="tasks-page">
    <div class="section mb-24">
      <div class="section-header collapsible" @click="showGuide = !showGuide">
        <h3>定时任务 — 由 AI Agent 自动管理</h3>
        <div class="section-toggle">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               :style="{ transform: showGuide ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
          <span class="toggle-label">{{ showGuide ? '收起指令' : '展开指令' }}</span>
        </div>
      </div>
      <div v-if="showGuide" class="onboard-body">
        <p>将下方指令发送给您的 AI Agent，它会自动汇报执行结果并管理定时任务。</p>
        <div class="code-block">
          <div class="code-tabs">
            <button :class="{ active: tab === 'report' }" @click="tab = 'report'">汇报执行</button>
            <button :class="{ active: tab === 'register' }" @click="tab = 'register'">注册任务</button>
            <button :class="{ active: tab === 'batch' }" @click="tab = 'batch'">批量注册</button>
          </div>
          <div class="code-body">
            <pre>{{ codes[tab] }}</pre>
          </div>
          <button class="btn-copy" @click="copyCode">复制</button>
        </div>
      </div>
    </div>

    <!-- Task list -->
    <div class="section">
      <div class="section-header">
        <h3>所有任务</h3>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
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
              <td class="cell-mono">#{{ t.id }}</td>
              <td><span class="cell-badge">{{ t.agent_name }}</span></td>
              <td class="cell-name">{{ t.name }}</td>
              <td><code class="cell-code">{{ t.cron_expression }}</code></td>
              <td>
                <span class="tag" :class="t.status === 'active' ? 'tag-green' : 'tag-gray'">
                  {{ t.status === 'active' ? '运行中' : t.status === 'paused' ? '已暂停' : '已停止' }}
                </span>
              </td>
              <td class="cell-mono">{{ t.last_run_at ? beijing(t.last_run_at) : '—' }}</td>
              <td>
                <span v-if="t.last_run_result" class="tag" :class="t.last_run_result === 'success' ? 'tag-green' : 'tag-red'">
                  {{ t.last_run_result === 'success' ? '成功' : '失败' }}
                </span>
                <span v-else class="cell-muted">—</span>
              </td>
              <td class="cell-mono">{{ t.total_run_count }}</td>
              <td>
                <router-link :to="`/tasks/${t.id}`" class="cell-link">详情</router-link>
                <button class="btn-icon" @click="handleDelete(t)" title="删除">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                </button>
              </td>
            </tr>
            <tr v-if="tasks.length === 0">
              <td colspan="9" class="cell-empty">暂无任务 — Agent 注册后会自动出现在这里</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { beijing } from '../utils/time.js'
import { listTasks, deleteTask, getSystemConfig } from '../api/index.js'

const tasks = ref([])
const tab = ref('report')
const showGuide = ref(false)
const baseUrl = ref(window.location.origin)

const loadData = async () => {
  const [taskRes, cfgRes] = await Promise.all([
    listTasks(),
    getSystemConfig(),
  ])
  tasks.value = taskRes.data
  baseUrl.value = cfgRes.data.base_url
}

const handleDelete = async (row) => {
  try {
    await deleteTask(row.id)
    await loadData()
  } catch (e) {
    console.error(e)
  }
}

const codes = computed(() => {
  const b = baseUrl.value
  return {
    report: `# TaskPulse — 汇报执行结果

你已注册到 TaskPulse。每次任务运行后（无论成功失败），主动汇报执行结果。

## 汇报成功

curl -X POST ${b}/api/tasks/<TASK_ID>/executions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer <API_KEY>" \\
  -d '{"status":"success","duration_ms":2500,"log":"[INFO] 任务执行完成，同步了100条记录"}'

## 汇报失败

curl -X POST ${b}/api/tasks/<TASK_ID>/executions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer <API_KEY>" \\
  -d '{"status":"failed","duration_ms":1200,"log":"[ERROR] 连接超时","error_message":"TimeoutError: connection to DB timed out"}'

## 修改你的代码自动汇报

在你的每个定时任务函数末尾，加上汇报逻辑。参考以下实现：

import time
import requests

def run_task(task_func, task_id, api_key):
    """包裹你的任务函数，自动汇报执行结果"""
    start = time.time()
    try:
        result = task_func()
        elapsed = int((time.time() - start) * 1000)
        requests.post(f"${b}/api/tasks/{task_id}/executions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"status": "success", "duration_ms": elapsed, "log": str(result)})
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        requests.post(f"${b}/api/tasks/{task_id}/executions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"status": "failed", "duration_ms": elapsed, "error_message": str(e)})

# 在你的循环/调度中这样使用：
run_task(my_task_func, TASK_ID, API_KEY)`,
    register: `# TaskPulse — 注册新任务

你需要注册自己管理的每一个定时任务，系统才知道你的执行计划。

## 单个注册

curl -X POST "${b}/api/tasks?agent_id=<AGENT_ID>" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer <API_KEY>" \\
  -d '{"name":"数据同步","cron_expression":"*/5 * * * *","description":"每5分钟同步一次数据","grace_period":300}'

参数说明：
- name: 任务名称（必填）
- cron_expression: Cron 表达式，格式：分 时 日 月 周（必填）
- description: 任务描述（可选）
- grace_period: 容忍窗口（秒），任务超时N秒未执行则告警（默认300）

## 查看已注册的任务

curl -X GET "${b}/api/tasks" \\
  -H "Authorization: Bearer <API_KEY>"

## 更新现有任务（修改 cron 等）

curl -X PUT "${b}/api/tasks/<TASK_ID>" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer <API_KEY>" \\
  -d '{"cron_expression":"0 * * * *","status":"active"}'

## 删除任务

curl -X DELETE "${b}/api/tasks/<TASK_ID>" \\
  -H "Authorization: Bearer <API_KEY>"`,
    batch: `# TaskPulse — 批量注册（推荐）

如果你有多个定时任务，推荐使用批量注册接口，一次完成 Agent 注册 + 所有任务登记。

## 批量注册 Agent + 全部任务

curl -X POST ${b}/api/agents/register-with-tasks \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "<你的Agent名称>",
    "description": "<你的职责描述>",
    "tasks": [
      {"name": "数据同步", "cron_expression": "*/5 * * * *", "description": "定时同步数据", "grace_period": 300},
      {"name": "日报通知", "cron_expression": "0 9 * * *", "description": "每天早上9点生成报告", "grace_period": 600},
      {"name": "周报汇总", "cron_expression": "0 10 * * 1", "description": "每周一早10点汇总", "grace_period": 900}
    ]
  }'

响应中包含 agent 信息和任务创建数量。返回的 api_key 请保存好。

## Python 示例

import requests

resp = requests.post(f"${b}/api/agents/register-with-tasks", json={
    "name": "data-agent",
    "description": "数据相关的全部定时任务",
    "tasks": [
        {"name": "sync-data", "cron_expression": "*/5 * * * *"},
        {"name": "daily-report", "cron_expression": "0 9 * * *"}
    ]
})
result = resp.json()
print(f"Agent ID: {result['agent']['id']}, 任务数: {result['tasks_created']}")
API_KEY = result["agent"]["api_key"]

---

注册完成后，回到仪表盘页面，将「汇报执行结果」的指令一并发送给 AI Agent，它就知道如何自动向你汇报运行状态。`,
  }
})

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(codes.value[tab.value])
    const { ElMessage } = await import('element-plus')
    ElMessage.success('已复制')
  } catch {}
}

onMounted(loadData)
</script>

<style scoped>
.tasks-page { max-width: 1200px; }
.mb-24 { margin-bottom: 24px; }

.section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  overflow: hidden;
}
.section-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}
.section-header h3 { font-size: 15px; font-weight: 600; color: #e0e0f0; margin: 0; }
.section-header.collapsible { cursor: pointer; user-select: none; }
.section-header.collapsible:hover { background: rgba(255,255,255,0.02); }
.section-toggle {
  display: flex; align-items: center; gap: 6px;
  color: var(--text-muted); font-size: 12px;
}
.section-toggle:hover { color: var(--text-secondary); }

.onboard-body { padding: 20px; }
.onboard-body > p { font-size: 13px; color: var(--text-secondary); margin-bottom: 16px; }

.code-block {
  position: relative;
  background: rgba(0,0,0,0.3);
  border-radius: 10px;
  overflow: hidden;
}
.code-tabs { display: flex; border-bottom: 1px solid rgba(255,255,255,0.06); }
.code-tabs button {
  padding: 8px 16px; background: none; border: none;
  color: rgba(255,255,255,0.4); font-size: 12px; cursor: pointer;
  border-bottom: 2px solid transparent;
}
.code-tabs button.active { color: #a8b4ff; border-bottom-color: #667eea; }
.code-body { padding: 16px; overflow-x: auto; }
.code-body pre {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12px; line-height: 1.7; color: rgba(255,255,255,0.75);
  white-space: pre; margin: 0;
}
.btn-copy {
  position: absolute; top: 44px; right: 12px;
  padding: 4px 12px; border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.5); font-size: 11px; cursor: pointer;
}
.btn-copy:hover { background: rgba(255,255,255,0.1); color: #fff; }

.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
  text-align: left; padding: 12px 16px; font-size: 11px; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.5px;
  color: var(--text-secondary); background: rgba(255,255,255,0.02);
  border-bottom: 1px solid var(--border-color);
}
.data-table td {
  padding: 12px 16px; font-size: 13px;
  color: var(--text-primary); border-bottom: 1px solid var(--border-color);
}
.data-table tbody tr:hover { background: rgba(255,255,255,0.02); }
.cell-badge {
  display: inline-block; padding: 2px 10px; border-radius: 20px;
  background: rgba(255,255,255,0.04); color: var(--text-secondary); font-size: 12px;
}
.cell-name { font-weight: 500; }
.cell-code {
  font-family: 'JetBrains Mono', monospace; font-size: 12px;
  color: #a8b4ff; background: rgba(102,126,234,0.1);
  padding: 2px 8px; border-radius: 4px;
}
.cell-mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-secondary); }
.cell-muted { color: var(--text-muted); }
.cell-empty { text-align: center; color: var(--text-muted); padding: 40px 16px !important; }
.cell-link { color: var(--accent-1); text-decoration: none; font-size: 13px; margin-right: 8px; }
.cell-link:hover { text-decoration: underline; }

.tag { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 500; }
.tag-green { background: rgba(34,197,94,0.12); color: #4ade80; }
.tag-red { background: rgba(239,68,68,0.12); color: #f87171; }
.tag-gray { background: rgba(255,255,255,0.05); color: var(--text-secondary); }

.btn-icon {
  background: none; border: none; color: var(--text-muted);
  cursor: pointer; padding: 4px; vertical-align: middle;
}
.btn-icon:hover { color: var(--danger); }
</style>

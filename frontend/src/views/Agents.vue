<template>
  <div class="agents-page">
    <!-- Quick onboard -->
    <div class="section mb-24">
      <div class="section-header">
        <h3>Agent 接入指南</h3>
      </div>
      <div class="onboard-body">
        <p>让 AI Agent 通过以下方式自动注册，无需手动填写。</p>
        <div class="code-block">
          <div class="code-tabs">
            <button :class="{ active: tab === 'curl' }" @click="tab = 'curl'">curl</button>
            <button :class="{ active: tab === 'python' }" @click="tab = 'python'">Python</button>
            <button :class="{ active: tab === 'batch' }" @click="tab = 'batch'">批量注册</button>
          </div>
          <div class="code-body">
            <pre>{{ codes[tab] }}</pre>
          </div>
          <button class="btn-copy" @click="copyCode">复制</button>
        </div>
      </div>
    </div>

    <!-- Agent list -->
    <div class="section">
      <div class="section-header">
        <h3>已注册 Agent</h3>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>描述</th>
              <th>状态</th>
              <th>任务数</th>
              <th>最后心跳</th>
              <th>API Key</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in agents" :key="a.id">
              <td class="cell-mono">#{{ a.id }}</td>
              <td class="cell-name">{{ a.name }}</td>
              <td class="cell-muted">{{ a.description || '—' }}</td>
              <td>
                <span class="tag" :class="a.status === 'active' ? 'tag-green' : 'tag-gray'">
                  {{ a.status === 'active' ? '活跃' : '停用' }}
                </span>
              </td>
              <td class="cell-mono">{{ a.task_count }}</td>
              <td class="cell-mono">{{ a.last_heartbeat_at ? dayjs(a.last_heartbeat_at).format('MM-DD HH:mm') : '—' }}</td>
              <td>
                <code class="cell-key">{{ a.api_key.substring(0, 16) }}...</code>
                <button class="btn-icon" @click="copyKey(a.api_key)" title="复制 API Key">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                </button>
              </td>
              <td>
                <router-link to="/tasks" class="cell-link">任务</router-link>
              </td>
            </tr>
            <tr v-if="agents.length === 0">
              <td colspan="8" class="cell-empty">暂无 Agent — 让 AI Agent 调用上方 API 自动注册</td>
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
import { listAgents, getSystemConfig } from '../api/index.js'

const agents = ref([])
const tab = ref('curl')
const baseUrl = ref(window.location.origin)

const loadData = async () => {
  const [agentRes, cfgRes] = await Promise.all([
    listAgents(),
    getSystemConfig(),
  ])
  agents.value = agentRes.data
  baseUrl.value = cfgRes.data.base_url
}

const copyKey = async (key) => {
  try {
    await navigator.clipboard.writeText(key)
    const { ElMessage } = await import('element-plus')
    ElMessage.success('已复制 API Key')
  } catch {}
}

const codes = computed(() => {
  const b = baseUrl.value
  return {
    curl: `# 注册单个 Agent
curl -X POST ${b}/api/agents \\
  -H "Content-Type: application/json" \\
  -d '{"name": "my-agent", "description": "你的 AI Agent"}'`,
    python: `import requests\n\nresp = requests.post("${b}/api/agents", json={\n    "name": "my-agent",\n    "description": "你的 AI Agent"\n})\nprint(resp.json())`,
    batch: `curl -X POST ${b}/api/agents/register-with-tasks \\\n  -H "Content-Type: application/json" \\\n  -d '{\n    "name": "my-agent",\n    "description": "全能数据Agent",\n    "tasks": [\n      {"name": "sync-data", "cron_expression": "*/5 * * * *"},\n      {"name": "daily-report", "cron_expression": "0 9 * * *"}\n    ]\n  }'`,
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
.agents-page { max-width: 1200px; }
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

.onboard-body {
  padding: 20px;
}
.onboard-body > p {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.code-block {
  position: relative;
  background: rgba(0,0,0,0.3);
  border-radius: 10px;
  overflow: hidden;
}
.code-tabs {
  display: flex;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.code-tabs button {
  padding: 8px 16px;
  background: none;
  border: none;
  color: rgba(255,255,255,0.4);
  font-size: 12px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}
.code-tabs button.active {
  color: #a8b4ff;
  border-bottom-color: #667eea;
}
.code-body { padding: 16px; overflow-x: auto; }
.code-body pre {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12px;
  line-height: 1.7;
  color: rgba(255,255,255,0.75);
  white-space: pre;
  margin: 0;
}
.btn-copy {
  position: absolute;
  top: 44px;
  right: 12px;
  padding: 4px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.5);
  font-size: 11px;
  cursor: pointer;
}
.btn-copy:hover { background: rgba(255,255,255,0.1); color: #fff; }

/* Table */
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
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
.data-table tbody tr:hover { background: rgba(255,255,255,0.02); }
.cell-name { font-weight: 500; }
.cell-mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-secondary); }
.cell-muted { color: var(--text-muted); }
.cell-key { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-muted); }
.cell-empty { text-align: center; color: var(--text-muted); padding: 40px 16px !important; }
.cell-link { color: var(--accent-1); text-decoration: none; font-size: 13px; }
.cell-link:hover { text-decoration: underline; }

.tag { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 500; }
.tag-green { background: rgba(34,197,94,0.12); color: #4ade80; }
.tag-gray { background: rgba(255,255,255,0.05); color: var(--text-secondary); }

.btn-icon {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  vertical-align: middle;
}
.btn-icon:hover { color: var(--accent-1); }
</style>

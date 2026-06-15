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
              <td>
                <span class="agent-avatar" :style="{background: $avatar(a.name).bg}">{{ $avatar(a.name).letter }}</span>
                <span class="cell-name">{{ a.name }}</span>
              </td>
              <td class="cell-muted">{{ a.description || '—' }}</td>
              <td>
                <span class="tag" :class="a.status === 'active' ? 'tag-green' : 'tag-gray'">
                  {{ a.status === 'active' ? '活跃' : '停用' }}
                </span>
              </td>
              <td class="cell-mono">{{ a.task_count }}</td>
              <td class="cell-mono">{{ a.last_heartbeat_at ? dayjs.utc(a.last_heartbeat_at).local().format('MM-DD HH:mm') : '—' }}</td>
              <td>
                <code class="cell-key">{{ a.api_key.substring(0, 16) }}...</code>
                <button class="btn-icon" @click="copyKey(a.api_key)" title="复制 API Key">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                </button>
              </td>
              <td>
                <router-link to="/tasks" class="cell-link">任务</router-link>
                <button class="cell-link-btn" style="color:var(--accent-1)" @click="showEdit(a)">编辑</button>
                <button class="cell-link-btn" style="color:var(--danger)" @click="confirmDelete(a)">删除</button>
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

  <!-- Edit Agent Modal -->
  <div v-if="editAgent" class="modal-overlay" @click.self="editAgent = null">
    <div class="modal">
      <div class="modal-header">
        <h4>编辑 Agent</h4>
        <button class="modal-close" @click="editAgent = null">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="modal-body">
        <div class="field">
          <label>Agent 名称</label>
          <div class="field-avatar-row">
            <span class="agent-avatar-lg" :style="{background: $avatar(editForm.name).bg}">{{ $avatar(editForm.name).letter }}</span>
            <input v-model="editForm.name" class="input" placeholder="Agent 名称" />
          </div>
        </div>
        <div class="field">
          <label>描述</label>
          <input v-model="editForm.description" class="input" placeholder="描述" />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" @click="editAgent = null">取消</button>
        <button class="btn-primary" @click="handleEdit">保存</button>
      </div>
    </div>
  </div>

  <!-- Delete Confirm Modal -->
  <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
    <div class="modal" style="width:400px">
      <div class="modal-header">
        <h4>删除 Agent</h4>
        <button class="modal-close" @click="deleteTarget = null">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="modal-body">
        <p style="color:var(--text-secondary);font-size:14px;line-height:1.6">
          确定要删除 Agent <strong style="color:var(--text-primary)">{{ deleteTarget.name }}</strong> 吗？
        </p>
        <p style="color:var(--text-muted);font-size:12px;margin-top:8px">
          其关联的定时任务也将一并删除。Agent 后续仍可重新注册。
        </p>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" @click="deleteTarget = null">取消</button>
        <button class="btn-danger" @click="handleDelete">确认删除</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import dayjs from 'dayjs'
import { listAgents, updateAgent, deleteAgent, getSystemConfig } from '../api/index.js'

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

// Edit
const editAgent = ref(null)
const editForm = ref({ name: '', description: '' })
const showEdit = (agent) => {
  editForm.value = { name: agent.name, description: agent.description }
  editAgent.value = agent
}
const handleEdit = async () => {
  try {
    await updateAgent(editAgent.value.id, editForm.value)
    editAgent.value = null
    await loadData()
    const { ElMessage } = await import('element-plus')
    ElMessage.success('已更新')
  } catch (e) {
    console.error(e)
  }
}

// Delete
const deleteTarget = ref(null)
const confirmDelete = (agent) => { deleteTarget.value = agent }
const handleDelete = async () => {
  try {
    await deleteAgent(deleteTarget.value.id)
    deleteTarget.value = null
    await loadData()
    const { ElMessage } = await import('element-plus')
    ElMessage.success('已删除')
  } catch (e) {
    console.error(e)
  }
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
.agents-page {}
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

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
}
.modal {
  width: 480px; max-width: 90vw;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  overflow: hidden;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid var(--border-color);
}
.modal-header h4 { font-size: 15px; font-weight: 600; color: #e0e0f0; margin: 0; }
.modal-close { background: none; border: none; color: var(--text-muted); cursor: pointer; }
.modal-close:hover { color: #fff; }
.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 16px 20px; border-top: 1px solid var(--border-color);
}

.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 12px; color: var(--text-secondary); }
.field-avatar-row { display: flex; align-items: center; gap: 12px; }
.input {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: rgba(255,255,255,0.04);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}
.input:focus { border-color: var(--accent-1); }

.agent-avatar-lg {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  flex-shrink: 0;
}

.btn-primary {
  padding: 7px 16px; border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff; font-size: 13px; font-weight: 500;
  cursor: pointer;
}
.btn-primary:hover { opacity: 0.9; }
.btn-secondary {
  padding: 7px 16px; border-radius: 8px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary); font-size: 13px;
  cursor: pointer;
}
.btn-secondary:hover { color: #fff; border-color: rgba(255,255,255,0.15); }
.btn-danger {
  padding: 7px 16px; border-radius: 8px;
  border: none;
  background: rgba(239,68,68,0.8);
  color: #fff; font-size: 13px; font-weight: 500;
  cursor: pointer;
}
.btn-danger:hover { background: #ef4444; }

.cell-link-btn {
  background: none; border: none;
  font-size: 13px; cursor: pointer;
  margin-left: 8px;
}
.cell-link-btn:hover { text-decoration: underline; }
</style>

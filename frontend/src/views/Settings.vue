<template>
  <div class="settings-page">
    <!-- System Configuration -->
    <div class="section mb-24">
      <div class="section-header">
        <h3>系统配置</h3>
      </div>
      <div class="config-body">
        <div class="config-row">
          <div class="config-info">
            <div class="config-label">公网访问地址 (Base URL)</div>
            <div class="config-desc">AI Agent 可通过此地址访问本系统 API。修改后页面上的接入指令会自动更新。</div>
          </div>
          <div class="config-input-group">
            <input v-model="configForm.base_url" class="input config-input" placeholder="https://your-domain.com" />
            <button class="btn-primary" @click="handleSaveConfig" :disabled="savingConfig">
              {{ savingConfig ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
        <div v-if="configSaved" class="config-success">配置已保存</div>
      </div>
    </div>

    <!-- Notification Channels -->
    <div class="section mb-24">
      <div class="section-header">
        <h3>通知渠道</h3>
        <button class="btn-primary" @click="showChannelDialog = true">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          添加渠道
        </button>
      </div>

      <div class="card-grid">
        <div v-for="c in channels" :key="c.id" class="channel-card">
          <div class="channel-top">
            <div class="channel-icon" :class="c.channel_type">
              <svg v-if="c.channel_type === 'feishu_cli'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/><path d="M5 15h14l-1.5 6H6.5L5 15z"/></svg>
              <svg v-else-if="c.channel_type === 'email'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
            </div>
            <div>
              <div class="channel-name">{{ c.name }}</div>
              <div class="channel-type">{{ c.channel_type === 'feishu_cli' ? '飞书' : c.channel_type === 'email' ? '邮件' : 'Webhook' }}</div>
            </div>
            <div class="channel-spacer"></div>
            <label class="toggle">
              <input type="checkbox" :checked="c.enabled" @change="(e) => toggleChannel(c, e.target.checked)">
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="channel-config">{{ c.config }}</div>
          <button class="channel-delete" @click="handleDeleteChannel(c)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
          </button>
        </div>
        <div v-if="channels.length === 0" class="empty-state">
          <p>暂无通知渠道 — 添加飞书或邮件通知</p>
        </div>
      </div>
    </div>

    <!-- Alert Rules -->
    <div class="section mb-24">
      <div class="section-header">
        <h3>告警规则</h3>
        <button class="btn-primary" @click="showRuleDialog = true">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          添加规则
        </button>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>任务</th>
              <th>通知渠道</th>
              <th>告警类型</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in rules" :key="r.id">
              <td class="cell-mono">#{{ r.id }}</td>
              <td class="cell-name">任务 #{{ r.task_id }}</td>
              <td>{{ r.channel_name }}</td>
              <td><span class="tag" :class="r.alert_type === 'missed_run' ? 'tag-warn' : 'tag-red'">{{ r.alert_type === 'missed_run' ? '未按时执行' : '执行失败' }}</span></td>
              <td><button class="cell-link-btn" @click="handleDeleteRule(r)">删除</button></td>
            </tr>
            <tr v-if="rules.length === 0">
              <td colspan="5" class="cell-empty">暂无规则</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Channel Modal -->
    <div v-if="showChannelDialog" class="modal-overlay" @click.self="showChannelDialog = false">
      <div class="modal">
        <div class="modal-header">
          <h4>添加通知渠道</h4>
          <button class="modal-close" @click="showChannelDialog = false"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
        </div>
        <div class="modal-body">
          <div class="field">
            <label>渠道名称</label>
            <input v-model="channelForm.name" placeholder="例如：我的飞书" class="input" />
          </div>
          <div class="field">
            <label>渠道类型</label>
            <select v-model="channelForm.channel_type" class="input">
              <option value="feishu_cli">飞书 Webhook</option>
              <option value="email">邮件 (SMTP)</option>
              <option value="webhook">通用 Webhook</option>
            </select>
          </div>
          <div class="field">
            <label>配置 (JSON)</label>
            <textarea v-model="channelForm.config" rows="4" class="input" placeholder='飞书: {"webhook_url":"..."}'></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showChannelDialog = false">取消</button>
          <button class="btn-primary" @click="handleAddChannel">添加</button>
        </div>
      </div>
    </div>

    <!-- Add Rule Modal -->
    <div v-if="showRuleDialog" class="modal-overlay" @click.self="showRuleDialog = false">
      <div class="modal">
        <div class="modal-header">
          <h4>添加告警规则</h4>
          <button class="modal-close" @click="showRuleDialog = false"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
        </div>
        <div class="modal-body">
          <div class="field">
            <label>任务</label>
            <select v-model="ruleForm.task_id" class="input">
              <option v-for="t in allTasks" :key="t.id" :value="t.id">[{{ t.id }}] {{ t.name }}</option>
            </select>
          </div>
          <div class="field">
            <label>通知渠道</label>
            <select v-model="ruleForm.channel_id" class="input">
              <option v-for="c in channels" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div class="field">
            <label>告警类型</label>
            <select v-model="ruleForm.alert_type" class="input">
              <option value="missed_run">未按时执行</option>
              <option value="failure">执行失败</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showRuleDialog = false">取消</button>
          <button class="btn-primary" @click="handleAddRule">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  listChannels, createChannel, updateChannel, deleteChannel,
  listAlertRules, createAlertRule, deleteAlertRule,
  listTasks, getSystemConfig, saveSystemConfig,
} from '../api/index.js'

const channels = ref([])
const rules = ref([])
const allTasks = ref([])
const showChannelDialog = ref(false)
const showRuleDialog = ref(false)
const channelForm = ref({ name: '', channel_type: 'feishu_cli', config: '' })
const ruleForm = ref({ task_id: null, channel_id: null, alert_type: 'missed_run' })

// System config
const configForm = ref({ base_url: '' })
const savingConfig = ref(false)
const configSaved = ref(false)

const loadData = async () => {
  const [chRes, ruleRes, taskRes, cfgRes] = await Promise.all([
    listChannels(), listAlertRules(), listTasks(), getSystemConfig(),
  ])
  channels.value = chRes.data
  rules.value = ruleRes.data
  allTasks.value = taskRes.data
  configForm.value.base_url = cfgRes.data.base_url
}

const handleSaveConfig = async () => {
  savingConfig.value = true
  configSaved.value = false
  try {
    const res = await saveSystemConfig({ base_url: configForm.value.base_url })
    configForm.value.base_url = res.data.base_url
    configSaved.value = true
    setTimeout(() => { configSaved.value = false }, 3000)
  } catch (e) {
    console.error(e)
  } finally {
    savingConfig.value = false
  }
}

const handleAddChannel = async () => {
  try {
    await createChannel(channelForm.value)
    showChannelDialog.value = false
    channelForm.value = { name: '', channel_type: 'feishu_cli', config: '' }
    await loadData()
  } catch (e) { console.error(e) }
}

const toggleChannel = async (row, enabled) => {
  try { await updateChannel(row.id, { enabled }) } catch (e) { console.error(e) }
}

const handleDeleteChannel = async (row) => {
  try { await deleteChannel(row.id); await loadData() } catch (e) { console.error(e) }
}

const handleAddRule = async () => {
  try {
    await createAlertRule(ruleForm.value)
    showRuleDialog.value = false
    ruleForm.value = { task_id: null, channel_id: null, alert_type: 'missed_run' }
    await loadData()
  } catch (e) { console.error(e) }
}

const handleDeleteRule = async (row) => {
  try { await deleteAlertRule(row.id); await loadData() } catch (e) { console.error(e) }
}

onMounted(loadData)
</script>

<style scoped>
.settings-page {}
.mb-24 { margin-bottom: 24px; }

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
.section-header h3 { font-size: 15px; font-weight: 600; color: #e0e0f0; margin: 0; }

/* System Config */
.config-body { padding: 20px; }
.config-row { display: flex; align-items: flex-start; gap: 20px; }
.config-info { flex: 1; }
.config-label { font-size: 14px; font-weight: 500; color: var(--text-primary); margin-bottom: 4px; }
.config-desc { font-size: 12px; color: var(--text-muted); line-height: 1.5; }
.config-input-group { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
.config-input { width: 320px; }
.config-success {
  margin-top: 12px;
  font-size: 13px;
  color: #4ade80;
  padding: 6px 12px;
  background: rgba(34,197,94,0.1);
  border-radius: 6px;
  display: inline-block;
}

/* Cards */
.card-grid { padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.channel-card {
  position: relative;
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 16px;
}
.channel-top { display: flex; align-items: center; gap: 12px; }
.channel-icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.channel-icon.feishu_cli { background: rgba(102,126,234,0.15); color: #a8b4ff; }
.channel-icon.email { background: rgba(34,197,94,0.15); color: #4ade80; }
.channel-icon.webhook { background: rgba(245,158,11,0.15); color: #fbbf24; }
.channel-spacer { flex: 1; }
.channel-name { font-size: 14px; font-weight: 500; color: var(--text-primary); }
.channel-type { font-size: 11px; color: var(--text-muted); }
.channel-config {
  margin-top: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.channel-delete {
  position: absolute; top: 12px; right: 12px;
  background: none; border: none;
  color: var(--text-muted); cursor: pointer;
}
.channel-delete:hover { color: var(--danger); }

/* Toggle */
.toggle { position: relative; display: inline-block; width: 36px; height: 20px; }
.toggle input { opacity: 0; width: 0; height: 0; }
.toggle-slider {
  position: absolute; inset: 0;
  background: rgba(255,255,255,0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: 0.2s;
}
.toggle-slider::before {
  content: '';
  position: absolute;
  width: 16px; height: 16px;
  left: 2px; top: 2px;
  background: #fff;
  border-radius: 50%;
  transition: 0.2s;
}
.toggle input:checked + .toggle-slider { background: var(--accent-1); }
.toggle input:checked + .toggle-slider::before { transform: translateX(16px); }

/* Table */
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
.cell-mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-secondary); }
.cell-name { font-weight: 500; }
.cell-empty { text-align: center; color: var(--text-muted); padding: 40px 16px !important; }
.cell-link-btn { background: none; border: none; color: var(--danger); font-size: 13px; cursor: pointer; }
.cell-link-btn:hover { text-decoration: underline; }

.tag { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 500; }
.tag-warn { background: rgba(245,158,11,0.12); color: #fbbf24; }
.tag-red { background: rgba(239,68,68,0.12); color: #f87171; }

.empty-state { text-align: center; padding: 40px 20px; color: var(--text-muted); }

/* Buttons */
.btn-primary {
  display: inline-flex; align-items: center; gap: 6px;
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

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
}
.modal {
  width: 500px; max-width: 90vw;
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
.input {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: rgba(255,255,255,0.04);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}
.input:focus { border-color: var(--accent-1); }
textarea.input { resize: vertical; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
select.input { cursor: pointer; }
</style>

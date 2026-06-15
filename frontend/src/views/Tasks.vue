<template>
  <div class="tasks-page">
    <!-- Search & Filter Bar -->
    <div class="section mb-24">
      <div class="section-header">
        <h3>所有任务</h3>
      </div>
      <div class="search-bar">
        <div class="search-input-wrap">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input v-model="searchQ" class="search-input" placeholder="搜索任务名称..." @input="loadData" />
        </div>
        <input v-model="searchTags" class="search-input" style="width:200px" placeholder="标签筛选（逗号分隔）" @input="loadData" />
        <select v-model="searchStatus" class="search-input" style="width:130px" @change="loadData">
          <option value="">全部状态</option>
          <option value="active">运行中</option>
          <option value="paused">已暂停</option>
          <option value="stopped">已停止</option>
        </select>
      </div>
    </div>

    <!-- Task list -->
    <div class="section">
      <div class="section-header">
        <h3>任务列表（{{ tasks.length }}）</h3>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Agent</th>
              <th>任务名称</th>
              <th>Cron</th>
              <th>标签</th>
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
              <td>
                <span class="agent-avatar" :style="{background: $avatar(t.agent_name).bg}">{{ $avatar(t.agent_name).letter }}</span>
                <span class="cell-badge">{{ t.agent_name }}</span>
              </td>
              <td class="cell-name">{{ t.name }}</td>
              <td><code class="cell-code" :title="t.cron_expression">{{ $cron(t.cron_expression) }}</code></td>
              <td>
                <span v-for="tag in (t.tags || [])" :key="tag" class="tag-pill">{{ tag }}</span>
                <span v-if="!t.tags || t.tags.length === 0" class="cell-muted">—</span>
              </td>
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
                <button class="cell-link-btn" style="color:var(--accent-1);margin-left:6px" @click="showEdit(t)">编辑</button>
                <button class="cell-link-btn" style="color:var(--danger);margin-left:4px" @click="handleDelete(t)">删除</button>
              </td>
            </tr>
            <tr v-if="tasks.length === 0">
              <td colspan="10" class="cell-empty">暂无任务 — Agent 注册后会自动出现在这里</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Task Modal -->
    <div v-if="editTask" class="modal-overlay" @click.self="editTask = null">
      <div class="modal modal-wide">
        <div class="modal-header">
          <h4>编辑任务</h4>
          <button class="modal-close" @click="editTask = null">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-fields">
            <div class="field">
              <label>任务名称</label>
              <input v-model="editForm.name" class="input" />
            </div>
            <div class="field">
              <label>标签（回车添加）</label>
              <div class="tags-edit">
                <span v-for="(tag, i) in editForm.tags" :key="i" class="tag-pill">
                  {{ tag }}
                  <button class="tag-remove" @click="editForm.tags.splice(i, 1)">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  </button>
                </span>
                <input v-model="tagInput" class="tag-input" placeholder="输入标签后回车" @keydown.enter.prevent="addTag" @keydown.,.prevent="addTag" />
              </div>
            </div>
            <div class="field">
              <label>描述</label>
              <input v-model="editForm.description" class="input" placeholder="任务描述（选填）" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="editTask = null">取消</button>
          <button class="btn-primary" @click="handleEdit">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'
import { listTasks, deleteTask, updateTask } from '../api/index.js'

const tasks = ref([])
const searchQ = ref('')
const searchTags = ref('')
const searchStatus = ref('')

const loadData = async () => {
  const params = {}
  if (searchQ.value) params.q = searchQ.value
  if (searchTags.value) params.tags = searchTags.value
  if (searchStatus.value) params.status = searchStatus.value
  const res = await listTasks(params)
  tasks.value = res.data
}

// Edit
const editTask = ref(null)
const editForm = ref({ name: '', description: '', tags: [] })
const tagInput = ref('')

const addTag = () => {
  const val = tagInput.value.replace(/,/g, '').trim()
  if (val && !editForm.value.tags.includes(val)) editForm.value.tags.push(val)
  tagInput.value = ''
}

const showEdit = (t) => {
  editForm.value = {
    name: t.name,
    description: t.description || '',
    tags: [...(t.tags || [])],
  }
  editTask.value = t
}

const handleEdit = async () => {
  try {
    await updateTask(editTask.value.id, editForm.value)
    editTask.value = null
    await loadData()
    const { ElMessage } = await import('element-plus')
    ElMessage.success('已保存')
  } catch (e) { console.error(e) }
}

const handleDelete = async (row) => {
  try {
    await deleteTask(row.id)
    await loadData()
  } catch (e) { console.error(e) }
}

onMounted(loadData)
</script>

<style scoped>
.tasks-page {}
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

/* Search */
.search-bar {
  display: flex; gap: 10px; padding: 12px 20px;
  align-items: center;
}
.search-input-wrap {
  display: flex; align-items: center; gap: 8px; flex: 1;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: rgba(255,255,255,0.04);
  color: var(--text-muted);
}
.search-input-wrap svg { flex-shrink: 0; }
.search-input {
  flex: 1;
  padding: 8px 0;
  background: none;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 13px;
}
.search-input::placeholder { color: var(--text-muted); }

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
.cell-link { color: var(--accent-1); text-decoration: none; font-size: 13px; }
.cell-link:hover { text-decoration: underline; }
.cell-link-btn { background: none; border: none; font-size: 12px; cursor: pointer; }
.cell-link-btn:hover { text-decoration: underline; }

.tag { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 500; }
.tag-green { background: rgba(34,197,94,0.12); color: #4ade80; }
.tag-red { background: rgba(239,68,68,0.12); color: #f87171; }
.tag-gray { background: rgba(255,255,255,0.05); color: var(--text-secondary); }

/* Tag Pills */
.tag-pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  background: rgba(102,126,234,0.12);
  color: #a8b4ff;
  margin-right: 4px;
  margin-bottom: 2px;
  white-space: nowrap;
}

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
}
.modal {
  width: 480px; max-width: 90vw;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  overflow: hidden;
}
.modal-wide { width: 560px; }
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid var(--border-color);
}
.modal-header h4 { font-size: 15px; font-weight: 600; color: #e0e0f0; margin: 0; }
.modal-close { background: none; border: none; color: var(--text-muted); cursor: pointer; }
.modal-close:hover { color: #fff; }
.modal-body { padding: 20px; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 16px 20px; border-top: 1px solid var(--border-color);
}

.form-fields { display: flex; flex-direction: column; gap: 16px; }
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
}
.input:focus { border-color: var(--accent-1); }
select.input { cursor: pointer; }

.tags-edit {
  display: flex; flex-wrap: wrap; gap: 4px;
  padding: 6px 8px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: rgba(255,255,255,0.04);
  min-height: 36px;
  align-items: center;
}
.tag-remove { background: none; border: none; color: inherit; cursor: pointer; padding: 0; margin-left: 2px; opacity: 0.6; }
.tag-remove:hover { opacity: 1; }
.tag-input {
  flex: 1; min-width: 100px;
  background: none; border: none; outline: none;
  color: var(--text-primary);
  font-size: 12px;
}
.tag-input::placeholder { color: var(--text-muted); }

.btn-primary { padding: 7px 16px; border-radius: 8px; border: none; background: linear-gradient(135deg,#667eea,#764ba2); color: #fff; font-size: 13px; font-weight: 500; cursor: pointer; }
.btn-primary:hover { opacity: 0.9; }
.btn-secondary { padding: 7px 16px; border-radius: 8px; border: 1px solid var(--border-color); background: transparent; color: var(--text-secondary); font-size: 13px; cursor: pointer; }
.btn-secondary:hover { color: #fff; border-color: rgba(255,255,255,0.15); }
</style>

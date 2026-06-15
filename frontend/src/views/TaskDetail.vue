<template>
  <div class="task-detail">
    <button class="back-btn" @click="$router.back()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
      返回
    </button>

    <div v-if="task" class="section mb-24">
      <div class="section-header">
        <h3>{{ task.name }}</h3>
        <span class="tag" :class="task.status === 'active' ? 'tag-green' : 'tag-gray'">
          {{ task.status === 'active' ? '运行中' : task.status === 'paused' ? '已暂停' : '已停止' }}
        </span>
      </div>
      <div class="detail-grid">
        <div class="detail-item">
  <span class="detail-label">Agent</span>
  <span class="detail-value">
    <span class="agent-avatar-sm" :style="{background: $avatar(task.agent_name).bg}">{{ $avatar(task.agent_name).letter }}</span>
    {{ task.agent_name }}
  </span>
</div>
        <div class="detail-item"><span class="detail-label">Cron</span><code class="detail-code" :title="task.cron_expression">{{ $cron(task.cron_expression) }}</code></div>
        <div class="detail-item"><span class="detail-label">容忍窗口</span><span class="detail-value">{{ task.grace_period }}s</span></div>
        <div class="detail-item"><span class="detail-label">最近运行</span><span class="detail-value mono">{{ task.last_run_at ? dayjs.utc(task.last_run_at).local().format('YYYY-MM-DD HH:mm:ss') : '—' }}</span></div>
        <div class="detail-item">
          <span class="detail-label">最近结果</span>
          <span v-if="task.last_run_result" class="tag" :class="task.last_run_result === 'success' ? 'tag-green' : 'tag-red'">
            {{ task.last_run_result === 'success' ? '成功' : '失败' }}
          </span>
          <span v-else class="detail-value">—</span>
        </div>
        <div class="detail-item"><span class="detail-label">执行次数</span><span class="detail-value mono">{{ task.total_run_count }}</span></div>
        <div class="detail-item"><span class="detail-label">预计下次</span><span class="detail-value mono">{{ task.next_run_at ? dayjs.utc(task.next_run_at).local().format('YYYY-MM-DD HH:mm:ss') : '待计算' }}</span></div>
        <div class="detail-item"><span class="detail-label">描述</span><span class="detail-value">{{ task.description || '无' }}</span></div>
      </div>
    </div>

    <!-- Execution History -->
    <div class="section">
      <div class="section-header">
        <h3>执行历史</h3>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>状态</th>
              <th>开始时间</th>
              <th>耗时(ms)</th>
              <th>结果摘要</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in executions" :key="e.id">
              <td class="cell-mono">#{{ e.id }}</td>
              <td>
                <span class="tag" :class="e.status === 'success' ? 'tag-green' : e.status === 'failed' ? 'tag-red' : 'tag-warn'">
                  {{ e.status === 'success' ? '成功' : e.status === 'failed' ? '失败' : '运行中' }}
                </span>
              </td>
              <td class="cell-mono">{{ dayjs.utc(e.started_at).local().format('MM-DD HH:mm:ss') }}</td>
              <td class="cell-mono">{{ e.duration_ms ?? '—' }}</td>
              <td class="cell-muted cell-ellipsis">{{ e.result || '—' }}</td>
              <td><button class="cell-link-btn" @click="showLog(e)">日志</button></td>
            </tr>
            <tr v-if="executions.length === 0">
              <td colspan="6" class="cell-empty">暂无执行记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Log Dialog -->
    <div v-if="logVisible" class="modal-overlay" @click.self="logVisible = false">
      <div class="modal">
        <div class="modal-header">
          <h4>执行日志 #{{ logExecution?.id }}</h4>
          <button class="modal-close" @click="logVisible = false">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <pre class="log-viewer">{{ currentLog || '暂无日志' }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { beijing } from '../utils/time.js'
import { getTask, listExecutions } from '../api/index.js'

const route = useRoute()
const taskId = Number(route.params.id)
const task = ref(null)
const executions = ref([])
const logVisible = ref(false)
const currentLog = ref('')
const logExecution = ref(null)

onMounted(async () => {
  try {
    const [taskRes, execRes] = await Promise.all([
      getTask(taskId),
      listExecutions(taskId, { limit: 100 }),
    ])
    task.value = taskRes.data
    executions.value = execRes.data
  } catch (e) {
    console.error(e)
  }
})

const showLog = (row) => {
  logExecution.value = row
  currentLog.value = row.log || '暂无日志'
  logVisible.value = true
}
</script>

<style scoped>
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 6px 14px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  margin-bottom: 16px;
}
.back-btn:hover { color: #fff; border-color: rgba(255,255,255,0.15); }

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

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}
.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-color);
}
.detail-item:nth-child(odd) { border-right: 1px solid var(--border-color); }
.detail-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
.detail-value { font-size: 13px; color: var(--text-primary); }
.detail-value.mono, .cell-mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-secondary); }
.detail-code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px; color: #a8b4ff;
  background: rgba(102,126,234,0.1);
  padding: 2px 8px; border-radius: 4px;
  display: inline-block;
}

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
.cell-muted { color: var(--text-muted); }
.cell-empty { text-align: center; color: var(--text-muted); padding: 40px 16px !important; }
.cell-ellipsis { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cell-link-btn {
  background: none; border: none; color: var(--accent-1);
  font-size: 13px; cursor: pointer;
}
.cell-link-btn:hover { text-decoration: underline; }

.tag { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 500; }
.tag-green { background: rgba(34,197,94,0.12); color: #4ade80; }
.tag-red { background: rgba(239,68,68,0.12); color: #f87171; }
.tag-warn { background: rgba(245,158,11,0.12); color: #fbbf24; }
.tag-gray { background: rgba(255,255,255,0.05); color: var(--text-secondary); }

/* Log Modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
}
.modal {
  width: 700px; max-width: 90vw;
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
.log-viewer {
  background: #0d0d14;
  color: #c0c4d0;
  padding: 20px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  max-height: 500px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}
</style>

<template>
  <div class="alerts-page">
    <div class="section">
      <div class="section-header">
        <h3>告警历史</h3>
        <div class="filter-group">
          <button :class="{ active: filterStatus === '' }" @click="filterStatus = ''; loadData()">全部</button>
          <button :class="{ active: filterStatus === 'pending' }" @click="filterStatus = 'pending'; loadData()">待处理</button>
          <button :class="{ active: filterStatus === 'acknowledged' }" @click="filterStatus = 'acknowledged'; loadData()">已确认</button>
        </div>
      </div>
      <div class="alert-list">
        <div v-for="a in alerts" :key="a.id" class="alert-item" :class="{ 'alert-pending': a.status === 'pending' }">
          <div class="alert-left">
            <div class="alert-dot" :class="a.status === 'pending' ? 'dot-red' : 'dot-gray'"></div>
          </div>
          <div class="alert-body">
            <div class="alert-top">
              <span class="tag" :class="a.alert_type === 'missed_run' ? 'tag-warn' : 'tag-red'">
                {{ a.alert_type === 'missed_run' ? '未按时执行' : '执行失败' }}
              </span>
              <span class="alert-task">{{ a.task_name || '未知任务' }}</span>
              <span class="alert-time">{{ dayjs.utc(a.created_at).local().format('MM-DD HH:mm') }}</span>
            </div>
            <div class="alert-msg">{{ a.message }}</div>
            <div class="alert-bottom">
              <span class="alert-status" :class="a.status === 'pending' ? 'text-red' : 'text-muted'">
                {{ a.status === 'pending' ? '待处理' : '已确认' }}
              </span>
              <button v-if="a.status === 'pending'" class="btn-ack" @click="handleAcknowledge(a)">确认</button>
            </div>
          </div>
        </div>
        <div v-if="alerts.length === 0" class="empty-state">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color:var(--text-muted);margin-bottom:12px"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          <p>暂无告警</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'
import { listAlerts, acknowledgeAlert } from '../api/index.js'

const alerts = ref([])
const filterStatus = ref('')

const loadData = async () => {
  const params = { limit: 200 }
  if (filterStatus.value) params.status = filterStatus.value
  const res = await listAlerts(params)
  alerts.value = res.data
}

const handleAcknowledge = async (row) => {
  try {
    await acknowledgeAlert(row.id)
    await loadData()
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadData)
</script>

<style scoped>
.alerts-page {}

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

.filter-group { display: flex; gap: 4px; background: rgba(255,255,255,0.04); border-radius: 8px; padding: 3px; }
.filter-group button {
  padding: 5px 14px; border-radius: 6px;
  background: none; border: none;
  color: var(--text-muted); font-size: 12px; cursor: pointer;
  transition: all 0.15s;
}
.filter-group button.active {
  background: var(--accent-1);
  color: #fff;
}

.alert-list { padding: 0; }
.alert-item {
  display: flex;
  gap: 14px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.15s;
}
.alert-item:last-child { border-bottom: none; }
.alert-item:hover { background: rgba(255,255,255,0.02); }
.alert-pending { background: rgba(239,68,68,0.03); }

.alert-left { padding-top: 2px; }
.alert-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 4px; }
.dot-red { background: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.4); }
.dot-gray { background: rgba(255,255,255,0.15); }

.alert-body { flex: 1; min-width: 0; }
.alert-top { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.alert-task { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.alert-time { font-size: 11px; color: var(--text-muted); margin-left: auto; }
.alert-msg {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.alert-bottom { display: flex; align-items: center; gap: 12px; }
.alert-status { font-size: 11px; }
.text-red { color: #f87171; }
.text-muted { color: var(--text-muted); }
.btn-ack {
  padding: 3px 12px;
  border-radius: 6px;
  border: 1px solid rgba(102,126,234,0.3);
  background: rgba(102,126,234,0.1);
  color: #a8b4ff;
  font-size: 11px;
  cursor: pointer;
}
.btn-ack:hover { background: rgba(102,126,234,0.2); }

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
  font-size: 14px;
}

.tag { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 500; }
.tag-warn { background: rgba(245,158,11,0.12); color: #fbbf24; }
.tag-red { background: rgba(239,68,68,0.12); color: #f87171; }
</style>

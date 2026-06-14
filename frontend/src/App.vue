<template>
  <div id="app-container">
    <!-- Login page: standalone without sidebar -->
    <template v-if="isLoginPage">
      <router-view />
    </template>

    <!-- App pages: with sidebar -->
    <template v-else>
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <span class="logo-text">TaskPulse</span>
      </div>

      <nav class="nav-menu">
        <router-link to="/" class="nav-item" :class="{ active: currentRoute === '/' }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          <span>仪表盘</span>
        </router-link>
        <router-link to="/tasks" class="nav-item" :class="{ active: currentRoute.startsWith('/tasks') }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
          <span>所有任务</span>
        </router-link>
        <router-link to="/agents" class="nav-item" :class="{ active: currentRoute.startsWith('/agents') }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          <span>Agent 管理</span>
        </router-link>
        <router-link to="/alerts" class="nav-item" :class="{ active: currentRoute.startsWith('/alerts') }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          <span>告警历史</span>
        </router-link>
        <router-link to="/settings" class="nav-item" :class="{ active: currentRoute.startsWith('/settings') }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          <span>系统配置</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="status-dot"></div>
        <span>系统运行中</span>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="main-area">
      <header class="topbar">
        <h2 class="page-title">{{ pageTitle }}</h2>
        <div class="topbar-right">
          <template v-if="isLoggedIn">
            <span class="user-name">{{ userName }}</span>
            <button class="btn-logout" @click="handleLogout">退出</button>
          </template>
          <span v-else class="version-badge">v1.0</span>
        </div>
      </header>
      <main class="content">
        <router-view />
      </main>
    </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const currentRoute = computed(() => route.path)
const isLoginPage = computed(() => route.path === '/login')

const isLoggedIn = computed(() => !!localStorage.getItem('token'))
const userName = ref('')

// Load user info from localStorage
try {
  const userData = JSON.parse(localStorage.getItem('user') || '{}')
  userName.value = userData.display_name || userData.username || ''
} catch {}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

const routeTitles = {
  '/': '仪表盘',
  '/tasks': '所有任务',
  '/agents': 'Agent 管理',
  '/alerts': '告警历史',
  '/settings': '系统配置',
}
const pageTitle = computed(() => routeTitles[route.path] || 'TaskPulse')
</script>

<style scoped>
#app-container {
  display: flex;
  height: 100vh;
  background: #0a0a0f;
  color: #e0e0e0;
}

/* ── Sidebar ───────────────────────────────────── */
.sidebar {
  width: 220px;
  min-width: 220px;
  background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
  border-right: 1px solid rgba(255,255,255,0.05);
  display: flex;
  flex-direction: column;
  padding: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 24px 20px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.logo-text {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #a8b4ff 0%, #c084fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  flex: 1;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  color: rgba(255,255,255,0.55);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
}
.nav-item:hover {
  color: #fff;
  background: rgba(255,255,255,0.06);
}
.nav-item.active {
  color: #fff;
  background: linear-gradient(135deg, rgba(102,126,234,0.2) 0%, rgba(118,75,162,0.2) 100%);
  border: 1px solid rgba(102,126,234,0.15);
}

.sidebar-footer {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255,255,255,0.35);
  border-top: 1px solid rgba(255,255,255,0.06);
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34,197,94,0.5);
}

/* ── Main ──────────────────────────────────────── */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #0a0a0f;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 28px;
  background: rgba(15,15,26,0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #e0e0e0;
  margin: 0;
}
.version-badge {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 20px;
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.4);
  border: 1px solid rgba(255,255,255,0.08);
}
.user-name {
  font-size: 13px;
  color: var(--text-secondary);
}
.btn-logout {
  padding: 4px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04);
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
}
.btn-logout:hover {
  color: #f87171;
  border-color: rgba(239,68,68,0.2);
  background: rgba(239,68,68,0.08);
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 24px 28px;
}
</style>

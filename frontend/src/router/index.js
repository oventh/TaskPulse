import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Tasks from '../views/Tasks.vue'
import TaskDetail from '../views/TaskDetail.vue'
import Agents from '../views/Agents.vue'
import Alerts from '../views/Alerts.vue'
import Settings from '../views/Settings.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/tasks', component: Tasks },
  { path: '/tasks/:id', component: TaskDetail, name: 'TaskDetail' },
  { path: '/agents', component: Agents },
  { path: '/alerts', component: Alerts },
  { path: '/settings', component: Settings },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

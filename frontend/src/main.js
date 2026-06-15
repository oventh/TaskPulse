import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import App from './App.vue'
import router from './router'
import './assets/style.css'

// Extend dayjs with UTC plugin for timezone conversion
dayjs.extend(utc)

const app = createApp(App)

// Register all Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Global helper: cron expression to readable Chinese
app.config.globalProperties.$cron = (expr) => {
  if (!expr) return ''
  try {
    const parts = expr.trim().split(/\s+/)
    if (parts.length !== 5) return expr
    const [min, hour, dom, month, dow] = parts

    // Helper: describe a cron field
    const descField = (val, unit) => {
      if (val === '*') return `每${unit}`
      if (val.startsWith('*/')) return `每${val.slice(2)}${unit}`
      if (val.includes(',')) {
        const items = val.split(',').map(v => v.padStart(2, '0')).join('分、')
        return `第 ${items}分`
      }
      if (val.includes('-')) {
        const [from, to] = val.split('-')
        return `${from.padStart(2,'0')}分到${to.padStart(2,'0')}分`
      }
      return `${val.padStart(2,'0')}${unit}`
    }

    const allStar = (...args) => args.every(v => v === '*')

    // Every minute
    if (min === '*' && hour === '*' && allStar(dom, month, dow)) return '每分钟'

    // Every N minutes (always)
    if (min.startsWith('*/') && hour === '*' && allStar(dom, month, dow)) {
      return `每${min.slice(2)}分钟`
    }

    // Every N hours (at min 0)
    if (min === '0' && hour.startsWith('*/') && allStar(dom, month, dow)) {
      return `每${hour.slice(2)}小时`
    }

    // Specific minutes every hour
    if (min !== '*' && !min.startsWith('*/') && hour === '*' && allStar(dom, month, dow)) {
      if (min.includes(',')) {
        const items = min.split(',').map(v => v.padStart(2, '0'))
        return `每小时 ${items.join('、')}分`
      }
      return `每小时 第${min.padStart(2,'0')}分钟`
    }

    // Daily at specific time(s)
    if (allStar(dom, month, dow)) {
      if (min.startsWith('*/')) {
        const interval = min.slice(2)
        if (hour.includes('-')) {
          const [hFrom, hTo] = hour.split('-').map(h => h.padStart(2,'0'))
          return `每${interval}分钟（${hFrom}:00-${hTo}:00）`
        }
        if (hour !== '*') return `每${interval}分钟（${hour.padStart(2,'0')}点）`
        return `每${interval}分钟`
      }
      if (hour.includes(',')) {
        const times = hour.split(',').map(h => `${h.padStart(2,'0')}:${min.padStart(2,'0')}`)
        return `每天 ${times.join('、')}`
      }
      if (hour.includes('-')) {
        return `每天 ${hour.split('-')[0].padStart(2,'0')}:${min.padStart(2,'0')} 到 ${hour.split('-')[1].padStart(2,'0')}:${min.padStart(2,'0')}`
      }
      return `每天 ${hour.padStart(2,'0')}:${min.padStart(2,'0')}`
    }

    // Weekly
    const dowNames = ['日', '一', '二', '三', '四', '五', '六', '日']
    if (allStar(dom, month) && dow !== '*') {
      if (dow.includes(',')) {
        const days = dow.split(',').map(d => `周${dowNames[parseInt(d)]}`)
        return `每${days.join('、')} ${hour.padStart(2,'0')}:${min.padStart(2,'0')}`
      }
      if (dow.includes('-')) {
        const [from, to] = dow.split('-')
        return `每周${dowNames[parseInt(from)]}到${dowNames[parseInt(to)]} ${hour.padStart(2,'0')}:${min.padStart(2,'0')}`
      }
      return `每周${dowNames[parseInt(dow)]} ${hour.padStart(2,'0')}:${min.padStart(2,'0')}`
    }

    // Every N minutes within specific hours (e.g., */15 9-18 * * *)
    if (min.startsWith('*/') && !allStar(dom, month, dow)) {
      const interval = min.slice(2)
      let hourDesc = ''
      if (hour !== '*') hourDesc = descField(hour, '点')
      return `每${interval}分钟${hourDesc ? ` (${hourDesc})` : ''}`
    }

    return expr
  } catch {
    return expr
  }
}

// Global helper: agent name → avatar { letter, bg color }
const AVATAR_COLORS = [
  '#667eea', '#22c55e', '#f59e0b', '#ef4444', '#ec4899',
  '#8b5cf6', '#06b6d4', '#f97316', '#14b8a6', '#a855f7',
  '#6366f1', '#84cc16', '#e11d48', '#0ea5e9',
]
app.config.globalProperties.$avatar = (name) => {
  if (!name) return { letter: '?', bg: AVATAR_COLORS[0] }
  const letter = name.trim()[0]
  // Deterministic color from name
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = ((hash << 5) - hash) + name.charCodeAt(i)
  const idx = Math.abs(hash) % AVATAR_COLORS.length
  return { letter, bg: AVATAR_COLORS[idx] }
}

app.use(ElementPlus, { locale: zhCn })
app.use(router)
app.mount('#app')

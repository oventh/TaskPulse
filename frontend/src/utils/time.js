/**
 * 时间工具 — 北京时间 (Asia/Shanghai, UTC+8)
 *
 * 后端存储的日期时间均为 UTC（naive datetime），
 * 前端统一转换为北京时间展示。
 */
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)

const TZ = 'Asia/Shanghai'

/**
 * 将 UTC 时间戳格式化为北京时间字符串
 * @param {string|Date|null} ts  ISO 时间字符串或 Date 对象
 * @param {string} fmt          dayjs 格式模板，默认 'MM-DD HH:mm'
 * @returns {string} 格式化后的北京时间
 */
export function beijing(ts, fmt = 'MM-DD HH:mm') {
  if (!ts) return '—'
  return dayjs.utc(ts).tz(TZ).format(fmt)
}

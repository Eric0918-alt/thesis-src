import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: '/api',
  timeout: 20000
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    if (status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      if (window.location.pathname !== '/login') {
        ElMessage.error('登录状态已失效，请重新登录')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export function extractErrorMessage(error: unknown, fallback = '操作失败'): string {
  const err = error as { response?: { data?: unknown } }
  const data = err?.response?.data
  if (!data) return fallback
  if (typeof data === 'string') return data
  if (typeof data === 'object') {
    const record = data as Record<string, unknown>
    if (typeof record.detail === 'string') return record.detail
    if (Array.isArray(record.non_field_errors) && record.non_field_errors.length > 0) {
      return String(record.non_field_errors[0])
    }
    for (const val of Object.values(record)) {
      if (Array.isArray(val) && val.length > 0) return String(val[0])
      if (typeof val === 'string') return val
    }
  }
  return fallback
}

export async function downloadBlob(url: string, params: Record<string, unknown>, filename: string) {
  const response = await http.get(url, { params, responseType: 'blob' })
  const blobUrl = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = blobUrl
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(blobUrl)
}

export default http

import http, { downloadBlob } from './http'

export type UserRole = 'student' | 'teacher' | 'admin'

export interface UserInfo {
  id: number
  username: string
  role: UserRole
  role_label: string
  real_name: string
  cohort: string
  gender: string
  phone: string
  avatar: string
  date_joined?: string
}

export interface PaginatedResponse<T> {
  count: number
  page: number
  page_size: number
  results: T[]
}

export interface StudentRecord {
  id: number
  student_no: string
  student_name: string
  cohort: string
  gender: string
  phone: string
  avatar: string
  date_joined?: string
}

export interface TeacherRecord {
  id: number
  teacher_no: string
  teacher_name: string
  gender: string
  phone: string
  avatar: string
  date_joined?: string
}

export interface CohortRecord {
  id: number
  name: string
  created_at?: string
}

export interface CodingResultRecord {
  id: number
  student_no: string
  article_no: string
  cohort: string
  segment_no: string
  segment_order: number
  source_row_no: number
  problem_description: number
  cause_analysis: number
  improvement_strategy: number
  effectiveness_eval: number
  description_level: number
  descriptive_reflection: number
  dialogic_reflection: number
  critical_reflection: number
  created_at?: string
  updated_at?: string
}

export interface SystemLogRecord {
  id: number
  username: string
  role: string
  module: string
  action: string
  method: string
  path: string
  detail: string
  ip_address: string
  status: string
  created_at: string
}

export const authApi = {
  login: (payload: { username: string; password: string; role: UserRole }) =>
    http.post<{ access: string; refresh: string; user: UserInfo }>('/auth/login/', payload),
  registerStudent: (payload: Record<string, unknown>) =>
    http.post('/auth/register/student/', payload),
  registerTeacher: (payload: Record<string, unknown>) =>
    http.post('/auth/register/teacher/', payload),
  getProfile: () => http.get<UserInfo>('/auth/profile/'),
  updateProfile: (payload: Partial<UserInfo>) => http.put<UserInfo>('/auth/profile/', payload),
  changePassword: (payload: {
    old_password: string
    new_password: string
    confirm_password: string
  }) => http.post('/auth/change-password/', payload),
  uploadAvatar: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return http.post<{ url: string }>('/upload/avatar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

export const studentApi = {
  list: (params: Record<string, unknown>) =>
    http.get<PaginatedResponse<StudentRecord>>('/students/', { params }),
  create: (payload: Record<string, unknown>) => http.post('/students/', payload),
  update: (id: number, payload: Record<string, unknown>) => http.put(`/students/${id}/`, payload),
  remove: (id: number) => http.delete(`/students/${id}/`),
  batchDelete: (ids: number[]) => http.post('/students/batch-delete/', { ids }),
  importExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return http.post('/students/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  exportExcel: (params: Record<string, unknown>, filename = '学生列表.xlsx') =>
    downloadBlob('/students/export/', params, filename),
  downloadTemplate: () => downloadBlob('/students/template/', {}, '学生导入模板.xlsx')
}

export const teacherApi = {
  list: (params: Record<string, unknown>) =>
    http.get<PaginatedResponse<TeacherRecord>>('/teachers/', { params }),
  create: (payload: Record<string, unknown>) => http.post('/teachers/', payload),
  update: (id: number, payload: Record<string, unknown>) => http.put(`/teachers/${id}/`, payload),
  remove: (id: number) => http.delete(`/teachers/${id}/`),
  batchDelete: (ids: number[]) => http.post('/teachers/batch-delete/', { ids }),
  importExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return http.post('/teachers/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  exportExcel: (params: Record<string, unknown>, filename = '教师列表.xlsx') =>
    downloadBlob('/teachers/export/', params, filename),
  downloadTemplate: () => downloadBlob('/teachers/template/', {}, '教师导入模板.xlsx')
}

export const cohortApi = {
  list: (params: Record<string, unknown>) =>
    http.get<PaginatedResponse<CohortRecord>>('/cohorts/', { params }),
  all: () => http.get<CohortRecord[]>('/cohorts/all/'),
  create: (payload: { name: string }) => http.post('/cohorts/', payload),
  update: (id: number, payload: { name: string }) => http.put(`/cohorts/${id}/`, payload),
  remove: (id: number) => http.delete(`/cohorts/${id}/`),
  batchDelete: (ids: number[]) => http.post('/cohorts/batch-delete/', { ids })
}

export const codingResultApi = {
  list: (params: Record<string, unknown>) =>
    http.get<PaginatedResponse<CodingResultRecord>>('/coding-results/', { params }),
  create: (payload: Record<string, unknown>) => http.post('/coding-results/', payload),
  update: (id: number, payload: Record<string, unknown>) =>
    http.put(`/coding-results/${id}/`, payload),
  remove: (id: number) => http.delete(`/coding-results/${id}/`),
  batchDelete: (ids: number[]) => http.post('/coding-results/batch-delete/', { ids }),
  importExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return http.post('/coding-results/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  exportExcel: (params: Record<string, unknown>, filename = '编码结果.xlsx') =>
    downloadBlob('/coding-results/export/', params, filename),
  downloadTemplate: () => downloadBlob('/coding-results/template/', {}, '编码结果导入模板.xlsx')
}

export const logApi = {
  list: (params: Record<string, unknown>) =>
    http.get<PaginatedResponse<SystemLogRecord>>('/logs/', { params }),
  remove: (id: number) => http.delete(`/logs/${id}/`),
  batchDelete: (ids: number[]) => http.post('/logs/batch-delete/', { ids }),
  exportExcel: (params: Record<string, unknown>, filename = '系统日志.xlsx') =>
    downloadBlob('/logs/export/', params, filename)
}

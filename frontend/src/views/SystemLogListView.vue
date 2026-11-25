<template>
  <div class="page-card">
    <div class="search-bar">
      <div class="search-item">
        <span class="search-label">操作用户</span>
        <el-input
          v-model="filters.username"
          placeholder="操作用户"
          clearable
          style="width: 160px"
          @keyup.enter="handleSearch"
        />
      </div>
      <div class="search-item">
        <span class="search-label">操作模块</span>
        <el-input
          v-model="filters.module"
          placeholder="如 编码结果 / 认证登录"
          clearable
          style="width: 180px"
          @keyup.enter="handleSearch"
        />
      </div>
      <div class="search-item">
        <span class="search-label">状态</span>
        <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px">
          <el-option label="成功" value="成功" />
          <el-option label="失败" value="失败" />
        </el-select>
      </div>
      <el-button class="btn-blue" @click="handleSearch">
        <el-icon style="margin-right: 4px"><Search /></el-icon>
        查询
      </el-button>
    </div>

    <div class="toolbar-bar">
      <el-button class="btn-green" @click="fetchData">刷新</el-button>
      <el-button class="btn-red" @click="handleBatchDelete">批量删除</el-button>
      <el-button class="btn-green" @click="handleExportSelected">导出选中</el-button>
      <el-button class="btn-green" @click="handleExportAll">导出全部</el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="tableData"
      border
      class="proto-table"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
    >
      <el-table-column type="selection" width="46" align="center" />
      <el-table-column label="序号" width="64" align="center">
        <template #default="{ $index }">
          {{ (page - 1) * pageSize + $index + 1 }}
        </template>
      </el-table-column>
      <el-table-column prop="username" label="操作用户" sortable="custom" width="110" />
      <el-table-column prop="role" label="角色" width="84" align="center" />
      <el-table-column prop="module" label="操作模块" sortable="custom" width="116" />
      <el-table-column prop="action" label="操作类型" width="116" />
      <el-table-column prop="method" label="请求方法" width="90" align="center" />
      <el-table-column prop="detail" label="操作详情" min-width="220" show-overflow-tooltip />
      <el-table-column prop="ip_address" label="IP地址" width="126" />
      <el-table-column prop="status" label="状态" width="84" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === '成功' ? 'success' : 'danger'" size="small">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="操作时间" sortable="custom" width="166" />
      <el-table-column label="操作" width="110" align="center" fixed="right">
        <template #default="{ row }">
          <div class="op-links">
            <span class="op-link op-view" @click="openDetail(row)">查看</span>
            <span class="op-link op-delete" @click="handleDelete(row)">删除</span>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <PaginationBar
      v-model:page="page"
      v-model:page-size="pageSize"
      :total="total"
      @change="fetchData"
    />

    <el-dialog v-model="detailVisible" title="系统日志详情" width="540px">
      <el-descriptions v-if="currentLog" :column="2" border>
        <el-descriptions-item label="操作用户">{{ currentLog.username }}</el-descriptions-item>
        <el-descriptions-item label="用户角色">{{ currentLog.role || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作模块">{{ currentLog.module }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">{{ currentLog.action }}</el-descriptions-item>
        <el-descriptions-item label="请求方法">{{ currentLog.method }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ currentLog.status }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ currentLog.ip_address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作时间">{{ currentLog.created_at }}</el-descriptions-item>
        <el-descriptions-item label="请求路径" :span="2">{{ currentLog.path || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作详情" :span="2">{{ currentLog.detail || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PaginationBar from '@/components/PaginationBar.vue'
import { logApi, type SystemLogRecord } from '@/api/services'
import { extractErrorMessage } from '@/api/http'

const loading = ref(false)
const tableData = ref<SystemLogRecord[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const ordering = ref('-created_at')
const selectedRows = ref<SystemLogRecord[]>([])

const detailVisible = ref(false)
const currentLog = ref<SystemLogRecord | null>(null)

const filters = reactive({
  username: '',
  module: '',
  status: ''
})

async function fetchData() {
  loading.value = true
  try {
    const { data } = await logApi.list({
      page: page.value,
      page_size: pageSize.value,
      username: filters.username.trim() || undefined,
      module: filters.module.trim() || undefined,
      status: filters.status || undefined,
      ordering: ordering.value
    })
    tableData.value = data.results
    total.value = data.count
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '获取系统日志失败'))
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

function handleSearch() {
  page.value = 1
  fetchData()
}

function handleSelectionChange(rows: SystemLogRecord[]) {
  selectedRows.value = rows
}

function handleSortChange({ prop, order }: { prop: string; order: string | null }) {
  if (order === 'ascending') ordering.value = prop
  else if (order === 'descending') ordering.value = `-${prop}`
  else ordering.value = '-created_at'
  fetchData()
}

function openDetail(row: SystemLogRecord) {
  currentLog.value = row
  detailVisible.value = true
}

async function handleDelete(row: SystemLogRecord) {
  try {
    await ElMessageBox.confirm('确认删除该条系统日志吗？', '提示', { type: 'warning' })
    await logApi.remove(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(extractErrorMessage(err, '删除失败'))
  }
}

async function handleBatchDelete() {
  if (selectedRows.value.length === 0) {
    return ElMessage.warning('请先勾选要删除的日志')
  }
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedRows.value.length} 条系统日志吗？`, '批量删除', {
      type: 'warning'
    })
    await logApi.batchDelete(selectedRows.value.map((r) => r.id))
    ElMessage.success('批量删除成功')
    fetchData()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(extractErrorMessage(err, '批量删除失败'))
  }
}

async function handleExportSelected() {
  if (selectedRows.value.length === 0) {
    return ElMessage.warning('请先勾选要导出的日志')
  }
  try {
    await logApi.exportExcel({ ids: selectedRows.value.map((r) => r.id).join(',') }, '系统日志_选中.xlsx')
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '导出失败'))
  }
}

async function handleExportAll() {
  try {
    await logApi.exportExcel(
      {
        username: filters.username.trim() || undefined,
        module: filters.module.trim() || undefined,
        status: filters.status || undefined
      },
      '系统日志_全部.xlsx'
    )
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '导出失败'))
  }
}
</script>

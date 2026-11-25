<template>
  <div class="page-card">
    <div class="search-bar">
      <div class="search-item">
        <span class="search-label">届别</span>
        <el-input
          v-model="queryName"
          placeholder="届别"
          clearable
          style="width: 190px"
          @keyup.enter="handleSearch"
        />
      </div>
      <el-button class="btn-blue" @click="handleSearch">
        <el-icon style="margin-right: 4px"><Search /></el-icon>
        查询
      </el-button>
    </div>

    <div class="toolbar-bar">
      <el-button class="btn-blue" @click="openForm('create')">新增</el-button>
      <el-button class="btn-red" @click="handleBatchDelete">批量删除</el-button>
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
      <el-table-column label="序号" width="76" align="center">
        <template #default="{ $index }">
          {{ (page - 1) * pageSize + $index + 1 }}
        </template>
      </el-table-column>
      <el-table-column prop="name" label="届别" sortable="custom" />
      <el-table-column label="操作" width="200" align="center">
        <template #default="{ row }">
          <div class="op-links">
            <span class="op-link op-view" @click="openForm('view', row)">查看</span>
            <span class="op-link op-edit" @click="openForm('edit', row)">编辑</span>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="420px" destroy-on-close>
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="76px"
        :disabled="dialogMode === 'view'"
      >
        <el-form-item label="届别" prop="name">
          <el-input v-model="formData.name" placeholder="例如：2023届" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ dialogMode === 'view' ? '关闭' : '取消' }}</el-button>
        <el-button v-if="dialogMode !== 'view'" class="btn-blue" :loading="saving" @click="handleSave">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import PaginationBar from '@/components/PaginationBar.vue'
import { cohortApi, type CohortRecord } from '@/api/services'
import { extractErrorMessage } from '@/api/http'

const loading = ref(false)
const saving = ref(false)
const queryName = ref('')
const tableData = ref<CohortRecord[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const ordering = ref('id')
const selectedRows = ref<CohortRecord[]>([])

const dialogVisible = ref(false)
const dialogMode = ref<'view' | 'create' | 'edit'>('view')
const currentId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const formData = reactive({ name: '' })
const formRules: FormRules = {
  name: [{ required: true, message: '请输入届别名称', trigger: 'blur' }]
}

const dialogTitle = computed(() => {
  if (dialogMode.value === 'create') return '新增届别'
  if (dialogMode.value === 'edit') return '编辑届别'
  return '查看届别'
})

async function fetchData() {
  loading.value = true
  try {
    const { data } = await cohortApi.list({
      page: page.value,
      page_size: pageSize.value,
      name: queryName.value.trim() || undefined,
      ordering: ordering.value
    })
    tableData.value = data.results
    total.value = data.count
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '获取届别列表失败'))
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

function handleSearch() {
  page.value = 1
  fetchData()
}

function handleSelectionChange(rows: CohortRecord[]) {
  selectedRows.value = rows
}

function handleSortChange({ prop, order }: { prop: string; order: string | null }) {
  if (order === 'ascending') ordering.value = prop
  else if (order === 'descending') ordering.value = `-${prop}`
  else ordering.value = 'id'
  fetchData()
}

function openForm(mode: 'view' | 'create' | 'edit', row?: CohortRecord) {
  dialogMode.value = mode
  currentId.value = row?.id ?? null
  formData.name = row?.name ?? ''
  dialogVisible.value = true
}

async function handleSave() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (dialogMode.value === 'create') {
      await cohortApi.create({ name: formData.name.trim() })
      ElMessage.success('新增届别成功')
    } else if (currentId.value) {
      await cohortApi.update(currentId.value, { name: formData.name.trim() })
      ElMessage.success('编辑届别成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '保存失败'))
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: CohortRecord) {
  try {
    await ElMessageBox.confirm(`确认删除届别“${row.name}”吗？`, '提示', { type: 'warning' })
    await cohortApi.remove(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(extractErrorMessage(err, '删除失败'))
  }
}

async function handleBatchDelete() {
  if (selectedRows.value.length === 0) {
    return ElMessage.warning('请先勾选要删除的届别')
  }
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedRows.value.length} 个届别吗？`, '批量删除', {
      type: 'warning'
    })
    await cohortApi.batchDelete(selectedRows.value.map((r) => r.id))
    ElMessage.success('批量删除成功')
    fetchData()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(extractErrorMessage(err, '批量删除失败'))
  }
}
</script>

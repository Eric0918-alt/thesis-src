<template>
  <div class="page-card">
    <div class="toolbar-bar">
      <el-button class="btn-green" @click="fetchData">刷新</el-button>
      <el-button class="btn-blue" @click="openForm('create')">新增</el-button>
      <el-button class="btn-red" @click="handleBatchDelete">批量删除</el-button>
      <el-button class="btn-green" @click="importVisible = true">导入</el-button>
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
      <el-table-column label="序号" width="66" align="center">
        <template #default="{ $index }">
          {{ (page - 1) * pageSize + $index + 1 }}
        </template>
      </el-table-column>
      <el-table-column prop="teacher_no" label="教师工号" sortable="custom" min-width="120" />
      <el-table-column prop="teacher_name" label="教师姓名" sortable="custom" min-width="120" />
      <el-table-column prop="gender" label="性别" sortable="custom" width="100" />
      <el-table-column prop="phone" label="手机号码" sortable="custom" min-width="150" />
      <el-table-column label="头像" width="130" align="center">
        <template #default="{ row }">
          <el-image
            v-if="row.avatar"
            :src="row.avatar"
            :preview-src-list="[row.avatar]"
            preview-teleported
            fit="cover"
            class="table-avatar"
          />
          <span v-else style="color: #909399; font-size: 12px">暂无</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="center" fixed="right">
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="540px" destroy-on-close>
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="92px"
        :disabled="dialogMode === 'view'"
      >
        <el-form-item label="教师工号" prop="teacher_no">
          <el-input v-model="formData.teacher_no" placeholder="请输入教师工号" />
        </el-form-item>
        <el-form-item label="教师姓名" prop="teacher_name">
          <el-input v-model="formData.teacher_name" placeholder="请输入教师姓名" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="formData.gender" placeholder="请选择性别" style="width: 100%" clearable>
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="formData.phone" placeholder="请输入手机号码" />
        </el-form-item>
        <el-form-item v-if="dialogMode !== 'view'" :label="dialogMode === 'create' ? '初始密码' : '重置密码'">
          <el-input
            v-model="formData.password"
            type="password"
            show-password
            :placeholder="dialogMode === 'create' ? '留空默认 123456' : '留空则不修改密码'"
          />
        </el-form-item>
        <el-form-item label="头像">
          <AvatarUploader v-model="formData.avatar" :disabled="dialogMode === 'view'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ dialogMode === 'view' ? '关闭' : '取消' }}</el-button>
        <el-button v-if="dialogMode !== 'view'" class="btn-blue" :loading="saving" @click="handleSave">
          确定
        </el-button>
      </template>
    </el-dialog>

    <ExcelImportDialog
      v-model:visible="importVisible"
      title="批量导入教师"
      strict-hint="包含列：教师工号、教师姓名、性别（选填）、手机号码（选填）、初始密码（选填，默认 123456）。"
      :upload-fn="teacherApi.importExcel"
      :template-fn="teacherApi.downloadTemplate"
      @success="fetchData"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import AvatarUploader from '@/components/AvatarUploader.vue'
import ExcelImportDialog from '@/components/ExcelImportDialog.vue'
import PaginationBar from '@/components/PaginationBar.vue'
import { teacherApi, type TeacherRecord } from '@/api/services'
import { extractErrorMessage } from '@/api/http'

const loading = ref(false)
const saving = ref(false)
const tableData = ref<TeacherRecord[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const ordering = ref('-id')
const selectedRows = ref<TeacherRecord[]>([])

const importVisible = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'view' | 'create' | 'edit'>('view')
const currentId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const formData = reactive({
  teacher_no: '',
  teacher_name: '',
  gender: '',
  phone: '',
  password: '',
  avatar: ''
})

const formRules: FormRules = {
  teacher_no: [{ required: true, message: '请输入教师工号', trigger: 'blur' }],
  teacher_name: [{ required: true, message: '请输入教师姓名', trigger: 'blur' }]
}

const dialogTitle = computed(() => {
  if (dialogMode.value === 'create') return '新增教师'
  if (dialogMode.value === 'edit') return '编辑教师'
  return '查看教师信息'
})

const SORT_FIELD_MAP: Record<string, string> = {
  teacher_no: 'username',
  teacher_name: 'real_name',
  gender: 'gender',
  phone: 'phone'
}

async function fetchData() {
  loading.value = true
  try {
    const { data } = await teacherApi.list({
      page: page.value,
      page_size: pageSize.value,
      ordering: ordering.value
    })
    tableData.value = data.results
    total.value = data.count
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '获取教师列表失败'))
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

function handleSelectionChange(rows: TeacherRecord[]) {
  selectedRows.value = rows
}

function handleSortChange({ prop, order }: { prop: string; order: string | null }) {
  const mapped = SORT_FIELD_MAP[prop] || 'id'
  if (order === 'ascending') ordering.value = mapped
  else if (order === 'descending') ordering.value = `-${mapped}`
  else ordering.value = '-id'
  fetchData()
}

function openForm(mode: 'view' | 'create' | 'edit', row?: TeacherRecord) {
  dialogMode.value = mode
  currentId.value = row?.id ?? null
  formData.teacher_no = row?.teacher_no ?? ''
  formData.teacher_name = row?.teacher_name ?? ''
  formData.gender = row?.gender ?? ''
  formData.phone = row?.phone ?? ''
  formData.avatar = row?.avatar ?? ''
  formData.password = ''
  dialogVisible.value = true
}

async function handleSave() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload: Record<string, unknown> = {
      teacher_no: formData.teacher_no.trim(),
      teacher_name: formData.teacher_name.trim(),
      gender: formData.gender,
      phone: formData.phone.trim(),
      avatar: formData.avatar
    }
    if (formData.password.trim()) {
      payload.password = formData.password.trim()
    }
    if (dialogMode.value === 'create') {
      await teacherApi.create(payload)
      ElMessage.success('新增教师成功')
    } else if (currentId.value) {
      await teacherApi.update(currentId.value, payload)
      ElMessage.success('更新教师信息成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '保存失败'))
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: TeacherRecord) {
  try {
    await ElMessageBox.confirm(`确认删除教师“${row.teacher_name}（${row.teacher_no}）”吗？`, '提示', {
      type: 'warning'
    })
    await teacherApi.remove(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(extractErrorMessage(err, '删除失败'))
  }
}

async function handleBatchDelete() {
  if (selectedRows.value.length === 0) {
    return ElMessage.warning('请先勾选要删除的教师')
  }
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedRows.value.length} 名教师吗？`, '批量删除', {
      type: 'warning'
    })
    await teacherApi.batchDelete(selectedRows.value.map((r) => r.id))
    ElMessage.success('批量删除成功')
    fetchData()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(extractErrorMessage(err, '批量删除失败'))
  }
}

async function handleExportSelected() {
  if (selectedRows.value.length === 0) {
    return ElMessage.warning('请先勾选要导出的教师')
  }
  try {
    await teacherApi.exportExcel({ ids: selectedRows.value.map((r) => r.id).join(',') }, '教师列表_选中.xlsx')
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '导出失败'))
  }
}

async function handleExportAll() {
  try {
    await teacherApi.exportExcel({}, '教师列表_全部.xlsx')
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '导出失败'))
  }
}
</script>

<style scoped>
.table-avatar {
  width: 68px;
  height: 68px;
  border-radius: 4px;
  display: block;
  margin: 0 auto;
}
</style>

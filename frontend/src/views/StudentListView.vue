<template>
  <div class="page-card">
    <!-- 顶部工具栏（教师端仅刷新；管理员端完整按钮组） -->
    <div class="toolbar-bar">
      <el-button class="btn-green" @click="fetchData">刷新</el-button>
      <template v-if="isAdmin">
        <el-button class="btn-blue" @click="openForm('create')">新增</el-button>
        <el-button class="btn-red" @click="handleBatchDelete">批量删除</el-button>
        <el-button class="btn-green" @click="importVisible = true">导入</el-button>
        <el-button class="btn-green" @click="handleExportSelected">导出选中</el-button>
        <el-button class="btn-green" @click="handleExportAll">导出全部</el-button>
      </template>
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
      <el-table-column prop="student_no" label="学生学号" sortable="custom" min-width="120" />
      <el-table-column prop="student_name" label="学生姓名" sortable="custom" min-width="120" />
      <el-table-column prop="cohort" label="届别" sortable="custom" min-width="110" />
      <el-table-column prop="gender" label="性别" sortable="custom" width="90" />
      <el-table-column prop="phone" label="手机" sortable="custom" min-width="140" />
      <el-table-column label="头像" width="120" align="center">
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
            <template v-if="isAdmin">
              <span class="op-link op-edit" @click="openForm('edit', row)">编辑</span>
              <span class="op-link op-delete" @click="handleDelete(row)">删除</span>
            </template>
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

    <!-- 查看 / 新增 / 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px" destroy-on-close>
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="92px"
        :disabled="dialogMode === 'view'"
      >
        <el-form-item label="学生学号" prop="student_no">
          <el-input v-model="formData.student_no" placeholder="请输入学生学号" />
        </el-form-item>
        <el-form-item label="学生姓名" prop="student_name">
          <el-input v-model="formData.student_name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="届别" prop="cohort">
          <el-select v-model="formData.cohort" placeholder="请选择届别" style="width: 100%" clearable>
            <el-option v-for="c in cohortOptions" :key="c.id" :label="c.name" :value="c.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="formData.gender" placeholder="请选择性别" style="width: 100%" clearable>
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机" prop="phone">
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
      title="批量导入学生"
      strict-hint="包含列：学生学号、学生姓名、届别、性别、手机、初始密码（选填，默认 123456）。"
      :upload-fn="studentApi.importExcel"
      :template-fn="studentApi.downloadTemplate"
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
import { cohortApi, studentApi, type CohortRecord, type StudentRecord } from '@/api/services'
import { extractErrorMessage } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const isAdmin = computed(() => auth.role === 'admin')

const loading = ref(false)
const saving = ref(false)
const tableData = ref<StudentRecord[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const ordering = ref('-id')
const selectedRows = ref<StudentRecord[]>([])
const cohortOptions = ref<CohortRecord[]>([])

const importVisible = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'view' | 'create' | 'edit'>('view')
const currentId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const formData = reactive({
  student_no: '',
  student_name: '',
  cohort: '',
  gender: '',
  phone: '',
  password: '',
  avatar: ''
})

const formRules: FormRules = {
  student_no: [{ required: true, message: '请输入学生学号', trigger: 'blur' }],
  student_name: [{ required: true, message: '请输入学生姓名', trigger: 'blur' }],
  cohort: [{ required: true, message: '请选择届别', trigger: 'change' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  phone: [{ required: true, message: '请输入手机号码', trigger: 'blur' }]
}

const dialogTitle = computed(() => {
  if (dialogMode.value === 'create') return '新增学生'
  if (dialogMode.value === 'edit') return '编辑学生'
  return '查看学生信息'
})

const SORT_FIELD_MAP: Record<string, string> = {
  student_no: 'username',
  student_name: 'real_name',
  cohort: 'cohort',
  gender: 'gender',
  phone: 'phone'
}

async function fetchData() {
  loading.value = true
  try {
    const { data } = await studentApi.list({
      page: page.value,
      page_size: pageSize.value,
      ordering: ordering.value
    })
    tableData.value = data.results
    total.value = data.count
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '获取学生列表失败'))
  } finally {
    loading.value = false
  }
}

async function fetchCohorts() {
  try {
    const { data } = await cohortApi.all()
    cohortOptions.value = data
  } catch {
    cohortOptions.value = []
  }
}

onMounted(() => {
  fetchData()
  fetchCohorts()
})

function handleSelectionChange(rows: StudentRecord[]) {
  selectedRows.value = rows
}

function handleSortChange({ prop, order }: { prop: string; order: string | null }) {
  const mapped = SORT_FIELD_MAP[prop] || 'id'
  if (order === 'ascending') ordering.value = mapped
  else if (order === 'descending') ordering.value = `-${mapped}`
  else ordering.value = '-id'
  fetchData()
}

function openForm(mode: 'view' | 'create' | 'edit', row?: StudentRecord) {
  dialogMode.value = mode
  currentId.value = row?.id ?? null
  formData.student_no = row?.student_no ?? ''
  formData.student_name = row?.student_name ?? ''
  formData.cohort = row?.cohort ?? ''
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
      student_no: formData.student_no.trim(),
      student_name: formData.student_name.trim(),
      cohort: formData.cohort,
      gender: formData.gender,
      phone: formData.phone.trim(),
      avatar: formData.avatar
    }
    if (formData.password.trim()) {
      payload.password = formData.password.trim()
    }

    if (dialogMode.value === 'create') {
      await studentApi.create(payload)
      ElMessage.success('新增学生成功')
    } else if (currentId.value) {
      await studentApi.update(currentId.value, payload)
      ElMessage.success('更新学生信息成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '保存失败'))
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: StudentRecord) {
  try {
    await ElMessageBox.confirm(`确认删除学生“${row.student_name}（${row.student_no}）”吗？`, '提示', {
      type: 'warning'
    })
    await studentApi.remove(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(extractErrorMessage(err, '删除失败'))
  }
}

async function handleBatchDelete() {
  if (selectedRows.value.length === 0) {
    return ElMessage.warning('请先勾选要删除的学生')
  }
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedRows.value.length} 名学生吗？`, '批量删除', {
      type: 'warning'
    })
    await studentApi.batchDelete(selectedRows.value.map((r) => r.id))
    ElMessage.success('批量删除成功')
    fetchData()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(extractErrorMessage(err, '批量删除失败'))
  }
}

async function handleExportSelected() {
  if (selectedRows.value.length === 0) {
    return ElMessage.warning('请先勾选要导出的学生')
  }
  try {
    await studentApi.exportExcel({ ids: selectedRows.value.map((r) => r.id).join(',') }, '学生列表_选中.xlsx')
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '导出失败'))
  }
}

async function handleExportAll() {
  try {
    await studentApi.exportExcel({}, '学生列表_全部.xlsx')
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

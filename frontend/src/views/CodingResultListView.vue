<template>
  <div class="page-card">
    <!-- 顶部查询栏（三端一致） -->
    <div class="search-bar">
      <div class="search-item">
        <span class="search-label">学生学号</span>
        <el-input
          v-model="filters.student_no"
          placeholder="学生学号"
          clearable
          style="width: 170px"
          @keyup.enter="handleSearch"
        />
      </div>
      <div class="search-item">
        <span class="search-label">文章编号</span>
        <el-input
          v-model="filters.article_no"
          placeholder="文章编号"
          clearable
          style="width: 170px"
          @keyup.enter="handleSearch"
        />
      </div>
      <div class="search-item">
        <span class="search-label">届别</span>
        <el-input
          v-model="filters.cohort"
          placeholder="届别"
          clearable
          style="width: 160px"
          @keyup.enter="handleSearch"
        />
      </div>
      <el-button class="btn-blue" @click="handleSearch">
        <el-icon style="margin-right: 4px"><Search /></el-icon>
        查询
      </el-button>
    </div>

    <!-- 管理员操作工具栏 -->
    <div v-if="isAdmin" class="toolbar-bar">
      <el-button class="btn-blue" @click="openForm('create')">新增</el-button>
      <el-button class="btn-red" @click="handleBatchDelete">批量删除</el-button>
      <el-button class="btn-green" @click="importVisible = true">导入</el-button>
      <el-button class="btn-green" @click="handleExportSelected">导出选中</el-button>
      <el-button class="btn-green" @click="handleExportAll">导出全部</el-button>
    </div>

    <!-- 严格对齐原型的 17 列编码结果表格 -->
    <el-table
      v-loading="loading"
      :data="tableData"
      border
      class="proto-table"
      empty-text="暂无数据"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
    >
      <el-table-column type="selection" width="44" align="center" />
      <el-table-column label="序号" width="60" align="center">
        <template #default="{ $index }">
          {{ (page - 1) * pageSize + $index + 1 }}
        </template>
      </el-table-column>
      <el-table-column prop="student_no" label="学生学号" sortable="custom" min-width="96" />
      <el-table-column prop="article_no" label="文章编号" sortable="custom" min-width="102" />
      <el-table-column prop="cohort" label="届别" sortable="custom" min-width="88" />
      <el-table-column prop="segment_no" label="片段编号" sortable="custom" min-width="102" />
      <el-table-column prop="segment_order" label="片段顺序" sortable="custom" min-width="96" align="center" />
      <el-table-column prop="source_row_no" label="来源表行号" sortable="custom" min-width="106" align="center" />
      <el-table-column prop="problem_description" label="问题描述" sortable="custom" min-width="96" align="center" />
      <el-table-column prop="cause_analysis" label="原因分析" sortable="custom" min-width="96" align="center" />
      <el-table-column prop="improvement_strategy" label="改进策略" sortable="custom" min-width="96" align="center" />
      <el-table-column prop="effectiveness_eval" label="有效性评估" sortable="custom" min-width="106" align="center" />
      <el-table-column prop="description_level" label="描述层" sortable="custom" min-width="86" align="center" />
      <el-table-column prop="descriptive_reflection" label="描述性反思" sortable="custom" min-width="106" align="center" />
      <el-table-column prop="dialogic_reflection" label="对话性反思" sortable="custom" min-width="106" align="center" />
      <el-table-column prop="critical_reflection" label="批判性反思" sortable="custom" min-width="106" align="center" />
      <el-table-column label="操作" :width="isAdmin ? 136 : 76" align="center" fixed="right">
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="680px" destroy-on-close>
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="96px"
        :disabled="dialogMode === 'view'"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="学生学号" prop="student_no">
              <el-input v-model="formData.student_no" placeholder="如 001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="文章编号" prop="article_no">
              <el-input v-model="formData.article_no" placeholder="如 文章编号1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="届别" prop="cohort">
              <el-select v-model="formData.cohort" placeholder="请选择届别" style="width: 100%" filterable allow-create>
                <el-option v-for="c in cohortOptions" :key="c.id" :label="c.name" :value="c.name" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="片段编号" prop="segment_no">
              <el-input v-model="formData.segment_no" placeholder="如 片段编号1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="片段顺序" prop="segment_order">
              <el-input-number v-model="formData.segment_order" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="来源表行号" prop="source_row_no">
              <el-input-number v-model="formData.source_row_no" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">反思要素编码（严格二值：0 未出现 / 1 出现）</el-divider>

        <el-row :gutter="16">
          <el-col v-for="item in CODE_FIELDS" :key="item.key" :span="12">
            <el-form-item :label="item.label" :prop="item.key">
              <el-radio-group v-model="formData[item.key]">
                <el-radio :value="0">0（无）</el-radio>
                <el-radio :value="1">1（有）</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ dialogMode === 'view' ? '关闭' : '取消' }}</el-button>
        <el-button v-if="dialogMode !== 'view'" class="btn-blue" :loading="saving" @click="handleSave">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 严格编码结果批量导入校验弹窗 -->
    <ExcelImportDialog
      v-model:visible="importVisible"
      title="批量导入编码结果"
      strict-hint="系统将严格校验必填列、片段顺序、0/1合法取值、重复片段及学号-届别/文章冲突；若存在错误将定位行号与原因，不自动补写或篡改编码。"
      :upload-fn="codingResultApi.importExcel"
      :template-fn="codingResultApi.downloadTemplate"
      @success="fetchData"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import ExcelImportDialog from '@/components/ExcelImportDialog.vue'
import PaginationBar from '@/components/PaginationBar.vue'
import {
  codingResultApi,
  cohortApi,
  type CodingResultRecord,
  type CohortRecord
} from '@/api/services'
import { extractErrorMessage } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

type CodeFieldKey =
  | 'problem_description'
  | 'cause_analysis'
  | 'improvement_strategy'
  | 'effectiveness_eval'
  | 'description_level'
  | 'descriptive_reflection'
  | 'dialogic_reflection'
  | 'critical_reflection'

const CODE_FIELDS: { key: CodeFieldKey; label: string }[] = [
  { key: 'problem_description', label: '问题描述' },
  { key: 'cause_analysis', label: '原因分析' },
  { key: 'improvement_strategy', label: '改进策略' },
  { key: 'effectiveness_eval', label: '有效性评估' },
  { key: 'description_level', label: '描述层' },
  { key: 'descriptive_reflection', label: '描述性反思' },
  { key: 'dialogic_reflection', label: '对话性反思' },
  { key: 'critical_reflection', label: '批判性反思' }
]

const auth = useAuthStore()
const isAdmin = computed(() => auth.role === 'admin')

const loading = ref(false)
const saving = ref(false)
const tableData = ref<CodingResultRecord[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const ordering = ref('-id')
const selectedRows = ref<CodingResultRecord[]>([])
const cohortOptions = ref<CohortRecord[]>([])

const filters = reactive({
  student_no: '',
  article_no: '',
  cohort: ''
})

const importVisible = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'view' | 'create' | 'edit'>('view')
const currentId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const formData = reactive({
  student_no: '',
  article_no: '',
  cohort: '',
  segment_no: '',
  segment_order: 1,
  source_row_no: 1,
  problem_description: 0,
  cause_analysis: 0,
  improvement_strategy: 0,
  effectiveness_eval: 0,
  description_level: 0,
  descriptive_reflection: 0,
  dialogic_reflection: 0,
  critical_reflection: 0
})

const formRules: FormRules = {
  student_no: [{ required: true, message: '请输入学生学号', trigger: 'blur' }],
  article_no: [{ required: true, message: '请输入文章编号', trigger: 'blur' }],
  cohort: [{ required: true, message: '请选择届别', trigger: 'change' }],
  segment_no: [{ required: true, message: '请输入片段编号', trigger: 'blur' }],
  segment_order: [{ required: true, message: '请输入片段顺序', trigger: 'blur' }],
  source_row_no: [{ required: true, message: '请输入来源表行号', trigger: 'blur' }]
}

const dialogTitle = computed(() => {
  if (dialogMode.value === 'create') return '新增编码结果'
  if (dialogMode.value === 'edit') return '编辑编码结果'
  return '查看编码结果详情'
})

async function fetchData() {
  loading.value = true
  try {
    const { data } = await codingResultApi.list({
      page: page.value,
      page_size: pageSize.value,
      student_no: filters.student_no.trim() || undefined,
      article_no: filters.article_no.trim() || undefined,
      cohort: filters.cohort.trim() || undefined,
      ordering: ordering.value
    })
    tableData.value = data.results
    total.value = data.count
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '获取编码结果失败'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  fetchData()
  try {
    const { data } = await cohortApi.all()
    cohortOptions.value = data
  } catch {
    cohortOptions.value = []
  }
})

function handleSearch() {
  page.value = 1
  fetchData()
}

function handleSelectionChange(rows: CodingResultRecord[]) {
  selectedRows.value = rows
}

function handleSortChange({ prop, order }: { prop: string; order: string | null }) {
  if (order === 'ascending') ordering.value = prop
  else if (order === 'descending') ordering.value = `-${prop}`
  else ordering.value = '-id'
  fetchData()
}

function openForm(mode: 'view' | 'create' | 'edit', row?: CodingResultRecord) {
  dialogMode.value = mode
  currentId.value = row?.id ?? null
  formData.student_no = row?.student_no ?? ''
  formData.article_no = row?.article_no ?? ''
  formData.cohort = row?.cohort ?? ''
  formData.segment_no = row?.segment_no ?? ''
  formData.segment_order = row?.segment_order ?? 1
  formData.source_row_no = row?.source_row_no ?? 1
  formData.problem_description = row?.problem_description ?? 0
  formData.cause_analysis = row?.cause_analysis ?? 0
  formData.improvement_strategy = row?.improvement_strategy ?? 0
  formData.effectiveness_eval = row?.effectiveness_eval ?? 0
  formData.description_level = row?.description_level ?? 0
  formData.descriptive_reflection = row?.descriptive_reflection ?? 0
  formData.dialogic_reflection = row?.dialogic_reflection ?? 0
  formData.critical_reflection = row?.critical_reflection ?? 0
  dialogVisible.value = true
}

async function handleSave() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = { ...formData }
    if (dialogMode.value === 'create') {
      await codingResultApi.create(payload)
      ElMessage.success('新增编码结果成功')
    } else if (currentId.value) {
      await codingResultApi.update(currentId.value, payload)
      ElMessage.success('更新编码结果成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '保存失败'))
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: CodingResultRecord) {
  try {
    await ElMessageBox.confirm(
      `确认删除“${row.student_no} - ${row.article_no} - ${row.segment_no}”吗？`,
      '提示',
      { type: 'warning' }
    )
    await codingResultApi.remove(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(extractErrorMessage(err, '删除失败'))
  }
}

async function handleBatchDelete() {
  if (selectedRows.value.length === 0) {
    return ElMessage.warning('请先勾选要删除的编码结果')
  }
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedRows.value.length} 条编码结果吗？`, '批量删除', {
      type: 'warning'
    })
    await codingResultApi.batchDelete(selectedRows.value.map((r) => r.id))
    ElMessage.success('批量删除成功')
    fetchData()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(extractErrorMessage(err, '批量删除失败'))
  }
}

async function handleExportSelected() {
  if (selectedRows.value.length === 0) {
    return ElMessage.warning('请先勾选要导出的编码结果')
  }
  try {
    await codingResultApi.exportExcel(
      { ids: selectedRows.value.map((r) => r.id).join(',') },
      '编码结果_选中.xlsx'
    )
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '导出失败'))
  }
}

async function handleExportAll() {
  try {
    await codingResultApi.exportExcel(
      {
        student_no: filters.student_no.trim() || undefined,
        article_no: filters.article_no.trim() || undefined,
        cohort: filters.cohort.trim() || undefined
      },
      '编码结果_全部.xlsx'
    )
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '导出失败'))
  }
}
</script>

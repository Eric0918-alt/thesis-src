<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    width="680px"
    destroy-on-close
    @update:model-value="emit('update:visible', $event)"
  >
    <div class="import-tip-box">
      <div class="tip-text">
        <p style="margin: 0 0 6px 0">
          支持上传 <strong>.xlsx</strong> 或 <strong>.csv</strong> 格式文件。
        </p>
        <p v-if="strictHint" style="margin: 0; color: #606266; font-size: 12px">
          {{ strictHint }}
        </p>
      </div>
      <el-button type="primary" link @click="onDownloadTemplate">
        <el-icon style="margin-right: 4px"><Download /></el-icon>
        下载导入模板
      </el-button>
    </div>

    <el-upload
      drag
      action="#"
      :auto-upload="false"
      :limit="1"
      accept=".xlsx,.xls,.csv"
      :on-change="handleFileChange"
      :on-remove="handleFileRemove"
      :file-list="fileList"
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">将文件拖到此处，或 <em>点击选择文件</em></div>
    </el-upload>

    <div v-if="validationErrors.length > 0" class="error-report">
      <el-alert
        :title="errorSummary || `校验未通过，共发现 ${validationErrors.length} 处错误，请修正后重新导入`"
        type="error"
        :closable="false"
        show-icon
        style="margin-bottom: 10px"
      />
      <el-table :data="validationErrors" border size="small" max-height="240">
        <el-table-column prop="row" label="行号" width="76" align="center" />
        <el-table-column prop="field" label="字段" width="120" />
        <el-table-column prop="reason" label="错误原因" />
      </el-table>
    </div>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button class="btn-blue" :loading="submitting" :disabled="!selectedFile" @click="handleSubmit">
        开始校验并导入
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage, type UploadFile, type UploadUserFile } from 'element-plus'
import { extractErrorMessage } from '@/api/http'

interface ValidationErrorItem {
  row: number
  field: string
  reason: string
}

const props = defineProps<{
  visible: boolean
  title: string
  strictHint?: string
  uploadFn: (file: File) => Promise<{ data: { imported?: number; detail?: string } }>
  templateFn: () => Promise<void>
}>()

const emit = defineEmits<{
  (e: 'update:visible', val: boolean): void
  (e: 'success'): void
}>()

const selectedFile = ref<File | null>(null)
const fileList = ref<UploadUserFile[]>([])
const submitting = ref(false)
const errorSummary = ref('')
const validationErrors = ref<ValidationErrorItem[]>([])

watch(
  () => props.visible,
  (val) => {
    if (val) {
      selectedFile.value = null
      fileList.value = []
      errorSummary.value = ''
      validationErrors.value = []
    }
  }
)

function handleFileChange(file: UploadFile) {
  selectedFile.value = (file.raw as File) || null
  fileList.value = file.raw ? [file] : []
  errorSummary.value = ''
  validationErrors.value = []
}

function handleFileRemove() {
  selectedFile.value = null
  fileList.value = []
}

async function onDownloadTemplate() {
  try {
    await props.templateFn()
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '模板下载失败'))
  }
}

async function handleSubmit() {
  if (!selectedFile.value) return
  submitting.value = true
  errorSummary.value = ''
  validationErrors.value = []
  try {
    const res = await props.uploadFn(selectedFile.value)
    ElMessage.success(res.data.detail || '导入成功')
    emit('success')
    close()
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string; errors?: ValidationErrorItem[] } } }
    const data = e?.response?.data
    if (data?.errors && Array.isArray(data.errors) && data.errors.length > 0) {
      errorSummary.value = data.detail || '导入数据存在校验错误'
      validationErrors.value = data.errors
    } else {
      ElMessage.error(extractErrorMessage(err, '导入失败'))
    }
  } finally {
    submitting.value = false
  }
}

function close() {
  emit('update:visible', false)
}
</script>

<style scoped>
.import-tip-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f5f9ff;
  border: 1px solid #d6e8ff;
  border-radius: 6px;
  padding: 12px 14px;
  margin-bottom: 14px;
  font-size: 13px;
}

.error-report {
  margin-top: 14px;
}
</style>

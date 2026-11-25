<template>
  <div class="avatar-uploader-wrap">
    <div v-if="modelValue" class="avatar-preview-box">
      <img :src="modelValue" alt="头像" class="avatar-img" />
      <span v-if="!disabled" class="avatar-remove-btn" title="移除头像" @click.stop="handleRemove">×</span>
    </div>
    <el-upload
      v-if="!disabled"
      class="avatar-upload-trigger"
      action="#"
      :show-file-list="false"
      accept="image/*"
      :http-request="handleUpload"
    >
      <div class="upload-square">
        <el-icon v-if="!uploading" :size="20" color="#8c939d"><Plus /></el-icon>
        <el-icon v-else class="is-loading" :size="20" color="#1677ff"><Loading /></el-icon>
      </div>
    </el-upload>
  </div>
  <div v-if="!disabled" class="upload-caption">{{ caption }}</div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, type UploadRequestOptions } from 'element-plus'
import { authApi } from '@/api/services'
import { extractErrorMessage } from '@/api/http'

withDefaults(
  defineProps<{
    modelValue: string
    caption?: string
    disabled?: boolean
  }>(),
  {
    caption: '点击上传头像',
    disabled: false
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const uploading = ref(false)

async function handleUpload(options: UploadRequestOptions) {
  uploading.value = true
  try {
    const { data } = await authApi.uploadAvatar(options.file as File)
    emit('update:modelValue', data.url)
    ElMessage.success('头像上传成功')
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '头像上传失败'))
  } finally {
    uploading.value = false
  }
}

function handleRemove() {
  emit('update:modelValue', '')
}
</script>

<style scoped>
.avatar-uploader-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-preview-box {
  position: relative;
  width: 68px;
  height: 68px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #e4e7ed;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-remove-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 13px;
  line-height: 17px;
  text-align: center;
  cursor: pointer;
}

.upload-square {
  width: 68px;
  height: 68px;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: #fafafa;
  transition: border-color 0.2s;
}

.upload-square:hover {
  border-color: #1677ff;
}

.upload-caption {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}
</style>

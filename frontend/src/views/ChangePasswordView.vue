<template>
  <div class="page-card profile-card">
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="96px"
      class="two-col-form"
    >
      <el-row :gutter="40">
        <el-col :span="12">
          <el-form-item label="原密码" prop="old_password">
            <el-input v-model="form.old_password" type="password" show-password placeholder="请输入原密码" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="新密码" prop="new_password">
            <el-input v-model="form.new_password" type="password" show-password placeholder="请输入新密码" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="确认密码" prop="confirm_password">
            <el-input v-model="form.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
          </el-form-item>
        </el-col>
      </el-row>

      <div class="submit-row">
        <el-button class="btn-blue submit-btn" :loading="submitting" @click="handleSubmit">
          提交
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { authApi } from '@/api/services'
import { extractErrorMessage } from '@/api/http'

const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const rules: FormRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码长度不能少于 6 位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.new_password) {
          callback(new Error('两次输入的新密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await authApi.changePassword({
      old_password: form.old_password,
      new_password: form.new_password,
      confirm_password: form.confirm_password
    })
    ElMessage.success('密码修改成功')
    form.old_password = ''
    form.new_password = ''
    form.confirm_password = ''
    formRef.value.clearValidate()
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '密码修改失败'))
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.profile-card {
  padding: 40px 32px 36px;
}

.two-col-form {
  max-width: 820px;
  margin: 0 auto;
}

.submit-row {
  margin-top: 22px;
  text-align: center;
}

.submit-btn {
  min-width: 88px;
}
</style>

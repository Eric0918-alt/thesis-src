<template>
  <div class="auth-page">
    <div class="register-card">
      <h2 class="register-title">基于ENA与聚类的师范生教学反思分析系统设计与实现</h2>

      <div class="register-rows">
        <div class="register-field-box">
          <span class="register-field-label">教师工号:<span class="req-star">*</span></span>
          <el-input v-model="form.teacher_no" placeholder="教师工号" clearable />
        </div>

        <div class="register-field-box">
          <span class="register-field-label">教师姓名:<span class="req-star">*</span></span>
          <el-input v-model="form.name" placeholder="教师姓名" clearable />
        </div>

        <div class="register-field-box">
          <span class="register-field-label">密码:<span class="req-star">*</span></span>
          <el-input v-model="form.password" type="password" show-password placeholder="密码" />
        </div>

        <div class="register-field-box">
          <span class="register-field-label">确认密码:<span class="req-star">*</span></span>
          <el-input v-model="form.confirm_password" type="password" show-password placeholder="确认密码" />
        </div>

        <div class="register-field-box">
          <span class="register-field-label">性别:</span>
          <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%" clearable>
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </div>

        <div class="register-field-box">
          <span class="register-field-label">手机号码:</span>
          <el-input v-model="form.phone" placeholder="手机号码" clearable />
        </div>

        <div class="register-field-box register-avatar-box">
          <span class="register-field-label">头像:</span>
          <div class="avatar-inner">
            <AvatarUploader v-model="form.avatar" />
          </div>
        </div>
      </div>

      <el-button
        class="btn-blue register-submit-btn"
        size="large"
        :loading="loading"
        @click="handleSubmit"
      >
        注册
      </el-button>

      <div class="back-login-wrap">
        <router-link to="/login" class="back-login-link">已有账号，直接登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AvatarUploader from '@/components/AvatarUploader.vue'
import { authApi } from '@/api/services'
import { extractErrorMessage } from '@/api/http'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  teacher_no: '',
  name: '',
  password: '',
  confirm_password: '',
  gender: '',
  phone: '',
  avatar: ''
})

async function handleSubmit() {
  if (!form.teacher_no.trim()) return ElMessage.warning('请输入教师工号')
  if (!form.name.trim()) return ElMessage.warning('请输入教师姓名')
  if (!form.password || form.password.length < 6) return ElMessage.warning('请输入至少6位密码')
  if (form.password !== form.confirm_password) return ElMessage.warning('两次输入的密码不一致')

  loading.value = true
  try {
    await authApi.registerTeacher({
      teacher_no: form.teacher_no.trim(),
      name: form.name.trim(),
      password: form.password,
      confirm_password: form.confirm_password,
      gender: form.gender,
      phone: form.phone.trim(),
      avatar: form.avatar
    })
    ElMessage.success('教师注册成功，请登录')
    router.push('/login')
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '注册失败'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-card {
  width: 470px;
  max-width: 100%;
  background: #ffffff;
  border-radius: 10px;
  padding: 28px 34px 24px;
  box-shadow: 0 20px 50px rgba(0, 34, 110, 0.25);
}

.register-title {
  margin: 0 0 20px 0;
  text-align: center;
  font-size: 16px;
  font-weight: 700;
  color: #2b73df;
}

.register-rows {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.register-avatar-box {
  align-items: flex-start;
  padding-top: 10px;
  padding-bottom: 10px;
}

.avatar-inner {
  padding-left: 6px;
}

.register-submit-btn {
  width: 100%;
  margin-top: 18px;
  height: 42px;
  font-size: 15px;
  letter-spacing: 2px;
}

.back-login-wrap {
  margin-top: 12px;
  text-align: center;
}

.back-login-link {
  font-size: 12px;
  color: #909399;
  text-decoration: underline;
}

.back-login-link:hover {
  color: #1677ff;
}
</style>

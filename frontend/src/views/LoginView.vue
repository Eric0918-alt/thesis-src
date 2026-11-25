<template>
  <div class="auth-page">
    <div class="login-card">
      <div class="login-left">
        <LoginIllustration />
      </div>

      <div class="login-right">
        <h2 class="login-title">基于ENA与聚类的师范生教学反思分析系统设计与实现</h2>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              size="large"
              placeholder="请输入账号："
              clearable
            >
              <template #prefix>
                <el-icon color="#909399"><UserFilled /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              size="large"
              type="password"
              show-password
              placeholder="请输入密码："
              @keyup.enter="handleLogin"
            >
              <template #prefix>
                <el-icon color="#909399"><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="role">
            <div class="role-radio-box">
              <el-icon color="#909399" class="role-icon"><User /></el-icon>
              <el-radio-group v-model="form.role">
                <el-radio value="student">学生</el-radio>
                <el-radio value="teacher">教师</el-radio>
                <el-radio value="admin">管理员</el-radio>
              </el-radio-group>
            </div>
          </el-form-item>

          <el-button
            class="btn-blue login-submit-btn"
            size="large"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>

          <div class="register-links">
            <router-link to="/register/student" class="reg-link">注册学生</router-link>
            <router-link to="/register/teacher" class="reg-link">注册教师</router-link>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import LoginIllustration from '@/components/LoginIllustration.vue'
import { authApi, type UserRole } from '@/api/services'
import { extractErrorMessage } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive<{ username: string; password: string; role: UserRole }>({
  username: '',
  password: '',
  role: 'student'
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择身份', trigger: 'change' }]
}

async function handleLogin() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const { data } = await authApi.login({
      username: form.username.trim(),
      password: form.password,
      role: form.role
    })
    auth.setSession(data.access, data.refresh, data.user)
    ElMessage.success('登录成功')
    router.push('/home')
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '账号、密码或身份不正确'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-card {
  width: 860px;
  max-width: 100%;
  min-height: 440px;
  display: flex;
  border-radius: 10px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 20px 50px rgba(0, 34, 110, 0.28);
}

.login-left {
  width: 49%;
  flex-shrink: 0;
}

.login-right {
  width: 51%;
  padding: 54px 44px 42px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-title {
  margin: 0 0 26px 0;
  text-align: center;
  font-size: 16px;
  font-weight: 700;
  color: #2b73df;
  line-height: 1.4;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.role-radio-box {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 2px 12px;
  min-height: 40px;
}

.role-icon {
  flex-shrink: 0;
}

.role-radio-box :deep(.el-radio) {
  margin-right: 18px;
}

.login-submit-btn {
  width: 100%;
  margin-top: 6px;
  height: 42px;
  font-size: 15px;
  letter-spacing: 2px;
}

.register-links {
  margin-top: 18px;
  display: flex;
  align-items: center;
  gap: 18px;
}

.reg-link {
  font-size: 13px;
  color: #606266;
  text-decoration: none;
}

.reg-link:hover {
  color: #1677ff;
}

@media (max-width: 780px) {
  .login-left {
    display: none;
  }
  .login-right {
    width: 100%;
  }
}
</style>

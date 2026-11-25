<template>
  <div class="page-card profile-card">
    <el-form ref="formRef" :model="form" label-width="96px" class="two-col-form">
      <!-- 学生个人信息 -->
      <el-row v-if="role === 'student'" :gutter="40">
        <el-col :span="12">
          <el-form-item label="学生学号">
            <el-input v-model="form.username" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="学生姓名">
            <el-input v-model="form.real_name" placeholder="请输入学生姓名" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="届别">
            <el-select v-model="form.cohort" placeholder="请选择届别" style="width: 100%" clearable>
              <el-option v-for="c in cohortOptions" :key="c.id" :label="c.name" :value="c.name" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="性别">
            <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%" clearable>
              <el-option label="男" value="男" />
              <el-option label="女" value="女" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机">
            <el-input v-model="form.phone" placeholder="请输入手机号码" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 教师个人信息 -->
      <el-row v-else-if="role === 'teacher'" :gutter="40">
        <el-col :span="12">
          <el-form-item label="教师工号">
            <el-input v-model="form.username" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="教师姓名">
            <el-input v-model="form.real_name" placeholder="请输入教师姓名" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="性别">
            <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%" clearable>
              <el-option label="男" value="男" />
              <el-option label="女" value="女" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机号码">
            <el-input v-model="form.phone" placeholder="请输入手机号码" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 管理员个人信息（与教师/学生保持完全一致） -->
      <el-row v-else :gutter="40">
        <el-col :span="12">
          <el-form-item label="管理员账号">
            <el-input v-model="form.username" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="姓名">
            <el-input v-model="form.real_name" placeholder="请输入姓名" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="性别">
            <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%" clearable>
              <el-option label="男" value="男" />
              <el-option label="女" value="女" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机号码">
            <el-input v-model="form.phone" placeholder="请输入手机号码" />
          </el-form-item>
        </el-col>
      </el-row>

      <div class="submit-row">
        <el-button class="btn-blue submit-btn" :loading="saving" @click="handleSubmit">
          提交
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { authApi, cohortApi, type CohortRecord } from '@/api/services'
import { extractErrorMessage } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const role = computed(() => auth.role)
const saving = ref(false)
const cohortOptions = ref<CohortRecord[]>([])

const form = reactive({
  username: '',
  real_name: '',
  cohort: '',
  gender: '',
  phone: ''
})

function syncFromProfile() {
  if (!auth.user) return
  form.username = auth.user.username
  form.real_name = auth.user.real_name || ''
  form.cohort = auth.user.cohort || ''
  form.gender = auth.user.gender || ''
  form.phone = auth.user.phone || ''
}

onMounted(async () => {
  syncFromProfile()
  try {
    await auth.refreshProfile()
    syncFromProfile()
  } catch {
    // ignore
  }
  if (role.value === 'student') {
    try {
      const { data } = await cohortApi.all()
      cohortOptions.value = data
    } catch {
      cohortOptions.value = []
    }
  }
})

async function handleSubmit() {
  saving.value = true
  try {
    const payload: Record<string, string> = {
      real_name: form.real_name.trim(),
      gender: form.gender,
      phone: form.phone.trim()
    }
    if (role.value === 'student') {
      payload.cohort = form.cohort
    }
    const { data } = await authApi.updateProfile(payload)
    auth.updateUser(data)
    ElMessage.success('个人信息保存成功')
  } catch (err) {
    ElMessage.error(extractErrorMessage(err, '保存失败'))
  } finally {
    saving.value = false
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

<template>
  <div class="app-shell">
    <!-- 顶部栏 -->
    <header class="app-header">
      <div class="header-left">
        <el-icon class="collapse-btn" :size="20" @click="collapsed = !collapsed">
          <Menu />
        </el-icon>
        <span class="system-title">基于ENA与聚类的师范生教学反思分析系统设计与实现</span>
      </div>
      <div class="header-right">
        <el-dropdown trigger="click" @command="handleUserCommand">
          <div class="user-trigger">
            <el-icon :size="18" color="#1677ff"><UserFilled /></el-icon>
            <span class="welcome-name">欢迎{{ auth.user?.username }}</span>
            <el-icon :size="12"><CaretBottom /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="info">个人信息</el-dropdown-item>
              <el-dropdown-item command="password">修改密码</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <div class="app-body">
      <!-- 左侧窄图标+文字居中导航栏（严格复刻原型图） -->
      <aside class="app-sidebar" :class="{ 'is-collapsed': collapsed }">
        <nav class="sidebar-nav">
          <div
            v-for="item in menuItems"
            :key="item.path"
            class="nav-item"
            :class="{ 'is-active': route.path === item.path }"
            @click="router.push(item.path)"
          >
            <el-icon :size="19"><component :is="item.icon" /></el-icon>
            <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
          </div>

          <!-- 个人中心可展开菜单 -->
          <div class="nav-group">
            <div
              class="nav-item nav-parent"
              :class="{ 'is-active': route.path.startsWith('/profile') }"
              @click="profileExpanded = !profileExpanded"
            >
              <el-icon :size="19"><Postcard /></el-icon>
              <span v-if="!collapsed" class="nav-label">个人中心</span>
              <el-icon v-if="!collapsed" class="nav-arrow" :size="12">
                <ArrowUp v-if="profileExpanded" />
                <ArrowDown v-else />
              </el-icon>
            </div>
            <div v-if="profileExpanded && !collapsed" class="sub-nav">
              <div
                class="sub-nav-item"
                :class="{ 'is-active': route.path === '/profile/password' }"
                @click="router.push('/profile/password')"
              >
                修改密码
              </div>
              <div
                class="sub-nav-item"
                :class="{ 'is-active': route.path === '/profile/info' }"
                @click="router.push('/profile/info')"
              >
                个人信息
              </div>
            </div>
          </div>
        </nav>
      </aside>

      <!-- 主内容区 -->
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const collapsed = ref(false)
const profileExpanded = ref(route.path.startsWith('/profile'))

watch(
  () => route.path,
  (newPath) => {
    if (newPath.startsWith('/profile')) {
      profileExpanded.value = true
    }
  }
)

onMounted(() => {
  auth.refreshProfile().catch(() => {})
})

const menuItems = computed(() => {
  const role = auth.role
  if (role === 'student') {
    return [
      { path: '/home', label: '系统首页', icon: 'HomeFilled' },
      { path: '/coding-results', label: '编码结果', icon: 'UserFilled' }
    ]
  }
  if (role === 'teacher') {
    return [
      { path: '/home', label: '系统首页', icon: 'HomeFilled' },
      { path: '/students', label: '学生', icon: 'User' },
      { path: '/coding-results', label: '编码结果', icon: 'Document' }
    ]
  }
  // admin
  return [
    { path: '/home', label: '系统首页', icon: 'HomeFilled' },
    { path: '/students', label: '学生', icon: 'Flag' },
    { path: '/teachers', label: '教师', icon: 'Grid' },
    { path: '/cohorts', label: '届别', icon: 'CollectionTag' },
    { path: '/coding-results', label: '编码结果', icon: 'Menu' },
    { path: '/logs', label: '系统日志', icon: 'Tickets' }
  ]
})

function handleUserCommand(cmd: string) {
  if (cmd === 'info') {
    router.push('/profile/info')
  } else if (cmd === 'password') {
    router.push('/profile/password')
  } else if (cmd === 'logout') {
    auth.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: #f0f2f5;
}

.app-header {
  height: 54px;
  background: #ffffff;
  border-bottom: 1px solid #ebeef5;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 28px;
}

.collapse-btn {
  cursor: pointer;
  color: #303133;
}

.system-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  letter-spacing: 0.3px;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
  font-size: 13px;
}

.welcome-name {
  color: #606266;
}

.app-body {
  display: flex;
  flex: 1;
  min-height: 0;
}

.app-sidebar {
  width: 108px;
  background: #ffffff;
  border-right: 1px solid #ebeef5;
  overflow-y: auto;
  flex-shrink: 0;
  transition: width 0.2s ease;
  padding: 12px 6px;
}

.app-sidebar.is-collapsed {
  width: 60px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 6px;
  border-radius: 6px;
  cursor: pointer;
  color: #606266;
  gap: 5px;
  transition: color 0.15s, background-color 0.15s;
}

.nav-item:hover {
  color: #1677ff;
  background-color: #f5f9ff;
}

.nav-item.is-active {
  color: #1677ff;
  font-weight: 500;
}

.nav-label {
  font-size: 12px;
  line-height: 1.2;
}

.nav-arrow {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  color: #909399;
}

.sub-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 2px;
}

.sub-nav-item {
  text-align: center;
  padding: 8px 4px;
  font-size: 12px;
  color: #606266;
  cursor: pointer;
  border-radius: 4px;
}

.sub-nav-item:hover {
  color: #1677ff;
  background: #f5f9ff;
}

.sub-nav-item.is-active {
  color: #1677ff;
  font-weight: 500;
}

.app-main {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
  padding: 16px;
  background: #f0f2f5;
}
</style>

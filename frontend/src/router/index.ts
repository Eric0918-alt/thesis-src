import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/api/services'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true }
  },
  {
    path: '/register/student',
    name: 'RegisterStudent',
    component: () => import('@/views/RegisterStudentView.vue'),
    meta: { public: true }
  },
  {
    path: '/register/teacher',
    name: 'RegisterTeacher',
    component: () => import('@/views/RegisterTeacherView.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/HomeView.vue'),
        meta: { roles: ['student', 'teacher', 'admin'] as UserRole[] }
      },
      {
        path: 'students',
        name: 'Students',
        component: () => import('@/views/StudentListView.vue'),
        meta: { roles: ['teacher', 'admin'] as UserRole[] }
      },
      {
        path: 'teachers',
        name: 'Teachers',
        component: () => import('@/views/TeacherListView.vue'),
        meta: { roles: ['admin'] as UserRole[] }
      },
      {
        path: 'cohorts',
        name: 'Cohorts',
        component: () => import('@/views/CohortListView.vue'),
        meta: { roles: ['admin'] as UserRole[] }
      },
      {
        path: 'coding-results',
        name: 'CodingResults',
        component: () => import('@/views/CodingResultListView.vue'),
        meta: { roles: ['student', 'teacher', 'admin'] as UserRole[] }
      },
      {
        path: 'logs',
        name: 'SystemLogs',
        component: () => import('@/views/SystemLogListView.vue'),
        meta: { roles: ['admin'] as UserRole[] }
      },
      {
        path: 'profile/password',
        name: 'ChangePassword',
        component: () => import('@/views/ChangePasswordView.vue'),
        meta: { roles: ['student', 'teacher', 'admin'] as UserRole[] }
      },
      {
        path: 'profile/info',
        name: 'PersonalInfo',
        component: () => import('@/views/PersonalInfoView.vue'),
        meta: { roles: ['student', 'teacher', 'admin'] as UserRole[] }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/home'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    if (auth.isAuthenticated) {
      return '/home'
    }
    return true
  }

  if (!auth.isAuthenticated) {
    return '/login'
  }

  const allowedRoles = to.meta.roles as UserRole[] | undefined
  if (allowedRoles && auth.role && !allowedRoles.includes(auth.role)) {
    return '/home'
  }

  return true
})

export default router

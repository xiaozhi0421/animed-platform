import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi } from '@/api'

export type UserRole = 'campus_student' | 'campus_teacher' | 'campus_admin'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const _storedInfo = localStorage.getItem('userInfo');
  const userInfo = ref<any>(_storedInfo ? JSON.parse(_storedInfo) : null)

  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed<UserRole>(() => userInfo.value?.role || 'campus_student')
  const userName = computed(() => userInfo.value?.name || userInfo.value?.realName || '')

  // 根据角色判断所属系统
  const currentSystem = computed(() => {
    const role = userRole.value
    if (['campus_student', 'campus_teacher', 'campus_admin'].includes(role)) return 'campus'
    return 'campus'
  })

  // 角色中文名
  const roleName = computed(() => {
    const map: Record<string, string> = {
      campus_student: '学生',
      campus_teacher: '教师',
      campus_admin: '校园管理员'
    }
    return map[userRole.value] || ''
  })

  async function login(data: { account: string; password: string; system: string }) {
    const res: any = await authApi.login(data)
    token.value = res.data.token
    localStorage.setItem('token', res.data.token)
    userInfo.value = res.data
    localStorage.setItem('userInfo', JSON.stringify(res.data))
  }

  async function fetchUserInfo() {
    const res: any = await userApi.getUserInfo()
    userInfo.value = res.data
    localStorage.setItem('userInfo', JSON.stringify(res.data))
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('system')
  }

  function initFromStorage() {
    const stored = localStorage.getItem('userInfo')
    if (stored) {
      try { userInfo.value = JSON.parse(stored) } catch {}
    }
  }

  // 根据角色获取默认跳转路径
  function getDefaultRoute(): string {
    const role = userRole.value
    const map: Record<string, string> = {
      campus_student: '/campus/dashboard',
      campus_teacher: '/campus/dashboard',
      campus_admin: '/admin/dashboard'
    }
    return map[role] || '/campus/dashboard'
  }

  return { token, userInfo, currentSystem, isLoggedIn, userRole, userName, roleName, login, fetchUserInfo, logout, initFromStorage, getDefaultRoute }
})

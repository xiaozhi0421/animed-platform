<template>

  <div class="campus-layout">

    <div class="particles-bg-layer">

      <ParticlesBg color="#ffffff" :quantity="250" class="particles-canvas" />

    </div>



    <!-- ===== Top Navigation ===== -->

    <header class="top-nav">

      <div class="nav-inner">

        <div class="nav-left">

          <div class="nav-logo" @click="$router.push('/campus/dashboard')">

            <CatLogo size="sm" color="#6366f1" />

            <span class="logo-text">AniMed <span class="logo-role">{{ logoText }}</span></span>

          </div>

        </div>



        <div class="nav-center">

          <!-- Student Nav -->

          <template v-if="userStore.userRole === 'campus_student'">

            <a class="nav-item" :class="{ active: currentPath === '/campus/dashboard' }" @click="router.push('/campus/dashboard')">首页</a>

            <el-dropdown trigger="hover" placement="bottom" @command="(p) => router.push(p)">

              <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/data') }">

                数据管理<el-icon style="margin-left:3px"><ArrowDown /></el-icon>

              </a>

              <template #dropdown>

                <el-dropdown-menu>

                  <el-dropdown-item command="/campus/data">数据管理</el-dropdown-item>

                  <el-dropdown-item command="/campus/data/clean">数据清洗</el-dropdown-item>

                </el-dropdown-menu>

              </template>

            </el-dropdown>

            <el-dropdown trigger="hover" placement="bottom" @command="(p) => router.push(p)">

              <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/analysis') }">

                数据分析<el-icon style="margin-left:3px"><ArrowDown /></el-icon>

              </a>

              <template #dropdown>

                <el-dropdown-menu>

                  <el-dropdown-item command="/campus/analysis">数据分析</el-dropdown-item>

                  <el-dropdown-item command="/campus/analysis/library">分析库</el-dropdown-item>

                </el-dropdown-menu>

              </template>

            </el-dropdown>
            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/data/mining') }" @click="router.push('/campus/data/mining')">数据挖掘</a>
            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/data/visualization') }" @click="router.push('/campus/data/visualization')">数据可视化</a>

            <a class="nav-item" :class="{ active: currentPath === '/campus/ai-chat' }" @click="router.push('/campus/ai-chat')">AI 助手</a>

            <a class="nav-item" :class="{ active: currentPath === '/campus/knowledge' }" @click="router.push('/campus/knowledge')">知识库</a>

            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/chat') }" @click="router.push('/campus/chat')">

              师生沟通

              <span v-if="chatStore.unreadCount > 0" class="nav-badge">{{ chatStore.unreadCount > 99 ? '99+' : chatStore.unreadCount }}</span>

            </a>

            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/my-class') }" @click="router.push('/campus/my-class')">我的班级</a>

            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/submission') }" @click="router.push('/campus/submission')">课题提交</a>

            <el-dropdown trigger="hover" placement="bottom" @command="(p) => router.push(p)">

              <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/lab-equipment') || currentPath.startsWith('/campus/equipment') || currentPath.startsWith('/campus/my-lab') }">

                实验室<el-icon style="margin-left:3px"><ArrowDown /></el-icon>

              </a>

              <template #dropdown>

                <el-dropdown-menu>

                  <el-dropdown-item command="/campus/lab-equipment">仪器列表</el-dropdown-item>

                  <el-dropdown-item command="/campus/my-lab-reservations">我的预约</el-dropdown-item>

                </el-dropdown-menu>

              </template>

            </el-dropdown>

          </template>



          <!-- Teacher Nav -->

          <template v-else-if="userStore.userRole === 'campus_teacher'">

            <a class="nav-item" :class="{ active: currentPath === '/campus/dashboard' }" @click="router.push('/campus/dashboard')">首页</a>

            <el-dropdown trigger="hover" placement="bottom" @command="(p) => router.push(p)">

              <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/data') }">

                数据管理<el-icon style="margin-left:3px"><ArrowDown /></el-icon>

              </a>

              <template #dropdown>

                <el-dropdown-menu>

                  <el-dropdown-item command="/campus/data">数据管理</el-dropdown-item>

                  <el-dropdown-item command="/campus/data/clean">数据清洗</el-dropdown-item>

                </el-dropdown-menu>

              </template>

            </el-dropdown>

            <el-dropdown trigger="hover" placement="bottom" @command="(p) => router.push(p)">

              <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/analysis') }">

                数据分析<el-icon style="margin-left:3px"><ArrowDown /></el-icon>

              </a>

              <template #dropdown>

                <el-dropdown-menu>

                  <el-dropdown-item command="/campus/analysis">数据分析</el-dropdown-item>

                  <el-dropdown-item command="/campus/analysis/library">分析库</el-dropdown-item>

                </el-dropdown-menu>

              </template>

            </el-dropdown>

            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/data/mining') }" @click="router.push('/campus/data/mining')">数据挖掘</a>
            <a class="nav-item" :class="{ active: currentPath === '/campus/ai-chat' }" @click="router.push('/campus/ai-chat')">AI 助手</a>

            <a class="nav-item" :class="{ active: currentPath === '/campus/knowledge' }" @click="router.push('/campus/knowledge')">知识库</a>

            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/chat') }" @click="router.push('/campus/chat')">

              师生沟通

              <span v-if="chatStore.unreadCount > 0" class="nav-badge">{{ chatStore.unreadCount > 99 ? '99+' : chatStore.unreadCount }}</span>

            </a>

            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/my-class') }" @click="router.push('/campus/my-class')">我的班级</a>

            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/submission') }" @click="router.push('/campus/submission')">课题审阅</a>

            <el-dropdown trigger="hover" placement="bottom" @command="(p) => router.push(p)">

              <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/lab-equipment') || currentPath.startsWith('/campus/equipment') || currentPath.startsWith('/campus/my-lab') }">

                实验室<el-icon style="margin-left:3px"><ArrowDown /></el-icon>

              </a>

              <template #dropdown>

                <el-dropdown-menu>

                  <el-dropdown-item command="/campus/lab-equipment">仪器列表</el-dropdown-item>

                  <el-dropdown-item command="/campus/my-lab-reservations">我的预约</el-dropdown-item>

                </el-dropdown-menu>

              </template>

            </el-dropdown>

          </template>



          <!-- Admin Nav -->

          <template v-else>

            <a class="nav-item" :class="{ active: currentPath === '/campus/dashboard' }" @click="router.push('/campus/dashboard')">首页</a>

            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/data') }" @click="router.push('/campus/data')">数据管理</a>

            <a class="nav-item" :class="{ active: currentPath === '/campus/knowledge' }" @click="router.push('/campus/knowledge')">知识库</a>

            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/student') }" @click="router.push('/campus/student-manage')">学生管理</a>

            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/teacher') }" @click="router.push('/campus/teacher-manage')">教师管理</a>

            <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/admin-submission') }" @click="router.push('/campus/admin-submissions')">课题管理</a>

            <el-dropdown trigger="hover" placement="bottom" @command="(p) => router.push(p)">

              <a class="nav-item" :class="{ active: currentPath.startsWith('/campus/labs') || currentPath.startsWith('/campus/admin-lab') || currentPath.startsWith('/campus/equipment') }">

                实验室管理<el-icon style="margin-left:3px"><ArrowDown /></el-icon>

              </a>

              <template #dropdown>

                <el-dropdown-menu>

                  <el-dropdown-item command="/campus/admin-lab-management">实验室列表</el-dropdown-item>

                  <el-dropdown-item command="/campus/admin-lab-equipment">设备管理</el-dropdown-item>

                  <el-dropdown-item command="/campus/admin-lab-maintenance">维护记录</el-dropdown-item>

                  <el-dropdown-item command="/campus/admin-lab-reservations">预约管理</el-dropdown-item>

                </el-dropdown-menu>

              </template>

            </el-dropdown>

            <a class="nav-item" :class="{ active: currentPath === '/campus/log' }" @click="router.push('/campus/log')">日志管理</a>

          </template>

        </div>



        <div class="nav-right">

          <el-tag size="small" class="role-tag" effect="plain">{{ userStore.roleName }}</el-tag>



          <!-- Notification Bell -->

          <el-badge :value="notificationStore.unreadCount" :max="99" :hidden="notificationStore.unreadCount === 0">

            <button class="icon-btn" @click="router.push('/campus/chat')">

              <el-icon><Bell /></el-icon>

            </button>

          </el-badge>



          <!-- User Dropdown -->

          <el-dropdown trigger="click">

            <div class="user-info">

              <el-avatar :size="30" :src="userStore.userInfo?.avatar" class="user-avatar">{{ userStore.userName?.charAt(0) }}</el-avatar>

            </div>

            <template #dropdown>

              <el-dropdown-menu>

                <el-dropdown-item @click="$router.push('/campus/profile')">

                  <el-icon><User /></el-icon> 个人中心

                </el-dropdown-item>

                <el-dropdown-item divided @click="handleLogout">

                  <el-icon><SwitchButton /></el-icon> 退出登录

                </el-dropdown-item>

              </el-dropdown-menu>

            </template>

          </el-dropdown>

        </div>

      </div>

    </header>



    <!-- Mobile Overlay -->

    <div v-if="mobileOpen" class="mobile-overlay" @click="mobileOpen = false"></div>



    <!-- Mobile Nav -->

    <div class="mobile-nav" :class="{ open: mobileOpen }">

      <div class="mobile-nav-header">

        <div class="mobile-nav-logo">

          <CatLogo size="sm" color="#6366f1" />

          <span style="font-size:14px;font-weight:600;color:#fff">AniMed {{ logoText }}</span>

        </div>

        <button class="mobile-close" @click="mobileOpen = false">

          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">

            <path d="M18 6 6 18" /><path d="m6 6 12 12" />

          </svg>

        </button>

      </div>

      <div class="mobile-nav-items">

        <a v-for="item in mobileNavItems" :key="item.path" :class="['mobile-nav-item', { active: currentPath === item.path }]" @click="router.push(item.path); mobileOpen = false">

          

          <span>{{ item.label }}</span>

        </a>

      </div>

    </div>



    <!-- Main Content -->

    <main class="main-content">

      <router-view v-slot="{ Component }">

        <component :is="Component" :key="$route.fullPath" />

      </router-view>

    </main>



    <!-- Mobile Menu Button -->

    <button class="mobile-menu-btn" @click="mobileOpen = !mobileOpen">

      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">

        <line x1="4" x2="20" y1="12" y2="12" /><line x1="4" x2="20" y1="6" y2="6" /><line x1="4" x2="20" y1="18" y2="18" />

      </svg>

    </button>



    <!-- Floating AI Assistant -->

    <FloatingAIAssistant />

  </div>

</template>



<script setup lang="ts">

import { ref, computed, onMounted } from 'vue'

import { useRoute, useRouter } from 'vue-router'

import { useUserStore } from '@/stores/user'

import { useChatStore } from '@/stores/chat'

import { useNotificationStore } from '@/stores/notification'

import CatLogo from '@/components/inspira/CatLogo.vue'

import ParticlesBg from '@/components/inspira/ParticlesBg.vue'

import FloatingAIAssistant from '@/components/FloatingAIAssistant.vue'

import { Bell, User, SwitchButton, ArrowDown } from '@element-plus/icons-vue'



const route = useRoute()

const router = useRouter()

const userStore = useUserStore()

const chatStore = useChatStore()

const notificationStore = useNotificationStore()

const mobileOpen = ref(false)



const currentPath = computed(() => route.path)



const logoText = computed(() => {

  const map: Record<string, string> = {

    campus_student: '学生端',

    campus_teacher: '教师端',

    campus_admin: '管理端'

  }

  return map[userStore.userRole] || '校园端'

})



const mobileNavItems = computed(() => {

  const role = userStore.userRole

  if (role === 'campus_student') {

    return [

      { path: '/campus/dashboard', label: '首页' },

      { path: '/campus/data', label: '数据管理' },

      { path: '/campus/analysis', label: '数据分析' },

      { path: '/campus/ai-chat', label: 'AI 助手' },
      { path: '/campus/data/mining', label: '数据挖掘' },

      { path: '/campus/knowledge', label: '知识库' },

      { path: '/campus/chat', label: '师生沟通' },

      { path: '/campus/my-class', label: '我的班级' },

      { path: '/campus/submission', label: '课题提交' },

      { path: '/campus/lab-equipment', label: '仪器列表' },

      { path: '/campus/my-lab-reservations', label: '我的预约' }

    ]

  }

  if (role === 'campus_teacher') {

    return [

      { path: '/campus/dashboard', label: '首页' },

      { path: '/campus/data', label: '数据管理' },

      { path: '/campus/analysis', label: '数据分析' },

      { path: '/campus/ai-chat', label: 'AI 助手' },
      { path: '/campus/data/mining', label: '数据挖掘' },

      { path: '/campus/knowledge', label: '知识库' },

      { path: '/campus/chat', label: '师生沟通' },

      { path: '/campus/my-class', label: '我的班级' },

      { path: '/campus/submission', label: '课题审阅' },

      { path: '/campus/lab-equipment', label: '仪器列表' },

      { path: '/campus/my-lab-reservations', label: '我的预约' }

    ]

  }

  // admin

  return [

    { path: '/campus/dashboard', label: '首页' },

    { path: '/campus/data', label: '数据管理' },

    { path: '/campus/knowledge', label: '知识库' },

    { path: '/campus/student-manage', label: '学生管理' },

    { path: '/campus/teacher-manage', label: '教师管理' },

    { path: '/campus/admin-submissions', label: '课题管理' },

    { path: '/campus/admin-lab-management', label: '实验室列表' },

    { path: '/campus/admin-lab-equipment', label: '设备管理' },

    { path: '/campus/admin-lab-maintenance', label: '维护记录' },

    { path: '/campus/admin-lab-reservations', label: '预约管理' },

    { path: '/campus/log', label: '日志管理' }

  ]

})



onMounted(() => {

  userStore.initFromStorage()

  chatStore.fetchUnreadCount().catch(() => {})

  notificationStore.fetchUnreadCount().catch(() => {})

})



function handleLogout() {

  userStore.logout()

  router.push('/login')

}

</script>



<style scoped lang="scss">

.campus-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #1d1e3a 30%, #0d7377 70%, #14b8a6 100%);

  position: relative;

}



/* ===== Particles Background ===== */

.particles-bg-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  background: transparent;

  pointer-events: none;

  overflow: hidden;

}

.particles-canvas {

  width: 100%;

  height: 100%;

}



/* ===== Top Navigation ===== */

.top-nav {
  position: sticky;
  top: 0;
  z-index: 60;
  background: rgba(15, 12, 41, 0.85);

  backdrop-filter: blur(12px);

  -webkit-backdrop-filter: blur(12px);

  border-bottom: 1px solid rgba(255, 255, 255, 0.08);

  height: 56px;

}

.nav-inner {

  max-width: 1280px;

  margin: 0 auto;

  padding: 0 24px;

  height: 100%;

  display: flex;

  align-items: center;

  justify-content: space-between;

  gap: 16px;

}

.nav-left {

  flex-shrink: 0;

}

.nav-logo {

  display: flex;

  align-items: center;

  gap: 8px;

  cursor: pointer;

}

.nav-logo svg {

  width: 24px;

  height: 24px;

}

.logo-text {

  font-size: 15px;

  font-weight: 700;

  color: #fff;

}

.logo-role {

  font-weight: 500;

  color: #6366f1;

}



/* ===== Center Navigation ===== */

.nav-center {

  display: flex;

  align-items: center;

  gap: 2px;

  overflow-x: auto;

  flex: 1;

  justify-content: center;

  -ms-overflow-style: none;

  scrollbar-width: none;

  padding: 0 8px;

}

.nav-center::-webkit-scrollbar {

  display: none;

}

.nav-item {

  display: inline-flex;

  align-items: center;

  gap: 4px;

  padding: 6px 12px;

  border-radius: 6px;

  font-size: 13px;

  font-weight: 500;

  color: rgba(255, 255, 255, 0.6);

  white-space: nowrap;

  cursor: pointer;

  transition: all 0.15s;

  text-decoration: none;

  position: relative;

}

.nav-item:hover {

  color: #fff;

  background: rgba(255, 255, 255, 0.1);

}

.nav-item.active {

  color: #818cf8;

  background: rgba(99, 102, 241, 0.15);

  font-weight: 600;

}

.nav-badge {

  display: inline-flex;

  align-items: center;

  justify-content: center;

  min-width: 18px;

  height: 18px;

  padding: 0 5px;

  border-radius: 10px;

  background: #ef4444;

  color: #fff;

  font-size: 11px;

  font-weight: 700;

  line-height: 1;

}



/* ===== Right Navigation ===== */

.nav-right {

  display: flex;

  align-items: center;

  gap: 12px;

  flex-shrink: 0;

}

.role-tag {

  border-radius: 6px;

  font-size: 12px;

}

.role-tag.el-tag--primary.el-tag--plain {

  background-color: rgba(255,255,255,0.05) !important;

  border-color: rgba(255,255,255,0.08) !important;

  color: rgba(255,255,255,0.7) !important;

}

.user-info {

  cursor: pointer;

  padding: 2px;

  border-radius: 50%;

  transition: all 0.2s;

  display: flex;

  align-items: center;

}

.user-info:hover {

  box-shadow: 0 0 0 2px rgba(224, 231, 255, 0.3);

}

.user-avatar {

  background: linear-gradient(135deg, #6366f1, #818cf8);

  font-size: 13px;

  flex-shrink: 0;

}

.icon-btn {

  width: 32px;

  height: 32px;

  border-radius: 8px;

  border: none;

  background: transparent;

  color: rgba(255,255,255,0.6);

  cursor: pointer;

  display: flex;

  align-items: center;

  justify-content: center;

  transition: all 0.15s;

}

.icon-btn:hover {

  background: rgba(255,255,255,0.1);

  color: #fff;

}



/* ===== Main Content ===== */

.main-content {

  max-width: 1280px;

  margin: 0 auto;

  padding-top: 8px;

  position: relative;

  z-index: 1;

}



/* ===== Mobile Menu ===== */

.mobile-menu-btn {

  position: fixed;

  bottom: 24px;

  right: 24px;

  z-index: 100;

  width: 48px;

  height: 48px;

  border-radius: 14px;

  background: #fff;

  color: #000;

  border: none;

  cursor: pointer;

  display: none;

  align-items: center;

  justify-content: center;

  box-shadow: 0 4px 16px rgba(0,0,0,0.15);

}

.mobile-overlay {

  position: fixed;

  top: 0;

  right: 0;

  bottom: 0;

  left: 0;

  z-index: 60;

  background: rgba(0,0,0,0.3);

}

.mobile-nav {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  z-index: 70;
  background: linear-gradient(180deg, #0f0c29, #1d1e3a);

  transform: translateX(-100%);

  transition: transform 0.25s ease;

  box-shadow: 4px 0 20px rgba(0,0,0,0.5);

  overflow-y: auto;

}

.mobile-nav.open {

  transform: translateX(0);

}

.mobile-nav-header {

  display: flex;

  align-items: center;

  justify-content: space-between;

  padding: 16px 20px;

  border-bottom: 1px solid rgba(255,255,255,0.08);

}

.mobile-nav-logo {

  display: flex;

  align-items: center;

  gap: 8px;

}

.mobile-close {

  width: 32px;

  height: 32px;

  border-radius: 8px;

  border: none;

  background: rgba(255,255,255,0.1);

  color: #fff;

  cursor: pointer;

  display: flex;

  align-items: center;

  justify-content: center;

}

.mobile-nav-items {

  padding: 8px;

}

.mobile-nav-item {

  display: flex;

  align-items: center;

  gap: 10px;

  padding: 12px 16px;

  border-radius: 8px;

  font-size: 14px;

  font-weight: 500;

  color: rgba(255,255,255,0.65);

  cursor: pointer;

  text-decoration: none;

  margin-bottom: 2px;

}

.mobile-nav-item:hover {

  background: rgba(255,255,255,0.08);

}

.mobile-nav-item.active {

  background: rgba(99,102,241,0.15);

  color: #818cf8;

  font-weight: 600;

}



/* ===== Page Transition ===== */

.slide-fade-enter-active {

  transition: all 0.2s ease;

}

.slide-fade-leave-active {

  transition: all 0.15s ease;

}

.slide-fade-enter-from {

  opacity: 0;

  transform: translateY(8px);

}

.slide-fade-leave-to {

  opacity: 0;

}



/* ===== Responsive ===== */

@media (max-width: 900px) {

  .nav-center {

    display: none;

  }

  .nav-inner {

    padding: 0 16px;

  }

  .main-content {

    padding-top: 0;

  }

  .mobile-menu-btn {

    display: flex;

  }

}

</style>


<!-- Global dark theme overrides for Element Plus components -->
<style>
/* Cards */
.main-content .el-card {
  background: rgba(0,0,0,0.5) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 10px !important;
  --el-card-bg-color: rgba(0,0,0,0.5) !important;
}
.main-content .el-card__header {
  border-bottom: 1px solid rgba(255,255,255,0.06) !important;
  background: rgba(255,255,255,0.05) !important;
  border-radius: 10px 10px 0 0 !important;
  padding: 16px 20px;
}
.main-content .el-card__header span,
.main-content .el-card__header div {
  color: #f1f5f9;
}

/* Tables */
.main-content .el-table {
  background: transparent !important;
  --el-table-bg-color: transparent !important;
  --el-table-tr-bg-color: transparent !important;
  --el-table-header-bg-color: rgba(255,255,255,0.03) !important;
  --el-table-row-hover-bg-color: rgba(255,255,255,0.06) !important;
  --el-table-border-color: rgba(255,255,255,0.06) !important;
  --el-table-header-text-color: rgba(255,255,255,0.5) !important;
  --el-table-text-color: rgba(255,255,255,0.8) !important;
  color: rgba(255,255,255,0.8);
}
.main-content .el-table th.el-table__cell {
  background: rgba(255,255,255,0.03) !important;
  border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}
.main-content .el-table td.el-table__cell {
  border-bottom: 1px solid rgba(255,255,255,0.04) !important;
}
.main-content .el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell {
  background: rgba(255,255,255,0.03) !important;
}
.main-content .el-table--enable-row-hover .el-table__body tr:hover > td {
  background: rgba(255,255,255,0.05) !important;
}

/* Global overrides */
body .el-card {
  background: rgba(0,0,0,0.4) !important;
  border-color: rgba(255,255,255,0.08) !important;
}
body .el-table {
  background: transparent !important;
  color: rgba(255,255,255,0.7) !important;
}
body .el-table th.el-table__cell {
  background: rgba(0,0,0,0.5) !important;
  color: rgba(255,255,255,0.6) !important;
}
body .el-table td.el-table__cell {
  background: transparent !important;
  color: rgba(255,255,255,0.6) !important;
}
body .el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell {
  background: rgba(255,255,255,0.03) !important;
}
body .el-table--enable-row-hover .el-table__body tr:hover > td {
  background: rgba(255,255,255,0.05) !important;
}
body .el-input__wrapper {
  background: rgba(255,255,255,0.06) !important;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.1) inset !important;
}
body .el-input__inner {
  color: rgba(255,255,255,0.7) !important;
}
body .el-button--default {
  --el-button-bg-color: rgba(255,255,255,0.05) !important;
  --el-button-border-color: rgba(255,255,255,0.08) !important;
  --el-button-text-color: rgba(255,255,255,0.7) !important;
  --el-button-hover-bg-color: rgba(255,255,255,0.08) !important;
  --el-button-hover-border-color: rgba(255,255,255,0.15) !important;
  --el-button-hover-text-color: rgba(255,255,255,0.7) !important;
}
body .el-pagination button,
body .el-pager li {
  background: transparent !important;
  color: rgba(255,255,255,0.45) !important;
}
body .el-pager li:hover {
  color: #818cf8 !important;
  background: rgba(99,102,241,0.12) !important;
}
body .el-pager li.is-active {
  color: #818cf8 !important;
  background: rgba(99,102,241,0.18) !important;
}
body .el-pagination__total,
body .el-pagination__jump {
  color: rgba(255,255,255,0.35) !important;
}

/* Dropdowns */
body div.el-select-dropdown,
body div.el-popper,
.el-select-dropdown,
.el-popper {
  background: #000 !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
}
.el-select-dropdown__item {
  color: rgba(255,255,255,0.6) !important;
  background: transparent !important;
}
.el-select-dropdown__item.hover,
.el-select-dropdown__item:hover {
  background: rgba(99,102,241,0.12) !important;
  color: #f1f5f9 !important;
}
.el-select-dropdown__item.selected {
  color: #818cf8 !important;
  background: rgba(99,102,241,0.18) !important;
}

/* Dialog */
.el-dialog {
  background: #1a1a2e !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 12px !important;
}
.el-dialog__title {
  color: rgba(255,255,255,0.85) !important;
}
.el-dialog__header {
  border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}

/* Message / Notification */
.el-message {
  background: rgba(0,0,0,0.9) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  box-shadow: 0 8px 30px rgba(0,0,0,0.4) !important;
  color: rgba(255,255,255,0.7) !important;
}
.el-message .el-message__content {
  color: rgba(255,255,255,0.7) !important;
}
.el-notification {
  background: rgba(0,0,0,0.95) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  box-shadow: 0 8px 30px rgba(0,0,0,0.4) !important;
}

/* Date picker */
.el-date-table td {
  color: rgba(255,255,255,0.5) !important;
}
.el-date-table td.today {
  color: #818cf8 !important;
  font-weight: 600 !important;
}
.el-date-table td:hover {
  background: rgba(255,255,255,0.06) !important;
}
.el-date-table td.current:not(.disabled) {
  background: rgba(99,102,241,0.15) !important;
  color: #818cf8 !important;
}
.el-date-picker__header-label {
  color: rgba(255,255,255,0.7) !important;
}
.el-time-panel {
  background: #000 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
}

/* Tooltip */
.el-tooltip__popper {
  background: rgba(0,0,0,0.9) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  color: rgba(255,255,255,0.7) !important;
}

/* Tags, Tabs, Radio, Textarea, Upload */
/* Tabs - Transparent background */
.el-tabs {
  background: transparent !important;
}
.el-tabs__header {
  background: rgba(255,255,255,0.05) !important;
  border-bottom: 1px solid rgba(255,255,255,0.08) !important;
  padding: 8px 16px !important;
  margin-bottom: 16px !important;
}
.el-tabs__nav-wrap {
  background: transparent !important;
}
.el-tabs__nav-scroll {
  background: transparent !important;
}
.el-tabs__nav {
  background: transparent !important;
}
.el-tabs__item {
  color: rgba(255,255,255,0.7) !important;
  background: transparent !important;
  padding: 8px 16px !important;
  margin-right: 8px !important;
  border-radius: 6px !important;
  transition: all 0.2s ease !important;
}
.el-tabs__item.is-active {
  color: #818cf8 !important;
  background: rgba(255,255,255,0.08) !important;
  border: 1px solid rgba(99,102,241,0.3) !important;
}
.el-tabs__item:hover {
  color: rgba(255,255,255,0.9) !important;
  background: rgba(255,255,255,0.06) !important;
}
.el-tabs__content {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 8px !important;
  padding: 16px !important;
}
.el-tab-pane {
  background: transparent !important;
}
.el-radio {
  border: 1px solid rgba(255,255,255,0.08) !important;
  background: transparent !important;
}
.el-radio.is-checked {
  border-color: #6366f1 !important;
}
.el-radio__label {
  color: rgba(255,255,255,0.7) !important;
}
.el-textarea__inner {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  box-shadow: none !important;
  color: rgba(255,255,255,0.7) !important;
}
.el-textarea__inner::placeholder {
  color: rgba(255,255,255,0.3) !important;
}
.el-upload-dragger {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
}
.el-upload__text {
  color: rgba(255,255,255,0.7) !important;
}
.el-upload__text em {
  color: #818cf8 !important;
}

/* Loading */
.el-loading-mask {
  background: rgba(0,0,0,0.6) !important;
}
.el-loading-spinner .circular {
  color: #818cf8 !important;
}

/* Empty */
.el-empty {
  --el-empty-fill-color-1: rgba(255,255,255,0.1) !important;
  --el-empty-fill-color-2: rgba(255,255,255,0.15) !important;
  --el-empty-fill-color-3: rgba(255,255,255,0.08) !important;
  --el-empty-fill-color-4: rgba(255,255,255,0.12) !important;
  --el-empty-fill-color-5: rgba(255,255,255,0.1) !important;
  --el-empty-fill-color-6: rgba(255,255,255,0.15) !important;
  --el-empty-fill-color-7: rgba(255,255,255,0.12) !important;
  --el-empty-fill-color-8: rgba(255,255,255,0.1) !important;
  --el-empty-fill-color-9: rgba(255,255,255,0.15) !important;
}
.el-empty__description p {
  color: rgba(255,255,255,0.5) !important;
}

/* Tag - Warning (black text) */
.el-tag.el-tag--warning {
  color: #000000 !important;
}
.el-tag.el-tag--warning .el-tag__content {
  color: #000000 !important;
}

/* Tag - Success (transparent background) */
.el-tag.el-tag--success {
  background: rgba(255,255,255,0.05) !important;
  border-color: rgba(255,255,255,0.08) !important;
}
.el-tag.el-tag--success .el-tag__content {
  color: rgba(255,255,255,0.7) !important;
}

/* Descriptions - transparent background */
.el-descriptions {
  background: transparent !important;
}
.el-descriptions__body {
  background: transparent !important;
}
.el-descriptions__cell {
  background: rgba(255,255,255,0.05) !important;
}
.el-descriptions__label.is-bordered-label {
  background: rgba(255,255,255,0.05) !important;
  color: #ffffff !important;
}
.el-descriptions__content.is-bordered-content {
  background: rgba(255,255,255,0.05) !important;
  color: #ffffff !important;
}
/* Descriptions - non-bordered text color */
.el-descriptions__label {
  color: #ffffff !important;
}
.el-descriptions__content {
  color: #ffffff !important;
}
.el-page-header__content {
  color: #ffffff !important;
}
.el-page-header__back {
  color: #ffffff !important;
}
.el-page-header__icon {
  color: #ffffff !important;
}
.el-page-header__title {
  color: #ffffff !important;
}
.preview-content {
  color: #ffffff !important;
}

/* Tag - Info (transparent background) */
.el-tag.el-tag--info {
  background: rgba(255,255,255,0.05) !important;
  border-color: rgba(255,255,255,0.08) !important;
}
.el-tag.el-tag--info .el-tag__content {
  color: rgba(255,255,255,0.7) !important;
}

/* Button - small (transparent background) */
.el-button--small {
  background: rgba(255,255,255,0.05) !important;
  border-color: rgba(255,255,255,0.08) !important;
  color: rgba(255,255,255,0.7) !important;
}
/* Plain el-button (transparent background) */
body .el-button:not(.el-button--primary):not(.el-button--success):not(.el-button--warning):not(.el-button--danger):not(.el-button--info) {
  background: rgba(255,255,255,0.05) !important;
  border-color: rgba(255,255,255,0.08) !important;
  color: rgba(255,255,255,0.7) !important;
}

/* Select wrapper (transparent background) */
.el-select__wrapper {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  box-shadow: none !important;
}
</style>









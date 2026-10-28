<template>
  <el-container class="admin-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo" @click="$router.push('/admin/dashboard')">
        <div class="logo-icon"><CatLogo size="md" color="rgba(255,255,255,0.6)" /></div>
        <transition name="fade">
          <span v-show="!isCollapse" class="logo-text">AniMed 管理端</span>
        </transition>
      </div>
      <el-menu
        :default-active="currentPath"
        :collapse="isCollapse"
        router
        background-color="transparent"
        text-color="rgba(255,255,255,0.65)"
        active-text-color="#fff"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><Monitor /></el-icon>
          <template #title>平台概览</template>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/data-screen">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>数据大屏</template>
        </el-menu-item>
        <el-sub-menu index="lab">
          <template #title>
            <el-icon><Tools /></el-icon>
            <span>实验室管理</span>
          </template>
          <el-menu-item index="/admin/lab-management">
            <el-icon><OfficeBuilding /></el-icon>
            <template #title>实验室列表</template>
          </el-menu-item>
          <el-menu-item index="/admin/lab-equipment">
            <el-icon><Monitor /></el-icon>
            <template #title>设备管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/lab-maintenance">
            <el-icon><Tools /></el-icon>
            <template #title>维护记录</template>
          </el-menu-item>
          <el-menu-item index="/admin/lab-reservations">
            <el-icon><Calendar /></el-icon>
            <template #title>预约审批</template>
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/admin/submissions">
          <el-icon><EditPen /></el-icon>
          <template #title>课题管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/system">
          <el-icon><Setting /></el-icon>
          <template #title>系统管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/logs">
          <el-icon><Document /></el-icon>
          <template #title>日志管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <button class="collapse-btn" @click="isCollapse = !isCollapse">
            <el-icon><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
          </button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="$route.meta.title">{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag type="danger" size="small" class="role-tag">{{ userStore.roleName }}</el-tag>
          <el-dropdown trigger="click">
            <div class="user-info">
              <el-avatar :size="32" :src="userStore.userInfo?.avatar" class="user-avatar">{{ userStore.userName?.charAt(0) }}</el-avatar>
              <span class="user-name">{{ userStore.userName }}</span>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <div class="admin-aurora-bg">
    <div class="admin-aurora-layer admin-aurora-1"></div>
    <div class="admin-aurora-layer admin-aurora-2"></div>
    <div class="admin-aurora-layer admin-aurora-3"></div>
  </div>
  <div class="admin-grid-overlay"></div>
  <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="slide-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import CatLogo from '@/components/inspira/CatLogo.vue'
import { Tools, OfficeBuilding, Calendar, EditPen, DataAnalysis } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isCollapse = ref(false)

const currentPath = computed(() => route.path)

onMounted(() => {
  userStore.initFromStorage()
})

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
.admin-layout { height: 100vh; }
.sidebar {
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  .logo {
    height: 64px; display: flex; align-items: center; justify-content: center;
    cursor: pointer; padding: 0 16px; gap: 10px;
        .logo-icon { width: 32px; height: 32px; flex-shrink: 0; svg { width: 100%; height: 100%; } }
    .logo-text { color: #fff; font-size: 15px; font-weight: 600; white-space: nowrap; letter-spacing: 1px; }
  }
  :deep(.el-menu) {
    border-right: none; padding: 8px;
    .el-menu-item, .el-sub-menu__title {
      border-radius: 8px; margin-bottom: 2px; height: 44px; line-height: 44px;
      &:hover { background: rgba(255,255,255,0.08) !important; }
    }
    .el-menu-item.is-active {
      background: linear-gradient(135deg, rgba(233,69,96,0.3), rgba(233,69,96,0.1)) !important;
      color: #fff !important; font-weight: 500; position: relative;
      &::before {
        content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%);
        width: 3px; height: 20px; background: #e94560; border-radius: 0 3px 3px 0;
      }
    }
  }
}
.header {
  display: flex; align-items: center; justify-content: space-between;
    background: linear-gradient(135deg, #0f0c29 0%, #1d1e3a 30%, #0d7377 70%, #14b8a6 100%);
  padding: 0 24px; height: 56px;
  display: flex; align-items: center; justify-content: space-between;
  .header-left {
    display: flex; align-items: center; gap: 16px;
    .collapse-btn {
      width: 36px; height: 36px; border: none; border-radius: 8px;
      background: rgba(255,255,255,0.08); cursor: pointer; display: flex; align-items: center; justify-content: center;
      transition: all 0.2s;
      &:hover { background: rgba(255,255,255,0.15); }
        .el-icon { font-size: 18px; color: rgba(255,255,255,0.7); }
    }
  }
  .header-right {
    display: flex; align-items: center; gap: 16px;
    .role-tag { border-radius: 12px; }
    .user-info {
      display: flex; align-items: center; gap: 8px; cursor: pointer;
      padding: 4px 8px; border-radius: 8px; transition: background 0.2s;
      background: rgba(255,255,255,0.08); cursor: pointer; display: flex; align-items: center; justify-content: center;
      .user-avatar { background: linear-gradient(135deg, #1a1a2e, #0f3460); font-size: 13px; }
        .user-name { font-size: 14px; color: rgba(255,255,255,0.85); font-weight: 500; }
        .dropdown-arrow { font-size: 12px; color: rgba(255,255,255,0.4); }
    }
  }
}
.main-content {
  background: linear-gradient(135deg, #0f0c29 0%, #1d1e3a 30%, #0d7377 70%, #14b8a6 100%);
  overflow-y: auto; width: 100%; position: relative;
}
.admin-aurora-bg { position: absolute; inset: 0; pointer-events: none; overflow: hidden; z-index: 0; }
.admin-aurora-layer {
  position: absolute; width: 120%; height: 120%; top: -10%; left: -10%;
  border-radius: 50%; filter: blur(80px); opacity: 0.12;
}
.admin-aurora-1 { background: radial-gradient(circle, #409eff, transparent 60%); animation: adminAuroraMove1 18s ease-in-out infinite; }
.admin-aurora-2 { background: radial-gradient(circle, #14b8a6, transparent 60%); animation: adminAuroraMove2 22s ease-in-out infinite; }
.admin-aurora-3 { background: radial-gradient(circle, #6366f1, transparent 60%); animation: adminAuroraMove3 20s ease-in-out infinite; }
.admin-grid-overlay {
  position: absolute; inset: 0; pointer-events: none; z-index: 0;
  background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
}
@keyframes adminAuroraMove1 {
  0%,100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.95); }
}
@keyframes adminAuroraMove2 {
  0%,100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-30px, 20px) scale(1.08); }
  66% { transform: translate(20px, -30px) scale(0.92); }
}
@keyframes adminAuroraMove3 {
  0%,100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(20px, 30px) scale(0.95); }
  66% { transform: translate(-25px, -15px) scale(1.1); }
}
.main-content :deep(.page-container), .main-content :deep(.dashboard) { position: relative; z-index: 1; }
.main-content :deep(.el-card) {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  backdrop-filter: blur(4px);
}
.main-content :deep(.el-card__header) {
  border-bottom: 1px solid rgba(255,255,255,0.06) !important;
  color: rgba(255,255,255,0.9);
}
.main-content :deep(.el-card__body) {
  color: rgba(255,255,255,0.8);
}
.main-content :deep(.el-table) {
  background-color: transparent !important;
  color: rgba(255,255,255,0.85);
}
.main-content :deep(.el-table th) {
  background-color: rgba(255,255,255,0.06) !important;
  color: rgba(255,255,255,0.9);
}
.main-content :deep(.el-table tr) {
  background-color: transparent !important;
}
.main-content :deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.main-content :deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background-color: rgba(255,255,255,0.03) !important;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>












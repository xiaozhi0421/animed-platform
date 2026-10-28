<template>
  <div class="page-container">
    <!-- 系统维护 -->
    <el-card class="page-card" style="margin-bottom:20px">
      <template #header>
        <div class="section-header">
          <el-icon :size="18" color="#e6a23c"><WarningFilled /></el-icon>
          <span>系统维护</span>
        </div>
      </template>
      <el-alert
        title="开启维护模式后，对应端的用户将无法登录系统，并会看到系统维护提示。管理员端不受影响。"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom:16px"
      />
      <el-row :gutter="24">
        <el-col :span="12">
          <div class="maintenance-card" :class="{ disabled: !maintenance.studentDisabled }">
            <div class="maintenance-header">
              <el-icon :size="40" color="#409eff"><User /></el-icon>
              <div class="maintenance-info">
                <span class="maintenance-title">学生端</span>
                <span class="maintenance-desc">禁用后学生无法登录校园端</span>
              </div>
            </div>
            <div class="maintenance-footer">
              <span class="maintenance-status" :class="{ danger: maintenance.studentDisabled }">
                <el-icon size="12"><CircleCheckFilled v-if="!maintenance.studentDisabled" /><WarningFilled v-else /></el-icon>
                {{ maintenance.studentDisabled ? '维护中' : '正常运行' }}
              </span>
              <el-switch
                v-model="maintenance.studentDisabled"
                active-color="#e94560"
                inactive-color="#67c23a"
                @change="updateMaintenance"
              />
            </div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="maintenance-card" :class="{ disabled: !maintenance.teacherDisabled }">
            <div class="maintenance-header">
              <el-icon :size="40" color="#0ea5e9"><UserFilled /></el-icon>
              <div class="maintenance-info">
                <span class="maintenance-title">教师端</span>
                <span class="maintenance-desc">禁用后教师无法登录校园端</span>
              </div>
            </div>
            <div class="maintenance-footer">
              <span class="maintenance-status" :class="{ danger: maintenance.teacherDisabled }">
                <el-icon size="12"><CircleCheckFilled v-if="!maintenance.teacherDisabled" /><WarningFilled v-else /></el-icon>
                {{ maintenance.teacherDisabled ? '维护中' : '正常运行' }}
              </span>
              <el-switch
                v-model="maintenance.teacherDisabled"
                active-color="#e94560"
                inactive-color="#67c23a"
                @change="updateMaintenance"
              />
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { get, put } from '@/utils/request'
import { ElMessage } from 'element-plus'
import { WarningFilled, CircleCheckFilled, User, UserFilled } from '@element-plus/icons-vue'

const maintenance = reactive({
  studentDisabled: false,
  teacherDisabled: false
})

async function fetchMaintenance() {
  try {
    const res: any = await get('/auth/admin/maintenance')
    const d = res?.data || res
    maintenance.studentDisabled = !!d.studentDisabled
    maintenance.teacherDisabled = !!d.teacherDisabled
  } catch {}
}

async function updateMaintenance() {
  try {
    await put('/auth/admin/maintenance', {
      studentDisabled: maintenance.studentDisabled,
      teacherDisabled: maintenance.teacherDisabled
    })
    ElMessage.success('维护状态已更新')
  } catch {
    ElMessage.error('更新失败')
  }
}


onMounted(() => { fetchMaintenance() })
</script>

<style scoped lang="scss">
.page-card { border-radius: 12px; }
.section-header { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 15px; }
.maintenance-card {
  background: rgba(0,0,0,0.04); border-radius: 12px; padding: 20px;
  transition: all 0.3s;
  &.disabled { background: rgba(0,0,0,0.02); }
  .maintenance-header { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
  .maintenance-info { display: flex; flex-direction: column; gap: 4px; }
  .maintenance-title { font-size: 16px; font-weight: 600; color: #1a1a2e; }
  .maintenance-desc { font-size: 12px; color: #94a3b8; }
  .maintenance-footer {
    display: flex; align-items: center; justify-content: space-between;
    padding-top: 12px; border-top: 1px solid rgba(0,0,0,0.06);
  }
  .maintenance-status {
    display: flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 500; color: #67c23a;
    &.danger { color: #e94560; }
  }
}
</style>





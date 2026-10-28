<template>
  <div class="admin-maintenance page-container">
    <el-card>
      <template #header>
        <span><el-icon><Tools /></el-icon> 维修管理</span>
      </template>
      <el-table :data="list" border stripe size="small" v-loading="loading" empty-text="暂无维修记录">
        <el-table-column prop="equipmentName" label="仪器" min-width="140" />
        <el-table-column prop="reporterName" label="报修人" width="100" />
        <el-table-column prop="description" label="故障描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reviewRemark" label="审查备注" width="140" show-overflow-tooltip />
        <el-table-column prop="repairRemark" label="维修备注" width="140" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button
              v-if="row.status==='pending_review'"
              size="small" type="warning"
              @click="handleReview(row.id, 'confirm')">确认维修</el-button>
            <el-button
              v-if="row.status==='pending_review'"
              size="small" type="info"
              @click="handleReview(row.id, 'reject')">驳回</el-button>
            <el-button
              v-if="row.status==='repairing'"
              size="small" type="success"
              @click="handleComplete(row.id)">修复完成</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { labApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Tools } from '@element-plus/icons-vue'

const list = ref<any[]>([])
const loading = ref(false)

function statusType(s: string): string {
  const map: Record<string, string> = {
    pending_review: 'warning',
    repairing: 'danger',
    completed: 'success',
    rejected: 'info'
  }
  return map[s] || 'info'
}

function statusLabel(s: string): string {
  const map: Record<string, string> = {
    pending_review: '待审查',
    repairing: '维修中',
    completed: '已修复',
    rejected: '已驳回'
  }
  return map[s] || s
}

async function loadData() {
  loading.value = true
  try {
    const res: any = await labApi.getMaintenanceList()
    list.value = res?.data || []
  } catch (e: any) {
    console.error('加载维修记录失败:', e)
    ElMessage.error(e?.response?.data?.msg || e?.message || '加载维修记录失败')
  } finally {
    loading.value = false
  }
}

async function handleReview(id: number, action: string) {
  const title = action === 'confirm' ? '确认维修' : '驳回报修'
  try {
    const { value } = await ElMessageBox.prompt(`请输入${title}备注`, title, {
      inputType: 'textarea',
      inputPlaceholder: '备注信息（可选）'
    })
    await labApi.reviewMaintenance(id, action, value || '')
    ElMessage.success('操作成功')
    await loadData()
  } catch {
    // 用户取消弹框或操作失败，静默处理
  }
}

async function handleComplete(id: number) {
  try {
    const { value } = await ElMessageBox.prompt('请输入维修完成备注', '修复完成', {
      inputType: 'textarea',
      inputPlaceholder: '备注信息（可选）'
    })
    await labApi.completeMaintenance(id, value || '')
    ElMessage.success('已标记为修复完成')
    await loadData()
  } catch {
    // 用户取消弹框或操作失败，静默处理
  }
}

onMounted(loadData)
</script>

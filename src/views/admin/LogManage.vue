<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <span><el-icon><Document /></el-icon> 登录日志</span>
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" size="small" style="width: 280px" @change="fetchLogs" />
        </div>
      </template>
      <el-table :data="paginatedLogs" stripe v-loading="loading" empty-text="暂无日志数据" style="width:100%">
        <el-table-column prop="time" label="时间" width="170" />
        <el-table-column prop="user" label="用户" width="120" />
        <el-table-column prop="action" label="操作" min-width="120" />
        <el-table-column prop="system" label="系统" min-width="120" />
        <el-table-column prop="ip" label="IP地址" width="140" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'danger'" size="small">{{ row.status ? '成功' : '失败' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="详情" min-width="200">
          <template #default="{ row }">
            <span style="color:#94a3b8;font-size:13px">{{ row.detail || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:16px">
        <el-pagination v-model:current-page="page" :page-size="30" :total="logs.length" layout="total, prev, pager, next" size="small" background />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'

const dateRange = ref<[Date, Date] | null>(null)
const logs = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 30

const paginatedLogs = computed(() => {
  const start = (page.value - 1) * pageSize
  return logs.value.slice(start, start + pageSize)
})

async function fetchLogs() {
  page.value = 1
  loading.value = true
  try {
    const params: any = {}
    if (dateRange.value) {
      params.startDate = formatDate(dateRange.value[0])
      params.endDate = formatDate(dateRange.value[1])
    }
    const res: any = await adminApi.getLogList(params)
    logs.value = res.data || []
  } catch { logs.value = [] }
  finally { loading.value = false }
}

function formatDate(d: Date) {
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
}

onMounted(fetchLogs)
</script>

<style scoped lang="scss">
.page-card { border-radius: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
</style>

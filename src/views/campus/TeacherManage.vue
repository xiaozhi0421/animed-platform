<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <span><el-icon><Avatar /></el-icon> 教师管理</span>
          <el-input v-model="keyword" placeholder="搜索教师号/姓名" style="width: 240px" prefix-icon="Search" clearable @input="fetchTeachers" />
        </div>
      </template>
      <el-table :data="teachers" stripe v-loading="loading" empty-text="暂无数据">
        <el-table-column prop="account" label="教师号" width="140" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="college" label="学院" />
        <el-table-column prop="department" label="院系" />
        <el-table-column prop="title" label="职称" width="80" />
        <el-table-column prop="createTime" label="注册时间" width="100" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">{{ row.status === 1 ? '正常' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="viewDetail(row)"><el-icon><View /></el-icon> 查看</el-button>
            <el-button size="small" :type="row.status === 1 ? 'warning' : 'success'" link @click="toggleStatus(row)">
              <el-icon><CircleCheck /></el-icon> {{ row.status === 1 ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="detailVisible" title="教师详情" width="500px">
      <template v-if="detailData">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="教师号">{{ detailData.account }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ detailData.name }}</el-descriptions-item>
          <el-descriptions-item label="学院">{{ detailData.collegeName }}</el-descriptions-item>
          <el-descriptions-item label="院系">{{ detailData.department || '-' }}</el-descriptions-item>
          <el-descriptions-item label="职称">{{ detailData.title || '-' }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ detailData.createTime || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="detailData.status === 1 ? 'success' : 'danger'" size="small">{{ detailData.status === 1 ? '正常' : '禁用' }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const keyword = ref('')
const teachers = ref<any[]>([])
const loading = ref(false)
const detailVisible = ref(false)
const detailData = ref<any>(null)

async function fetchTeachers() {
  loading.value = true
  try {
    const res: any = await adminApi.getTeacherList({ keyword: keyword.value || undefined })
    teachers.value = res.data || []
  } catch { teachers.value = [] }
  finally { loading.value = false }
}

async function viewDetail(row: any) {
  try {
    const res: any = await adminApi.getUserDetail(row.id)
    detailData.value = res.data || row
    detailVisible.value = true
  } catch { ElMessage.error('获取详情失败') }
}

async function toggleStatus(row: any) {
  const action = row.status === 1 ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定${action}该教师账号吗？`, '确认操作', { type: 'warning' })
    await adminApi.updateUserStatus(row.id, row.status === 1 ? 0 : 1)
    ElMessage.success(`${action}成功`)
    fetchTeachers()
  } catch { /* cancelled */ }
}

onMounted(fetchTeachers)
</script>

<style scoped lang="scss">
.page-card { border-radius: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>

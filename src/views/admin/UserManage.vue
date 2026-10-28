<template>
  <div class="page-container">
    <el-dialog v-model="detailVisible" title="账号信息" width="500px" :close-on-click-modal="false">
      <template v-if="detailUser">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="ID">{{ detailUser.id }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ detailUser.realName || detailUser.name }}</el-descriptions-item>
          <el-descriptions-item label="账号">{{ detailUser.username || detailUser.account }}</el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag :type="detailUser.role === 'campus_student' ? '' : 'success'" size="small">
              {{ detailUser.role === 'campus_student' ? '学生' : detailUser.role === 'campus_teacher' ? '教师' : detailUser.role }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="detailUser.collegeName || detailUser.college" label="学院">{{ detailUser.collegeName || detailUser.college }}</el-descriptions-item>
          <el-descriptions-item v-if="detailUser.majorName || detailUser.major" label="专业">{{ detailUser.majorName || detailUser.major }}</el-descriptions-item>
          <el-descriptions-item v-if="detailUser.className" label="班级">{{ detailUser.className }}</el-descriptions-item>
          <el-descriptions-item v-if="detailUser.department" label="部门">{{ detailUser.department }}</el-descriptions-item>
          <el-descriptions-item v-if="detailUser.title" label="职称">{{ detailUser.title }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="detailUser.status === 1 ? 'success' : 'danger'" size="small">
              {{ detailUser.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="detailUser.phone" label="手机号">{{ detailUser.phone }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ detailUser.createTime }}</el-descriptions-item>
        </el-descriptions>
      </template>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-card class="page-card">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span><el-icon><User /></el-icon> 用户管理</span>
          <el-button size="small" @click="fetchUsers"><el-icon><Refresh /></el-icon> 刷新</el-button>
        </div>
      </template>
      <div style="display:flex;gap:8px;margin-bottom:16px;">
        <el-select v-model="userType" size="small" style="width:130px;" @change="fetchUsers">
          <el-option label="全部用户" value="" />
          <el-option label="学生" value="campus_student" />
          <el-option label="教师" value="campus_teacher" />
        </el-select>
        <el-input v-model="keyword" placeholder="搜索姓名/账号" style="width: 200px" prefix-icon="Search" clearable @input="fetchUsers" />
      </div>
      <el-table :data="users" stripe v-loading="loading" empty-text="暂无数据">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="realName" label="姓名" min-width="100" />
        <el-table-column prop="username" label="账号" min-width="140" />
        <el-table-column prop="roleLabel" label="角色" width="80">
          <template #default="{ row }">
            <el-tag :type="row.role === 'campus_student' ? '' : 'success'" size="small">{{ row.roleLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="学院/专业" min-width="160">
          <template #default="{ row }">
            <span v-if="row.college">{{ row.college }}</span>
            <span v-if="row.major"> - {{ row.major }}</span>
            <span v-if="row.className"> [{{ row.className }}]</span>
            <span v-if="row.title && !row.college">{{ row.title }}</span>
            <span v-if="row.department && !row.college"> / {{ row.department }}</span>
            <span v-if="!row.college && !row.title && !row.department">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">{{ row.status === 1 ? '正常' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewUserDetail(row.id)">
              <el-icon><View /></el-icon> 查看
            </el-button>
            <el-button
              :type="row.status === 1 ? 'warning' : 'success'"
              link size="small"
              @click="toggleUserStatus(row)">
              <el-icon><CircleCheck /></el-icon> {{ row.status === 1 ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api'
import { User, View, CircleCheck, Refresh } from '@element-plus/icons-vue'

const keyword = ref('')
const userType = ref('')
const users = ref<any[]>([])
const loading = ref(false)
const detailVisible = ref(false)
const detailUser = ref<any>(null)

async function fetchUsers() {
  loading.value = true
  try {
    const params: any = { keyword: keyword.value || undefined }
    const studentRes: any = await adminApi.getStudentList(params)
    const teacherRes: any = await adminApi.getTeacherList(params)
    const students = (studentRes.data || []).map((s: any) => ({ ...s, roleLabel: '学生' }))
    const teachers = (teacherRes.data || []).map((t: any) => ({ ...t, roleLabel: '教师' }))

    if (userType.value === 'campus_student') {
      users.value = students
    } else if (userType.value === 'campus_teacher') {
      users.value = teachers
    } else {
      users.value = [...students, ...teachers]
    }
  } catch {
    users.value = []
  } finally {
    loading.value = false
  }
}

async function viewUserDetail(id: number) {
  try {
    const res: any = await adminApi.getUserDetail(id)
    if (res.code === 200 && res.data) {
      detailUser.value = res.data
    } else {
      const row = users.value.find(u => u.id === id)
      detailUser.value = row ? { ...row } : null
    }
    detailVisible.value = true
  } catch {
    const row = users.value.find(u => u.id === id)
    detailUser.value = row ? { ...row } : null
    detailVisible.value = true
  }
}

async function toggleUserStatus(row: any) {
  const action = row.status === 1 ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${row.realName}" (${row.username}) 吗？`,
      '提示',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  try {
    const newStatus = row.status === 1 ? 0 : 1
    const res: any = await adminApi.updateUserStatus(row.id, newStatus)
    if (res.code === 200) {
      ElMessage.success(`${action}成功`)
      row.status = newStatus
      await fetchUsers()
    } else {
      ElMessage.error(`${action}失败: ${res.msg}`)
    }
  } catch {
    ElMessage.error(`${action}失败: 请求异常`)
  }
}

onMounted(fetchUsers)
</script>

<style scoped lang="scss">
.page-card { border-radius: 12px; }
</style>

<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <span>日志管理</span>
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" size="small" style="width: 260px" />
        </div>
      </template>
      <el-table :data="logs" stripe size="small">
        <el-table-column prop="time" label="时间" width="170" />
        <el-table-column prop="user" label="操作人" width="100" />
        <el-table-column prop="role" label="角色" width="80" />
        <el-table-column prop="action" label="操作内容" />
        <el-table-column prop="ip" label="IP" width="130" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const dateRange = ref([])
const logs = ref([
  { time: '2024-12-01 10:23', user: '张三', role: '学生', action: '上传数据集 animal_data.csv', ip: '192.168.1.100' },
  { time: '2024-12-01 11:00', user: '王建国', role: '教师', action: '审核数据集 #12 通过', ip: '192.168.1.101' },
  { time: '2024-12-01 14:30', user: '管理员', role: '管理员', action: '禁用学生账号 20241001005', ip: '192.168.1.1' },
])
</script>

<style scoped lang="scss">
.page-card { border-radius: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>

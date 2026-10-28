<template>
  <div class="my-violations page-container">
    <el-card><template #header><div class="flex-between"><span><el-icon><Warning /></el-icon> 我的违规记录</span><el-button size="small" @click="$router.push('/campus/lab-equipment')">返回仪器预约</el-button></div></template>
      <el-alert v-if="banInfo.banned" :title="'预约功能已被禁用: ' + banInfo.reason" type="error" show-icon style="margin-bottom:16px" />
      <el-table :data="list" border stripe size="small" v-loading="loading" empty-text="暂无违规记录">
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{row}"><el-tag :type="row.type==='no_show'?'danger':'warning'" size="small">{{ row.type==='no_show'?'未使用':'超时' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="处罚" width="120">
          <template #default="{row}">
            <el-tag v-if="row.penaltyLevel===1" size="small" type="warning">警告</el-tag>
            <el-tag v-else-if="row.penaltyLevel===2" size="small" type="danger">禁用7天</el-tag>
            <el-tag v-else-if="row.penaltyLevel===3" size="small" type="danger">永久封禁</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="记录时间" width="170" />
      </el-table>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { labApi } from '@/api'
import { Warning } from '@element-plus/icons-vue'
const list = ref<any[]>([]); const loading = ref(false); const banInfo = ref<any>({ banned: false })
async function loadData() { loading.value = true; try { const [r1, r2] = await Promise.all([labApi.getMyViolations(), labApi.checkBan()]); list.value = r1.data || []; banInfo.value = r2.data || { banned: false } } catch {} finally { loading.value = false } }
onMounted(loadData)
</script>
<style scoped>.flex-between { display: flex; justify-content: space-between; align-items: center; }</style>

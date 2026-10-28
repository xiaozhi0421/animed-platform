<template>
  <div class="admin-reservations page-container">
    <el-card><template #header><span><el-icon><List /></el-icon> 预约审批管理</span></template>

      <!-- Search for pending -->
      <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap">
        <el-input v-model="pendingSearchEquipment" placeholder="搜索仪器名称..." clearable style="width:160px" size="small" @input="onPendingSearch" />
        <el-input v-model="pendingSearchLab" placeholder="搜索实验室..." clearable style="width:160px" size="small" @input="onPendingSearch" />
        <el-input v-model="pendingSearchPurpose" placeholder="搜索目的..." clearable style="width:160px" size="small" @input="onPendingSearch" />
        <el-input v-model="pendingSearchUser" placeholder="搜索预约人..." clearable style="width:140px" size="small" @input="onPendingSearch" />
      </div>

      <el-table :data="paginatedPendingList" border stripe size="small" v-loading="loading" empty-text="暂无待审批预约">
        <el-table-column prop="equipmentName" label="仪器" min-width="140" />
        <el-table-column prop="labName" label="实验室" width="130" />
        <el-table-column prop="userName" label="预约人" width="100" />
        <el-table-column prop="userRole" label="身份" width="70">
          <template #default="{row}"><el-tag :type="row.userRole==='teacher'?'success':'primary'" size="small">{{ row.userRole==='teacher'?'教师':'学生' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="reserveDate" label="日期" width="110" />
        <el-table-column prop="timeSlot" label="时段" width="110" />
        <el-table-column prop="purpose" label="目的" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button size="small" type="success" @click="approve(row.id)">批准</el-button>
            <el-button size="small" type="danger" @click="showReject(row.id)">拒绝</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination for pending -->
      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination
          v-model:current-page="pendingPage"
          :page-size="pendingPageSize"
          :total="filteredPendingList.length"
          layout="total, prev, pager, next"
          size="small"
          background
        />
      </div>
    </el-card>

    <el-card style="margin-top:16px">
      <template #header><span>全部预约记录</span></template>

      <!-- Search bar for all records -->
      <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap">
        <el-input v-model="searchEquipment" placeholder="搜索仪器名称..." clearable style="width:180px" size="small" @input="onAllSearch" />
        <el-input v-model="searchLab" placeholder="搜索实验室..." clearable style="width:180px" size="small" @input="onAllSearch" />
        <el-input v-model="searchPurpose" placeholder="搜索目的..." clearable style="width:180px" size="small" @input="onAllSearch" />
      </div>

      <el-table :data="paginatedAllList" border stripe size="small" max-height="400" empty-text="暂无记录">
        <el-table-column prop="equipmentName" label="仪器" min-width="130" />
        <el-table-column prop="labName" label="实验室" width="120" />
        <el-table-column prop="userName" label="预约人" width="90" />
        <el-table-column prop="reserveDate" label="日期" width="100" />
        <el-table-column prop="timeSlot" label="时段" width="100" />
        <el-table-column label="状态" width="90">
          <template #default="{row}"><el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="password" label="密码" width="80" align="center">
          <template #default="{row}"><el-tag v-if="row.password" size="small">{{ row.password }}</el-tag><span v-else>-</span></template>
        </el-table-column>
      </el-table>

      <!-- Pagination for all records -->
      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination
          v-model:current-page="allPage"
          :page-size="allPageSize"
          :total="filteredAllList.length"
          layout="total, prev, pager, next"
          size="small"
          background
        />
      </div>
    </el-card>
    <el-dialog v-model="rejectDialog" title="拒绝预约" width="400px">
      <el-input v-model="rejectReason" type="textarea" :rows="4" placeholder="请输入拒绝原因" />
      <template #footer><el-button @click="rejectDialog=false">取消</el-button><el-button type="primary" @click="confirmReject">确认拒绝</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { labApi } from '@/api'
import { ElMessage } from 'element-plus'
import { List } from '@element-plus/icons-vue'

const pendingList = ref<any[]>([])
const allList = ref<any[]>([])
const loading = ref(false)
const rejectDialog = ref(false)
const rejectReason = ref('')
const rejectId = ref(0)

// --- Pending list search & pagination ---
const pendingSearchEquipment = ref('')
const pendingSearchLab = ref('')
const pendingSearchPurpose = ref('')
const pendingSearchUser = ref('')
const pendingPage = ref(1)
const pendingPageSize = 10

const filteredPendingList = computed(() => {
  let result = pendingList.value
  const eq = pendingSearchEquipment.value.trim().toLowerCase()
  const lab = pendingSearchLab.value.trim().toLowerCase()
  const purp = pendingSearchPurpose.value.trim().toLowerCase()
  const user = pendingSearchUser.value.trim().toLowerCase()
  if (eq) result = result.filter(r => (r.equipmentName || '').toLowerCase().includes(eq))
  if (lab) result = result.filter(r => (r.labName || '').toLowerCase().includes(lab))
  if (purp) result = result.filter(r => (r.purpose || '').toLowerCase().includes(purp))
  if (user) result = result.filter(r => (r.userName || '').toLowerCase().includes(user))
  return result
})

const paginatedPendingList = computed(() => {
  const start = (pendingPage.value - 1) * pendingPageSize
  return filteredPendingList.value.slice(start, start + pendingPageSize)
})

function onPendingSearch() { pendingPage.value = 1 }

// --- All records search & pagination ---
const searchEquipment = ref('')
const searchLab = ref('')
const searchPurpose = ref('')
const allPage = ref(1)
const allPageSize = 10

const filteredAllList = computed(() => {
  let result = allList.value
  const eq = searchEquipment.value.trim().toLowerCase()
  const lab = searchLab.value.trim().toLowerCase()
  const purp = searchPurpose.value.trim().toLowerCase()
  if (eq) result = result.filter(r => (r.equipmentName || '').toLowerCase().includes(eq))
  if (lab) result = result.filter(r => (r.labName || '').toLowerCase().includes(lab))
  if (purp) result = result.filter(r => (r.purpose || '').toLowerCase().includes(purp))
  return result
})

const paginatedAllList = computed(() => {
  const start = (allPage.value - 1) * allPageSize
  return filteredAllList.value.slice(start, start + allPageSize)
})

function onAllSearch() { allPage.value = 1 }

function statusType(s: string) { return { pending: 'warning', approved: 'success', active: 'primary', in_use: 'primary', completed: 'info', rejected: 'danger', no_show: 'danger', overtime: 'danger' }[s] || 'info' }
function statusLabel(s: string) { return { pending: '待审批', approved: '已批准', active: '使用中', in_use: '使用中', completed: '已完成', rejected: '已拒绝', no_show: '未使用', overtime: '超时' }[s] || s }

async function loadData() {
  loading.value = true
  try {
    const [r1, r2] = await Promise.all([labApi.getPendingReservations(), labApi.getAllReservations()])
    pendingList.value = r1.data || []
    allList.value = r2.data || []
  } catch {}
  finally { loading.value = false }
}
async function approve(id: number) {
  try { await labApi.approveReservation(id); ElMessage.success('已批准'); await loadData() }
  catch (e: any) { ElMessage.error(e?.response?.data?.msg || '操作失败') }
}
function showReject(id: number) { rejectId.value = id; rejectReason.value = ''; rejectDialog.value = true }
async function confirmReject() {
  if (!rejectReason.value.trim()) { ElMessage.warning('请输入拒绝原因'); return }
  try { await labApi.rejectReservation(rejectId.value, rejectReason.value); ElMessage.success('已拒绝'); rejectDialog.value = false; await loadData() }
  catch (e: any) { ElMessage.error(e?.response?.data?.msg || '操作失败') }
}
onMounted(loadData)
</script>

<template>
  <div class="my-reservations page-container">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span><el-icon><Calendar /></el-icon> 我的预约</span>
          <el-button size="small" @click="$router.push('/campus/lab-equipment')">预约仪器</el-button>
        </div>
      </template>

      <!-- Search bar -->
      <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap">
        <el-input v-model="searchKeyword" placeholder="搜索仪器名称..." clearable style="width:200px" size="small" @input="onSearch" />
        <el-input v-model="searchLab" placeholder="搜索实验室..." clearable style="width:200px" size="small" @input="onSearch" />
        <el-input v-model="searchPurpose" placeholder="搜索目的..." clearable style="width:200px" size="small" @input="onSearch" />
      </div>

      <el-table :data="paginatedList" border stripe size="small" v-loading="loading" empty-text="暂无预约记录">
        <el-table-column prop="equipmentName" label="仪器" min-width="140" />
        <el-table-column prop="labName" label="实验室" width="140" />
        <el-table-column prop="reserveDate" label="日期" width="110" />
        <el-table-column prop="timeSlot" label="时间段" width="120" />
        <el-table-column prop="purpose" label="目的" min-width="120" show-overflow-tooltip />
        <el-table-column label="状态" width="110">
          <template #default="{row}"><el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column label="密码" width="100" align="center">
          <template #default="{row}">
            <el-tag v-if="row.password && (row.status==='approved'||row.status==='active'||row.status==='in_use'||row.status==='in_use')" size="small" type="warning">{{ row.password }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button v-if="row.status==='approved'" size="small" type="success" @click="showUseDialog(row)">开始使用</el-button>
            <el-button v-if="row.status==='active'||row.status==='in_use'" size="small" type="warning" @click="showEndDialog(row)">结束使用</el-button>
            <el-button v-if="row.status==='rejected'" size="small" type="danger" link @click="viewReject(row)">查看原因</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div style="display:flex;justify-content:flex-end;margin-top:16px">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredList.length"
          layout="total, prev, pager, next"
          size="small"
          background
        />
      </div>
    </el-card>
    <el-dialog v-model="useDialog" title="开始使用" width="400px">
      <p>请输入管理员提供的6位密码开始使用仪器：</p>
      <el-input v-model="password" maxlength="6" placeholder="请输入6位密码" style="margin:12px 0" size="large" />
      <template #footer><el-button @click="useDialog=false">取消</el-button><el-button type="primary" @click="confirmStart">确认开始</el-button></template>
    </el-dialog>
    <el-dialog v-model="endDialog" title="结束使用" width="400px">
      <p>请输入密码以结束使用：</p>
      <el-input v-model="password" maxlength="6" placeholder="请输入6位密码" style="margin:12px 0" size="large" />
      <template #footer><el-button @click="endDialog=false">取消</el-button><el-button type="primary" @click="confirmEnd">确认结束</el-button></template>
    </el-dialog>
    <el-dialog v-model="rejectDialog" title="拒绝原因" width="400px">
      <p>{{ rejectReason }}</p>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { labApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Calendar } from '@element-plus/icons-vue'

const list = ref<any[]>([])
const loading = ref(false)
const useDialog = ref(false)
const endDialog = ref(false)
const rejectDialog = ref(false)
const rejectReason = ref('')
const password = ref('')
const currentId = ref(0)

// Search & pagination
const searchKeyword = ref('')
const searchLab = ref('')
const searchPurpose = ref('')
const currentPage = ref(1)
const pageSize = 10

const filteredList = computed(() => {
  let result = list.value
  const kw = searchKeyword.value.trim().toLowerCase()
  const lab = searchLab.value.trim().toLowerCase()
  const purp = searchPurpose.value.trim().toLowerCase()
  if (kw) result = result.filter(r => (r.equipmentName || '').toLowerCase().includes(kw))
  if (lab) result = result.filter(r => (r.labName || '').toLowerCase().includes(lab))
  if (purp) result = result.filter(r => (r.purpose || '').toLowerCase().includes(purp))
  return result
})

const paginatedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredList.value.slice(start, start + pageSize)
})

function onSearch() { currentPage.value = 1 }

function statusType(s: string) { return { pending: 'warning', approved: 'success', active: 'primary', in_use: 'primary', completed: 'info', rejected: 'danger', no_show: 'danger', overtime: 'danger' }[s] || 'info' }
function statusLabel(s: string) { return { pending: '待审批', approved: '已批准', active: '使用中', in_use: '使用中', completed: '已完成', rejected: '已拒绝', no_show: '未使用', overtime: '超时' }[s] || s }

async function loadData() {
  loading.value = true
  try { const r: any = await labApi.getMyReservations(); list.value = r.data || [] }
  catch { list.value = [] }
  finally { loading.value = false }
}
function showUseDialog(row: any) { currentId.value = row.id; password.value = ''; useDialog.value = true }
function showEndDialog(row: any) { currentId.value = row.id; password.value = ''; endDialog.value = true }
function viewReject(row: any) { rejectReason.value = row.rejectReason || '无原因'; rejectDialog.value = true }

async function confirmStart() {
  if (!password.value || password.value.length !== 6) { ElMessage.warning('请输入6位密码'); return }
  try {
    await labApi.startUse(currentId.value, password.value)
    ElMessage.success('使用开始，请在结束后及时结束使用')
    useDialog.value = false; await loadData()
  } catch (e: any) { ElMessage.error(e?.response?.data?.msg || '密码错误') }
}
async function confirmEnd() {
  if (!password.value || password.value.length !== 6) { ElMessage.warning('请输入6位密码'); return }
  try {
    await labApi.endUse(currentId.value, password.value)
    ElMessage.success('使用已结束')
    endDialog.value = false; await loadData()
  } catch (e: any) { ElMessage.error(e?.response?.data?.msg || '密码错误') }
}
onMounted(loadData)
</script>

<style scoped>
.flex-between { display: flex; justify-content: space-between; align-items: center; }
</style>

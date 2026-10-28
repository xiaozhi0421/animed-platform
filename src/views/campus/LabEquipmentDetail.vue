<template>
  <div class="equip-detail page-container">
    <el-button size="small" @click="$router.back()" style="margin-bottom:16px"><el-icon><ArrowLeft /></el-icon> 返回仪器列表</el-button>
    <el-row :gutter="24">
      <el-col :span="10">
        <el-card>
          <div class="detail-img">
            <img v-if="eq.imageUrl" :src="eq.imageUrl" :alt="eq.name" class="detail-img-real" @error="onImgError" />
            <el-icon v-else :size="80" color="#409eff"><Monitor /></el-icon>
          </div>
          <h2 style="margin:8px 0 4px;text-align:center;color:#ffffff">{{ eq.name }}</h2>
          <div style="text-align:center;margin-bottom:6px">
            <el-tag :type="statusType(eq.status)" size="small">{{ statusLabel(eq.status) }}</el-tag>
          </div>
          <div v-if="labName" style="text-align:center;font-size:13px;color:rgba(255,255,255,0.7)">
            <el-icon><OfficeBuilding /></el-icon> {{ labName }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card><template #header><span>详细信息</span></template>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="型号">{{ eq.model || '-' }}</el-descriptions-item>
            <el-descriptions-item label="所在实验室">
              <el-tag size="small" type="info">{{ labName || '未知' }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>
          <el-descriptions :column="2" border size="small" style="margin-top:12px">
            <el-descriptions-item label="生产厂家">{{ eq.manufacturer || '-' }}</el-descriptions-item>
            <el-descriptions-item label="出厂编号">{{ eq.serialNumber || '-' }}</el-descriptions-item>
            <el-descriptions-item label="生产日期">{{ eq.productionDate || '-' }}</el-descriptions-item>
            <el-descriptions-item label="购买日期">{{ eq.purchaseDate || '-' }}</el-descriptions-item>
            <el-descriptions-item label="参考价格">¥{{ eq.price ? eq.price.toLocaleString() : '-' }}</el-descriptions-item>
            <el-descriptions-item label="损坏赔偿价" span="2">¥{{ eq.compensationPrice ? eq.compensationPrice.toLocaleString() : '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        <el-card style="margin-top:12px"><template #header><span>仪器描述</span></template>
          <p style="white-space:pre-wrap;line-height:1.8;font-size:13px;color:#ffffff">{{ eq.specifications || eq.description || '暂无说明' }}</p>
        </el-card>
        <el-card style="margin-top:12px" v-if="eq.usageNotes"><template #header><span>使用注意事项</span></template>
          <p style="white-space:pre-wrap;line-height:1.8;font-size:13px;color:#fbbf24">{{ eq.usageNotes }}</p>
        </el-card>
        <div style="margin-top:16px;display:flex;gap:12px">
          <el-button type="primary" size="large" :disabled="eq.status !== 'normal'" @click="showReserve = true" style="flex:1">立即预约</el-button>
          <el-button size="large" @click="reportDamage" :disabled="eq.status === 'repairing' || eq.status === 'pending_review'">报修</el-button>
        </div>
      </el-col>
    </el-row>
    <el-dialog v-model="showReserve" title="预约仪器" width="580px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="仪器"><el-tag>{{ eq.name }}</el-tag> ({{ eq.model }})</el-form-item>
        <el-form-item label="所在实验室"><el-tag>{{ labName }}</el-tag></el-form-item>
        <el-form-item label="预约日期"><el-date-picker v-model="reserveDate" type="date" placeholder="选择日期" :disabled-date="d => d < new Date()" style="width:100%" /></el-form-item>
        <el-form-item label="选择时段" v-if="reserveDate">
          <div class="slot-grid">
            <div v-for="s in slots" :key="s.timeSlot" :class="['slot-item', { booked: !s.available, selected: selectedSlot.includes(s.timeSlot) }]" @click="selectSlot(s)">
              <span>{{ s.timeSlot }}</span>
              <el-tag v-if="!s.available" size="small" type="danger">已约</el-tag>
              <el-tag v-else size="small" type="success">可约</el-tag>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="使用目的"><el-input v-model="purpose" type="textarea" :rows="3" placeholder="请简要说明使用目的" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReserve = false">取消</el-button>
        <el-button type="primary" :loading="submitting" :disabled="!selectedSlot.length || !reserveDate" @click="submitReserve">提交预约</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { labApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Monitor, OfficeBuilding } from '@element-plus/icons-vue'

const route = useRoute()
const eq = ref<any>({})
const labName = ref('')
const showReserve = ref(false)
const reserveDate = ref<any>(null)
const slots = ref<any[]>([])
const selectedSlot = ref<string[]>([])
const purpose = ref('')
const submitting = ref(false)

const stMap: Record<string, string> = { normal: 'success', in_use: 'warning', pending_review: 'info', repairing: 'danger', damaged: 'danger' }
const slMap: Record<string, string> = { normal: '正常', in_use: '使用中', pending_review: '待审查', repairing: '维修中', damaged: '损坏' }
function statusType(s: string) { return stMap[s] || 'info' }
function statusLabel(s: string) { return slMap[s] || s }
function onImgError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}

async function loadDetail() {
  const id = route.params.id
  if (!id) return
  try {
    const r: any = await labApi.getEquipment(parseInt(id as string))
    eq.value = r.data || {}
    if (eq.value.labId) {
      const r2: any = await labApi.getLab(eq.value.labId)
      labName.value = r2.data?.name || '未知实验室'
    }
  } catch { ElMessage.error('加载仪器信息失败') }
}

function selectSlot(s: any) {
  if (!s.available) return
  const v = selectedSlot.value
  const idx = v.indexOf(s.timeSlot)
  if (idx >= 0) { v.splice(idx, 1) } else { v.push(s.timeSlot) }
}

watch(reserveDate, async (date) => {
  selectedSlot.value = []
  if (!date) return
  try {
    const d = new Date(date).toISOString().split('T')[0]
    const r: any = await labApi.getTimeSlots(eq.value.id, d)
    slots.value = r.data || []
  } catch { slots.value = [] }
})

async function submitReserve() {
  if (!selectedSlot.value.length || !reserveDate.value) return
  const d = new Date(reserveDate.value).toISOString().split('T')[0]
  submitting.value = true
  try {
    const slots2 = selectedSlot.value
    for (const s of slots2) {
      await labApi.submitReservation({
        labId: eq.value.labId, labName: labName.value,
        equipmentId: eq.value.id, equipmentName: eq.value.name,
        reserveDate: d, timeSlot: s,
        purpose: purpose.value, userRole: localStorage.getItem('role') || 'student',
      })
    }
    ElMessage.success(`已提交 ${slots2.length} 个时段预约，等待管理员审批`)
    showReserve.value = false; selectedSlot.value = []; purpose.value = ''; reserveDate.value = null
  } catch (e: any) { ElMessage.error(e?.response?.data?.msg || e?.message || '预约失败') }
  finally { submitting.value = false }
}

async function reportDamage() {
  try {
    const { value } = await ElMessageBox.prompt('请描述仪器故障情况', '报修', {
      inputType: 'textarea', inputPlaceholder: '详细描述故障现象...',
      inputValidator: (v: string) => !!v.trim(), inputErrorMessage: '请填写故障描述'
    })
    await labApi.reportMaintenance({ equipmentId: eq.value.id, equipmentName: eq.value.name, description: value })
    ElMessage.success('报修已提交，等待管理员审查')
    eq.value.status = 'pending_review'
  } catch {}
}

onMounted(loadDetail)
</script>

<style scoped>
.slot-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.slot-item { border: 1px solid #d9d9d9; border-radius: 8px; padding: 12px; text-align: center; cursor: pointer; transition: all 0.2s; color: #ffffff; }
.slot-item.booked { background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.3); cursor: not-allowed; }
.slot-item.selected { border-color: #818cf8; background: rgba(99,102,241,0.15); }
.slot-item:not(.booked):hover { border-color: #818cf8; }
.slot-item span { display: block; margin-bottom: 4px; }
.detail-img { text-align: center; padding: 40px 0; background: rgba(0,0,0,0.3); border-radius: 8px; margin-bottom: 16px; }
.detail-img-real { max-width:100%; max-height:200px; object-fit:contain; }

/* 页面文字颜色统一为白色 */
.equip-detail :deep(.el-card__header) { color: #ffffff !important; }
.equip-detail :deep(.el-descriptions__title) { color: #ffffff !important; }
.equip-detail :deep(.el-descriptions__label) { color: rgba(255,255,255,0.85) !important; }
.equip-detail :deep(.el-descriptions__content) { color: #ffffff !important; }
.equip-detail :deep(.el-card__body) { color: #ffffff; }
.equip-detail :deep(.el-tag) { color: #ffffff; }
</style>

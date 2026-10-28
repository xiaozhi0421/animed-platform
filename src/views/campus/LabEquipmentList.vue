<template>
  <div class="lab-equip-list page-container">
    <el-card>
      <template #header>
        <div class="header-bar">
          <div class="header-left">
            <el-icon :size="20"><Monitor /></el-icon>
            <span class="header-title">实验仪器库</span>
          </div>
          <div class="header-right">
            <el-select v-model="selectedLab" placeholder="全部实验室" clearable style="width:160px;margin-right:10px" @change="searchEquip">
              <el-option v-for="l in labs" :key="l.id" :label="l.name" :value="l.id" />
            </el-select>
            <el-input v-model="keyword" placeholder="搜索仪器名称/型号/厂家" clearable style="width:260px;margin-right:10px" @clear="searchEquip" @keyup.enter="searchEquip" />
            <el-button type="primary" @click="searchEquip">搜索</el-button>
            <el-button @click="$router.push('/campus/my-lab-reservations')">我的预约</el-button>
            <el-button @click="$router.push('/campus/my-lab-violations')">我的违规</el-button>
            <el-button type="warning" @click="showAiPanel = !showAiPanel">
              <el-icon><MagicStick /></el-icon> AI 智能推荐
            </el-button>
          </div>
        </div>
      </template>

      <!-- AI 智能推荐面板 -->
      <transition name="el-zoom-in-top">
        <div v-if="showAiPanel" class="ai-panel">
          <div class="ai-panel-header">
            <el-icon><ChatLineSquare /></el-icon>
            <span>告诉我你想做什么实验，AI 帮你推荐仪器</span>
          </div>
          <div class="ai-panel-input">
            <el-input
              v-model="aiInput"
              type="textarea"
              :rows="2"
              placeholder="例如：我要做Western Blot实验、需要PCR扩增目的基因、想做细胞培养..."
            />
            <el-button type="warning" :loading="aiLoading" @click="handleAiRecommend" style="margin-top:8px">
              <el-icon><Search /></el-icon> 智能推荐
            </el-button>
          </div>

          <!-- 推荐结果 -->
          <div v-if="aiResult" class="ai-result">
            <div class="ai-result-title">
              <el-icon><CircleCheck /></el-icon>
              根据 "<span class="ai-experiment-name">{{ aiResult.experiment }}</span>"，推荐以下仪器：
            </div>
            <div class="ai-equip-grid">
              <div v-for="eq in aiResult.recommendations" :key="eq.equipmentId" class="ai-equip-card"
                :class="{ selected: selectedAiEquip.has(eq.equipmentId) }"
                @click="toggleAiEquip(eq.equipmentId)">
                <div class="ai-equip-check">
                  <el-checkbox :model-value="selectedAiEquip.has(eq.equipmentId)" />
                </div>
                <div class="ai-equip-info">
                  <div class="ai-equip-name">{{ eq.name }}</div>
                  <div class="ai-equip-model">{{ eq.model || "-" }} | {{ eq.manufacturer || "-" }}</div>
                  <div class="ai-equip-lab">{{ eq.labName || "未分配实验室" }}</div>
                  <div class="ai-equip-reason">{{ eq.reason }}</div>
                </div>
                <el-tag :type="eq.status === 'normal' ? 'success' : 'warning'" size="small">
                  {{ eq.status === 'normal' ? '可预约' : eq.status }}
                </el-tag>
              </div>
            </div>

            <!-- 已选仪器的独立时间选择 -->
            <div v-if="selectedAiEquip.size > 0" class="ai-schedule-section">
              <div class="ai-schedule-header">
                <el-icon><Clock /></el-icon>
                <span>为每个仪器单独选择预约时间</span>
                <el-tag type="info" size="small">已选 {{ selectedAiEquip.size }} 台</el-tag>
              </div>

              <div v-for="eqId in selectedAiEquipOrdered" :key="eqId" class="ai-equip-schedule-card">
                <div class="ai-schedule-equip-name">
                  <el-icon><Monitor /></el-icon>
                  <span>{{ getEquipName(eqId) }}</span>
                </div>
                <div class="ai-schedule-controls">
                  <el-date-picker
                    v-model="equipDates[eqId]"
                    type="date"
                    placeholder="选择日期"
                    :disabled-date="d => d < new Date()"
                    style="width:160px"
                    @change="(d) => loadEquipSlots(eqId, d)"
                  />
                  <div v-if="equipSlots[eqId] && equipSlots[eqId].length > 0" class="ai-slot-row">
                    <div
                      v-for="s in equipSlots[eqId]"
                      :key="s.timeSlot"
                      :class='[
                        "ai-slot-pill",
                        { booked: !s.available, selected: equipSelectedSlots[eqId] && equipSelectedSlots[eqId].includes(s.timeSlot) }
                      ]'
                      @click="selectEquipSlot(eqId, s)"
                    >
                      <span>{{ s.timeSlot }}</span>
                      <el-tag v-if="!s.available" size="small" type="danger">满</el-tag>
                      <el-tag v-else-if="equipSelectedSlots[eqId] && equipSelectedSlots[eqId].includes(s.timeSlot)" size="small" type="primary">✓</el-tag>
                      <el-tag v-else size="small" type="success">可约</el-tag>
                    </div>
                  </div>
                  <div v-else-if="equipDates[eqId] && (!equipSlots[eqId] || equipSlots[eqId].length === 0)" class="ai-slot-empty">
                    该日期暂无可用时段
                  </div>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="ai-actions">
                <el-button type="primary" :loading="aiReserving" :disabled="!canReserveAny" @click="quickReserve">
                  <el-icon><Select /></el-icon> 一键提交所有预约 ({{ readyCount }})
                </el-button>
                <el-button @click="clearAllSelections">清除所有选择</el-button>
              </div>
            </div>
          </div>
          <div v-if="aiError" class="ai-error">
            <el-icon><WarningFilled /></el-icon> {{ aiError }}
          </div>
        </div>
      </transition>

      <!-- 仪器列表 -->
      <div v-if="loading" class="loading-center"><el-icon class="is-loading" :size="32"><Loading /></el-icon><p style="margin-top:8px;color:#999">加载中...</p></div>
      <template v-else-if="paginatedList.length === 0">
        <div class="empty-state"><el-icon :size="64" color="#d9d9d9"><FolderOpened /></el-icon><p style="color:#999;margin-top:12px">暂无仪器数据</p></div>
      </template>
      <template v-else>
        <div class="equip-grid">
          <div v-for="eq in paginatedList" :key="eq.id" class="equip-card" @click="$router.push('/campus/equipment/' + eq.id)">
            <div class="equip-img-wrapper">
              <img v-if="eq.imageUrl" :src="eq.imageUrl" :alt="eq.name" class="equip-img" @error="onImgError()" />
              <div v-else class="equip-img-placeholder"><el-icon :size="48" color="#b0c4de"><Monitor /></el-icon></div>
            </div>
            <div class="equip-info">
              <h3 class="equip-name" :title="eq.name">{{ eq.name }}</h3>
              <p class="equip-desc">{{ eq.description || "暂无描述" }}</p>
              <div class="equip-meta">
                <el-tag size="small">{{ eq.labName || "未分配实验室" }}</el-tag>
                <span class="equip-price">{{ eq.model || "" }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="pagination-bar">
          <span class="pagination-info">共 {{ filteredList.length }} 台仪器</span>
          <el-pagination
            v-model:current-page="page"
            :page-size="pageSize"
            :total="filteredList.length"
            layout="prev, pager, next"
            size="small"
          />
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { labApi } from "@/api"
import { ElMessage } from "element-plus"
import { Monitor, MagicStick, Search, ChatLineSquare, CircleCheck, WarningFilled, Loading, FolderOpened, Clock, Select } from "@element-plus/icons-vue"

const labs = ref<any[]>([])
const allEquip = ref<any[]>([])
const selectedLab = ref<number | null>(null)
const keyword = ref("")
const loading = ref(false)
const page = ref(1)
const pageSize = ref(12)

// AI 推荐
const showAiPanel = ref(false)
const aiInput = ref("")
const aiLoading = ref(false)
const aiResult = ref<any>(null)
const aiError = ref("")
// 选中的仪器ID (Set 确保唯一)
const selectedAiEquip = ref<Set<number>>(new Set())
const aiReserving = ref(false)

// 每个仪器的独立预约状态
const equipDates = ref<Record<number, any>>({})
const equipSlots = ref<Record<number, any[]>>({})
const equipSelectedSlots = ref<Record<number, string[]>>({})
const equipSlotsLoading = ref<Record<number, boolean>>({})

// 已选仪器有序列表（按选择顺序）
const selectedAiEquipOrdered = ref<number[]>([])

const filteredList = computed(() => {
  let list = allEquip.value
  if (selectedLab.value) list = list.filter((e: any) => e.labId === selectedLab.value)
  if (keyword.value.trim()) {
    const kw = keyword.value.trim().toLowerCase()
    list = list.filter((e: any) =>
      (e.name && e.name.toLowerCase().includes(kw)) ||
      (e.model && e.model.toLowerCase().includes(kw)) ||
      (e.manufacturer && e.manufacturer.toLowerCase().includes(kw))
    )
  }
  return list
})

const paginatedList = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredList.value.slice(start, start + pageSize.value)
})

// 有多少个仪器已经选好了时间
const readyCount = computed(() => {
  let count = 0
  for (const eqId of selectedAiEquipOrdered.value) {
    const slots = equipSelectedSlots.value[eqId]
    if (equipDates.value[eqId] && slots && slots.length > 0) count++
  }
  return count
})

const canReserveAny = computed(() => readyCount.value > 0)

function getEquipName(eqId: number): string {
  if (!aiResult.value?.recommendations) return ""
  const eq = aiResult.value.recommendations.find((r: any) => r.equipmentId === eqId)
  return eq ? eq.name : ""
}

async function loadData() {
  loading.value = true
  try {
    const [labRes, eqRes] = await Promise.all([
      labApi.getLabList(),
      labApi.getEquipmentList()
    ])
    labs.value = labRes.data || []
    // 补充 labName
    const labMap: Record<number, string> = {}
    for (const lab of labs.value) {
      labMap[lab.id] = lab.name
    }
    allEquip.value = (eqRes.data || []).map((eq: any) => ({
      ...eq,
      labName: eq.labName || labMap[eq.labId] || "未分配实验室"
    }))
  } catch { ElMessage.error("加载数据失败") }
  finally { loading.value = false }
}

function searchEquip() { page.value = 1 }

function onImgError() {}

// === AI 智能推荐 ===
async function handleAiRecommend() {
  if (!aiInput.value.trim()) { aiError.value = "请描述你要做的实验"; return }
  aiLoading.value = true; aiError.value = ""
  aiResult.value = null
  // 清空所有选择状态
  selectedAiEquip.value = new Set()
  selectedAiEquipOrdered.value = []
  equipDates.value = {}
  equipSlots.value = {}
  equipSelectedSlots.value = {}
  try {
    const { analysisApi } = await import("@/api")
    const res: any = await analysisApi.experimentRecommend({ message: aiInput.value })
    if (res && res.code === 200 && res.data) {
      aiResult.value = res.data
      if (!res.data.recommendations || res.data.recommendations.length === 0) {
        aiError.value = "未找到匹配的仪器，请尝试换个描述方式"
      }
    } else {
      aiError.value = (res && res.msg) || "推荐失败，请稍后重试"
    }
  } catch (e: any) {
    aiError.value = e?.response?.data?.msg || e?.message || "请求异常"
  } finally {
    aiLoading.value = false
  }
}

function toggleAiEquip(id: number) {
  const s = selectedAiEquip.value
  if (s.has(id)) {
    s.delete(id)
    selectedAiEquipOrdered.value = selectedAiEquipOrdered.value.filter(i => i !== id)
    // 清除该仪器的时间选择
    delete equipDates.value[id]
    delete equipSlots.value[id]
    delete equipSelectedSlots.value[id]
  } else {
    s.add(id)
    selectedAiEquipOrdered.value.push(id)
    // 初始化该仪器的槽位
    equipDates.value = { ...equipDates.value }
    equipSlots.value = { ...equipSlots.value }
    equipSelectedSlots.value = { ...equipSelectedSlots.value }
  }
  // 触发响应式更新
  selectedAiEquip.value = new Set(s)
}

// 加载某个仪器的可用时段
async function loadEquipSlots(eqId: number, date: any) {
  if (!date) {
    equipSlots.value = { ...equipSlots.value, [eqId]: [] }
    equipSelectedSlots.value = { ...equipSelectedSlots.value, [eqId]: [] }
    return
  }
  equipSlotsLoading.value = { ...equipSlotsLoading.value, [eqId]: true }
  try {
    const d = new Date(date).toISOString().split("T")[0]
    const r: any = await labApi.getTimeSlots(eqId, d)
    equipSlots.value = { ...equipSlots.value, [eqId]: r.data || [] }
    equipSelectedSlots.value = { ...equipSelectedSlots.value, [eqId]: [] }
  } catch {
    equipSlots.value = { ...equipSlots.value, [eqId]: [] }
  } finally {
    equipSlotsLoading.value = { ...equipSlotsLoading.value, [eqId]: false }
  }
}

function selectEquipSlot(eqId: number, s: any) {
  if (!s.available) return
  const current = equipSelectedSlots.value[eqId] || []
  const idx = current.indexOf(s.timeSlot)
  if (idx >= 0) {
    // 取消选择
    current.splice(idx, 1)
  } else {
    // 选择
    current.push(s.timeSlot)
  }
  equipSelectedSlots.value = { ...equipSelectedSlots.value, [eqId]: [...current] }
}

function clearAllSelections() {
  selectedAiEquip.value = new Set()
  selectedAiEquipOrdered.value = []
  equipDates.value = {}
  equipSlots.value = {}
  equipSelectedSlots.value = {}
}

// 一键预约：提交所有已选好时间的仪器
async function quickReserve() {
  const toReserve: { eqId: number; date: string; slots: string[] }[] = []
  for (const eqId of selectedAiEquipOrdered.value) {
    const d = equipDates.value[eqId]
    const slots = equipSelectedSlots.value[eqId] || []
    if (d && slots.length > 0) {
      toReserve.push({
        eqId,
        date: new Date(d).toISOString().split("T")[0],
        slots
      })
    }
  }
  if (toReserve.length === 0) return

  aiReserving.value = true
  try {
    // 建立 equipmentId -> 推荐信息的映射
    const equipMap = new Map<number, any>()
    if (aiResult.value?.recommendations) {
      for (const eq of aiResult.value.recommendations) {
        equipMap.set(eq.equipmentId, eq)
      }
    }

    let successCount = 0
    let totalSlots = 0
    let failCount = 0
    const failDetails: string[] = []

    for (const item of toReserve) {
      const eqInfo = equipMap.get(item.eqId)
      if (!eqInfo) { failCount++; continue }
      totalSlots += item.slots.length
      for (const slot of item.slots) {
        try {
          await labApi.submitReservation({
            labId: eqInfo.labId || 0,
            labName: eqInfo.labName || "",
            equipmentId: item.eqId,
            equipmentName: eqInfo.name || "",
            reserveDate: item.date,
            timeSlot: slot,
            purpose: aiInput.value || "AI智能推荐预约",
            userRole: localStorage.getItem("role") || "student",
          })
          successCount++
        } catch (e: any) {
          failCount++
          failDetails.push(`${eqInfo.name}(${slot}): ${e?.response?.data?.msg || e?.message || "失败"}`)
        }
      }
    }

    if (successCount > 0) {
      const msg = `预约完成！成功提交 ${successCount} 个时段预约，等待管理员审批`
      ElMessage.success(msg)
      // 只清除已成功预约的仪器
      const selectedSet = selectedAiEquip.value
      for (const item of toReserve) {
        selectedSet.delete(item.eqId)
        selectedAiEquipOrdered.value = selectedAiEquipOrdered.value.filter(i => i !== item.eqId)
        delete equipDates.value[item.eqId]
        delete equipSlots.value[item.eqId]
        delete equipSelectedSlots.value[item.eqId]
      }
      selectedAiEquip.value = new Set(selectedSet)
    }
    if (failCount > 0) {
      ElMessage.warning(`${failCount} 台仪器预约失败：${failDetails.join("; ")}`)
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.msg || e?.message || "预约失败")
  } finally {
    aiReserving.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.header-bar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.header-left { display: flex; align-items: center; gap: 8px; }
.header-title { font-size: 16px; font-weight: 600; color: #1a1a2e; }
.header-right { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; }
.equip-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 18px; padding: 8px 0; }
.equip-card { border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; overflow: hidden; cursor: pointer; transition: all 0.3s; background: rgba(0,0,0,0.4); display: flex; flex-direction: column; }
.equip-card:hover { transform: translateY(-4px); box-shadow: 0 8px 28px rgba(0,0,0,0.1); border-color: #409eff; }
.equip-img-wrapper { height: 180px; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; overflow: hidden; }
.equip-img { width: 100%; height: 100%; object-fit: contain; padding: 12px; }
.equip-img-placeholder { display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; }
.equip-info { padding: 14px 16px 16px; flex: 1; display: flex; flex-direction: column; }
.equip-name { margin: 0 0 8px; font-size: 14px; color: #ffffff; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 40px; }
.equip-desc { margin: 0 0 12px; font-size: 12px; color: #999; line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; flex: 1; }
.equip-meta { display: flex; justify-content: space-between; align-items: center; }
.equip-price { font-size: 13px; color: #f87171; font-weight: 600; }
.pagination-bar { display: flex; justify-content: space-between; align-items: center; margin-top: 24px; padding-top: 16px; border-top: 1px solid #f0f0f0; }
.pagination-info { font-size: 13px; color: #888; }
.loading-center { text-align: center; padding: 80px 0; }
.empty-state { text-align: center; padding: 80px 0; }

/* === AI 推荐面板 === */
.ai-panel {
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}
.ai-panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
  color: #f1f5f9;
  margin-bottom: 12px;
}
.ai-panel-input { margin-bottom: 12px; }
.ai-result-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; color: #f1f5f9; margin-bottom: 12px;
  padding: 8px 12px; background: rgba(99,102,241,0.1); border-radius: 8px;
}
.ai-experiment-name { color: #818cf8; font-weight: 600; }
.ai-equip-grid { display: flex; flex-direction: column; gap: 8px; }
.ai-equip-card {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px; background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08); border-radius: 10px;
  cursor: pointer; transition: all 0.2s;
}
.ai-equip-card:hover { background: rgba(99,102,241,0.08); border-color: rgba(99,102,241,0.3); }
.ai-equip-card.selected { background: rgba(99,102,241,0.12); border-color: #818cf8; }
.ai-equip-check { flex-shrink: 0; }
.ai-equip-info { flex: 1; min-width: 0; }
.ai-equip-name { font-size: 14px; font-weight: 600; color: #f1f5f9; margin-bottom: 2px; }
.ai-equip-model { font-size: 12px; color: rgba(255,255,255,0.45); }
.ai-equip-lab { font-size: 12px; color: rgba(255,255,255,0.45); }
.ai-equip-reason { font-size: 12px; color: #818cf8; margin-top: 4px; }

/* === 每个仪器的独立时间选择 === */
.ai-schedule-section {
  margin-top: 16px;
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
}
.ai-schedule-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #f1f5f9;
  margin-bottom: 12px;
}
.ai-equip-schedule-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 12px 14px;
  margin-bottom: 8px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
}
.ai-schedule-equip-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #e2e8f0;
  min-width: 140px;
  flex-shrink: 0;
}
.ai-schedule-controls {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.ai-slot-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.ai-slot-pill {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.12);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 12px;
  color: #f1f5f9;
}
.ai-slot-pill:hover { border-color: #818cf8; background: rgba(99,102,241,0.08); }
.ai-slot-pill.selected { border-color: #818cf8; background: rgba(99,102,241,0.2); }
.ai-slot-pill.booked { opacity: 0.35; cursor: not-allowed; }
.ai-slot-empty {
  font-size: 12px;
  color: rgba(255,255,255,0.4);
  padding: 4px 0;
}
.ai-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  justify-content: center;
}
.ai-error {
  margin-top: 8px; padding: 8px 12px;
  background: rgba(239,68,68,0.1); border-radius: 8px;
  color: #f87171; font-size: 13px;
  display: flex; align-items: center; gap: 6px;
}
</style>

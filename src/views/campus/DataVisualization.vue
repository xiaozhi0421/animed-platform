<template>
  <div class="data-visualization page-container">
    <div class="viz-layout">
      <div class="viz-sidebar">
        <!-- Mode Switch -->
        <el-card>
          <template #header>
            <span style="font-weight:600"><el-icon><DataAnalysis /></el-icon> 图表配置</span>
          </template>
          <el-radio-group v-model="mode" style="width:100%;margin-bottom:12px" @change="onModeChange">
            <el-radio-button value="ai" style="width:50%">AI描述</el-radio-button>
            <el-radio-button value="manual" style="width:50%">手动选择</el-radio-button>
          </el-radio-group>

          <el-form label-position="top">
            <el-form-item label="选择数据集">
              <el-select v-model="datasetId" placeholder="请选择数据集" style="width:100%" @change="onDataSetChange" filterable>
                <el-option v-for="ds in datasets" :key="ds.id" :label="dsLabel(ds)" :value="ds.id" />
              </el-select>
            </el-form-item>
            <div v-if="selectedDataSet" style="margin:-8px 0 12px;font-size:12px;color:rgba(255,255,255,0.5)">
              {{ selectedDataSet.rowCount || "-" }} 行 · {{ columns.length }} 列
            </div>

            <!-- AI Mode -->
            <template v-if="mode === 'ai'">
              <el-form-item label="描述你想看到的图表">
                <el-input
                  v-model="userQuery"
                  type="textarea"
                  :rows="4"
                  placeholder="例如：按品种统计每个物种的数量&#10;分析白细胞和红细胞的关系&#10;看看不同品种的平均体重"
                />
              </el-form-item>
              <el-button type="primary" size="large" style="width:100%" :loading="loading" :disabled="!datasetId || !userQuery.trim()" @click="generateWithAI">
                <el-icon><TrendCharts /></el-icon> AI 智能生成
              </el-button>
            </template>

            <!-- Manual Mode -->
            <template v-if="mode === 'manual'">
              <template v-if="columns.length > 0">
                <el-form-item label="图表类型">
                  <el-radio-group v-model="chartType">
                    <el-radio-button value="bar">柱状图</el-radio-button>
                    <el-radio-button value="line">折线图</el-radio-button>
                    <el-radio-button value="pie">饼图</el-radio-button>
                    <el-radio-button value="scatter">散点图</el-radio-button>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="X轴（分类）">
                  <el-select v-model="manualXColumn" placeholder="请选择X轴" style="width:100%">
                    <el-option v-for="col in columns" :key="col" :label="col" :value="col" />
                  </el-select>
                </el-form-item>
                <el-form-item v-if="chartType !== 'pie'" label="Y轴（数值）">
                  <el-select v-model="manualYColumn" placeholder="请选择Y轴" style="width:100%">
                    <el-option v-for="col in columns" :key="col" :label="col" :value="col" />
                  </el-select>
                </el-form-item>
                <el-form-item v-else label="数值字段">
                  <el-select v-model="manualYColumn" placeholder="请选择数值字段" style="width:100%">
                    <el-option v-for="col in numericColumns" :key="col" :label="col" :value="col" />
                  </el-select>
                </el-form-item>
                <el-form-item label="聚合方式">
                  <el-select v-model="aggregateMode" style="width:100%">
                    <el-option value="count" label="计数" />
                    <el-option value="sum" label="求和" />
                    <el-option value="avg" label="平均值" />
                    <el-option value="max" label="最大值" />
                    <el-option value="min" label="最小值" />
                  </el-select>
                </el-form-item>
              </template>
              <el-button type="primary" size="large" style="width:100%;margin-top:8px" :loading="loading" :disabled="!canGenerateManual" @click="generateManual">
                <el-icon><TrendCharts /></el-icon> 生成图表
              </el-button>
            </template>
          </el-form>
        </el-card>
      </div>

      <div class="viz-main">
        <!-- Empty state -->
        <el-card v-if="!generated && !loading" class="viz-state-card">
          <div class="viz-state">
            <el-icon :size="48" style="color:#475569"><DataBoard /></el-icon>
            <p>选择数据集并配置图表参数</p>
            <p style="font-size:13px;color:rgba(255,255,255,0.35)">使用 AI 描述或手动选择字段</p>
          </div>
        </el-card>

        <!-- Loading -->
        <div v-if="loading" class="viz-loading">
          <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          <p>{{ loadingText }}</p>
        </div>

        <!-- Chart Display -->
        <template v-if="generated && !loading">
          <el-card class="viz-result-card">
            <template #header>
              <div class="flex-between">
                <span><el-icon style="margin-right:6px"><DataBoard /></el-icon>{{ chartTitle || "图表展示" }}</span>
                <span v-if="chartTypeLabel" style="font-size:12px;color:#94a3b8">{{ chartTypeLabel }}</span>
              </div>
            </template>
            <div class="svg-chart-wrapper" ref="chartWrapperRef">
              <template v-if="chartType !== 'pie'">
                <svg :width="svgWidth" :height="svgHeight" class="svg-chart" v-if="svgData.length > 0">
                  <line v-for="(g, gi) in gridLines" :key="'g'+gi"
                    :x1="g.x1" :y1="g.y1" :x2="g.x2" :y2="g.y2"
                    stroke="rgba(255,255,255,0.06)" stroke-width="1" stroke-dasharray="4,4" />
                  <line x1="60" :y1="svgHeight-50" :x2="svgWidth-20" :y2="svgHeight-50" stroke="#475569" stroke-width="1" />
                  <line x1="60" y1="20" x2="60" :y2="svgHeight-50" stroke="#475569" stroke-width="1" />
                  <template v-if="chartType === 'bar'">
                    <rect v-for="(d, di) in svgData" :key="'b'+di"
                      :x="d.x" :y="d.y" :width="d.w" :height="d.h"
                      :fill="d.color || '#818cf8'" rx="3" ry="3" class="chart-bar"
                      @mouseenter="showTooltip($event, d)" @mouseleave="hideTooltip" />
                  </template>
                  <template v-if="chartType === 'line'">
                    <polyline :points="svgData.map(d => `${d.cx},${d.cy}`).join(' ')" fill="none" stroke="#818cf8" stroke-width="2.5" stroke-linejoin="round" />
                    <circle v-for="(d, di) in svgData" :key="'l'+di"
                      :cx="d.cx" :cy="d.cy" r="5" fill="#818cf8" stroke="#1e293b" stroke-width="2"
                      @mouseenter="showTooltip($event, d)" @mouseleave="hideTooltip" />
                  </template>
                  <template v-if="chartType === 'scatter'">
                    <circle v-for="(d, di) in svgData" :key="'s'+di"
                      :cx="d.cx" :cy="d.cy" r="6" fill="#818cf8" fill-opacity="0.7" stroke="#818cf8" stroke-width="1"
                      @mouseenter="showTooltip($event, d)" @mouseleave="hideTooltip" />
                  </template>
                  <text v-for="(d, di) in xLabels" :key="'xl'+di"
                    :x="d.x" :y="d.y" text-anchor="middle" dominant-baseline="hanging"
                    fill="#94a3b8" font-size="11">{{ d.text }}</text>
                  <text v-for="(d, di) in yLabels" :key="'yl'+di"
                    :x="d.x" :y="d.y" text-anchor="end" dominant-baseline="middle"
                    fill="#94a3b8" font-size="11">{{ d.text }}</text>
                </svg>
                <div v-else class="viz-state" style="min-height:200px">
                  <p>没有可渲染的图表数据</p>
                </div>
              </template>
              <template v-if="chartType === 'pie'">
                <div class="pie-chart-area" v-if="chartItems.length > 0">
                  <div class="pie-chart-circle" :style="pieStyle"></div>
                  <div class="pie-legend">
                    <div v-for="(d, di) in chartItems" :key="'lg'+di" class="pie-legend-item">
                      <span class="pie-dot" :style="{background: pieColors[di % pieColors.length]}"></span>
                      {{ d.label }}<span class="pie-val"> ({{ d.value }})</span>
                    </div>
                  </div>
                </div>
                <div v-else class="viz-state" style="min-height:200px">
                  <p>没有可渲染的图表数据</p>
                </div>
              </template>
            </div>

          </el-card>

          <!-- Tooltip -->
          <div v-if="tooltip.visible" class="svg-tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
            <p v-for="(v, k) in tooltip.data" :key="k"><b>{{ k }}:</b> {{ v }}</p>
          </div>

          <!-- AI Analysis -->
          <el-card v-if="analysisText" style="margin-top:12px">
            <template #header>
              <span><el-icon><List /></el-icon> AI 数据分析解读</span>
            </template>
            <div class="analysis-content">{{ analysisText }}</div>
          </el-card>

          <!-- Data Preview -->
          <el-card v-if="chartItems.length > 0" style="margin-top:12px">
            <template #header>
              <span><el-icon><List /></el-icon> 数据预览（{{ chartItems.length }}项）</span>
            </template>
            <el-table :data="chartItems" max-height="200" size="small" border stripe>
              <el-table-column label="分类" min-width="150">
                <template #default="{ row }">{{ row.label }}</template>
              </el-table-column>
              <el-table-column label="数值" min-width="100">
                <template #default="{ row }">{{ row.value }}</template>
              </el-table-column>
            </el-table>
          </el-card>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from "vue"
import { analysisApi, dataApi } from "@/api"
import { ElMessage } from "element-plus"
import { DataAnalysis, DataBoard, TrendCharts, List, Loading } from "@element-plus/icons-vue"

/* --- State --- */
const datasets = ref<any[]>([])
const datasetId = ref<number | null>(null)
const selectedDataSet = ref<any>(null)
const columns = ref<string[]>([])
const numericColumns = ref<string[]>([])
const mode = ref("ai")
const userQuery = ref("")
const loading = ref(false)
const loadingText = ref("正在加载...")
const generated = ref(false)
const chartType = ref("bar")
const chartTitle = ref("")
const analysisText = ref("")
const chartWrapperRef = ref<HTMLDivElement | null>(null)

// Manual mode fields
const manualXColumn = ref("")
const manualYColumn = ref("")
const aggregateMode = ref("count")

// Chart data from AI or manual
const chartItems = ref<{label:string;value:number;color?:string}[]>([])

const svgWidth = 700
const svgHeight = 420
const pieColors = ["#818cf8", "#f472b6", "#34d399", "#fbbf24", "#60a5fa", "#a78bfa", "#fb923c", "#2dd4bf"]

const pieStyle = computed(() => {
  const data = chartItems.value
  if (!data.length) return {}
  const total = data.reduce((s, d) => s + d.value, 0)
  if (!total) return {}
  let start = 0
  const stops = data.map((d, i) => {
    const pct = (d.value / total) * 100
    const color = pieColors[i % pieColors.length]
    const from = start
    const to = start + pct
    start = to
    return color + ' ' + from + '% ' + to + '%'
  })
  return { background: 'conic-gradient(' + stops.join(', ') + ')' }
})

const tooltip = ref({ visible: false, x: 0, y: 0, data: {} as Record<string, any> })

const chartTypeLabel = computed(() => {
  const m: Record<string, string> = { bar: "柱状图", line: "折线图", pie: "饼图", scatter: "散点图" }
  return m[chartType.value] || ""
})

const canGenerateManual = computed(() => {
  return datasetId.value && manualXColumn.value && (chartType.value === "pie" ? manualYColumn.value : true)
})

/* --- SVG Computations --- */
const maxValue = computed(() => Math.max(...chartItems.value.map(d => d.value), 1))

const gridLines = computed(() => {
  const lines = []
  for (let i = 1; i <= 5; i++) {
    const y = svgHeight - 50 - (340 / 5) * i
    lines.push({ x1: 60, y1: y, x2: svgWidth - 20, y2: y })
  }
  return lines
})

const svgData = computed(() => {
  const data = chartItems.value
  if (!data.length) return data
  const w = svgWidth - 80
  const h = svgHeight - 70
  const count = data.length
  if (!count) return data

  if (chartType.value === "bar") {
    const bw = Math.min(50, w / count * 0.6)
    const gap = w / count
    return data.map((d, i) => ({
      ...d,
      x: 60 + gap * i + (gap - bw) / 2,
      y: svgHeight - 50 - (d.value / maxValue.value) * h,
      w: bw,
      h: (d.value / maxValue.value) * h,
      color: d.color || "#818cf8"
    }))
  }

  if (chartType.value === "line" || chartType.value === "scatter") {
    const gap = w / (count - 1 || 1)
    return data.map((d, i) => ({
      ...d,
      cx: 60 + gap * i,
      cy: svgHeight - 50 - (d.value / maxValue.value) * h
    }))
  }


  return data
})

const xLabels = computed(() => {
  if (chartType.value === "pie") return []
  const data = chartItems.value
  const count = data.length
  if (!count) return []
  const w = svgWidth - 80
  const gap = w / count
  return data.map((d, i) => ({
    x: 60 + gap * i + (chartType.value === "bar" ? gap / 2 : 0),
    y: svgHeight - 50 + 14,
    text: d.label.length > 8 ? d.label.substring(0, 8) + ".." : d.label
  }))
})

const yLabels = computed(() => {
  if (chartType.value === "pie") return []
  const labels = []
  for (let i = 0; i <= 5; i++) {
    const val = (maxValue.value / 5) * i
    const y = svgHeight - 50 - (340 / 5) * i
    labels.push({
      x: 55,
      y,
      text: val >= 1000 ? (val / 1000).toFixed(1) + "k" : Math.round(val).toString()
    })
  }
  return labels
})

/* --- Methods --- */
function dsLabel(ds: any) {
  return (ds.name || "") + " (" + (ds.fileFormat || "未知") + " - " + (ds.rowCount || 0) + "行)"
}

async function fetchDatasets() {
  try {
    const res: any = await dataApi.getDatasets({ pageNum: 1, pageSize: 999 })
    if (res.code === 200) datasets.value = res.data?.records || res.data || []
  } catch (e: any) {
    ElMessage.error("获取数据集失败: " + (e.message || ""))
  }
}

function onDataSetChange() {
  selectedDataSet.value = datasets.value.find((d: any) => d.id === datasetId.value) || null
  columns.value = []
  numericColumns.value = []
  manualXColumn.value = ""
  manualYColumn.value = ""
  chartItems.value = []
  generated.value = false
  chartType.value = "bar"
  chartTitle.value = ""
  analysisText.value = ""
  if (datasetId.value) fetchColumns()
}

function onModeChange() {
  // Reset when switching modes
  generated.value = false
  chartItems.value = []
  analysisText.value = ""
}

async function fetchColumns() {
  if (!datasetId.value) return
  try {
    const res: any = await dataApi.getDataRows(datasetId.value, 1, 100)
    const rows = res.data?.records || []
    if (rows.length > 0) {
      const cols = Object.keys(rows[0])
      columns.value = cols
      numericColumns.value = cols.filter((col: string) => {
        const val = rows[0][col]
        return val !== null && val !== undefined && !isNaN(Number(val))
      })
    }
  } catch (e: any) {
    console.error("Failed to fetch columns:", e)
  }
}

function aggregateData(xCol: string, yCol: string, agg: string): {label:string;value:number}[] {
  if (!datasetId.value || !xCol) return []
  // We need raw data - fetch a batch
  dataApi.getDataRows(datasetId.value, 1, 500).then((res: any) => {
    const rows = res.data?.records || []
    if (!rows.length) return
    const groups = new Map<string, number[]>()
    for (const row of rows) {
      const key = String(row[xCol] ?? "未知")
      const val = parseFloat(row[yCol]) || 0
      if (!groups.has(key)) groups.set(key, [])
      groups.get(key)!.push(val)
    }
    const result: {label:string;value:number}[] = []
    for (const [key, vals] of groups) {
      let v = 0
      if (agg === "sum") v = vals.reduce((a, b) => a + b, 0)
      else if (agg === "avg") v = vals.reduce((a, b) => a + b, 0) / vals.length
      else if (agg === "max") v = Math.max(...vals)
      else if (agg === "min") v = Math.min(...vals)
      else v = vals.length
      result.push({ label: key, value: Math.round(v * 100) / 100 })
    }
    chartItems.value = result.sort((a, b) => b.value - a.value)
  }).catch((e: any) => {
    ElMessage.error("数据聚合失败: " + (e.message || ""))
  })
  return []
}

async function generateManual() {
  if (!datasetId.value || !manualXColumn.value) return
  loading.value = true
  generated.value = false
  loadingText.value = "正在聚合数据..."
  analysisText.value = ""
  
  try {
    const xCol = manualXColumn.value
    const yCol = manualYColumn.value || manualXColumn.value
    const agg = aggregateMode.value
    
    const res: any = await dataApi.getDataRows(datasetId.value, 1, 500)
    const rows = res.data?.records || []
    if (!rows.length) {
      ElMessage.warning("该数据集没有数据")
      return
    }
    
    const groups = new Map<string, number[]>()
    for (const row of rows) {
      const key = String(row[xCol] ?? "未知")
      const val = parseFloat(row[yCol]) || 0
      if (!groups.has(key)) groups.set(key, [])
      groups.get(key)!.push(val)
    }
    const result: {label:string;value:number}[] = []
    for (const [key, vals] of groups) {
      let v = 0
      if (agg === "sum") v = vals.reduce((a, b) => a + b, 0)
      else if (agg === "avg") v = vals.reduce((a, b) => a + b, 0) / vals.length
      else if (agg === "max") v = Math.max(...vals)
      else if (agg === "min") v = Math.min(...vals)
      else v = vals.length
      result.push({ label: key, value: Math.round(v * 100) / 100 })
    }
    chartItems.value = result.sort((a, b) => b.value - a.value)
    chartTitle.value = xCol + " - " + yCol + " (" + agg + ")"
    generated.value = true
    
  } catch (e: any) {
    ElMessage.error("生成图表失败: " + (e.message || ""))
  } finally {
    loading.value = false
  }
}

async function generateWithAI() {
  if (!datasetId.value || !userQuery.value.trim()) return
  loading.value = true
  generated.value = false
  loadingText.value = "AI 正在分析数据和生成图表..."

  try {
    const res: any = await dataApi.getDataRows(datasetId.value, 1, 500)
    const rows = res.data?.records || []
    if (!rows.length) {
      ElMessage.warning("该数据集没有数据")
      return
    }

    const cols = Object.keys(rows[0])

    const aiRes: any = await analysisApi.chartGeneration({
      message: JSON.stringify({
        datasetId: datasetId.value,
        datasetName: selectedDataSet.value?.name || "数据集",
        rows,
        columns: cols,
        rowCount: rows.length,
        query: userQuery.value
      })
    })

    if (aiRes.code !== 200) {
      ElMessage.error("AI图表生成失败: " + (aiRes.message || ""))
      return
    }

    const result = aiRes.data
    
    // Apply AI config
    if (result.chartType) chartType.value = result.chartType
    chartTitle.value = result.chartTitle || "数据分析图表"
    analysisText.value = result.analysis || ""
    
    // Use AI-returned chart data if available
    if (result.chartData && result.chartData.length > 0) {
      chartItems.value = result.chartData
    } else {
      // Fallback: use first two columns
      const xCol = cols[0]
      const yCol = cols.length > 1 ? cols[1] : cols[0]
      const groups = new Map<string, number[]>()
      for (const row of rows) {
        const key = String(row[xCol] ?? "未知")
        const val = parseFloat(row[yCol]) || 1
        if (!groups.has(key)) groups.set(key, [])
        groups.get(key)!.push(val)
      }
      const items: {label:string;value:number}[] = []
      for (const [key, vals] of groups) {
        items.push({ label: key, value: Math.round(vals.reduce((a,b) => a+b, 0) * 100) / 100 })
      }
      chartItems.value = items.sort((a,b) => b.value - a.value)
    }

    generated.value = true
    await nextTick()
  } catch (e: any) {
    console.error("AI chart generation error:", e)
    ElMessage.error("图表生成失败: " + (e.message || "未知错误"))
  } finally {
    loading.value = false
  }
}

function showTooltip(event: MouseEvent, data: any) {
  const wrapper = chartWrapperRef.value
  if (!wrapper) return
  const rect = wrapper.getBoundingClientRect()
  const items: Record<string, any> = {}
  if (data.label !== undefined) items["名称"] = data.label
  if (data.value !== undefined) items["值"] = data.value
  tooltip.value = { visible: true, x: event.clientX - rect.left + 12, y: event.clientY - rect.top - 10, data: items }
}

function hideTooltip() {
  tooltip.value.visible = false
}

/* --- Init --- */
fetchDatasets()
</script>

<style scoped>
.viz-layout { display: flex; gap: 20px; align-items: flex-start; }
.viz-sidebar { width: 340px; flex-shrink: 0; }
.viz-main { flex: 1; min-width: 0; width: 100%; }
.viz-main .el-card { width: 100%; }

.viz-state { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 400px; gap: 12px; color: rgba(255,255,255,0.4); font-size: 14px; }
.viz-state-card { min-height: 500px; }
.viz-loading { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 300px; gap: 16px; color: rgba(255,255,255,0.6); font-size: 15px; }

.svg-chart-wrapper { width: 100%; overflow-x: auto; position: relative; }
.svg-chart { display: block; margin: 0 auto; }
.chart-bar { cursor: pointer; transition: opacity 0.2s; }
.chart-bar:hover { opacity: 0.8; }
.chart-pie-slice { cursor: pointer; transition: opacity 0.2s; }
.chart-pie-slice:hover { opacity: 0.8; }

.svg-tooltip { position: absolute; background: rgba(15,23,42,0.95); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 8px 12px; font-size: 13px; pointer-events: none; z-index: 100; white-space: nowrap; }
.svg-tooltip p { margin: 2px 0; color: #e2e8f0; }
.svg-tooltip p b { color: #94a3b8; }
/* 手动选择按钮位置 */
.viz-sidebar :deep(.el-radio-button:nth-child(2) .el-radio-button__inner) {
  left: -76px !important;
}
/* 图表类型折线图按钮位置重置 */
.viz-sidebar :deep(.el-form-item .el-radio-button:nth-child(2) .el-radio-button__inner) {
  left: 0px !important;
}

.viz-result-card { min-height: 500px; }
.pie-chart-area { display: flex; align-items: center; gap: 30px; justify-content: center; min-height: 350px; padding: 20px 0; }
.pie-chart-circle { width: 260px; height: 260px; border-radius: 50%; flex-shrink: 0; border: 2px solid rgba(255,255,255,0.1); }
.pie-legend { display: flex; flex-direction: column; gap: 8px; }
.pie-legend-item { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #cbd5e1; }
.pie-dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
.pie-val { color: #94a3b8; margin-left: 4px; }
.analysis-content { font-size: 14px; line-height: 1.8; color: rgba(255,255,255,0.85); white-space: pre-wrap; }
.flex-between { display: flex; justify-content: space-between; align-items: center; }

@media (max-width: 900px) { .viz-layout { flex-direction: column; } .viz-sidebar { width: 100%; } }
</style>
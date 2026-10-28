<template>
  <div class="data-mining page-container">
    <div class="mining-layout">
      <!-- Left: Configuration Panel -->
      <div class="mining-sidebar">
        <el-card>
          <template #header><span><el-icon><Aim /></el-icon> 挖掘设置</span></template>
          <el-form label-position="top">
            <el-form-item label="数据来源">
              <el-radio-group v-model="sourceMode" class="source-radio-group" @change="onSourceModeChange">
                <el-radio-button value="file">上传文件</el-radio-button>
                <el-radio-button value="dataset">选择数据集</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <!-- File Upload Mode -->
            <template v-if="sourceMode === 'file'">
              <el-form-item label="上传文件">
                <div class="file-upload-area" @drop.prevent="onDrop" @dragover.prevent>
                  <input ref="fileInputRef" type="file" hidden accept=".csv,.xlsx,.xls,.json,.pdf,.txt,.docx,.doc" @change="onFileSelected" />
                  <div v-if="!uploadedFile" class="upload-placeholder" @click="fileInputRef?.click()">
                    <el-icon :size="40"><UploadFilled /></el-icon>
                    <p>点击选择文件，或将文件拖拽到此区域</p>
                    <span class="upload-hint">支持 CSV、Excel、JSON、PDF、TXT、Word 等格式</span>
                  </div>
                  <div v-else class="file-info">
                    <div class="file-name-row">
                      <el-icon><Document /></el-icon>
                      <span class="file-name">{{ uploadedFile.name }}</span>
                      <el-button size="small" text @click="removeFile"><el-icon><Close /></el-icon></el-button>
                    </div>
                    <div v-if="extractedText" class="text-preview">
                      <p class="preview-label">文件内容预览（前500字）</p>
                      <p class="preview-text">{{ extractedText.substring(0, 500) }}{{ extractedText.length > 500 ? '...' : '' }}</p>
                    </div>
                    <div v-if="extracting" class="extracting-hint">
                      <el-icon class="is-loading"><Loading /></el-icon> 正在提取文本...
                    </div>
                    <div v-if="extractError" class="extract-error">{{ extractError }}</div>
                  </div>
                </div>
              </el-form-item>
            </template>

            <!-- Dataset Mode -->
            <template v-if="sourceMode === 'dataset'">
              <el-form-item label="选择数据集">
                <el-select v-model="datasetId" placeholder="请选择数据集" style="width:100%" @change="onDataSetChange">
                  <el-option v-for="ds in datasets" :key="ds.id" :label="dsLabel(ds)" :value="ds.id" />
                </el-select>
                <div v-if="selectedDataSet" class="ds-info" style="margin-top:8px">
                  <p><b>名称：</b>{{ selectedDataSet.name }}</p>
                  <p><b>行数：</b>{{ selectedDataSet.rowCount || '-' }}</p>
                  <p><b>格式：</b>{{ selectedDataSet.fileFormat || '-' }}</p>
                </div>
              </el-form-item>
            </template>

            <el-form-item label="挖掘需求描述">
              <el-input v-model="userQuery" type="textarea" :rows="5" placeholder="描述你想要挖掘的内容，例如：&#10;1. 分析这批数据中哪些数值异常#10;2. 预测下一批数据的变化趋势&#10;3. 找出数据中隐藏的关联规律" />
            </el-form-item>
            <el-button type="primary" size="large" style="width:100%" :loading="miningLoading" :disabled="!canMine" @click="startMining">
              <el-icon><Aim /></el-icon> 开始数据挖掘
            </el-button>
          </el-form>
        </el-card>

        <el-card style="margin-top:12px">
          <template #header><span>💡 挖掘说明</span></template>
          <ul style="margin:0;padding-left:16px;font-size:13px;line-height:1.8">
            <li>可选择已有数据集，或直接上传文件</li>
            <li>描述你的挖掘需求（越具体越好）</li>
            <li>AI 将自动提取内容并进行预测、异常检测和洞察分析</li>
          </ul>
        </el-card>
      </div>

      <!-- Right: Results Panel -->
      <div class="mining-results">
        <el-card>
          <template #header>
            <div class="flex-between">
              <span><el-icon><TrendCharts /></el-icon> 挖掘结果</span>
              <span v-if="result" style="font-size:12px;color:#94a3b8">{{ result.fileInfo || '' }}</span>
            </div>
          </template>

          <div v-if="!result && !miningLoading" class="empty-state">
            <el-icon :size="48" style="color:#475569"><Aim /></el-icon>
            <p>选择数据来源并描述需求，点击「开始数据挖掘。</p>
          </div>

          <div v-if="miningLoading" class="loading-state">
            <el-icon class="is-loading" :size="32"><Loading /></el-icon>
            <p>AI 正在分析数据，请稍候..</p>
          </div>

          <template v-if="result && !miningLoading">
            <el-alert v-if="result.error" :title="result.error" type="error" show-icon style="margin-bottom:16px" />

            <div v-if="result.predictions && result.predictions.length > 0" class="result-section">
              <div class="section-header">
                <el-icon style="color:#10b981"><DataBoard /></el-icon>
                <span class="section-title">预测分析</span>
                <el-tag size="small" type="success">{{ result.predictions.length }} 项</el-tag>
              </div>
              <div class="prediction-split-layout">
                <div class="prediction-text-col">
                  <div v-for="(p, idx) in result.predictions" :key="'pred-'+idx" class="result-card prediction-card">
                    <div class="card-header">
                      <span class="card-field">{{ p.field }}</span>
                      <el-tag :type="confidenceType(p.confidence)" size="small">{{ p.confidence }}</el-tag>
                    </div>
                    <div class="card-body">
                      <p><b>结论：</b>{{ p.conclusion }}</p>
                      <p v-if="p.detail" style="color:#94a3b8;font-size:13px;margin-top:4px">{{ p.detail }}</p>
                    </div>
                  </div>
                </div>
                <div class="prediction-chart-col">
                  <div class="prediction-chart-box">
                    <div class="chart-title">预测置信度散点图</div>
                    <svg class="prediction-scatter" :viewBox="'0 0 ' + scatterWidth + ' ' + scatterHeight">
                      <!-- Y-axis line -->
                      <line :x1="scatterPad" :y1="scatterPad" :x2="scatterPad" :y2="scatterH" stroke="#475569" stroke-width="1" />
                      <!-- X-axis line -->
                      <line :x1="scatterPad" :y1="scatterH" :x2="scatterW" :y2="scatterH" stroke="#475569" stroke-width="1" />
                      <!-- Y-axis labels -->
                      <text :x="scatterPad - 10" :y="scatterPad + 5" text-anchor="end" fill="#94a3b8" font-size="11">高</text>
                      <text :x="scatterPad - 10" :y="scatterH" text-anchor="end" fill="#94a3b8" font-size="11" dominant-baseline="middle">中</text>
                      <text :x="scatterPad - 10" :y="scatterH - scatterStep + 5" text-anchor="end" fill="#94a3b8" font-size="11">低</text>
                      <!-- Y-axis grid lines -->
                      <line :x1="scatterPad" :y1="scatterPad" :x2="scatterW" :y2="scatterPad" stroke="#334155" stroke-width="0.5" stroke-dasharray="3,3" />
                      <line :x1="scatterPad" :y1="scatterH" :x2="scatterW" :y2="scatterH" stroke="#334155" stroke-width="0.5" stroke-dasharray="3,3" />
                      <line :x1="scatterPad" :y1="scatterH - scatterStep" :x2="scatterW" :y2="scatterH - scatterStep" stroke="#334155" stroke-width="0.5" stroke-dasharray="3,3" />
                      <!-- Field labels above clusters -->
                      <text v-for="(p, idx) in result.predictions" :key="'xl-'+idx"
                        :x="scatterCenterX(idx)" :y="scatterH + 20"
                        text-anchor="middle" fill="#cbd5e1" font-size="10">{{ p.field }}</text>
                      <!-- Scatter clusters: each prediction forms a cluster around its center -->
                      <template v-for="(p, pi) in result.predictions" :key="'dots-'+pi">
                        <circle v-for="di in scatterDotIdx(scatterDotsPerPred)" :key="'d'+pi+'-'+di"
                          :cx="scatterClusterX(pi, di)" :cy="scatterClusterY(p.confidence, pi, di)"
                          :r="scatterDotR(p.confidence)"
                          :fill="confidenceColor(p.confidence)" opacity="0.7" />
                      </template>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
<div v-if="result.anomalies && result.anomalies.length > 0" class="result-section">
              <div class="section-header">
                <el-icon style="color:#ef4444"><WarningFilled /></el-icon>
                <span class="section-title">异常发现</span>
                <el-tag size="small" type="danger">{{ result.anomalies.length }} 来</el-tag>
              </div>
              <div v-for="(a, idx) in result.anomalies" :key="'anom-'+idx" class="result-card anomaly-card">
                <div class="card-header">
                  <span class="card-field">{{ a.field }}</span>
                  <el-tag :type="severityType(a.severity)" size="small">{{ a.severity }}</el-tag>
                </div>
                <div class="card-body">
                  <p><b>描述）</b>{{ a.description }}</p>
                  <p v-if="a.suggestion" style="color:#94a3b8;font-size:13px;margin-top:4px"><b>建议）</b>{{ a.suggestion }}</p>
                </div>
              </div>
            </div>

            <div v-if="result.insights && result.insights.length > 0" class="result-section">
              <div class="section-header">
                <el-icon style="color:#8b5cf6"><Lightning /></el-icon>
                <span class="section-title">洞察分析</span>
                <el-tag size="small" type="primary">{{ result.insights.length }}来</el-tag>
              </div>
              <div v-for="(i, idx) in result.insights" :key="'ins-'+idx" class="result-card insight-card">
                <div class="card-header">
                  <el-tag :type="insightType(i.type)" size="small">{{ i.type }}</el-tag>
                </div>
                <div class="card-body">
                  <p>{{ i.content }}</p>
                  <p v-if="i.impact" style="color:#94a3b8;font-size:13px;margin-top:4px"><b>影响）</b>{{ i.impact }}</p>
                </div>
              </div>
            </div>
          </template>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { analysisApi, dataApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Aim, TrendCharts, DataBoard, WarningFilled, Lightning, UploadFilled, Document, Close, Loading } from '@element-plus/icons-vue'

const sourceMode = ref('file')

const fileInputRef = ref<HTMLInputElement>()
const uploadedFile = ref<File | null>(null)
const extractedText = ref('')
const extracting = ref(false)
const extractError = ref('')

const datasets = ref<any[]>([])
const datasetId = ref<number | null>(null)
const selectedDataSet = ref<any>(null)

const userQuery = ref('')
const miningLoading = ref(false)
const result = ref<any>(null)

const canMine = computed(() => {
  if (sourceMode.value === 'file') {
    return uploadedFile.value && extractedText.value && userQuery.value.trim()
  }
  return datasetId.value && userQuery.value.trim()
})

function dsLabel(ds: any) {
  return (ds.name || '') + ' (' + (ds.fileFormat || '未知格式') + ' - ' + (ds.rowCount || 0) + '行'
}

function onSourceModeChange() {
  result.value = null
}

function onDataSetChange() {
  selectedDataSet.value = datasets.value.find((d: any) => d.id === datasetId.value) || null
  result.value = null
}

function onDrop(e: DragEvent) {
  const file = e.dataTransfer?.files?.[0]
  if (file) handleFile(file)
}

function onFileSelected(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) handleFile(file)
}

function removeFile() {
  uploadedFile.value = null
  extractedText.value = ''
  extractError.value = ''
  result.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

  function confidenceType(c: string) {
    if (!c) return 'info'
    if (c.includes('高')) return 'success'
    if (c.includes('中')) return 'warning'
    if (c.includes('不') || c.includes('低')) return 'danger'
    return 'info'
  }
  function confidenceWidth(c: string) {
    if (!c) return 50
    if (c.includes('高')) return 90
    if (c.includes('中')) return 60
    if (c.includes('低') || c.includes('不')) return 30
    return 50
  }
  function confidenceColor(c: string) {
    if (!c) return '#94a3b8'
    if (c.includes('高')) return '#10b981'
    if (c.includes('中')) return '#f59e0b'
    if (c.includes('低') || c.includes('不')) return '#ef4444'
    return '#94a3b8'
  }
function severityType(s: string) {
  if (!s) return 'info'
  if (s.includes('严重')) return 'danger'
  if (s.includes('中等')) return 'warning'
  return 'info'
}
  const scatterPad = 55
  const scatterStep = 60
  const scatterW = 560
  const scatterH = 320
  const scatterWidth = 640
  const scatterHeight = 360
  
  const scatterDotsPerPred = 35
  const scatterCenterJitter = 55  // max jitter from center

  // Pseudo-random number generator (seed-based, deterministic)
  function scatterRng(seed: number): number {
    const v = (seed * 9301 + 49297) % 233280
    return v / 233280
  }

  // Center X for a given prediction index
  function scatterCenterX(idx: number) {
    const count = result.value?.predictions?.length || 1
    const spacing = (scatterW - scatterPad * 2) / Math.max(count - 1, 1)
    return scatterPad + spacing * idx
  }

  // Center Y for a given confidence level
  function scatterCenterY(confidence: string) {
    if (!confidence) return scatterH - scatterStep / 2
    if (confidence.includes('高')) return scatterPad + 25
    if (confidence.includes('中')) return scatterH - scatterStep / 2
    if (confidence.includes('低') || confidence.includes('不')) return scatterH - scatterStep + 25
    return scatterH - scatterStep / 2
  }

  // Random offset in a disc shape (not uniform square)
  function scatterOffset(seed: number): { dx: number; dy: number } {
    const angle = scatterRng(seed) * 2 * Math.PI
    // Use square-root to get uniform distribution in disc
    const radius = Math.sqrt(scatterRng(seed + 777)) * scatterCenterJitter
    return {
      dx: Math.cos(angle) * radius,
      dy: Math.sin(angle) * radius
    }
  }

  // Cluster X: center + random offset, clamped to chart area
  function scatterClusterX(predIdx: number, dotIdx: number) {
    const off = scatterOffset(predIdx * 100 + dotIdx)
    const cx = scatterCenterX(predIdx) + off.dx
    return Math.max(scatterPad + 5, Math.min(scatterW - 5, cx))
  }

  // Cluster Y: confidence band center + random offset (compressed vertically), clamped
  function scatterClusterY(confidence: string, predIdx: number, dotIdx: number) {
    const off = scatterOffset(predIdx * 200 + dotIdx + 999)
    const cy = scatterCenterY(confidence) + off.dy * 0.6
    return Math.max(scatterPad + 5, Math.min(scatterH - 5, cy))
  }

  function scatterDotR(confidence: string) {
    if (!confidence) return 2
    if (confidence.includes('高')) return 2.8
    if (confidence.includes('中')) return 2.3
    if (confidence.includes('低') || confidence.includes('不')) return 1.8
    return 2
  }

  function scatterDotIdx(count: number) {
    return Array.from({ length: count }, (_, i) => i)
  }
function insightType(t: string) {
  if (!t) return 'info'
  if (t.includes('趋势') || t.includes('预测')) return 'success'
  if (t.includes('相关')) return 'primary'
  if (t.includes('规律')) return 'warning'
  if (t.includes('异常') || t.includes('错误')) return 'danger'
  return 'info'
}

async function handleFile(file: File) {
  uploadedFile.value = file
  extractedText.value = ''
  extractError.value = ''
  result.value = null
  extracting.value = true
  try {
    const ext = file.name.split('.').pop()?.toLowerCase() || ''
    if (['txt', 'csv', 'json'].includes(ext)) {
      extractedText.value = await file.text()
    } else {
      const formData = new FormData()
      formData.append('file', file)
      const res: any = await analysisApi.extractText(formData)
      if (res.code === 200 && res.data) {
        extractedText.value = res.data
      } else {
        throw new Error(res.msg || '文本提取失败')
      }
    }
    if (!extractedText.value.trim()) {
      extractError.value = '文件内容为空或无法提取文本'
    }
  } catch (e: any) {
    extractError.value = '文本提取失败: ' + (e.message || '未知错误')
  } finally {
    extracting.value = false
  }
}

async function startMining() {
  let dataName = ''
  let dataRows: any[] = []
  let dataColumns: string[] = []

  if (sourceMode.value === 'file') {
    if (!uploadedFile.value) { ElMessage.warning('请先上传文件'); return }
    if (!extractedText.value.trim()) { ElMessage.warning('文件内容为空'); return }
    dataName = uploadedFile.value.name
    dataRows = extractedText.value.split('\n').filter((l: string) => l.trim()).map((l: string) => ({ content: l }))
    dataColumns = ['content']
  } else {
    if (!datasetId.value) { ElMessage.warning('请选择数据集'); return }
    try {
      const dsRes: any = await dataApi.getDataset(datasetId.value)
      const ds = dsRes.data
      if (!ds) { ElMessage.error('数据集不存在'); return }
      dataName = ds.name
      const rowsRes: any = await dataApi.getDataRows(datasetId.value, 1, 200)
      dataRows = rowsRes.data?.records || []
      dataColumns = dataRows.length > 0 ? Object.keys(dataRows[0]) : []
      if (dataRows.length === 0) { ElMessage.warning('数据集中无数据'); return }
    } catch (e: any) {
      ElMessage.error('获取数据集失败 ' + (e.message || '未知错误'))
      return
    }
  }

  if (!userQuery.value.trim()) { ElMessage.warning('请输入挖掘需求'); return }

  miningLoading.value = true
  result.value = null
  try {
    const res = await analysisApi.dataMining({
      message: JSON.stringify({
        datasetName: dataName,
        rowCount: dataRows.length,
        columns: dataColumns,
        rows: dataRows.slice(0, 200),
        query: userQuery.value.trim()
      })
    })
    const data = (res as any)
    const innerData = data?.data || data
    if (innerData) {
      result.value = { ...innerData, fileInfo: dataName }
      if (innerData.error) { ElMessage.error(innerData.error) }
      else { ElMessage.success('数据挖掘完成') }
    }
  } catch (e: any) {
    ElMessage.error('挖掘失败: ' + (e?.response?.data?.msg || e.message || '未知错误'))
  } finally {
    miningLoading.value = false
  }
}

async function fetchDatasets() {
  try {
    const res: any = await dataApi.getDatasets({ pageNum: 1, pageSize: 100 })
    datasets.value = res.data?.records || []
  } catch {
    datasets.value = []
  }
}

onMounted(fetchDatasets)
</script>

<style scoped>
.data-mining { min-height: calc(100vh - 140px); }
.mining-layout { display: flex; gap: 20px; }
.mining-sidebar { width: 380px; flex-shrink: 0; overflow: hidden; }
.mining-results { flex: 1; min-width: 0; }

.file-upload-area {
  border: 2px dashed rgba(255,255,255,0.15);
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
  background: rgba(255,255,255,0.02);
  overflow: hidden;
}
.file-upload-area:hover { border-color: #409eff; }
.upload-placeholder { color: rgba(255,255,255,0.5); }
.upload-placeholder p { margin: 10px 0 4px; font-size: 14px; }
.upload-hint { font-size: 12px; color: rgba(255,255,255,0.35); }
.file-info { text-align: left; width: 100%; overflow: hidden; }
.file-name-row { display: flex; align-items: center; gap: 6px; padding: 6px 8px; background: rgba(255,255,255,0.05); border-radius: 6px; width: 100%; box-sizing: border-box; }
.file-name { flex: 1; font-size: 13px; color: #e2e8f0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.text-preview { margin-top: 8px; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px; width: 100%; box-sizing: border-box; overflow: hidden; }
.preview-label { font-size: 12px; color: #94a3b8; margin-bottom: 4px; }
.preview-text { font-size: 12px; color: #cbd5e1; line-height: 1.5; max-height: 120px; overflow-y: auto; overflow-wrap: break-word; word-break: break-all; }
.extracting-hint { margin-top: 8px; font-size: 13px; color: #94a3b8; display: flex; align-items: center; gap: 6px; }
.source-radio-group { display: flex; width: 100%; gap: 0 !important; column-gap: 0 !important; } .source-radio-group.el-radio-group { gap: 0 !important; column-gap: 0 !important; }
.source-radio-group .el-radio-button { flex: 1; margin: 0 !important; } .source-radio-group .el-radio-button:not(:first-child) { margin-left: 0 !important; }
.source-radio-group .el-radio-button:not(:first-child) .el-radio-button__inner { border-left: 1px solid var(--el-border-color) !important; } .source-radio-group .el-radio-button__inner { width: 100%; border-radius: 0 !important; }
.source-radio-group .el-radio-button:first-child .el-radio-button__inner { border-radius: 4px 0 0 4px !important; }
.source-radio-group .el-radio-button:last-child .el-radio-button__inner { border-radius: 0 4px 4px 0 !important; }
/* Adjust second radio button position */
.source-radio-group :deep(.el-radio-button:nth-child(2) .el-radio-button__inner) {
  left: -82px;
}

.extract-error { margin-top: 8px; font-size: 12px; color: #ef4444; }

.ds-info { background: rgba(255,255,255,0.04); border-radius: 8px; padding: 10px 12px; font-size: 13px; line-height: 1.7; color: #cbd5e1; }
.ds-info b { color: #e2e8f0; }

.empty-state { text-align: center; padding: 80px 20px; color: #64748b; }
.empty-state p { margin-top: 12px; font-size: 14px; }
.loading-state { text-align: center; padding: 80px 20px; color: #94a3b8; }
.loading-state p { margin-top: 12px; font-size: 14px; }
.prediction-split-layout { display: flex; gap: 20px; }
.prediction-text-col { flex: 1; min-width: 0; }
.prediction-chart-col { flex: 1; min-width: 0; }
.prediction-chart-box { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 14px; height: 100%; }
.chart-title { font-size: 13px; color: #94a3b8; margin-bottom: 10px; font-weight: 500; }
.prediction-scatter { width: 100%; height: 320px; margin-top: 4px; }
@media (max-width: 768px) { .prediction-split-layout { flex-direction: column; } }
.result-section { margin-bottom: 20px; }
.section-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.06); }
.section-title { font-weight: 600; font-size: 15px; color: #e2e8f0; }
.result-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 14px; margin-bottom: 8px; }
.prediction-card { border-left: 3px solid #10b981; }
.anomaly-card { border-left: 3px solid #ef4444; }
.insight-card { border-left: 3px solid #8b5cf6; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.card-field { font-weight: 600; font-size: 14px; color: #e2e8f0; }
.card-body { font-size: 13px; line-height: 1.6; color: #cbd5e1; }
.card-body b { color: #e2e8f0; }
.flex-between { display: flex; justify-content: space-between; align-items: center; }

@media (max-width: 768px) {
  .mining-layout { flex-direction: column; }
  .mining-sidebar { width: 100%; }
}
</style>

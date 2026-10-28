<template>
  <div class="analysis page-container">
      <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <template #header><span><el-icon><DataAnalysis /></el-icon> 分析设置</span></template>
          <el-form label-position="top">
            <el-form-item label="选择数据集">
              <el-select v-model="datasetId" placeholder="请选择数据集" style="width:100%" @change="onDataSetChange">
                <el-option v-for="ds in datasets" :key="ds.id" :label="dsLabel(ds)" :value="ds.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="基本信息">
              <div v-if="selectedDataSet" class="ds-info">
                <p><b>名称：</b>{{ selectedDataSet.name }}</p>
                <p><b>行数：</b>{{ selectedDataSet.rowCount || '-' }}</p>
                <p><b>列数：</b>{{ selectedDataSet.columnCount || '-' }}</p>
                <p><b>状态：</b>
                  <el-tag size="small" :type="selectedDataSet.cleanStatus==='已清洗'||selectedDataSet.cleanStatus==='cleaned'?'success':'warning'">
                    {{ selectedDataSet.cleanStatus==='cleaned'||selectedDataSet.cleanStatus==='已清洗'?'已清洗':'未清洗' }}
                  </el-tag>
                </p>
              </div>
              <el-empty v-else description="请选择数据集" :image-size="80" />
            </el-form-item>
            <el-divider />

            <el-form-item label="分析类型">
              <el-radio-group v-model="analysisType" style="width:100%;display:flex;flex-direction:column;gap:4px;">
                <el-radio value="descriptive" style="display:flex;align-items:flex-start;white-space:normal;height:auto;padding:8px 12px;border:1px solid #e4e7ed;border-radius:6px;margin:0;width:100%;">
                  <div style="line-height:1.5;"><b>描述性统计</b><br><span style="font-size:12px;color:rgba(255,255,255,0.45);">均值、中位数、标准差、最大最小值等</span></div>
                </el-radio>
                <el-radio value="distribution" style="display:flex;align-items:flex-start;white-space:normal;height:auto;padding:8px 12px;border:1px solid #e4e7ed;border-radius:6px;margin:0;width:100%;">
                  <div style="line-height:1.5;"><b>分布分析</b><br><span style="font-size:12px;color:rgba(255,255,255,0.45);">数值列的频率分布直方图</span></div>
                </el-radio>
                <el-radio value="correlation" style="display:flex;align-items:flex-start;white-space:normal;height:auto;padding:8px 12px;border:1px solid #e4e7ed;border-radius:6px;margin:0;width:100%;">
                  <div style="line-height:1.5;"><b>相关性分析</b><br><span style="font-size:12px;color:rgba(255,255,255,0.45);">各数值列之间的皮尔逊相关系数</span></div>
                </el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item v-if="analysisType==='distribution'" label="选择分析列">
              <el-select v-model="distColumn" placeholder="请选择数值列" style="width:100%">
                <el-option v-for="col in numericColumns" :key="col" :label="col" :value="col" />
              </el-select>
            </el-form-item>

            <el-form-item v-if="analysisType==='distribution'" label="分箱数">
              <el-slider v-model="distBins" :min="3" :max="20" show-input style="width:100%" />
            </el-form-item>

            <el-button type="primary" size="large" style="width:100%" :loading="analyzing" :disabled="!canAnalyze" @click="runAnalysis">
              <el-icon><VideoPlay /></el-icon> 开始分析
            </el-button>
          </el-form>
        </el-card>

        <!-- AI 智能分析推荐 -->
        <el-card style="margin-top:20px;">
          <template #header><span><el-icon><Promotion /></el-icon> AI 智能分析推荐</span></template>
          <el-form label-position="top">
            <el-form-item label="描述你的分析需求">
              <el-input
                v-model="aiDescription"
                type="textarea"
                :rows="4"
                placeholder="例如：我想看看这些数据的整体分布情况，哪些列之间可能存在相关性"
              />
            </el-form-item>
            <el-button type="primary" size="large" style="width:100%" :loading="aiLoading" @click="fetchAiAnalysisRecommend">
              <el-icon><Aim /></el-icon> AI 智能推荐
            </el-button>
            <div v-if="aiRecommendation" style="margin-top:12px;">
              <el-divider />
              <div class="ai-rec-content">{{ aiRecommendation }}</div>
              <el-button type="success" size="large" plain style="width:100%;margin-top:12px;" @click="applyAiRecommendation">
                <el-icon><VideoPlay /></el-icon> 一键执行推荐分析
              </el-button>
            </div>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="18">
        <el-card v-loading="analyzing">
          <template #header>
            <div class="flex-between">
              <span><el-icon><TrendCharts /></el-icon> 分析结果</span>
              <div v-if="result">
                <el-tag size="small" type="success" effect="plain" style="margin-right:8px">
                  数据集: {{ result.dataSetName }}
                </el-tag>
                <el-tag size="small" type="info" effect="plain">
                  {{ analysisTypeLabel }}
                </el-tag>
                <el-button size="small" type="primary" plain @click="saveToLibrary" style="margin-left:8px;">
                  <el-icon><Folder /></el-icon> 保存到分析库
                </el-button>
              </div>
            </div>
          </template>

          <el-empty v-if="!result && !analyzing" description="选择数据集和分析类型，点击「开始分析」" :image-size="120" />

          <template v-if="result?.analysisType === 'descriptive'">
            <el-table :data="result.columnStats" border stripe size="small" max-height="500">
              <el-table-column prop="columnName" label="列名" fixed min-width="140" />
              <el-table-column prop="dataType" label="类型" width="80">
                <template #default="{row}">
                  <el-tag size="small" :type="row.dataType==='numeric'?'primary':row.dataType==='text'?'success':'warning'">
                    {{ {numeric:'数值',text:'文本',mixed:'混合',empty:'空',date:'日期'}[row.dataType] || row.dataType }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="count" label="有效值" width="70" align="center" />
              <el-table-column prop="missingCount" label="缺失值" width="70" align="center" />
              <el-table-column prop="mean" label="均值" width="90" align="center">
                <template #default="{row}">{{ row.mean ?? '-' }}</template>
              </el-table-column>
              <el-table-column prop="median" label="中位数" width="90" align="center">
                <template #default="{row}">{{ row.median ?? '-' }}</template>
              </el-table-column>
              <el-table-column prop="min" label="最小值" width="90" align="center">
                <template #default="{row}">{{ row.min ?? '-' }}</template>
              </el-table-column>
              <el-table-column prop="max" label="最大值" width="90" align="center">
                <template #default="{row}">{{ row.max ?? '-' }}</template>
              </el-table-column>
              <el-table-column prop="stdDev" label="标准差" width="90" align="center">
                <template #default="{row}">{{ row.stdDev ?? '-' }}</template>
              </el-table-column>
              <el-table-column prop="mode" label="众数" min-width="120">
                <template #default="{row}">{{ row.mode || '-' }}</template>
              </el-table-column>
            </el-table>
          </template>

          <template v-if="result?.analysisType === 'distribution'">
            <div style="margin-bottom:16px;">
              <el-tag type="primary">分析列：{{ result.columnName }}</el-tag>
            </div>
            <div ref="chartRef" style="width:100%;height:450px;"></div>
            <el-table :data="result.distribution" border stripe size="small" max-height="300" style="margin-top:16px;">
              <el-table-column prop="label" label="区间" width="160" />
              <el-table-column prop="count" label="频数" width="80" align="center" />
              <el-table-column label="可视化" min-width="300">
                <template #default="{row}">
                  <div class="bar-cell">
                    <div class="bar-fill" :style="{width: barWidth(row.count) + '%'}"></div>
                    <span class="bar-label">{{ row.count }}</span>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </template>

          <template v-if="result?.analysisType === 'correlation'">
            <p style="color:#666;margin-bottom:12px;font-size:13px;">
              皮尔逊相关系数（-1 ~ 1）：越接近 1 正相关越强，越接近 -1 负相关越强，0 表示无线性相关
            </p>
            <div ref="heatmapRef" style="width:100%;height:500px;"></div>
            <el-table :data="correlationRows" border stripe size="small" max-height="400" style="margin-top:16px;">
              <el-table-column prop="col1" label="列1" min-width="120" />
              <el-table-column prop="col2" label="列2" min-width="120" />
              <el-table-column prop="value" label="相关系数" width="120" align="center">
                <template #default="{row}">
                  <el-tag :type="row.value > 0.5 ? 'success' : row.value < -0.5 ? 'danger' : 'info'" size="small">
                    {{ row.value.toFixed(2) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="相关性强度" min-width="150">
                <template #default="{row}">
                  {{ correlationStrength(row.value) }}
                </template>
              </el-table-column>
            </el-table>
          </template>

          <el-alert v-if="error" :title="error" type="error" show-icon style="margin-top:16px;" closable @close="error=''" />
        </el-card>
      </el-col>
    </el-row>
</div>
</template>
<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { dataApi, analysisLibraryApi, analysisApi } from '@/api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const datasets = ref<any[]>([])
const selectedDataSet = ref<any>(null)
const datasetId = ref<number | null>(null)
const analysisType = ref('descriptive')
const distColumn = ref('')
const distBins = ref(10)
const analyzing = ref(false)
const aiDescription = ref('')
const aiLoading = ref(false)
const aiRecommendation = ref('')
const previewColumns = ref<{name:string;type:string}[]>([])
const result = ref<any>(null)
const error = ref('')
const chartRef = ref<HTMLElement>()
const heatmapRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null
let heatmap: echarts.ECharts | null = null

const numericColumns = computed(() => {
  if (previewColumns.value.length > 0) {
    return previewColumns.value.filter(c => c.type === 'numeric').map(c => c.name)
  }
  if (result.value?.columnStats) {
    return result.value.columnStats
      .filter((s: any) => s.dataType === 'numeric')
      .map((s: any) => s.columnName)
  }
  return []
})

async function loadPreviewColumns() {
  if (!datasetId.value) { previewColumns.value = []; return }
  try {
    const res: any = await dataApi.getDataset(datasetId.value)
    const detail = res.data
    if (detail?.columnCount) {
      const descRes: any = await dataApi.describeDataSet(datasetId.value)
      if (descRes.data?.columnStats) {
        previewColumns.value = descRes.data.columnStats.map((s: any) => ({
          name: s.columnName,
          type: s.dataType
        }))
        return
      }
    }
  } catch {}
}

const canAnalyze = computed(() => datasetId.value && (analysisType.value !== 'distribution' || distColumn.value))

function dsLabel(ds: any) {
  return (ds.name || '') + (ds.fileName ? ' (' + ds.fileName + ')' : '')
}

const analysisTypeLabel = computed(() => {
  const labels: any = { descriptive: '描述性统计', distribution: '分布分析', correlation: '相关性分析' }
  return labels[analysisType.value] || analysisType.value
})

function barWidth(count: number) {
  if (!result.value?.distribution) return 0
  const max = Math.max(...result.value.distribution.map((b: any) => b.count), 1)
  return Math.max((count / max) * 100 * 0.8, 3)
}

const correlationRows = computed(() => {
  if (!result.value?.correlationMatrix) return []
  const cols = result.value.correlationColumns
  const matrix = result.value.correlationMatrix
  const rows: any[] = []
  for (let i = 0; i < cols.length; i++) {
    for (let j = i + 1; j < cols.length; j++) {
      rows.push({ col1: cols[i], col2: cols[j], value: matrix[i][j] })
    }
  }
  return rows.sort((a: any, b: any) => Math.abs(b.value) - Math.abs(a.value))
})

function correlationStrength(v: number) {
  const a = Math.abs(v)
  if (a >= 0.8) return '极强相关'
  if (a >= 0.6) return '强相关'
  if (a >= 0.4) return '中等相关'
  if (a >= 0.2) return '弱相关'
  return '极弱/无相关'
}

async function fetchDatasets() {
  try {
    const res: any = await dataApi.getDatasets({ pageNum: 1, pageSize: 100 })
    datasets.value = res.data?.records || []
  } catch { datasets.value = [] }
}

watch(analysisType, (val) => {
  if (val === 'distribution' && datasetId.value) loadPreviewColumns()
  if (val !== 'distribution') previewColumns.value = []
})

function onDataSetChange() {
  selectedDataSet.value = datasets.value.find((d: any) => d.id === datasetId.value) || null
  distColumn.value = ''
  result.value = null
  error.value = ''
  previewColumns.value = []
  if (analysisType.value === 'distribution') loadPreviewColumns()
}

async function runAnalysis() {
  if (!datasetId.value) { ElMessage.warning('请选择数据集'); return }
  analyzing.value = true
  error.value = ''
  result.value = null
  chart?.dispose(); chart = null
  heatmap?.dispose(); heatmap = null
  try {
    let res: any
    if (analysisType.value === 'descriptive') {
      res = await dataApi.describeDataSet(datasetId.value)
    } else if (analysisType.value === 'distribution') {
      if (!distColumn.value) { ElMessage.warning('请选择分析列'); analyzing.value = false; return }
      res = await dataApi.distributionAnalysis(datasetId.value, distColumn.value, distBins.value)
    } else if (analysisType.value === 'correlation') {
      res = await dataApi.correlationAnalysis(datasetId.value)
    }
    result.value = res.data
    await nextTick()
    if (analysisType.value === 'distribution') renderDistributionChart()
    if (analysisType.value === 'correlation') renderCorrelationHeatmap()
  } catch (e: any) {
    error.value = e?.response?.data?.msg || e.message || '分析失败'
  } finally {
    analyzing.value = false
  }
}

function renderDistributionChart() {
  if (!chartRef.value || !result.value?.distribution) return
  if (chart) chart.dispose()
  if (!chartRef.value) return
  try { chart = echarts.init(chartRef.value) } catch { return }
  const bins = result.value.distribution
  chart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => params[0].name + '<br/>??: ' + params[0].value },
    grid: { left: 60, right: 30, top: 20, bottom: 50 },
    xAxis: { type: 'category', data: bins.map((b: any) => b.label), axisLabel: { rotate: 45, fontSize: 11 } },
    yAxis: { type: 'value', name: '??' },
    series: [{ type: 'bar', data: bins.map((b: any) => b.count), itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] }, barMaxWidth: 50 }]
  })
}

function renderCorrelationHeatmap() {
  if (!heatmapRef.value || !result.value?.correlationMatrix) return
  if (heatmap) heatmap.dispose()
  if (!heatmapRef.value) return
  try { heatmap = echarts.init(heatmapRef.value) } catch { return }
  const cols = result.value.correlationColumns
  const matrix = result.value.correlationMatrix
  const data: any[] = []
  for (let i = 0; i < cols.length; i++) {
    for (let j = 0; j < cols.length; j++) {
      data.push([j, i, matrix[i][j]])
    }
  }
  heatmap.setOption({
    tooltip: { formatter: (params: any) => cols[params.data[0]] + ' x ' + cols[params.data[1]] + '<br/>????: ' + params.data[2].toFixed(2) },
    grid: { left: 120, right: 60, top: 20, bottom: 80 },
    xAxis: { type: 'category', data: cols, axisLabel: { rotate: 45, fontSize: 10 } },
    yAxis: { type: 'category', data: cols, axisLabel: { fontSize: 10 } },
    visualMap: {
      min: -1, max: 1,
      inRange: { color: ['#d73027','#f46d43','#fdae61','#fee08b','#ffffbf','#d9ef8b','#a6d96a','#66bd63','#1a9850'] },
      text: ['正相关', '负相关'], textStyle: { fontSize: 11 }, calculable: true
    },
    series: [{ type: 'heatmap', data: data, label: { show: true, fontSize: 11, color: '#333', formatter: (p: any) => p.data[2].toFixed(1) }, emphasis: { itemStyle: { shadowBlur: 5 } } }]
  })
}

async function fetchAiAnalysisRecommend() {
  if (!aiDescription.value.trim()) { ElMessage.warning('请输入你的分析需求'); return }
  if (!datasetId.value) { ElMessage.warning('请先选择数据集'); return }
  aiLoading.value = true
  aiRecommendation.value = ''
  try {
    const ds = selectedDataSet.value
      const context = '当前选中的数据集是「' + (ds?.name || '未知') + '」，包含 ' + (ds?.rowCount || '?') + ' 行 ' + (ds?.columnCount || '?') + ' 列数据。'
    const res: any = await analysisApi.agentAnalysisRecommend({
        message: context + '\n\n用户的分析需求：' + aiDescription.value


    })
    if (res.data?.content) {
      let txt = res.data.content;
      // Replace corrupted emoji/symbols with readable alternatives
      txt = txt.replace(/\u00a0/g, " ");
      txt = txt.replace(/\ufffd/g, "");
      txt = txt.replace(/## \? /g, "## ");
      txt = txt.replace(/### \? /g, "### ");
      txt = txt.replace(/#### \? /g, "#### ");
      txt = txt.replace(/\? \?/g, "");
      aiRecommendation.value = txt;
    } else {
      aiRecommendation.value = 'AI 暂未返回推荐结果，请稍后重试'
    }
  } catch (e: any) {
    aiRecommendation.value = '获取推荐失败：' + (e?.response?.data?.msg || e.message || '网络错误')
  } finally {
    aiLoading.value = false
  }
}

function applyAiRecommendation() {
  if (!aiRecommendation.value) return
  const rec = aiRecommendation.value
  if (rec.includes('描述性') || rec.includes('描述性统计')) {
    analysisType.value = 'descriptive'
  } else if (rec.includes('分布') || rec.includes('分布分析') || rec.includes('频率分布')) {
    analysisType.value = 'distribution'
    const colMatch = rec.match(/分析列[：:]\s*(\S+)/)
    if (colMatch && numericColumns.value.includes(colMatch[1])) {
      distColumn.value = colMatch[1]
    }
  } else if (rec.includes('相关') || rec.includes('相关性') || rec.includes('相关系数')) {
    analysisType.value = 'correlation'
  }
  ElMessage.success('已自动选择推荐的分析类型，点击「开始分析」执行')
}

async function saveToLibrary() {
  if (!result.value) return
  const r = result.value
  let lines = []
  lines.push('========================================')
  lines.push('  ' + analysisTypeLabel.value)
  lines.push('========================================')
  lines.push('')
  lines.push('数据集: ' + (selectedDataSet.value?.name || r.dataSetName || '??'))
  lines.push('分析时间: ' + new Date().toLocaleString())
  lines.push('')
  if (r.analysisType === 'descriptive' && r.columnStats) {
    lines.push('--- 描述性统计 ---')
    lines.push('')
    const h = '列名'.padEnd(16) + '类型'.padEnd(8) + '有效值'.padEnd(8) + '均值'.padEnd(10) + '中位数'.padEnd(10) + '标准差'.padEnd(10) + '最小值'.padEnd(10) + '最大值'.padEnd(10)
    lines.push(h)
    lines.push('-'.repeat(80))
    for (const col of r.columnStats) {
      lines.push((col.columnName||'').padEnd(16) + (col.dataType||'').padEnd(8) + (String(col.count)||'').padEnd(8) + (col.mean!=null?String(Number(col.mean).toFixed(2)):'-').padEnd(10) + (col.median!=null?String(Number(col.median).toFixed(2)):'-').padEnd(10) + (col.stdDev!=null?String(Number(col.stdDev).toFixed(2)):'-').padEnd(10) + (col.min!=null?String(col.min):'-').padEnd(10) + (col.max!=null?String(col.max):'-').padEnd(10))
    }
  }
  if (r.analysisType === 'distribution' && r.distribution) {
    lines.push('--- 分布分析 ---')
    lines.push('分析列: ' + r.columnName)
    lines.push('')
    lines.push('区间'.padEnd(20) + '频数')
    lines.push('-'.repeat(30))
    for (const b of r.distribution) {
      lines.push((b.label||'').padEnd(20) + String(b.count))
    }
  }
  if (r.analysisType === 'correlation' && r.correlationMatrix) {
    lines.push('--- 相关性分析 ---')
    lines.push('')
    const cols = r.correlationColumns || []
    for (let i = 0; i < cols.length; i++) {
      for (let j = i + 1; j < cols.length; j++) {
        const v = r.correlationMatrix[i][j]
        let strength = '极弱/无相关'
        const a = Math.abs(v)
        if (a >= 0.8) strength = '极强相关'
        else if (a >= 0.6) strength = '强相关'
        else if (a >= 0.4) strength = '中等相关'
        else if (a >= 0.2) strength = '弱相关'
        lines.push(cols[i].padEnd(16) + ' x ' + cols[j].padEnd(16) + ' ' + String(v.toFixed(4)).padEnd(10) + strength)
      }
    }
  }
  lines.push('')
  lines.push('========================================')
  try {
    await analysisLibraryApi.saveAnalysis({
      datasetId: datasetId.value,
      datasetName: selectedDataSet.value?.name || r.dataSetName || '未知数据集',
      analysisType: r.analysisType,
      analysisTypeLabel: analysisTypeLabel.value,
      resultJson: lines.join(String.fromCharCode(10))
    })
    ElMessage.success('已保存到分析库')
  } catch (e) { ElMessage.error('保存失败') }
}

onMounted(fetchDatasets)
onUnmounted(() => { chart?.dispose(); heatmap?.dispose() })
</script>

<style scoped>
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.ds-info p { margin: 4px 0; font-size: 13px; color: rgba(255,255,255,0.6); }
.bar-cell { display: flex; align-items: center; height: 22px; }
.bar-fill { height: 18px; background: linear-gradient(90deg, #409eff, #79bbff); border-radius: 3px; min-width: 4px; transition: width 0.3s; }
.bar-label { margin-left: 8px; font-size: 12px; color: rgba(255,255,255,0.5); }
.ai-rec-content { color: #ffffff; font-size: 13px; line-height: 1.6; white-space: pre-wrap; }
</style>
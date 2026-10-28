<template>
  <div class="analysis-report page-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="flex-between">
          <span><el-icon><Tickets /></el-icon> 分析报告详情</span>
          <el-button @click="$router.push('/campus/analysis')"><el-icon><ArrowLeft /></el-icon> 返回分析页</el-button>
        </div>
      </template>

      <el-empty v-if="!report && !loading" description="报告不存在" />

      <!-- 描述性统计 -->
      <template v-if="report?.analysisType === 'descriptive'">
        <el-descriptions :column="2" border style="margin-bottom:16px;">
          <el-descriptions-item label="数据集">{{ report.dataSetName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分析类型">描述性统计</el-descriptions-item>
        </el-descriptions>
        <el-table :data="report.columnStats" border stripe size="small" max-height="500">
          <el-table-column prop="columnName" label="列名" fixed min-width="140" />
          <el-table-column prop="dataType" label="类型" width="80">
            <template #default="{row}">
              <el-tag size="small" :type="row.dataType==='numeric'?'primary':'success'">
                {{ {numeric:'数值',text:'文本',mixed:'混合',empty:'空'}[row.dataType] || row.dataType }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="count" label="有效值" width="70" align="center" />
          <el-table-column prop="missingCount" label="缺失值" width="70" align="center" />
          <el-table-column prop="mean" label="均值" width="90" align="center"><template #default="{row}">{{ row.mean ?? '-' }}</template></el-table-column>
          <el-table-column prop="median" label="中位数" width="90" align="center"><template #default="{row}">{{ row.median ?? '-' }}</template></el-table-column>
          <el-table-column prop="min" label="最小值" width="90" align="center"><template #default="{row}">{{ row.min ?? '-' }}</template></el-table-column>
          <el-table-column prop="max" label="最大值" width="90" align="center"><template #default="{row}">{{ row.max ?? '-' }}</template></el-table-column>
          <el-table-column prop="stdDev" label="标准差" width="90" align="center"><template #default="{row}">{{ row.stdDev ?? '-' }}</template></el-table-column>
          <el-table-column prop="mode" label="众数" min-width="120"><template #default="{row}">{{ row.mode || '-' }}</template></el-table-column>
        </el-table>
      </template>

      <!-- 分布分析 -->
      <template v-if="report?.analysisType === 'distribution'">
        <el-descriptions :column="2" border style="margin-bottom:16px;">
          <el-descriptions-item label="数据集">{{ report.dataSetName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分析列">{{ report.columnName }}</el-descriptions-item>
        </el-descriptions>
        <div ref="chartRef" style="width:100%;height:400px;"></div>
        <el-table :data="report.distribution" border stripe size="small" max-height="300" style="margin-top:16px;">
          <el-table-column prop="label" label="区间" width="160" />
          <el-table-column prop="count" label="频数" width="80" align="center" />
        </el-table>
      </template>

      <!-- 相关性分析 -->
      <template v-if="report?.analysisType === 'correlation'">
        <el-descriptions :column="1" border style="margin-bottom:16px;">
          <el-descriptions-item label="数据集">{{ report.dataSetName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分析类型">相关性分析</el-descriptions-item>
          <el-descriptions-item label="参与分析列数">{{ report.correlationColumns?.length || 0 }}</el-descriptions-item>
        </el-descriptions>
        <div ref="heatmapRef" style="width:100%;height:450px;"></div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { dataApi } from '@/api'
import * as echarts from 'echarts'

const route = useRoute()
const loading = ref(true)
const report = ref<any>(null)
const chartRef = ref<HTMLElement>()
const heatmapRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null
let heatmap: echarts.ECharts | null = null

async function fetchReport() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const res: any = await dataApi.getDataset(id)
    report.value = {}
  } catch { report.value = null }
  finally { loading.value = false }
}

onMounted(() => { fetchReport() })
onUnmounted(() => { chart?.dispose(); heatmap?.dispose() })
</script>

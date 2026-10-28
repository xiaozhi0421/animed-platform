<template>
  <div class="data-screen">
    <div class="bg-canvas">
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
      <div class="bg-orb bg-orb-3"></div>
      <div class="bg-grid"></div>
    </div>
    <div class="screen-container">
      <header class="screen-header">
        <div class="header-left">
          <div class="header-badge"><span class="live-dot"></span><span>LIVE</span></div>
          <h1 class="screen-title">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/><path d="M15 21V9"/>
            </svg>
            平台数据驾驶舱
          </h1>
        </div>
        <div class="header-right">
          <div class="time-display">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
            </svg>
            <span>{{ currentTime }}</span>
          </div>
          <button class="refresh-btn" :class="{ refreshing: loading }" @click="fetchData">
            <svg class="refresh-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>刷新
          </button>
        </div>
      </header>
      <div v-if="loading && !stats" class="loading-state"><div class="loader"></div><span>正在加载数据...</span></div>

      <!-- Row 1: Big metrics -->
      <section class="metrics-row" v-if="stats">
        <div class="metric-card" v-for="(card, idx) in row1Cards" :key="'r1-'+idx">
          <div class="metric-icon-wrap" :style="{ background: card.bg }"><span v-html="card.icon"></span></div>
          <div class="metric-body">
            <div class="metric-label">{{ card.label }}</div>
            <div class="metric-value">{{ formatNum(card.value) }}</div>
            <div class="metric-footer">
              <span v-for="(item, i) in card.items" :key="i" class="metric-tag">
                <span class="metric-dot" :style="{ background: item.color }"></span>
                {{ item.label }}{{ formatNum(item.value) }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Row 2: Daily activity -->
      <section class="metrics-row sm" v-if="stats">
        <div class="metric-card sm" v-for="(card, idx) in row2Cards" :key="'r2-'+idx">
          <div class="metric-icon-wrap sm" :style="{ background: card.bg }"><span v-html="card.icon"></span></div>
          <div class="metric-body">
            <div class="metric-label">{{ card.label }}</div>
            <div class="metric-value sm">{{ formatNum(card.value) }}</div>
          </div>
        </div>
      </section>

      <!-- Charts 2x2 -->
      <section class="charts-main" v-if="stats">
        <div class="chart-panel">
          <div class="panel-header"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg><span>用户角色分布</span></div>
          <div ref="userChartRef" class="chart-container"></div>
        </div>
        <div class="chart-panel">
          <div class="panel-header"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/></svg><span>设备状态分布</span></div>
          <div ref="equipChartRef" class="chart-container"></div>
        </div>
        <div class="chart-panel">
          <div class="panel-header"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg><span>预约状态分布</span></div>
          <div ref="resChartRef" class="chart-container"></div>
        </div>
        <div class="chart-panel">
          <div class="panel-header"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg><span>维修 &amp; 课题状态</span></div>
          <div ref="maintChartRef" class="chart-container"></div>
        </div>
      </section>

      <!-- Trend charts -->
      <section class="charts-trend" v-if="stats && trendData">
        <div class="chart-panel wide">
          <div class="panel-header"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg><span>近7日访问趋势</span></div>
          <div ref="visitTrendRef" class="chart-container lg"></div>
        </div>
        <div class="chart-panel wide">
          <div class="panel-header"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg><span>近7日课题 &amp; 预约趋势</span></div>
          <div ref="topicTrendRef" class="chart-container lg"></div>
        </div>
      </section>

      <!-- Bottom -->
      <section class="bottom-section" v-if="stats">
        <div class="bottom-panel">
          <div class="panel-header"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><span>全量数据指标</span></div>
          <div class="table-wrap">
            <table class="screen-table">
              <thead><tr><th>分类</th><th>指标</th><th style="text-align:right">数值</th><th>说明</th></tr></thead>
              <tbody>
                <tr v-for="(row, i) in overviewTable" :key="i">
                  <td><span class="badge-cat" :style="{ background: row.catColor }">{{ row.category }}</span></td>
                  <td><span class="cell-primary">{{ row.name }}</span></td>
                  <td style="text-align:right"><span class="cell-value">{{ row.value }}</span></td>
                  <td class="cell-desc">{{ row.desc }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="bottom-panel">
          <div class="panel-header"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg><span>综合概览</span></div>
          <div class="summary-grid">
            <div class="summary-item" v-for="(item, i) in summaryItems" :key="i">
              <div class="summary-dot" :style="{ background: item.color }"></div>
              <div class="summary-info">
                <span class="summary-label">{{ item.label }}</span>
                <span class="summary-value">{{ typeof item.value === 'number' ? formatNum(item.value) : item.value }}</span>
              </div>
            </div>
          </div>
          <div class="health-bar-wrap">
            <div class="panel-header" style="margin-bottom:6px"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg><span>系统健康度</span></div>
            <div class="health-bar"><div class="health-fill" :style="{ width: healthPercent + '%' }"><span class="health-label">{{ healthPercent }}%</span></div></div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { adminApi } from '@/api'
import * as echarts from 'echarts'

const loading = ref(false)
const stats = ref<any>(null)
const trendData = ref<any>(null)
const currentTime = ref('')
const healthPercent = ref(100)

const userChartRef = ref<HTMLElement>()
const equipChartRef = ref<HTMLElement>()
const resChartRef = ref<HTMLElement>()
const maintChartRef = ref<HTMLElement>()
const visitTrendRef = ref<HTMLElement>()
const topicTrendRef = ref<HTMLElement>()

let charts: any[] = []
let timeInterval: any = null

const row1Cards = ref([
  { label: '用户总数', value: 0, bg: 'linear-gradient(135deg,rgba(99,102,241,.25),rgba(99,102,241,.05))', items: [],
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
  { label: '仪器设备', value: 0, bg: 'linear-gradient(135deg,rgba(16,185,129,.25),rgba(16,185,129,.05))', items: [],
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="1.5"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><path d="M6 6h.01M6 18h.01"/></svg>' },
  { label: '预约总次数', value: 0, bg: 'linear-gradient(135deg,rgba(168,85,247,.25),rgba(168,85,247,.05))', items: [],
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/></svg>' },
  { label: '维修记录', value: 0, bg: 'linear-gradient(135deg,rgba(239,68,68,.25),rgba(239,68,68,.05))', items: [],
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f87171" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>' },
  { label: '课题提交', value: 0, bg: 'linear-gradient(135deg,rgba(244,114,182,.25),rgba(244,114,182,.05))', items: [],
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f472b6" stroke-width="1.5"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>' },
  { label: '实验室数', value: 0, bg: 'linear-gradient(135deg,rgba(234,179,8,.25),rgba(234,179,8,.05))', items: [],
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>' }
])

const row2Cards = ref([
  { label: '今日登录', value: 0, bg: 'linear-gradient(135deg,rgba(6,182,212,.2),rgba(6,182,212,.05))',
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="1.5"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>' },
  { label: '今日活跃', value: 0, bg: 'linear-gradient(135deg,rgba(16,185,129,.2),rgba(16,185,129,.05))',
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="1.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>' },
  { label: '数据上传', value: 0, bg: 'linear-gradient(135deg,rgba(99,102,241,.2),rgba(99,102,241,.05))',
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>' },
  { label: '分析次数', value: 0, bg: 'linear-gradient(135deg,rgba(168,85,247,.2),rgba(168,85,247,.05))',
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="1.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>' },
  { label: '今日预约', value: 0, bg: 'linear-gradient(135deg,rgba(244,114,182,.2),rgba(244,114,182,.05))',
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f472b6" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/></svg>' },
  { label: '已使用预约', value: 0, bg: 'linear-gradient(135deg,rgba(6,182,212,.2),rgba(6,182,212,.05))',
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="1.5"><polyline points="20 6 9 17 4 12"/></svg>' },
  { label: '待审课题', value: 0, bg: 'linear-gradient(135deg,rgba(234,179,8,.2),rgba(234,179,8,.05))',
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' },
  { label: '待处理维修', value: 0, bg: 'linear-gradient(135deg,rgba(239,68,68,.2),rgba(239,68,68,.05))',
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f87171" stroke-width="1.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>' }
])

const overviewTable = ref<any[]>([])
const summaryItems = ref<any[]>([])

function formatNum(n: any): string {
  const v = Number(n) || 0
  if (v >= 10000) return (v / 10000).toFixed(1) + 'w'
  return v.toLocaleString()
}

function buildOverviewTable(d: any) {
  const catColor = (cat: string) => ({ '用户':'rgba(99,102,241,0.2)','设备':'rgba(16,185,129,0.2)','预约':'rgba(168,85,247,0.2)','维修':'rgba(239,68,68,0.2)','课题':'rgba(244,114,182,0.2)','教学':'rgba(234,179,8,0.2)' }[cat]||'rgba(255,255,255,0.05)')
  return [
    { category:'用户', name:'学生总数', value:formatNum(d.studentCount), desc:'已激活学生账号', catColor:catColor('用户') },
    { category:'用户', name:'教师总数', value:formatNum(d.teacherCount), desc:'已激活教师账号', catColor:catColor('用户') },
    { category:'用户', name:'今日登录', value:formatNum(d.todayLoginCount), desc:'当天登录人次', catColor:catColor('用户') },
    { category:'用户', name:'今日活跃', value:formatNum(d.todayActiveCount), desc:'当日活跃用户数', catColor:catColor('用户') },
    { category:'设备', name:'实验室数', value:formatNum(d.labCount), desc:'总实验室数量', catColor:catColor('设备') },
    { category:'设备', name:'设备总数', value:formatNum(d.equipmentCount), desc:'全部仪器设备', catColor:catColor('设备') },
    { category:'预约', name:'预约总数', value:formatNum(d.reservationCount), desc:'所有预约记录', catColor:catColor('预约') },
    { category:'预约', name:'已使用', value:formatNum(d.approvedReservationCount), desc:'已通过+已完成', catColor:catColor('预约') },
    { category:'预约', name:'今日预约', value:formatNum(d.todayReservationCount), desc:'今日新增预约', catColor:catColor('预约') },
    { category:'维修', name:'维修总数', value:formatNum(d.maintenanceCount), desc:'全部维修记录', catColor:catColor('维修') },
    { category:'维修', name:'待处理', value:formatNum(d.pendingMaintenanceCount), desc:'待审核', catColor:catColor('维修') },
    { category:'维修', name:'进行中', value:formatNum(d.inProgressMaintenanceCount), desc:'正在维修', catColor:catColor('维修') },
    { category:'维修', name:'已完成', value:formatNum(d.completedMaintenanceCount), desc:'维修完成', catColor:catColor('维修') },
    { category:'课题', name:'课题总数', value:formatNum(d.topicSubmissionCount), desc:'全部课题提交', catColor:catColor('课题') },
    { category:'课题', name:'待审核', value:formatNum(d.pendingTopicCount), desc:'待审批', catColor:catColor('课题') },
    { category:'课题', name:'今日提交', value:formatNum(d.todayTopicCount), desc:'今日新增', catColor:catColor('课题') },
    { category:'教学', name:'课程数', value:formatNum(d.courseCount), desc:'总课程', catColor:catColor('教学') },
    { category:'教学', name:'班级数', value:formatNum(d.classCount), desc:'总班级', catColor:catColor('教学') }
  ]
}

function buildSummaryItems(d: any) {
  return [
    { label:'系统健康率', value:(d.systemHealthRate??100)+'%', color:'#4ade80' },
    { label:'今日数据上传', value:d.todayDataUploadCount??0, color:'#22d3ee' },
    { label:'今日分析次数', value:d.todayAnalysisCount??0, color:'#fbbf24' },
    { label:'课程数量', value:d.courseCount??0, color:'#a78bfa' },
    { label:'班级数量', value:d.classCount??0, color:'#f472b6' },
    { label:'待审课题', value:d.pendingTopicCount??0, color:'#f87171' }
  ]
}

async function fetchData() {
  loading.value = true
  try {
    const [sr, tr] = await Promise.all([
      adminApi.getStats(),
      adminApi.getTrend().catch(() => ({ data: null }))
    ])
    const d = sr.data || sr
    stats.value = d
    trendData.value = tr?.data || tr

    row1Cards.value[0].value = d.totalCount ?? 0
    row1Cards.value[0].items = [{ label:'学 ', value:d.studentCount??0, color:'#818cf8' },{ label:'教 ', value:d.teacherCount??0, color:'#4ade80' }]
    row1Cards.value[1].value = d.equipmentCount ?? 0
    row1Cards.value[1].items = [{ label:'实 ', value:d.labCount??0, color:'#22d3ee' }]
    row1Cards.value[2].value = d.reservationCount ?? 0
    row1Cards.value[2].items = [{ label:'已用 ', value:d.approvedReservationCount??0, color:'#4ade80' },{ label:'今 ', value:d.todayReservationCount??0, color:'#fbbf24' }]
    row1Cards.value[3].value = d.maintenanceCount ?? 0
    row1Cards.value[3].items = [{ label:'待 ', value:d.pendingMaintenanceCount??0, color:'#f87171' },{ label:'中 ', value:d.inProgressMaintenanceCount??0, color:'#fbbf24' }]
    row1Cards.value[4].value = d.topicSubmissionCount ?? 0
    row1Cards.value[4].items = [{ label:'待审 ', value:d.pendingTopicCount??0, color:'#fbbf24' },{ label:'今 ', value:d.todayTopicCount??0, color:'#4ade80' }]
    row1Cards.value[5].value = d.labCount ?? 0
    row1Cards.value[5].items = [{ label:'课程 ', value:d.courseCount??0, color:'#a78bfa' },{ label:'班级 ', value:d.classCount??0, color:'#f472b6' }]

    row2Cards.value[0].value = d.todayLoginCount ?? 0
    row2Cards.value[1].value = d.todayActiveCount ?? 0
    row2Cards.value[2].value = d.todayDataUploadCount ?? 0
    row2Cards.value[3].value = d.todayAnalysisCount ?? 0
    row2Cards.value[4].value = d.todayReservationCount ?? 0
    row2Cards.value[5].value = d.approvedReservationCount ?? 0
    row2Cards.value[6].value = d.pendingTopicCount ?? 0
    row2Cards.value[7].value = d.pendingMaintenanceCount ?? 0

    healthPercent.value = d.systemHealthRate ?? 100
    overviewTable.value = buildOverviewTable(d)
    summaryItems.value = buildSummaryItems(d)
  } catch (e) { console.warn(e) }
  finally {
    loading.value = false
    await nextTick()
    initCharts()
  }
}

function initCharts() {
  if (!stats.value) return
  charts.forEach(c => c?.dispose())
  charts = []
  const base = { textStyle: { color: 'rgba(255,255,255,0.5)' } }

  if (userChartRef.value) {
    const c = echarts.init(userChartRef.value!)
    c.setOption({ ...base, tooltip: { trigger:'item', formatter:'{b}: {c} ({d}%)' },
      series: [{ type:'pie', radius:['42%','68%'], label:{ color:'rgba(255,255,255,0.6)', fontSize:10 },
        data: [
          { value: stats.value.studentCount||0, name:'学生', itemStyle:{ color:'#818cf8' } },
          { value: stats.value.teacherCount||0, name:'教师', itemStyle:{ color:'#4ade80' } }
        ]
      }]
    })
    charts.push(c)
  }

  if (equipChartRef.value) {
    const c = echarts.init(equipChartRef.value!)
    const eqData = [
      { name:'正常', value: stats.value.equipmentNormal||0, itemStyle:{ color:'#4ade80' } },
      { name:'故障', value: stats.value.equipmentFaulty||0, itemStyle:{ color:'#f87171' } },
      { name:'维修中', value: stats.value.equipmentMaintenance||0, itemStyle:{ color:'#fbbf24' } },
      { name:'报废', value: stats.value.equipmentScrap||0, itemStyle:{ color:'#94a3b8' } },
      { name:'使用中', value: stats.value.equipmentInUse||0, itemStyle:{ color:'#22d3ee' } }
    ].filter(d => d.value > 0)
    if (!eqData.length) eqData.push({ name:'暂无', value:0, itemStyle:{ color:'#334155' } })
    c.setOption({ ...base, tooltip:{ trigger:'item', formatter:'{b}: {c} ({d}%)' },
      series: [{ type:'pie', radius:['42%','68%'], label:{ color:'rgba(255,255,255,0.6)', fontSize:10 }, data: eqData }]
    })
    charts.push(c)
  }

  if (resChartRef.value) {
    const c = echarts.init(resChartRef.value!)
    const rsData = [
      { name:'待审批', value: stats.value.reservationPending||0, itemStyle:{ color:'#fbbf24' } },
      { name:'已通过', value: stats.value.reservationApproved||0, itemStyle:{ color:'#4ade80' } },
      { name:'已完成', value: stats.value.reservationCompleted||0, itemStyle:{ color:'#818cf8' } },
      { name:'已拒绝', value: stats.value.reservationRejected||0, itemStyle:{ color:'#f87171' } },
      { name:'使用中', value: stats.value.reservationInUse||0, itemStyle:{ color:'#22d3ee' } },
      { name:'已取消', value: stats.value.reservationCancelled||0, itemStyle:{ color:'#94a3b8' } }
    ].filter(d => d.value > 0)
    if (!rsData.length) rsData.push({ name:'暂无', value:0, itemStyle:{ color:'#334155' } })
    c.setOption({ ...base, tooltip:{ trigger:'item', formatter:'{b}: {c} ({d}%)' },
      series: [{ type:'pie', radius:['42%','68%'], label:{ color:'rgba(255,255,255,0.6)', fontSize:10 }, data: rsData }]
    })
    charts.push(c)
  }

  if (maintChartRef.value) {
    const c = echarts.init(maintChartRef.value!)
    c.setOption({ ...base, tooltip:{ trigger:'axis' },
      grid: { left:'10%', right:'6%', bottom:'12%', containLabel:true },
      xAxis: { type:'category', data:['待审','已通过','待修','进行中','已完成'],
        axisLabel:{ color:'rgba(255,255,255,0.5)', fontSize:10, interval:0 },
        axisLine:{ lineStyle:{ color:'rgba(255,255,255,0.1)' } }
      },
      yAxis: { type:'value', minInterval:1, splitLine:{ lineStyle:{ color:'rgba(255,255,255,0.04)' } }, axisLabel:{ color:'rgba(255,255,255,0.4)' } },
      series: [{
        type:'bar', barWidth:28,
        data: [
          { value: stats.value.pendingTopicCount||0, itemStyle:{ color:'#fbbf24' } },
          { value: stats.value.topicApproved||0, itemStyle:{ color:'#4ade80' } },
          { value: stats.value.pendingMaintenanceCount||0, itemStyle:{ color:'#f87171' } },
          { value: stats.value.inProgressMaintenanceCount||0, itemStyle:{ color:'#22d3ee' } },
          { value: stats.value.completedMaintenanceCount||0, itemStyle:{ color:'#818cf8' } }
        ],
        label: { show:true, position:'top', color:'rgba(255,255,255,0.5)', fontSize:11 }
      }]
    })
    charts.push(c)
  }

  if (visitTrendRef.value && trendData.value) {
    const c = echarts.init(visitTrendRef.value!)
    const days = trendData.value.labels ?? []
    c.setOption({ ...base, tooltip:{ trigger:'axis' },
      legend: { data:['学生','教师'], textStyle:{ color:'rgba(255,255,255,0.5)', fontSize:11 } },
      grid: { left:'6%', right:'4%', bottom:'8%', containLabel:true },
      xAxis: { type:'category', data:days, axisLabel:{ color:'rgba(255,255,255,0.4)' }, axisLine:{ lineStyle:{ color:'rgba(255,255,255,0.1)' } } },
      yAxis: { type:'value', minInterval:1, splitLine:{ lineStyle:{ color:'rgba(255,255,255,0.04)' } }, axisLabel:{ color:'rgba(255,255,255,0.4)' } },
      series: [
        { name:'学生', type:'line', smooth:true, symbol:'circle', symbolSize:5, data:trendData.value.studentVisits??[], lineStyle:{ color:'#818cf8', width:2 }, itemStyle:{ color:'#818cf8' }, areaStyle:{ color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(99,102,241,0.2)'},{offset:1,color:'rgba(99,102,241,0)'}]) } },
        { name:'教师', type:'line', smooth:true, symbol:'circle', symbolSize:5, data:trendData.value.teacherVisits??[], lineStyle:{ color:'#4ade80', width:2 }, itemStyle:{ color:'#4ade80' }, areaStyle:{ color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(16,185,129,0.2)'},{offset:1,color:'rgba(16,185,129,0)'}]) } }
      ]
    })
    charts.push(c)
  }

  if (topicTrendRef.value && trendData.value) {
    const c = echarts.init(topicTrendRef.value!)
    const days = trendData.value.labels ?? []
    c.setOption({ ...base, tooltip:{ trigger:'axis' },
      legend: { data:['课题','预约'], textStyle:{ color:'rgba(255,255,255,0.5)', fontSize:11 } },
      grid: { left:'6%', right:'4%', bottom:'8%', containLabel:true },
      xAxis: { type:'category', data:days, axisLabel:{ color:'rgba(255,255,255,0.4)' }, axisLine:{ lineStyle:{ color:'rgba(255,255,255,0.1)' } } },
      yAxis: { type:'value', minInterval:1, splitLine:{ lineStyle:{ color:'rgba(255,255,255,0.04)' } }, axisLabel:{ color:'rgba(255,255,255,0.4)' } },
      series: [
        { name:'课题', type:'bar', barWidth:18, data:trendData.value.topicTrend??[], itemStyle:{ color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#f472b6'},{offset:1,color:'#f9a8d4'}]), borderRadius:[3,3,0,0] } },
        { name:'预约', type:'bar', barWidth:18, data:trendData.value.reservationTrend??[], itemStyle:{ color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#22d3ee'},{offset:1,color:'#67e8f9'}]), borderRadius:[3,3,0,0] } }
      ]
    })
    charts.push(c)
  }

  const resize = () => charts.forEach(c => c?.resize())
  window.addEventListener('resize', resize)
}

function updateTime() { currentTime.value = new Date().toLocaleString('zh-CN', { hour12: false }) }

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  fetchData()
})

onUnmounted(() => {
  clearInterval(timeInterval)
  charts.forEach(c => c?.dispose())
  charts = []
})
</script>

<style scoped lang="scss">
.data-screen { min-height:100%; position:relative; overflow:hidden; background:#0a0a1a; color:#e2e8f0; font-family:'Inter',system-ui,sans-serif; }
.bg-canvas { position:fixed; inset:0; pointer-events:none; overflow:hidden; z-index:0; }
.bg-orb { position:absolute; border-radius:50%; filter:blur(80px); animation:orbFloat 14s ease-in-out infinite; }
.bg-orb-1 { width:500px; height:500px; background:rgba(99,102,241,0.08); top:-120px; left:-80px; }
.bg-orb-2 { width:400px; height:400px; background:rgba(6,182,212,0.06); bottom:-100px; right:-60px; animation-delay:-5s; }
.bg-orb-3 { width:350px; height:350px; background:rgba(244,114,182,0.05); top:40%; left:40%; animation-delay:-9s; }
@keyframes orbFloat { 0%,100% { transform:translate(0,0) scale(1); } 25% { transform:translate(50px,-40px) scale(1.06); } 50% { transform:translate(-30px,30px) scale(0.94); } 75% { transform:translate(40px,50px) scale(1.03); } }
.bg-grid { position:absolute; inset:0; background-image:linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.015) 1px,transparent 1px); background-size:40px 40px; }
.screen-container { position:relative; z-index:1; padding:20px 24px; max-width:1600px; margin:0 auto; }
.screen-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; animation:fadeIn .5s ease-out; }
.header-left { display:flex; align-items:center; gap:14px; }
.header-badge { display:flex; align-items:center; gap:6px; background:rgba(6,182,212,0.1); border:1px solid rgba(6,182,212,0.2); border-radius:6px; padding:4px 10px; font-size:11px; font-weight:600; color:#22d3ee; }
.live-dot { width:6px; height:6px; border-radius:50%; background:#22d3ee; animation:livePulse 1.5s ease-in-out infinite; }
@keyframes livePulse { 0%,100% { opacity:1; box-shadow:0 0 4px #22d3ee; } 50% { opacity:.4; box-shadow:0 0 8px #22d3ee; } }
.screen-title { display:flex; align-items:center; gap:10px; font-size:22px; font-weight:700; background:linear-gradient(135deg,#e2e8f0,#94a3b8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.header-right { display:flex; align-items:center; gap:12px; }
.time-display { display:flex; align-items:center; gap:6px; font-size:13px; color:rgba(255,255,255,0.5); font-variant-numeric:tabular-nums; }
.refresh-btn { display:flex; align-items:center; gap:6px; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:7px 14px; font-size:12px; color:rgba(255,255,255,0.6); cursor:pointer; transition:all .2s; }
.refresh-btn:hover { background:rgba(6,182,212,0.12); border-color:rgba(6,182,212,0.25); color:#22d3ee; }
.refreshing .refresh-icon { animation:spin 1s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }
.loading-state { display:flex; flex-direction:column; align-items:center; gap:16px; padding:80px 0; color:rgba(255,255,255,0.4); }
.loader { width:32px; height:32px; border:2px solid rgba(255,255,255,0.1); border-top-color:#22d3ee; border-radius:50%; animation:spin .8s linear infinite; }
.metrics-row { display:grid; grid-template-columns:repeat(6,1fr); gap:12px; margin-bottom:14px; animation:fadeIn .5s ease-out; }
.metrics-row.sm { grid-template-columns:repeat(8,1fr); }
.metric-card { position:relative; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:16px 14px; overflow:hidden; transition:all .25s; }
.metric-card:hover { border-color:rgba(6,182,212,0.2); transform:translateY(-2px); background:rgba(255,255,255,0.05); }
.metric-card.sm { padding:12px 14px; display:flex; align-items:center; gap:12px; }
.metric-icon-wrap { width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; margin-bottom:10px; }
.metric-icon-wrap.sm { width:30px; height:30px; margin-bottom:0; flex-shrink:0; border-radius:8px; }
.metric-label { font-size:11px; color:rgba(255,255,255,0.45); font-weight:500; margin-bottom:4px; }
.metric-value { font-size:24px; font-weight:700; background:linear-gradient(135deg,#fff,#94a3b8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:6px; }
.metric-value.sm { font-size:17px; margin-bottom:0; }
.metric-footer { display:flex; gap:8px; flex-wrap:wrap; }
.metric-tag { display:flex; align-items:center; gap:3px; font-size:10px; padding:2px 7px; border-radius:4px; font-weight:500; background:rgba(255,255,255,0.04); }
.metric-dot { width:5px; height:5px; border-radius:50%; flex-shrink:0; }
.charts-main { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:14px; animation:fadeIn .5s ease-out .1s both; }
.charts-trend { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:14px; animation:fadeIn .5s ease-out .15s both; }
.chart-panel { background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:14px; }
.panel-header { display:flex; align-items:center; gap:7px; font-size:12px; font-weight:600; color:rgba(255,255,255,0.65); margin-bottom:10px; }
.chart-container { width:100%; height:210px; }
.chart-container.lg { height:240px; }
.bottom-section { display:grid; grid-template-columns:1.7fr 1fr; gap:14px; animation:fadeIn .5s ease-out .2s both; }
.bottom-panel { background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:16px; }
.table-wrap { overflow-x:auto; max-height:360px; overflow-y:auto; }
.screen-table { width:100%; border-collapse:collapse; font-size:12px; }
.screen-table th { text-align:left; padding:7px 10px; color:rgba(255,255,255,0.3); font-weight:500; border-bottom:1px solid rgba(255,255,255,0.05); font-size:11px; position:sticky; top:0; background:#0f0f2a; z-index:1; }
.screen-table td { padding:6px 10px; border-bottom:1px solid rgba(255,255,255,0.03); color:rgba(255,255,255,0.55); }
.screen-table tr:hover td { background:rgba(255,255,255,0.03); }
.cell-primary { color:rgba(255,255,255,0.8); font-weight:500; }
.cell-value { color:#22d3ee; font-weight:600; font-variant-numeric:tabular-nums; }
.cell-desc { font-size:11px; color:rgba(255,255,255,0.25); }
.badge-cat { display:inline-block; padding:2px 10px; border-radius:4px; font-size:11px; font-weight:500; }
.summary-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.summary-item { display:flex; align-items:center; gap:9px; padding:9px 11px; background:rgba(255,255,255,0.02); border-radius:8px; border:1px solid rgba(255,255,255,0.04); }
.summary-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
.summary-info { display:flex; flex-direction:column; gap:2px; }
.summary-label { font-size:11px; color:rgba(255,255,255,0.35); }
.summary-value { font-size:15px; font-weight:700; color:rgba(255,255,255,0.85); }
.health-bar-wrap { padding-top:8px; border-top:1px solid rgba(255,255,255,0.05); }
.health-bar { width:100%; height:10px; background:rgba(255,255,255,0.06); border-radius:5px; overflow:hidden; }
.health-fill { height:100%; border-radius:5px; background:linear-gradient(90deg,#22d3ee,#4ade80); transition:width 1s ease-out; position:relative; }
.health-label { position:absolute; right:4px; top:-1px; font-size:9px; font-weight:600; color:#fff; }
@keyframes fadeIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
@media(max-width:1200px) { .metrics-row { grid-template-columns:repeat(3,1fr); } .metrics-row.sm { grid-template-columns:repeat(4,1fr); } .charts-main { grid-template-columns:repeat(2,1fr); } .charts-trend { grid-template-columns:1fr; } .bottom-section { grid-template-columns:1fr; } }
@media(max-width:768px) { .metrics-row { grid-template-columns:repeat(2,1fr); } .metrics-row.sm { grid-template-columns:repeat(2,1fr); } .charts-main { grid-template-columns:1fr; } }
</style>

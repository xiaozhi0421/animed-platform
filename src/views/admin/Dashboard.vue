<template>
  <div class="dashboard page-container">
    <div class="welcome-banner">
      <div class="banner-particles">
        <span v-for="i in 12" :key="i" class="bp" :style="{left: (i*8)+'%', animationDelay: i*0.3+'s'}"></span>
      </div>
      <div class="banner-content">
        <div class="banner-text">
          <h2>平台管理概览</h2>
          <p>校园数据实时监控，高效管理运营</p>
        </div>
      </div>
    </div>
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6" v-for="(stat, idx) in stats" :key="idx">
        <div class="stat-card" :style="{'animation-delay': idx * 0.1 + 's'}">
          <div class="stat-icon" :style="{background: stat.gradient}">
            <el-icon><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header><span class="card-title">平台访问趋势</span></template>
          <div v-if="trendLoading" class="chart-skeleton"></div>
          <div v-else ref="chartRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="quick-card">
          <template #header><span class="card-title">快捷入口</span></template>
          <div class="quick-grid">
            <div class="quick-item" @click="$router.push('/admin/users')">
              <el-icon :size="28" color="#e94560"><User /></el-icon>
              <span>用户管理</span>
            </div>
            <div class="quick-item" @click="$router.push('/admin/system')">
              <el-icon :size="28" color="#e6a23c"><Setting /></el-icon>
              <span>系统管理</span>
            </div>
            <div class="quick-item" @click="$router.push('/admin/logs')">
              <el-icon :size="28" color="#67c23a"><Document /></el-icon>
              <span>日志管理</span>
            </div>
            <div class="quick-item" @click="$router.push('/admin/lab-management')">
              <el-icon :size="28" color="#0ea5e9"><OfficeBuilding /></el-icon>
              <span>实验室管理</span>
            </div>
            <div class="quick-item" @click="$router.push('/admin/lab-equipment')">
              <el-icon :size="28" color="#6366f1"><Monitor /></el-icon>
              <span>设备管理</span>
            </div>
            <div class="quick-item" @click="$router.push('/admin/lab-reservations')">
              <el-icon :size="28" color="#f59e0b"><Calendar /></el-icon>
              <span>预约审批</span>
            </div>
            <div class="quick-item" @click="$router.push('/admin/submissions')">
              <el-icon :size="28" color="#10b981"><EditPen /></el-icon>
              <span>课题管理</span>
            </div>
            <div class="quick-item" @click="$router.push('/admin/lab-maintenance')">
              <el-icon :size="28" color="#ef4444"><Tools /></el-icon>
              <span>维修管理</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Calendar, Tools, OfficeBuilding, Monitor, EditPen } from '@element-plus/icons-vue'
import { adminApi } from '@/api'
import * as echarts from 'echarts'

const chartRef = ref<HTMLElement>()
const trendLoading = ref(true)

const stats = ref([
  { label: '学生总数', value: 0, icon: 'User', gradient: 'linear-gradient(135deg, #6366f1, #4f46e5)' },
  { label: '教师总数', value: 0, icon: 'UserFilled', gradient: 'linear-gradient(135deg, #0ea5e9, #0284c7)' },
  { label: '待审批预约', value: 0, icon: 'Calendar', gradient: 'linear-gradient(135deg, #e6a23c, #cf8e24)' },
  { label: '未维修数', value: 0, icon: 'Tools', gradient: 'linear-gradient(135deg, #e94560, #c23152)' }
])

async function fetchStats() {
  try {
    const res: any = await adminApi.getStats()
    const d = res.data || res
    stats.value[0].value = d.studentCount ?? d.totalStudents ?? 0
    stats.value[1].value = d.teacherCount ?? d.totalTeachers ?? 0
    stats.value[2].value = d.pendingReservationCount ?? 0
    stats.value[3].value = d.pendingMaintenanceCount ?? 0
  } catch (e) {}
}

async function fetchTrend() {
  try {
    trendLoading.value = true
    const res: any = await adminApi.getTrend()
    const d = res.data || res
    trendData.value = d
  } catch (e) {
    trendData.value = null
  } finally {
    trendLoading.value = false
    await nextTick()
    if (chartRef.value && trendData.value) initChart()
  }
}

const trendData = ref<any>(null)

function initChart() {
  const chart = echarts.init(chartRef.value!)
  const campusData = trendData.value?.studentVisits ?? trendData.value?.campusValues ?? trendData.value?.values ?? [0,0,0,0,0,0,0]
  const teacherData = trendData.value?.teacherVisits ?? [0,0,0,0,0,0,0]
  const days = trendData.value?.labels ?? ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['学生访问', '教师访问'], textStyle: { color: '#fff' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: days, boundaryGap: false },
    yAxis: { type: 'value' },
    series: [
      {
        name: '学生访问', type: 'line', smooth: true, data: campusData,
        lineStyle: { color: '#6366f1' }, itemStyle: { color: '#6366f1' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1, [{offset:0,color:'rgba(99,102,241,0.2)'},{offset:1,color:'rgba(99,102,241,0)'}]) },
        animationDuration: 1500, animationEasing: 'cubicInOut'
      },
      {
        name: '教师访问', type: 'line', smooth: true, data: teacherData,
        lineStyle: { color: '#f59e0b' }, itemStyle: { color: '#f59e0b' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1, [{offset:0,color:'rgba(245,158,11,0.2)'},{offset:1,color:'rgba(245,158,11,0)'}]) },
        animationDuration: 1500, animationEasing: 'cubicInOut'
      }
    ]
  })
  window.addEventListener('resize', () => chart.resize())
}

onMounted(async () => {
  await fetchStats()
  await fetchTrend()
})
</script>

<style scoped lang="scss">
.welcome-banner {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border-radius: 16px; padding: 28px 32px; margin-bottom: 20px; color: #fff;
  animation: fadeInUp 0.5s ease-out; position: relative; overflow: hidden;
  .banner-particles { position: absolute; inset: 0; pointer-events: none; }
  .bp {
    position: absolute; bottom: -10px; width: 4px; height: 4px; border-radius: 50%;
    background: rgba(255,255,255,0.3); animation: bpFloat 4s ease-in-out infinite;
  }
  @keyframes bpFloat {
    0%,100% { transform: translateY(0) scale(1); opacity: 0; }
    20% { opacity: 1; } 80% { opacity: 1; }
    50% { transform: translateY(-60px) scale(1.5); }
  }
  .banner-text h2 { font-size: 22px; margin-bottom: 6px; }
  .banner-text p { opacity: 0.7; font-size: 14px; }
}
.stat-card {
  background: rgba(255,255,255,0.06); border-radius: 12px; padding: 20px;
  border: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(4px);
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
  animation: fadeInUp 0.5s ease-out both;
  display: flex; align-items: center; gap: 16px;
  &:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
  .stat-icon {
    width: 48px; height: 48px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 22px; flex-shrink: 0; transition: transform 0.3s;
  }
  &:hover .stat-icon { transform: scale(1.1) rotate(-5deg); }
  .stat-value { font-size: 24px; font-weight: 700; color: rgba(255,255,255,0.95); }
  .stat-label { font-size: 13px; color: rgba(255,255,255,0.6); margin-top: 2px; }
}
.chart-card, .quick-card {
  border-radius: 12px; background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(4px);
  animation: fadeInUp 0.5s ease-out 0.2s both;
}
.chart-skeleton {
  height: 350px; background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 8px;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
.card-title { font-weight: 600; font-size: 15px; color: rgba(255,255,255,0.9); }
.quick-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
  .quick-item {
    display: flex; flex-direction: column; align-items: center; gap: 8px;
    padding: 20px 12px; border-radius: 12px; background: rgba(255,255,255,0.04); cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1); border: 1px solid rgba(255,255,255,0.06);
    span { font-size: 13px; color: rgba(255,255,255,0.8); }
    &:hover { background: rgba(255,255,255,0.1); transform: translateY(-4px) scale(1.02); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
  }
}
@keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>

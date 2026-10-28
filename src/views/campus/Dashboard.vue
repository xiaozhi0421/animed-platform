<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-inner">

      <!-- ===== Hero Section ===== -->
      <div class="hero-section">
        <div class="hero-tag">
          <el-icon size="14"><Monitor /></el-icon>
          <span v-if="userStore.userRole === 'campus_student'">学生端</span>
          <span v-else-if="userStore.userRole === 'campus_teacher'">教师端</span>
          <span v-else>管理端</span>
        </div>
        <h1 class="hero-title">
          <span class="hero-greeting">欢迎回来</span>
          <span class="hero-gradient">{{ userStore.userName || '用户' }}</span>
        </h1>
        <p class="hero-desc">
          <span v-if="userStore.userRole === 'campus_student'">查看你的学习进度、课题动态和数据管理情况</span>
          <span v-else-if="userStore.userRole === 'campus_teacher'">查看你的教学概览和学生课题动态</span>
          <span v-else>管理系统运行状态，查看平台数据概况</span>
        </p>
      </div>

      <!-- ===== Stats Row ===== -->
      <div class="section-label">数据概况</div>
      <div class="stats-grid">
        <div v-for="(stat, idx) in currentStats" :key="idx" class="stat-card">
          <div class="stat-icon-wrap" :style="{ background: stat.gradient }">
            <el-icon><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-body">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>

      <!-- ===== Content Grid ===== -->
      <div class="content-grid">
        <!-- Main content -->
        <div class="content-main">

          <!-- Student: new sections -->
          <template v-if="userStore.userRole === 'campus_student'">

            <div class="section-label">代办事项</div>
            <div class="todo-grid">
              <!-- pending topics -->
              <div class="todo-card">
                <div class="todo-header">
                  <span class="todo-title">待完成课题</span>
                  <el-tag size="small" type="warning" effect="dark">{{ pendingTopics.length }}</el-tag>
                </div>
                <div class="todo-body">
                  <div v-if="pendingTopics.length === 0" class="todo-empty">暂无待完成课题</div>
                  <div v-else v-for="(t, i) in pendingTopics.slice(0, 3)" :key="i" class="todo-item">
                    <span class="todo-dot warning"></span>
                    <span class="todo-text">{{ t.title }}</span>
                  </div>
                </div>
                <div class="todo-footer">
                  <el-button size="small" text @click="router.push('/campus/submission')">前往提交 <el-icon><ArrowRight /></el-icon></el-button>
                </div>
              </div>

              <!-- pending homework -->
              <div class="todo-card">
                <div class="todo-header">
                  <span class="todo-title">待提交作业</span>
                  <el-tag size="small" type="primary" effect="dark">{{ pendingHomework.length }}</el-tag>
                </div>
                <div class="todo-body">
                  <div v-if="pendingHomework.length === 0" class="todo-empty">暂无待提交作业</div>
                  <div v-else v-for="(h, i) in pendingHomework.slice(0, 3)" :key="i" class="todo-item">
                    <span class="todo-dot primary"></span>
                    <span class="todo-class">[{{ h.className || '' }}]</span>
                    <span class="todo-text">{{ h.title || '' }}</span>
                  </div>
                </div>
                <div class="todo-footer">
                  <el-button size="small" text @click="router.push('/campus/my-class')">前往查看 <el-icon><ArrowRight /></el-icon></el-button>
                </div>
              </div>

              <!-- active sign-ins -->
              <div class="todo-card">
                <div class="todo-header">
                  <span class="todo-title">进行中签到</span>
                  <el-tag size="small" type="success" effect="dark">{{ activeSignIns.length }}</el-tag>
                </div>
                <div class="todo-body">
                  <div v-if="activeSignIns.length === 0" class="todo-empty">暂无进行中签到</div>
                  <div v-else v-for="(s, i) in activeSignIns.slice(0, 3)" :key="i" class="todo-item">
                    <span class="todo-dot success"></span>
                    <span class="todo-class">[{{ s.className || '' }}]</span>
                    <span class="todo-text">{{ s.title || '' }}</span>
                  </div>
                </div>
                <div class="todo-footer">
                  <el-button size="small" text @click="router.push('/campus/my-class')">前往签到 <el-icon><ArrowRight /></el-icon></el-button>
                </div>
              </div>
            </div>

            <!-- Reservations -->
            <div class="section-label" style="margin-top:24px;">实验仪器预约情况</div>
            <div class="reservation-card">
              <div v-if="reservations.length === 0" class="empty-state">暂无预约记录</div>
              <el-table v-else :data="reservations.slice(0, 5)" stripe style="width:100%" size="small">
                <el-table-column prop="equipmentName" label="仪器名称" min-width="120" />
                <el-table-column prop="reserveTime" label="预约时间" min-width="160">
                  <template #default="{ row }">
                    {{ row.reserveDate || row.date }} {{ row.timeSlot || row.time || '' }}
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="statusTagType(row.status)" size="small" effect="dark">
                      {{ statusLabel(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
              <div class="reservation-footer">
                <el-button size="small" text @click="router.push('/campus/my-lab-reservations')">
                  查看全部预约 <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>

            <!-- Available topics -->
            <div class="section-label" style="margin-top:24px;">可选择课题</div>
            <div class="topics-card">
              <div v-if="availableTopics.length === 0" class="empty-state">暂无新课题</div>
              <div v-else v-for="(t, i) in availableTopics.slice(0, 5)" :key="i" class="topic-item">
                <div class="topic-info">
                  <span class="topic-title">{{ t.title }}</span>
                  <span class="topic-teacher">{{ t.teacherName || t.publisherName || '' }}</span>
                </div>
              </div>
              <div class="topics-footer">
                <el-button size="small" text @click="router.push('/campus/submission')">
                  前往选择课题 <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>

          </template>

          <!-- Teacher: new content -->
          <template v-else-if="userStore.userRole === 'campus_teacher'">

            <!-- 实验仪器预约情况 -->
            <div class="section-label">实验仪器预约情况</div>
            <div class="reservation-card">
              <div v-if="teacherReservations.length === 0" class="empty-state">暂无预约记录</div>
              <el-table v-else :data="teacherReservations.slice(0, 5)" stripe style="width:100%" size="small">
                <el-table-column prop="equipmentName" label="仪器名称" min-width="120" />
                <el-table-column prop="reserveTime" label="预约时间" min-width="160">
                  <template #default="{ row }">
                    {{ row.reserveDate || row.date }} {{ row.timeSlot || row.time || '' }}
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="statusTagType(row.status)" size="small" effect="dark">
                      {{ statusLabel(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
              <div class="reservation-footer">
                <el-button size="small" text @click="router.push('/campus/my-lab-reservations')">
                  查看全部预约 <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>

            <!-- 课题监控 -->
            <div class="section-label" style="margin-top:24px;">我的课题监控</div>
            <div class="topics-card">
              <div v-if="myTopics.length === 0" class="empty-state">暂无发布的课题</div>
              <div v-else v-for="(tp, i) in myTopics.slice(0, 5)" :key="i" class="topic-item">
                <div class="topic-info">
                  <span class="topic-title">{{ tp.title }}</span>
                  <span class="topic-teacher">确认人数: {{ tp.confirmedCount ?? tp.studentCount ?? 0 }}</span>
                </div>
              </div>
              <div class="topics-footer">
                <el-button size="small" text @click="router.push('/campus/submission')">
                  管理课题 <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>

            <!-- 待审课题 -->
            <div class="section-label" style="margin-top:24px;">待审课题</div>
            <div class="reservation-card">
              <div v-if="pendingSubmissions.length === 0" class="empty-state">暂无待审课题</div>
              <el-table v-else :data="pendingSubmissions.slice(0, 5)" stripe style="width:100%" size="small">
                <el-table-column prop="topicTitle" label="课题名称" min-width="120" />
                <el-table-column prop="studentName" label="提交学生" width="100" />
                <el-table-column prop="submitTime" label="提交时间" min-width="140">
                  <template #default="{ row }">{{ row.submitTime || row.createdAt || '' }}</template>
                </el-table-column>
              </el-table>
              <div class="reservation-footer">
                <el-button size="small" text @click="router.push('/campus/submission')">
                  前往审阅 <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>

            <!-- 学生签到 -->
            <div class="section-label" style="margin-top:24px;">学生签到情况</div>
            <div class="signin-card">
              <div v-if="signInList.length === 0" class="empty-state">暂无签到数据</div>
              <div v-else class="signin-list">
                <div v-for="(si, idx) in signInList.slice(0, 3)" :key="idx" class="signin-item">
                  <div class="signin-chart-wrap">
                    <svg viewBox="0 0 80 80" class="donut-chart">
                      <circle cx="40" cy="40" r="32" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8" />
                      <circle cx="40" cy="40" r="32" fill="none" stroke="#10b981" stroke-width="8"
                        :stroke-dasharray="(2 * Math.PI * 32 * (si.percent || 0) / 100) + ', ' + (2 * Math.PI * 32)" stroke-linecap="round"
                        transform="rotate(-90 40 40)" style="transition: stroke-dasharray 0.6s ease" />
                    </svg>
                    <div class="donut-label-sm">
                      <span class="donut-value-sm">{{ si.percent || 0 }}%</span>
                    </div>
                  </div>
                  <div class="signin-info">
                    <div class="signin-title">{{ si.title }}</div>
                    <div class="signin-stats">
                      <span class="signin-stat-item">
                        <span class="signin-dot signed"></span>{{ si.signed }}
                      </span>
                      <span class="signin-stat-item">
                        <span class="signin-dot unsigned"></span>{{ si.total - si.signed }}
                      </span>
                      <span class="signin-stat-item">
                        <span class="signin-dot total"></span>{{ si.total }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="reservation-footer" style="margin-top:12px;">
                <el-button size="small" text @click="router.push('/campus/my-class')">
                  查看全部签到 <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>

          </template>

          <!-- Admin: keep existing chart -->
          <template v-else>
            <div class="section-label">用户登录趋势</div>
            <div class="chart-card">
              <div v-if="trendLoading" class="chart-skeleton" />
              <div v-else ref="chartRef" class="chart-container" />
            </div>
          </template>

        </div>

        <!-- Sidebar: Quick Actions -->
        <div class="content-side">
          <div class="section-label">快捷操作</div>
          <div class="quick-grid">
            <div v-for="(item, idx) in quickActions" :key="idx" class="quick-item" @click="router.push(item.path)">
              <div class="quick-icon" :style="{ background: item.bg }">
                <el-icon :size="20"><component :is="item.icon" /></el-icon>
              </div>
              <span class="quick-label">{{ item.label }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowRight, Monitor, Aim } from '@element-plus/icons-vue'
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'
import { dashboardApi, adminApi, submissionApi, labApi, classApi } from '@/api'
import * as echarts from 'echarts'
import { useRouter } from 'vue-router'

const router = useRouter()
const userStore = useUserStore()
const chartRef = ref<HTMLDivElement | null>(null)
const trendLoading = ref(false)
let chartInstance: echarts.ECharts | null = null

// === Stats ===
const studentStats = reactive([
  { label: '数据集', value: '0', icon: 'DataBoard', gradient: 'linear-gradient(135deg, #6366f1, #818cf8)' },
  { label: '分析结果', value: '0', icon: 'DataAnalysis', gradient: 'linear-gradient(135deg, #10b981, #34d399)' },
  { label: '我的班级', value: '0', icon: 'UserFilled', gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)' },
  { label: '未完成课题', value: '0', icon: 'EditPen', gradient: 'linear-gradient(135deg, #ef4444, #f87171)' },
])

const teacherStats = reactive([
  { label: '学生人数', value: '36', icon: 'UserFilled', gradient: 'linear-gradient(135deg, #6366f1, #818cf8)' },
  { label: '数据集数', value: '45', icon: 'DataBoard', gradient: 'linear-gradient(135deg, #10b981, #34d399)' },
  { label: '待审课题', value: '5', icon: 'EditPen', gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)' },
  { label: '我的班级', value: '0', icon: 'School', gradient: 'linear-gradient(135deg, #8b5cf6, #a78bfa)' },
])

const adminStats = reactive([
  { label: '用户总数', value: '156', icon: 'UserFilled', gradient: 'linear-gradient(135deg, #6366f1, #818cf8)' },
  { label: '数据总量', value: '1.2TB', icon: 'DataBoard', gradient: 'linear-gradient(135deg, #10b981, #34d399)' },
  { label: '课题数量', value: '28', icon: 'EditPen', gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)' },
  { label: '待处理', value: '7', icon: 'WarningFilled', gradient: 'linear-gradient(135deg, #ef4444, #f87171)' },
])

const currentStats = computed(() => {
  if (userStore.userRole === 'campus_admin') return adminStats
  if (userStore.userRole === 'campus_teacher') return teacherStats
  return studentStats
})

const studentActions = [
  { label: '数据采集', icon: 'Upload', path: '/campus/data/upload', bg: '#6366f1' },
  { label: '数据分析', icon: 'TrendCharts', path: '/campus/analysis', bg: '#10b981' },
  { label: '数据清洗', icon: 'Filter', path: '/campus/data/clean', bg: '#f59e0b' },
  { label: '数据挖掘', icon: 'Aim', path: '/campus/data/mining', bg: '#8b5cf6' },
  { label: '数据可视化', icon: 'TrendCharts', path: '/campus/data/visualization', bg: '#8b5cf6' },
  { label: '知识库', icon: 'Notebook', path: '/campus/knowledge', bg: '#06b6d4' },
  { label: '实验仪器', icon: 'Monitor', path: '/campus/lab-equipment', bg: '#ec4899' },
  { label: '课题提交', icon: 'EditPen', path: '/campus/submission', bg: '#ef4444' },
]

const teacherActions = [
  { label: '课题审阅', icon: 'EditPen', path: '/campus/submission', bg: '#6366f1' },
  { label: '我的班级', icon: 'UserFilled', path: '/campus/my-class', bg: '#10b981' },
  { label: '数据分析', icon: 'TrendCharts', path: '/campus/analysis', bg: '#f59e0b' },
  { label: '知识库', icon: 'Notebook', path: '/campus/knowledge', bg: '#06b6d4' },
  { label: 'AI助手', icon: 'MagicStick', path: '/campus/ai-chat', bg: '#8b5cf6' },
  { label: '实验仪器', icon: 'Monitor', path: '/campus/lab-equipment', bg: '#ec4899' },
  { label: '数据管理', icon: 'DataBoard', path: '/campus/data', bg: '#f97316' },
  { label: '师生沟通', icon: 'ChatDotSquare', path: '/campus/chat', bg: '#ef4444' },
]

const adminActions = [
  { label: '用户管理', icon: 'UserFilled', path: '/campus/student-manage', bg: '#6366f1' },
  { label: '数据分析', icon: 'TrendCharts', path: '/campus/analysis', bg: '#10b981' },
  { label: '日志管理', icon: 'Document', path: '/campus/log', bg: '#f59e0b' },
  { label: '数据大屏', icon: 'DataBoard', path: '/campus/data-screen', bg: '#ef4444' },
]

const quickActions = computed(() => {
  if (userStore.userRole === 'campus_admin') return adminActions
  if (userStore.userRole === 'campus_teacher') return teacherActions
  return studentActions
})

// === Student-specific data ===
const pendingTopics = ref<any[]>([])
const pendingHomework = ref<any[]>([])
const activeSignIns = ref<any[]>([])
const reservations = ref<any[]>([])
const availableTopics = ref<any[]>([])

// === Teacher-specific data ===
const teacherReservations = ref<any[]>([])
const myTopics = ref<any[]>([])
const pendingSubmissions = ref<any[]>([])
const signInList = ref<any[]>([])

function statusTagType(status: string | number): string {
  if (status === 0 || status === 'PENDING' || status === 'pending' || status === '待审批' || status === '待审核') return 'warning'
  if (status === 1 || status === 'APPROVED' || status === 'approved' || status === '已通过' || status === '通过') return 'success'
  if (status === 2 || status === 'REJECTED' || status === 'rejected' || status === '已拒绝' || status === '拒绝') return 'danger'
  if (status === 3 || status === 'IN_USE' || status === 'in_use' || status === '使用中') return 'primary'
  return 'info'
}

function statusLabel(status: string | number): string {
  if (status === 0 || status === 'PENDING' || status === 'pending') return '待审批'
  if (status === 1 || status === 'APPROVED' || status === 'approved') return '已通过'
  if (status === 2 || status === 'REJECTED' || status === 'rejected') return '已拒绝'
  if (status === 3 || status === 'IN_USE' || status === 'in_use') return '使用中'
  if (status === 4 || status === 'COMPLETED' || status === 'completed') return '已完成'
  return String(status)
}

async function fetchStudentTodos() {
  try {
    const topicRes = await submissionApi.getConfirmedTopics()
    pendingTopics.value = Array.isArray(topicRes.data) ? topicRes.data : []
  } catch { pendingTopics.value = [] }

  try {
    const classesRes = await classApi.getStudentClasses()
    const classes = Array.isArray(classesRes.data) ? classesRes.data : []
    const allHomework: any[] = []
    const allSignIns: any[] = []

    for (const cls of classes) {
      try {
        const hwRes = await classApi.getStudentHomeworkList(cls.id)
        const hwList = Array.isArray(hwRes.data) ? hwRes.data : []
        for (const h of hwList) {
          if (h.status !== '已批改' && h.status !== 2) {
            allHomework.push({ ...h, className: cls.className, _title: h.title || h.homeworkName || h.name || '', _display: (h.title || h.homeworkName || h.name || '') + ' [' + cls.className + ']' })
          }
        }
      } catch {}

      try {
        const siRes = await classApi.getSignInList(cls.id)
        const siList = Array.isArray(siRes.data) ? siRes.data : []
        for (const s of siList) {
          // 数值状态：奇数为进行中，1=未签到 3=已签到
          const sn = Number(s.status)
          if (!isNaN(sn) && sn % 2 === 1) {
            allSignIns.push({ ...s, className: cls.className, _title: s.title || s.signInName || s.name || '' })
          }
        }
      } catch {}
    }

    pendingHomework.value = allHomework
    activeSignIns.value = allSignIns
  } catch {
    pendingHomework.value = []
    activeSignIns.value = []
  }

  try {
    const resRes = await labApi.getMyReservations()
    const all = Array.isArray(resRes.data) ? resRes.data : []
    reservations.value = all.filter((r: any) => {
      const s = r.status
      return s !== 4 && s !== '已完成' && s !== 2 && s !== '已拒绝'
    })
  } catch { reservations.value = [] }

  try {
    const availRes = await submissionApi.getAvailableTopics()
    availableTopics.value = Array.isArray(availRes.data) ? availRes.data : []
  } catch { availableTopics.value = [] }
}

async function fetchStats() {
  if (userStore.userRole === 'campus_student') {
    try {
      const res = await dashboardApi.getStudentStats()
      const d: any = res.data
      if (d) {
        studentStats[0].value = String(d.datasetCount ?? 0)
        studentStats[1].value = String(d.analysisResultCount ?? 0)
        studentStats[2].value = String(d.classCount ?? 0)
        studentStats[3].value = String(d.pendingTopicCount ?? 0)
      }
    } catch {}
  } else if (userStore.userRole === 'campus_teacher') {
    try {
      const res = await dashboardApi.getTeacherStats()
      const d: any = res.data
      if (d) {
        teacherStats[0].value = String(d.studentCount ?? '0')
        teacherStats[1].value = String(d.datasetCount ?? '0')
        teacherStats[2].value = String(d.pendingTopicCount ?? '0')
      }
    } catch {}
    // Fetch teacher's class count from real data
    try {
      const classesRes = await classApi.getTeacherClasses()
      const classes = Array.isArray(classesRes.data) ? classesRes.data : []
      teacherStats[3].value = String(classes.length)
    } catch { teacherStats[3].value = '0' }
  } else {
    try {
      const res = await dashboardApi.getCampusAdminStats()
      const d: any = res.data?.data || res.data
      if (d) {
        adminStats[0].value = String(d.userCount ?? d.totalUsers ?? '156')
        adminStats[1].value = String(d.dataCount ?? d.totalData ?? '1.2TB')
        adminStats[2].value = String(d.topicCount ?? '28')
        adminStats[3].value = String(d.pendingCount ?? '7')
      }
    } catch {}
  }
}

async function initChart() {
  if (userStore.userRole === 'campus_student') return
  await nextTick()
  if (!chartRef.value) return
  trendLoading.value = true
  try {
    const days = 7
    const res = await dashboardApi.getTrendData({ days })
    const raw = res.data?.data || res.data || []
    const dates: string[] = []
    const vals: number[] = []
    if (Array.isArray(raw)) {
      raw.forEach((r: any) => {
        dates.push(r.date || r.day || '')
        vals.push(r.count || r.value || 0)
      })
    }
    chartInstance = echarts.init(chartRef.value)
    chartInstance.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '3%', bottom: '8%', top: '6%', containLabel: true },
      xAxis: { type: 'category', data: dates.length ? dates : ['暂无数据'], axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }, axisLabel: { color: 'rgba(255,255,255,0.45)', fontSize: 11 } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }, axisLabel: { color: 'rgba(255,255,255,0.45)', fontSize: 11 } },
      series: [{ type: 'line', data: vals.length ? vals : [0], smooth: true, symbol: 'circle', symbolSize: 7, lineStyle: { width: 2, color: '#818cf8' }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(129,140,248,0.3)' }, { offset: 1, color: 'rgba(129,140,248,0)' }]) }, itemStyle: { color: '#818cf8' } }],
    })
  } catch { /* chart empty */ }
  finally { trendLoading.value = false }
}

async function fetchTeacherData() {
  // 实验仪器预约
  try {
    const res = await labApi.getMyReservations()
    const all = Array.isArray(res.data) ? res.data : []
    teacherReservations.value = all.filter((r: any) => {
      const s = r.status
      return s !== 4 && s !== '已完成' && s !== 2 && s !== '已拒绝'
    })
  } catch { teacherReservations.value = [] }

  // 我的课题
  try {
    const res = await submissionApi.getMyTopics()
    myTopics.value = Array.isArray(res.data) ? res.data : []
  } catch { myTopics.value = [] }

  // 待审课题
  try {
    const res = await submissionApi.getTeacherSubmissions()
    const all = Array.isArray(res.data) ? res.data : []
    pendingSubmissions.value = all.filter((s: any) => {
      const st = s.status !== undefined ? s.status : (s.reviewStatus ?? '')
      // Backend status: 0=pending review, 1=approved, 2=rejected
      return st === 0 || st === '0' || st === '' || st === 'pending' || st === '待审核' || st === '未处理'
    })
  } catch { pendingSubmissions.value = [] }
    // Update stats card with real pending count
    teacherStats[2].value = String(pendingSubmissions.value.length)

  // 学生签到 - 获取最新的3条
  const allSignIns: any[] = []
  try {
    const classesRes = await classApi.getTeacherClasses()
    const classes = Array.isArray(classesRes.data) ? classesRes.data : []
    for (const cls of classes) {
      try {
        const siRes = await classApi.getSignInList(cls.id)
        const siList = Array.isArray(siRes.data) ? siRes.data : []
        for (const s of siList) {
          allSignIns.push({ ...s, className: cls.className })
        }
      } catch {}
    }
    // 按时间排序取最新3条
    allSignIns.sort((a: any, b: any) => ((b.createdAt || b.id || '') > (a.createdAt || a.id || '') ? 1 : -1))
    const top3 = allSignIns.slice(0, 3)
    const result: any[] = []
    for (const si of top3) {
      try {
        const recRes = await classApi.getSignInRecords(si.id)
        const records = Array.isArray(recRes.data) ? recRes.data : []
        const signed = records.filter((r: any) => {
          const st = r.result
          return st === '成功' || st === 'SUCCESS' || st === 'success' || st === 1 || st === '1' || st === true
        }).length
        const total = records.length
        result.push({
          ...si,
          signed,
          total,
          percent: total > 0 ? Math.round((signed / total) * 100) : 0
        })
      } catch {
        result.push({ ...si, signed: 0, total: 0, percent: 0 })
      }
    }
    signInList.value = result
  } catch { signInList.value = [] }
}

onMounted(async () => {
  await fetchStats()
  if (userStore.userRole === 'campus_student') {
    await fetchStudentTodos()
    studentStats[3].value = String(pendingTopics.value.length)
  } else if (userStore.userRole === 'campus_teacher') {
    await fetchTeacherData()
  } else {
    initChart()
  }
})

onBeforeUnmount(() => {
  if (chartInstance) { chartInstance.dispose(); chartInstance = null }
})
</script>

<style scoped>
/* === Wrapper === */
.dashboard-wrapper {
  position: relative;
  min-height: calc(100vh - 56px);
}
.dashboard-inner {
  position: relative;
  z-index: 1;
  max-width: 1120px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}

/* === Hero === */
.hero-section {
  text-align: center;
  padding: 32px 0 40px;
}
.hero-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 500;
  color: #a5b4fc;
  background: rgba(99,102,241,0.12);
  border: 1px solid rgba(99,102,241,0.2);
  margin-bottom: 20px;
}
.hero-title {
  font-size: 40px;
  font-weight: 700;
  line-height: 1.15;
  margin: 0 0 12px;
  letter-spacing: -0.02em;
}
.hero-greeting {
  color: #f1f5f9;
  margin-right: 8px;
}
.hero-gradient {
  background: linear-gradient(135deg, #818cf8, #c084fc, #f472b6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-desc {
  font-size: 16px;
  color: rgba(255,255,255,0.45);
  max-width: 480px;
  margin: 0 auto;
  line-height: 1.6;
}

/* === Section Labels === */
.section-label {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255,255,255,0.35);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 12px;
  padding-left: 2px;
}

/* === Stats Grid === */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 32px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  backdrop-filter: blur(6px);
  transition: all 0.2s ease;
}
.stat-card:hover {
  background: rgba(0,0,0,0.3);
  border-color: rgba(255,255,255,0.1);
}
.stat-icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-icon-wrap :deep(.el-icon) {
  font-size: 20px;
  color: #fff;
}
.stat-body {
  flex: 1;
  min-width: 0;
}
.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #f1f5f9;
  line-height: 1.2;
}
.stat-label {
  font-size: 12px;
  color: rgba(255,255,255,0.4);
  margin-top: 2px;
}

/* === Content Grid === */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 16px;
}

/* === TODO Grid (3 cards) === */
.todo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.todo-card {
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}
.todo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.todo-title {
  font-size: 14px;
  font-weight: 600;
  color: #f1f5f9;
}
.todo-body {
  flex: 1;
  min-height: 60px;
}
.todo-empty {
  color: rgba(255,255,255,0.25);
  font-size: 13px;
  padding: 8px 0;
}
.todo-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
  flex-wrap: wrap;
}
.todo-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.todo-dot.warning { background: #f59e0b; }
.todo-dot.primary { background: #6366f1; }
.todo-dot.success { background: #10b981; }
.todo-text {
  font-size: 13px;
  color: rgba(255,255,255,0.65);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.todo-class {
  font-size: 11px;
  color: rgba(255,255,255,0.35);
  flex-shrink: 0;
}
.todo-footer {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.todo-footer :deep(.el-button) {
  color: rgba(255,255,255,0.5);
  font-size: 12px;
}
.todo-footer :deep(.el-button:hover) {
  color: #818cf8;
}

/* === Reservation Card === */
.reservation-card {
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
}
.reservation-card :deep(.el-table) {
  background: transparent;
  color: rgba(255,255,255,0.75);
  font-size: 13px;
}
.reservation-card :deep(.el-table th.el-table__cell) {
  background: rgba(255,255,255,0.04);
  color: rgba(255,255,255,0.45);
  font-size: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.reservation-card :deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(255,255,255,0.04);
  background: transparent;
}
.reservation-card :deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(255,255,255,0.02);
}
.reservation-footer {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.reservation-footer :deep(.el-button) {
  color: rgba(255,255,255,0.5);
  font-size: 12px;
}
.reservation-footer :deep(.el-button:hover) {
  color: #818cf8;
}

/* === Topics Card === */
.topics-card {
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
}
.topic-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.topic-item:last-child {
  border-bottom: none;
}
.topic-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.topic-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255,255,255,0.75);
}
.topic-teacher {
  font-size: 12px;
  color: rgba(255,255,255,0.35);
}
.topics-footer {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.topics-footer :deep(.el-button) {
  color: rgba(255,255,255,0.5);
  font-size: 12px;
}
.topics-footer :deep(.el-button:hover) {
  color: #818cf8;
}

/* === Sign-in Card === */
.signin-card {
  padding: 16px;
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  backdrop-filter: blur(6px);
}
.signin-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.signin-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px;
  background: rgba(0,0,0,0.15);
  border-radius: 10px;
}
.signin-chart-wrap {
  position: relative;
  width: 56px;
  height: 56px;
  flex-shrink: 0;
}
.donut-chart {
  width: 100%;
  height: 100%;
}
.donut-label-sm {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}
.donut-value-sm {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: #10b981;
  line-height: 1;
}
.signin-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}
.signin-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #f1f5f9;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.signin-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.signin-stat-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: rgba(255,255,255,0.55);
}
.signin-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
  display: inline-block;
}
.signin-dot.signed { background: #10b981; }
.signin-dot.unsigned { background: rgba(255,255,255,0.15); }
.signin-dot.total { background: #6366f1; }

/* === Empty State === */
.empty-state {
  text-align: center;
  padding: 24px 0;
  color: rgba(255,255,255,0.25);
  font-size: 14px;
}

/* === Chart (teacher/admin) === */
.chart-card {
  padding: 20px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
}
.chart-container {
  height: 320px;
}
.chart-skeleton {
  height: 320px;
  background: linear-gradient(90deg, rgba(255,255,255,0.02) 25%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.02) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease infinite;
  border-radius: 8px;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* === Quick Actions === */
.quick-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 18px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
}
.quick-item:hover {
  background: rgba(0,0,0,0.3);
  border-color: rgba(255,255,255,0.1);
  transform: translateY(-1px);
}
.quick-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.quick-icon :deep(.el-icon) {
  color: #fff;
}
.quick-label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255,255,255,0.55);
  text-align: center;
}

/* === Responsive === */
@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .content-grid {
    grid-template-columns: 1fr;
  }
  .todo-grid {
    grid-template-columns: 1fr;
  }
  .hero-title {
    font-size: 28px;
  }
  .dashboard-inner {
    padding: 24px 16px 40px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>


import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

NProgress.configure({ showSpinner: false })

const campusRoutes: RouteRecordRaw[] = [
  {
    path: '/campus',
    component: () => import('@/layouts/CampusLayout.vue'),
    meta: { requiresAuth: true, system: 'campus' },
    children: [
      { path: '', redirect: '/campus/dashboard' },
      { path: 'dashboard', component: () => import('@/views/campus/Dashboard.vue'), meta: { title: '首页' } },
      { path: 'data', component: () => import('@/views/campus/DataManage.vue'), meta: { title: '数据管理' } },
      { path: 'data/upload', component: () => import('@/views/campus/DataUpload.vue'), meta: { title: '数据上传' } },
      { path: 'data/clean', component: () => import('@/views/campus/DataClean.vue'), meta: { title: '数据清洗' } },
      { path: 'data/mining', component: () => import('@/views/campus/DataMining.vue'), meta: { title: '数据挖掘' } },
      { path: 'data/visualization', component: () => import('@/views/campus/DataVisualization.vue'), meta: { title: '数据可视化' } },
      { path: 'data/detail/:id', component: () => import('@/views/campus/DataDetail.vue'), meta: { title: '数据集详情' } },
      { path: 'analysis', component: () => import('@/views/campus/Analysis.vue'), meta: { title: '数据分析' } },
      { path: 'analysis/report/:id', component: () => import('@/views/campus/AnalysisReport.vue'), meta: { title: '分析报告' } },
      { path: 'analysis/library', component: () => import('@/views/campus/AnalysisLibrary.vue'), meta: { title: '分析库' } },
      { path: 'ai-chat', component: () => import('@/views/campus/AiChat.vue'), meta: { title: 'AI助手' } },
      { path: 'data-screen', component: () => import('@/views/campus/DataScreen.vue'), meta: { title: '数据大屏', role: 'campus_admin' } },
      { path: 'knowledge', component: () => import('@/views/campus/Knowledge.vue'), meta: { title: '知识库' } },
      { path: 'chat', component: () => import('@/views/campus/Chat.vue'), meta: { title: '师生沟通' } },
      { path: 'my-class', component: () => import('@/views/campus/MyClass.vue'), meta: { title: '我的班级' } },
      { path: 'my-class/:classId', component: () => import('@/views/campus/ClassDetail.vue'), meta: { title: '班级详情' } },
      { path: 'submission', component: () => import('@/views/campus/SubmissionCenter.vue'), meta: { title: '课题提交' } },
      { path: 'student-manage', component: () => import('@/views/campus/StudentManage.vue'), meta: { title: '学生管理' } },
      { path: 'teacher-manage', component: () => import('@/views/campus/TeacherManage.vue'), meta: { title: '教师管理' } },
      { path: 'log', component: () => import('@/views/campus/LogManage.vue'), meta: { title: '日志管理' } },
            { path: 'lab-equipment', component: () => import('@/views/campus/LabEquipmentList.vue'), meta: { title: '实验仪器预约' } },
      { path: 'equipment/:id', component: () => import('@/views/campus/LabEquipmentDetail.vue'), meta: { title: '仪器详情' } },
      { path: 'my-lab-reservations', component: () => import('@/views/campus/MyLabReservations.vue'), meta: { title: '我的预约' } },
      { path: 'my-lab-violations', component: () => import('@/views/campus/MyLabViolations.vue'), meta: { title: '我的违约' } },
      { path: 'admin-lab-reservations', component: () => import('@/views/campus/AdminLabReservations.vue'), meta: { title: '预约审批', role: 'campus_admin' } },
      { path: 'admin-lab-management', component: () => import('@/views/campus/AdminLabManagement.vue'), meta: { title: '实验室管理', role: 'campus_admin' } },
      { path: 'admin-lab-equipment', component: () => import('@/views/campus/AdminLabEquipment.vue'), meta: { title: '仪器管理', role: 'campus_admin' } },
      { path: 'admin-lab-maintenance', component: () => import('@/views/campus/AdminLabMaintenance.vue'), meta: { title: '维修管理', role: 'campus_admin' } },
      { path: 'admin-submissions', component: () => import('@/views/campus/AdminSubmission.vue'), meta: { title: '课题管理', role: 'campus_admin' } },{ path: 'profile', component: () => import('@/views/common/Profile.vue'), meta: { title: '个人中心' } }
    ]
  }
]


const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { title: '平台概览' } },
      { path: 'users', component: () => import('@/views/admin/UserManage.vue'), meta: { title: '用户管理' } },
      { path: 'system', component: () => import('@/views/admin/SystemManage.vue'), meta: { title: '系统管理' } },
      { path: 'logs', component: () => import('@/views/admin/LogManage.vue'), meta: { title: '日志管理' } },
      { path: 'data-screen', component: () => import('@/views/admin/DataScreen.vue'), meta: { title: '数据大屏' } },
      { path: 'lab-management', component: () => import('@/views/campus/AdminLabManagement.vue'), meta: { title: '实验室管理' } },
      { path: 'lab-equipment', component: () => import('@/views/campus/AdminLabEquipment.vue'), meta: { title: '仪器管理' } },
      { path: 'lab-maintenance', component: () => import('@/views/campus/AdminLabMaintenance.vue'), meta: { title: '维修管理' } },
      { path: 'lab-reservations', component: () => import('@/views/campus/AdminLabReservations.vue'), meta: { title: '预约审批' } },
      { path: 'submissions', component: () => import('@/views/campus/AdminSubmission.vue'), meta: { title: '课题管理' } }
    ]
  }
]

const publicRoutes: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: () => import('@/views/auth/Login.vue'), meta: { title: '登录' } },
  { path: '/register', component: () => import('@/views/auth/Register.vue'), meta: { title: '注册' } },
  { path: '/register/student', component: () => import('@/views/auth/StudentRegister.vue'), meta: { title: '学生注册' } },
  { path: '/register/teacher', component: () => import('@/views/auth/TeacherRegister.vue'), meta: { title: '教师注册' } },
  { path: '/forgot-password', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [...adminRoutes, ...publicRoutes, ...campusRoutes]
})

router.beforeEach((to, _from, next) => {
  NProgress.start()
  document.title = `${to.meta.title || 'AniMed'} - AniMed`
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router








<template>
  <div class="admin-submission page-container">
    <el-card>
      <template #header>
        <div class="header-bar">
          <div class="header-left">
            <el-icon :size="20"><EditPen /></el-icon>
            <span class="header-title">课题总览</span>
          </div>
          <div class="header-right">
            <el-select v-model="statusFilter" placeholder="全部状态" clearable style="width:150px;margin-right:10px" @change="fetchTopics">
              <el-option label="待审核" :value="0" />
              <el-option label="审核通过" :value="1" />
              <el-option label="待修改" :value="2" />
              <el-option label="成果待审查" :value="3" />
              <el-option label="已完成" :value="4" />
              <el-option label="成果需修改" :value="5" />
            </el-select>
            <el-input v-model="keyword" placeholder="搜索课题标题/学生/教师" clearable style="width:260px;margin-right:10px" @clear="fetchTopics" @keyup.enter="fetchTopics" />
            <el-button type="primary" @click="fetchTopics">搜索</el-button>
            <el-button @click="fetchTopics"><el-icon><Refresh /></el-icon> 刷新</el-button>
          </div>
        </div>
      </template>
      <el-table :data="filteredList" border stripe size="small" v-loading="loading" empty-text="暂无课题数据" style="width:100%">
        <el-table-column prop="title" label="课题标题" min-width="180" />
        <el-table-column label="来源" width="90">
          <template #default="{ row }">
            <el-tag :type="row.source === 'teacher' ? 'info' : 'primary'" size="small">{{ row.source === 'teacher' ? '教师发布' : '自主创建' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="studentName" label="学生" width="100" />
        <el-table-column prop="teacherName" label="指导教师" width="100" />
        <el-table-column label="状态" width="140">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="160">
          <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">查看</el-button>
            <el-button v-if="row.status >= 3" type="success" link size="small" @click="viewSubmission(row)">查看成果</el-button>
            <el-button type="info" link size="small" @click="viewReviews(row)">审核记录</el-button>
            <el-button v-if="row.status !== 4" type="warning" link size="small" @click="forceComplete(row)">强制结题</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDetail" title="课题详情" width="700px" destroy-on-close>
      <el-descriptions :column="2" border size="small" v-if="currentTopic">
        <el-descriptions-item label="课题标题" span="2">{{ currentTopic.title }}</el-descriptions-item>
        <el-descriptions-item label="学生">{{ currentTopic.studentName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="指导教师">{{ currentTopic.teacherName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="来源">
          <el-tag :type="currentTopic.source === 'teacher' ? 'info' : 'primary'" size="small">{{ currentTopic.source === 'teacher' ? '教师发布' : '自主创建' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(currentTopic.status)" size="small">{{ statusLabel(currentTopic.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(currentTopic.createTime) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(currentTopic.updateTime) }}</el-descriptions-item>
        <el-descriptions-item label="课题描述" span="2">
          <p style="white-space:pre-wrap;margin:0">{{ currentTopic.description || '暂无描述' }}</p>
        </el-descriptions-item>
        <el-descriptions-item label="驳回原因" span="2" v-if="currentTopic.rejectReason">
          <p style="white-space:pre-wrap;margin:0;color:#e6a23c">{{ currentTopic.rejectReason }}</p>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="showDetail = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showSubmission" title="课题成果" width="700px" destroy-on-close>
      <div v-if="!submissionData" class="empty-state">
        <el-icon :size="48" color="#cbd5e1"><FolderOpened /></el-icon>
        <p>该课题暂无提交的成果</p>
      </div>
      <template v-else>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="提交人">{{ submissionData.studentName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="submissionData.status === 1 ? 'success' : 'info'" size="small">{{ submissionData.status === 1 ? '已通过' : '待审核' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="评分" v-if="submissionData.score">{{ submissionData.score }} 分</el-descriptions-item>
          <el-descriptions-item label="版本">v{{ submissionData.version }}</el-descriptions-item>
          <el-descriptions-item label="提交时间" span="2">{{ formatTime(submissionData.createTime) }}</el-descriptions-item>
        </el-descriptions>
        <h4 style="margin:16px 0 8px">提交文件</h4>
        <div v-if="submissionFiles.length === 0" class="empty-mini">暂无文件</div>
        <div v-else class="file-list">
          <div v-for="f in submissionFiles" :key="f.id" class="file-item">
            <el-icon><Document /></el-icon>
            <a :href="f.fileUrl" target="_blank" class="file-link">{{ f.fileName }}</a>
            <span class="file-size">{{ formatFileSize(f.fileSize) }}</span>
          </div>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="showReviews" title="审核记录" width="650px" destroy-on-close>
      <div v-if="reviewList.length === 0" class="empty-state">
        <el-icon :size="48" color="#cbd5e1"><FolderChecked /></el-icon>
        <p>暂无审核记录</p>
      </div>
      <div v-else v-for="r in reviewList" :key="r.id" class="review-box" style="margin-bottom:12px">
        <div class="review-item"><span class="review-label">审核人：</span>{{ r.teacherName || '系统' }}</div>
        <div class="review-item"><span class="review-label">评分：</span>{{ r.score || '-' }} 分</div>
        <div class="review-item"><span class="review-label">评语：</span>{{ r.comment || '无' }}</div>
        <div class="review-item" v-if="r.suggestion"><span class="review-label">修改意见：</span>{{ r.suggestion }}</div>
        <div class="review-item"><span class="review-label">结果：</span>
          <el-tag :type="r.status === 1 ? 'success' : 'danger'" size="small">{{ r.status === 1 ? '通过' : '需修改' }}</el-tag>
        </div>
        <div class="review-item"><span class="review-label">时间：</span>{{ formatTime(r.createTime) }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { EditPen, Refresh, Document, FolderOpened, FolderChecked } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const topics = ref<any[]>([])
const statusFilter = ref<number | null>(null)
const keyword = ref('')
const showDetail = ref(false)
const currentTopic = ref<any>(null)
const showSubmission = ref(false)
const submissionData = ref<any>(null)
const submissionFiles = ref<any[]>([])
const showReviews = ref(false)
const reviewList = ref<any[]>([])

const statusMap: Record<number, string> = { 0: '待审核', 1: '审核通过', 2: '待修改', 3: '成果待审查', 4: '已完成', 5: '成果需修改' }
const typeMap: Record<number, string> = { 0: 'warning', 1: 'success', 2: 'danger', 3: 'primary', 4: 'success', 5: 'warning' }

function statusType(s: number) { return typeMap[s] || 'info' }
function statusLabel(s: number) { return statusMap[s] || '未知' }

const filteredList = computed(() => {
  let list = topics.value
  if (keyword.value) {
    const kw = keyword.value.toLowerCase()
    list = list.filter((t: any) =>
      (t.title && t.title.toLowerCase().includes(kw)) ||
      (t.studentName && t.studentName.includes(kw)) ||
      (t.teacherName && t.teacherName.includes(kw))
    )
  }
  return list
})

function formatTime(t: string) {
  if (!t) return ''
  try { return t.replace('T', ' ').substring(0, 16) } catch { return t }
}

function formatFileSize(bytes: number) {
  if (!bytes) return '0B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0; let size = bytes
  while (size >= 1024 && i < 3) { size /= 1024; i++ }
  return size.toFixed(1) + units[i]
}

async function fetchTopics() {
  loading.value = true
  try {
    const params: any = {}
    if (statusFilter.value !== null) params.status = statusFilter.value
    const res = await request.get('/admin/submission/topics', { params })
    topics.value = res?.data || []
  } catch {
    topics.value = []
  } finally {
    loading.value = false
  }
}

function viewDetail(row: any) {
  currentTopic.value = row
  showDetail.value = true
}

async function viewSubmission(row: any) {
  showSubmission.value = true
  submissionData.value = null
  submissionFiles.value = []
  try {
    const res = await request.get('/user/submission/topic/' + row.id + '/student-submission')
    submissionData.value = res?.data || null
    if (submissionData.value?.id) {
      const fres = await request.get('/user/submission/' + submissionData.value.id + '/files')
      submissionFiles.value = fres?.data || []
    }
  } catch { submissionData.value = null }
}

async function viewReviews(row: any) {
  showReviews.value = true
  reviewList.value = []
  try {
    const res = await request.get('/user/submission/topic/' + row.id + '/student-submission')
    if (res?.data?.id) {
      const rres = await request.get('/user/submission/review/' + res.data.id + '/history')
      reviewList.value = rres?.data || []
    }
  } catch {}
}

async function forceComplete(row: any) {
  try {
    await ElMessageBox.confirm('确定强制结题？该操作将把课题状态标记为已完成。', '确认操作', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
    await request.put('/admin/submission/topic/' + row.id + '/complete')
    ElMessage.success('已强制结题')
    fetchTopics()
  } catch {}
}

onMounted(fetchTopics)
</script>

<style scoped>
.page-container { max-width: 1200px; margin: 0 auto; padding: 20px 24px; }
.header-bar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.header-left { display: flex; align-items: center; gap: 8px; }
.header-title { font-size: 16px; font-weight: 600; }
.empty-state { text-align: center; padding: 60px 20px; color: rgba(255,255,255,0.35); }
.empty-state p { margin-top: 16px; font-size: 15px; }
.empty-mini { text-align: center; padding: 20px; color: rgba(255,255,255,0.35); font-size: 14px; }
.file-list { display: flex; flex-wrap: wrap; gap: 8px; }
.file-item { display: flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.06); padding: 6px 12px; border-radius: 6px; font-size: 13px; }
.file-link { color: #409eff; text-decoration: none; cursor: pointer; }
.file-link:hover { text-decoration: underline; }
.file-size { color: rgba(255,255,255,0.35); font-size: 12px; }
.review-box { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 16px; }
.review-item { margin-bottom: 8px; }
.review-item:last-child { margin-bottom: 0; }
.review-label { font-weight: 600; color: #475569; font-size: 13px; }
</style>


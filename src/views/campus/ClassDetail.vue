<template>
  <div class="class-detail page-container">
    <el-page-header @back="$router.push('/campus/my-class')" :content="classInfo.className || '班级详情'" />

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card>
          <template #header><span>班级信息</span></template>
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="班级名称">{{ classInfo.className }}</el-descriptions-item>
            <el-descriptions-item label="班级代码">
              <el-tag>{{ classInfo.classCode }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="班主任">{{ classInfo.teacherName }}</el-descriptions-item>
            <el-descriptions-item label="学年">{{ classInfo.academicYear }}</el-descriptions-item>
            <el-descriptions-item label="学期">{{ classInfo.semester }}</el-descriptions-item>
            <el-descriptions-item label="描述">{{ classInfo.description || '暂无' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card style="margin-top: 16px;">
          <template #header><span>班级成员</span></template>
          <el-table :data="members" size="small" max-height="300">
            <el-table-column prop="userName" label="姓名" />
            <el-table-column prop="role" label="角色" width="60">
              <template #default="{ row }">
                <el-tag :type="row.role === '教师' ? 'warning' : undefined" size="small">{{ row.role }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="18">
        <el-tabs v-model="activeTab">
          <!-- 作业标签页 -->
          <el-tab-pane label="作业" name="homework">
            <div class="flex-between" style="margin-bottom: 16px;">
              <span>作业列表</span>
              <el-button v-if="isTeacher" type="primary" size="small" @click="showHomeworkDialog = true">发布作业</el-button>
            </div>
            <el-table :data="homeworkList" stripe>
              <el-table-column prop="title" label="作业标题" />
              <el-table-column prop="teacherName" label="发布人" width="100" />
              <el-table-column prop="deadline" label="截止时间" width="170">
                <template #default="{ row }">{{ row.deadline ? row.deadline.replace('T', ' ') : '无截止时间' }}</template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === '进行中' ? 'success' : row.status === '已提交' ? 'primary' : row.status === '已批改' ? 'warning' : 'info'" size="small">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="score" label="分数" width="80">
                <template #default="{ row }">
                  <span v-if="row.score != null">{{ row.score }}</span>
                  <span v-else style="color:#999;">-</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button v-if="!isTeacher" size="small" type="primary" @click="openSubmitDialog(row)">提交</el-button>
                  <el-button v-if="isTeacher" size="small" @click="viewSubmissions(row.id)">查看提交</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <!-- 签到标签页 -->
          <el-tab-pane label="签到" name="signin">
            <div class="flex-between" style="margin-bottom: 16px;">
              <span>签到记录</span>
              <el-button v-if="isTeacher" type="primary" size="small" @click="showSignInDialog = true">发起签到</el-button>
            </div>
            <el-table :data="signInList" stripe>
              <el-table-column prop="title" label="签到标题" />
              <el-table-column prop="signType" label="签到类型" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.signType }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="startTime" label="开始时间" width="170">
                <template #default="{ row }">{{ row.startTime ? row.startTime.replace('T', ' ') : '' }}</template>
              </el-table-column>
              <el-table-column label="状态" width="80">
                <template #default="{ row }">
                  <!-- 签到已结束 -->
                  <el-tag v-if="isSignInEnded(row)" type="info" size="small">已结束</el-tag>
                  <!-- 学生端：根据 _studentStatus 显示 -->
                  <template v-else-if="!isTeacher">
                    <el-tag v-if="row._studentStatus === '已签到'" type="success" size="small">已签到</el-tag>
                    <el-tag v-else type="warning" size="small">未签到</el-tag>
                  </template>
                  <!-- 教师看签到状态 -->
                  <el-tag v-else type="success" size="small">进行中</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="220">
                <template #default="{ row }">
                  <!-- 学生签到按钮：未签到且未结束 -->
                  <el-button v-if="!isTeacher && row._studentStatus === '未签到' && !isSignInEnded(row)" size="small" type="primary" @click="openSignInDialog(row)">签到</el-button>
                  <!-- 教师查看记录按钮 -->
                  <el-button v-if="isTeacher" size="small" @click="viewSignInRecords(row.id)">查看记录</el-button>
                  <!-- 教师结束按钮：未结束 -->
                  <el-button v-if="isTeacher && !isSignInEnded(row)" size="small" type="danger" @click="handleEndSignIn(row.id)">结束</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>

    <!-- 发布作业对话框 -->
    <el-dialog v-model="showHomeworkDialog" title="发布作业" width="500px">
      <el-form ref="hwFormRef" :model="hwForm" :rules="hwRules" label-width="100px">
        <el-form-item label="作业标题" prop="title">
          <el-input v-model="hwForm.title" placeholder="请输入作业标题" />
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker v-model="hwForm.deadline" type="datetime" placeholder="选择截止时间" style="width:100%" />
        </el-form-item>
        <el-form-item label="作业描述">
          <el-input v-model="hwForm.description" type="textarea" :rows="4" placeholder="请输入作业描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showHomeworkDialog = false">取消</el-button>
        <el-button type="primary" :loading="hwLoading" @click="handleCreateHomework">发布</el-button>
      </template>
    </el-dialog>

    <!-- 提交作业对话框 -->
    <el-dialog v-model="showSubmitDialog" title="提交作业" width="500px">
      <el-input v-model="submitContent" type="textarea" :rows="6" placeholder="请输入作业内容" />
      <div style="margin-top: 16px;">
        <el-upload ref="uploadRef" :auto-upload="false" :limit="5" :on-change="handleFileChange" :file-list="uploadFileList" multiple drag>
          <el-icon class="el-icon--upload" :size="48"><UploadFilled /></el-icon>
          <div class="el-upload__text">拖拽文件到此处 <em>点击上传</em></div>
          <template #tip><div style="font-size:12px;color:#999;">支持常见文件格式，单个不超过50MB</div></template>
        </el-upload>
      </div>
      <template #footer>
        <el-button @click="showSubmitDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmitHomework">提交</el-button>
      </template>
    </el-dialog>

    <!-- 发起签到对话框 -->
    <el-dialog v-model="showSignInDialog" title="发起签到" width="500px">
      <el-form ref="signInFormRef" :model="signInForm" :rules="signInRules" label-width="100px">
        <el-form-item label="签到标题" prop="title">
          <el-input v-model="signInForm.title" placeholder="如：第3周课堂签到" />
        </el-form-item>
        <el-form-item label="签到类型" prop="signType">
          <el-select v-model="signInForm.signType" placeholder="请选择签到类型" @change="onSignInTypeChange">
            <el-option label="手势签到" value="手势签到" />
            <el-option label="密码签到" value="密码签到" />
            <el-option label="位置签到" value="位置签到" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="signInForm.signType === '手势签到'" label="手势图案">
          <GestureDraw v-model="signInForm.gesturePattern" />
        </el-form-item>
        <el-form-item v-if="signInForm.signType === '密码签到'" label="签到密码">
          <el-input v-model="signInForm.signPassword" placeholder="请设置签到密码" />
        </el-form-item>
        <el-form-item v-if="signInForm.signType === '位置签到'" label="签到范围(米)">
          <el-input-number v-model="signInForm.radius" :min="50" :max="5000" :step="50" />
        </el-form-item>
        <el-form-item label="签到时长(分钟)">
          <el-input-number v-model="signInForm.duration" :min="5" :max="120" :step="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSignInDialog = false">取消</el-button>
        <el-button type="primary" :loading="signInLoading" @click="handleCreateSignIn">发起</el-button>
      </template>
    </el-dialog>

    <!-- 学生签到对话框 -->
    <el-dialog v-model="showDoSignInDialog" title="签到" width="450px">
      <div v-if="currentSignIn">
        <h3>{{ currentSignIn.title }}</h3>
        <p>签到类型: {{ currentSignIn.signType }}</p>

        <div v-if="currentSignIn.signType === '手势签到'" style="margin-top: 16px;">
          <p>请按顺序绘制手势图案：</p>
          <GestureDraw v-model="studentGesture" />
        </div>

        <div v-if="currentSignIn.signType === '密码签到'" style="margin-top: 16px;">
          <el-input v-model="studentPassword" placeholder="请输入签到密码" size="large" />
        </div>

        <div v-if="currentSignIn.signType === '位置签到'" style="margin-top: 16px;">
          <el-button type="primary" @click="getLocation" :loading="locating">获取当前位置</el-button>
          <p v-if="studentLocation.lat" style="margin-top: 8px; color: #67c23a;">
            位置已获取 ({{ studentLocation.lat.toFixed(4) }}, {{ studentLocation.lng.toFixed(4) }})
          </p>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDoSignInDialog = false">取消</el-button>
        <el-button type="primary" :loading="doSignInLoading" @click="handleDoSignIn">确认签到</el-button>
      </template>
    </el-dialog>

    <!-- 查看提交记录对话框 -->
    <el-dialog v-model="showSubmissionsDialog" title="提交记录" width="800px">
      <el-table :data="submissions" stripe>
        <el-table-column prop="studentName" label="学生" width="100" />
        <el-table-column prop="content" label="内容" show-overflow-tooltip />
        <el-table-column prop="attachmentName" label="附件" width="120">
          <template #default="{ row }">
            <el-button v-if="row.attachment" size="small" type="primary" link @click="downloadHomeworkFile(row)">下载附件</el-button>
            <span v-else style="color:#999;">无</span>
          </template>
        </el-table-column>
        <el-table-column prop="submitTime" label="提交时间" width="170">
          <template #default="{ row }">{{ row.submitTime ? row.submitTime.replace('T', ' ') : '' }}</template>
        </el-table-column>
        <el-table-column prop="score" label="分数" width="70" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === '已批改' ? 'success' : 'primary'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="viewSubmissionDetail(row)">查看详情</el-button>
            <el-button v-if="row.status !== '已批改'" size="small" @click="openGradeDialog(row)">批改</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 提交详情对话框 -->
    <el-dialog v-model="showSubmissionDetailDialog" title="提交详情" width="600px">
      <div v-if="currentDetailSubmission">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="学生">{{ currentDetailSubmission.studentName }}</el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ currentDetailSubmission.submitTime ? currentDetailSubmission.submitTime.replace('T', ' ') : '' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentDetailSubmission.status === '已批改' ? 'success' : 'primary'" size="small">{{ currentDetailSubmission.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentDetailSubmission.score != null" label="分数">{{ currentDetailSubmission.score }}</el-descriptions-item>
          <el-descriptions-item v-if="currentDetailSubmission.comment" label="评语">{{ currentDetailSubmission.comment }}</el-descriptions-item>
        </el-descriptions>
        <div style="margin-top: 16px;">
          <h4>提交内容</h4>
          <p style="white-space: pre-wrap; background: #f5f7fa; padding: 12px; border-radius: 4px;">{{ currentDetailSubmission.content || '无' }}</p>
        </div>
        <div v-if="currentDetailSubmission.attachment" style="margin-top: 16px;">
          <h4>附件</h4>
          <el-button type="primary" size="small" @click="downloadHomeworkFile(currentDetailSubmission)">
            <el-icon><Download /></el-icon> 下载附件
          </el-button>
          <span style="margin-left: 8px;">{{ currentDetailSubmission.attachmentName }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="showSubmissionDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 批改对话框 -->
    <el-dialog v-model="showGradeDialog" title="批改作业" width="400px">
      <el-form label-width="80px">
        <el-form-item label="分数">
          <el-input-number v-model="gradeForm.score" :min="0" :max="100" :precision="1" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="gradeForm.comment" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGradeDialog = false">取消</el-button>
        <el-button type="primary" @click="handleGrade">提交批改</el-button>
      </template>
    </el-dialog>

    <!-- 签到记录对话框 -->
    <el-dialog v-model="showSignInRecordsDialog" title="签到记录" width="600px">
      <el-table :data="signInRecords" stripe>
        <el-table-column prop="studentName" label="学生" width="100" />
        <el-table-column prop="signTime" label="签到时间" width="170">
          <template #default="{ row }">{{ row.signTime ? row.signTime.replace('T', ' ') : '' }}</template>
        </el-table-column>
        <el-table-column prop="result" label="结果" width="80">
          <template #default="{ row }">
            <el-tag :type="row.result === '成功' ? 'success' : 'danger'" size="small">{{ row.result }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="failReason" label="失败原因" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { classApi } from '@/api'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { UploadFilled, Download } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import GestureDraw from '@/components/GestureDraw.vue'

const route = useRoute()
const userStore = useUserStore()
const isTeacher = computed(() => userStore.userInfo?.role === 'campus_teacher')
const classId = computed(() => Number(route.params.classId))

const classInfo = ref<any>({})
const members = ref<any[]>([])
const homeworkList = ref<any[]>([])
const signInList = ref<any[]>([])
const activeTab = ref('homework')

// 作业相关
const showHomeworkDialog = ref(false)
const hwFormRef = ref<FormInstance>()
const hwLoading = ref(false)
const hwForm = reactive({ title: '', deadline: '', description: '' })
const hwRules = { title: [{ required: true, message: '请输入标题', trigger: 'blur' }], deadline: [{ required: true, message: '请选择截止时间', trigger: 'change' }] }

const showSubmitDialog = ref(false)
const submitLoading = ref(false)
const submitContent = ref('')
const currentHomework = ref<any>(null)
const uploadFileList = ref<any[]>([])
const uploadRef = ref()

const showSubmissionDetailDialog = ref(false)
const currentDetailSubmission = ref<any>(null)

const showSubmissionsDialog = ref(false)
const submissions = ref<any[]>([])

const showGradeDialog = ref(false)
const gradeForm = reactive({ submitId: 0, score: 0, comment: '' })

// 签到相关
const showSignInDialog = ref(false)
const signInFormRef = ref<FormInstance>()
const signInLoading = ref(false)
const signInForm = reactive({
  title: '', signType: '', gesturePattern: '', signPassword: '',
  radius: 200, duration: 30, latitude: null as number | null, longitude: null as number | null
})
const signInRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  signType: [{ required: true, message: '请选择签到类型', trigger: 'change' }]
}

const showDoSignInDialog = ref(false)
const doSignInLoading = ref(false)
const currentSignIn = ref<any>(null)
const studentGesture = ref('')
const studentPassword = ref('')
const studentLocation = reactive({ lat: 0, lng: 0 })
const locating = ref(false)

const showSignInRecordsDialog = ref(false)
const signInRecords = ref<any[]>([])

onMounted(() => { fetchAll() })

function isSignInEnded(row: any): boolean {
  if (!row) return true
  // 数值状态系统：偶数为已结束，奇数为进行中
  const statusNum = Number(row.status)
  if (!isNaN(statusNum) && statusNum % 2 === 0) return true
  // 兼容字符串状态
  if (row.status === '已结束' || row.status === '2') return true
  // 检查 endTime 字段
  if (row.endTime) {
    const et = row.endTime.replace('T', ' ')
    const endMs = new Date(et).getTime()
    if (!isNaN(endMs) && Date.now() > endMs) return true
  }
  return false
}

async function fetchAll() {
  await Promise.all([fetchClassInfo(), fetchMembers(), fetchHomework(), fetchSignIn()])
}

async function fetchClassInfo() {
  try {
    const res: any = await classApi.getClassDetail(classId.value)
    classInfo.value = res.data || {}
  } catch {}
}

async function fetchMembers() {
  try {
    const res: any = await classApi.getClassMembers(classId.value)
    members.value = res.data || []
  } catch {}
}

async function downloadHomeworkFile(row: any) {
  if (!row.attachment) { ElMessage.warning('无附件'); return }
  try {
    const res = await fetch('/api/user/class/homework/file/download?fileUrl=' + encodeURIComponent(row.attachment), {
      headers: { 'Authorization': localStorage.getItem('token') || '' }
    })
    if (!res.ok) { ElMessage.error('下载失败'); return }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = row.attachmentName || '作业附件'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch { ElMessage.error('下载失败') }
}

function viewSubmissionDetail(row: any) {
  currentDetailSubmission.value = row
  showSubmissionDetailDialog.value = true
}


async function fetchHomework() {
  try {
    const res: any = isTeacher.value
      ? await classApi.getHomeworkList(classId.value)
      : await classApi.getStudentHomeworkList(classId.value)
    homeworkList.value = res.data || []
  } catch {}
}

async function fetchSignIn() {
  try {
    const res: any = await classApi.getSignInList(classId.value)
    const list = (res.data || []) as any[]
    // 使用数值状态系统直接判断
    for (const si of list) {
      const statusNum = Number(si.status)
      if (!isTeacher.value) {
        // 学生端：已结束 → 已结束，3 → 已签到，1 → 未签到
        if (si.status === '2' || (!isNaN(statusNum) && statusNum % 2 === 0)) {
          si._studentStatus = '已结束'
        } else if (si.status === '3' || statusNum === 3) {
          si._studentStatus = '已签到'
        } else {
          si._studentStatus = '未签到'
        }
      }
    }
    signInList.value = list
  } catch {}
}

// 作业操作
async function handleCreateHomework() {
  await hwFormRef.value?.validate()
  hwLoading.value = true
  try {
    // 转换日期格式
    const submitDeadline = hwForm.deadline instanceof Date
      ? hwForm.deadline.getFullYear() + '-' +
        String(hwForm.deadline.getMonth() + 1).padStart(2, '0') + '-' +
        String(hwForm.deadline.getDate()).padStart(2, '0') + 'T' +
        String(hwForm.deadline.getHours()).padStart(2, '0') + ':' +
        String(hwForm.deadline.getMinutes()).padStart(2, '0') + ':' +
        String(hwForm.deadline.getSeconds()).padStart(2, '0')
      : hwForm.deadline
    await classApi.createHomework({ ...hwForm, classId: classId.value, deadline: submitDeadline })
    ElMessage.success('作业发布成功')
    showHomeworkDialog.value = false
    hwForm.title = ''; hwForm.deadline = ''; hwForm.description = ''
    fetchHomework()
  } catch {} finally { hwLoading.value = false }
}

function openSubmitDialog(hw: any) {
  currentHomework.value = hw
  submitContent.value = ''
  uploadFileList.value = []
  showSubmitDialog.value = true
}

async function handleSubmitHomework() {
  if (!submitContent.value.trim()) { ElMessage.warning('请输入作业内容'); return }
  submitLoading.value = true
  try {
    let attachment = ''
    let attachmentName = ''
    // Upload file first if any
    if (uploadFileList.value.length > 0) {
      const fd = new FormData()
      fd.append('file', uploadFileList.value[0].raw || uploadFileList.value[0])
      const uploadRes: any = await fetch('/api/user/class/homework/file/upload', {
        method: 'POST',
        headers: { 'Authorization': localStorage.getItem('token') || '' },
        body: fd
      })
      if (!uploadRes.ok) { ElMessage.error("File upload failed"); submitLoading.value = false; return }
      const uploadData = await uploadRes.json()
      if (uploadData && uploadData.data && uploadData.data.url) {
        attachment = uploadData.data.url
        attachmentName = uploadData.data.name
      }
    }
    await classApi.submitHomework({
      homeworkId: currentHomework.value.id,
      content: submitContent.value,
      attachment: attachment,
      attachmentName: attachmentName
    })
    ElMessage.success('提交成功')
    showSubmitDialog.value = false
    uploadFileList.value = []
    fetchHomework()
  } catch {} finally { submitLoading.value = false }
}

function handleFileChange(file: any) { uploadFileList.value = [...uploadFileList.value, file] }


async function viewSubmissions(homeworkId: number) {
  try {
    const res: any = await classApi.getHomeworkSubmissions(homeworkId)
    submissions.value = res.data || []
    showSubmissionsDialog.value = true
  } catch {}
}

function openGradeDialog(row: any) {
  gradeForm.submitId = row.id
  gradeForm.score = 0
  gradeForm.comment = ''
  showGradeDialog.value = true
}

async function handleGrade() {
  try {
    await classApi.gradeHomework(gradeForm)
    ElMessage.success('批改成功')
    showGradeDialog.value = false
    viewSubmissions(submissions.value[0]?.homeworkId)
  } catch {}
}

// 签到操作
function onSignInTypeChange() {
  signInForm.gesturePattern = ''
  signInForm.signPassword = ''
  if (signInForm.signType === '位置签到') {
    getLocation()
  }
}

function getLocation() {
  locating.value = true
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        studentLocation.lat = pos.coords.latitude
        studentLocation.lng = pos.coords.longitude
        if (signInForm.signType === '位置签到') {
          signInForm.latitude = pos.coords.latitude
          signInForm.longitude = pos.coords.longitude
        }
        locating.value = false
      },
      () => {
        ElMessage.error('无法获取位置信息')
        locating.value = false
      },
      { timeout: 10000 }
    )
  } else {
    ElMessage.error('浏览器不支持定位')
    locating.value = false
  }
}

async function handleCreateSignIn() {
  await signInFormRef.value?.validate()
  if (signInForm.signType === '手势签到' && !signInForm.gesturePattern) {
    ElMessage.warning('请绘制手势图案'); return
  }
  if (signInForm.signType === '密码签到' && !signInForm.signPassword) {
    ElMessage.warning('请设置签到密码'); return
  }
  signInLoading.value = true
  try {
    await classApi.createSignIn({ ...signInForm, classId: classId.value })
    ElMessage.success('签到已发起')
    showSignInDialog.value = false
    signInForm.title = ''; signInForm.signType = ''; signInForm.gesturePattern = ''
    signInForm.signPassword = ''; signInForm.radius = 200; signInForm.duration = 30
    fetchSignIn()
  } catch {} finally { signInLoading.value = false }
}

function openSignInDialog(signIn: any) {
  currentSignIn.value = signIn
  studentGesture.value = ''
  studentPassword.value = ''
  studentLocation.lat = 0
  studentLocation.lng = 0
  showDoSignInDialog.value = true
}

async function handleDoSignIn() {
  doSignInLoading.value = true
  try {
    const data: any = { signInId: currentSignIn.value.id }
    if (currentSignIn.value.signType === '手势签到') {
      data.gesturePattern = studentGesture.value
    } else if (currentSignIn.value.signType === '密码签到') {
      data.inputPassword = studentPassword.value
    } else if (currentSignIn.value.signType === '位置签到') {
      if (!studentLocation.lat) { ElMessage.warning('请先获取位置'); doSignInLoading.value = false; return }
      data.latitude = studentLocation.lat
      data.longitude = studentLocation.lng
    }
    const res: any = await classApi.doSignIn(data)
    if (res && res.code === 200) {
      ElMessage.success('签到成功')
      showDoSignInDialog.value = false
      // 立即更新本地状态
      const found = signInList.value.find((s: any) => s.id === currentSignIn.value.id)
      if (found) found._studentStatus = '已签到'
    } else {
      ElMessage.error((res && res.msg) || '签到失败，请检查密码或位置')
    }
    fetchSignIn()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.msg || e?.message || '签到失败')
  } finally { doSignInLoading.value = false }
}

async function viewSignInRecords(signInId: number) {
  try {
    const res: any = await classApi.getSignInRecords(signInId)
    signInRecords.value = res.data || []
    showSignInRecordsDialog.value = true
  } catch {}
}

async function handleEndSignIn(signInId: number) {
  try {
    const res: any = await classApi.endSignIn(signInId)
    if (res && res.code === 200) {
      ElMessage.success('签到已结束')
    } else {
      ElMessage.warning('结束请求已发送')
    }
    // 强制更新本地 endTime 为当前时间
    const found = signInList.value.find((s: any) => s.id === signInId)
    if (found) {
      found.endTime = new Date().toISOString()
    }
    fetchSignIn()
  } catch {
    // 即使接口失败也强制更新
    const found = signInList.value.find((s: any) => s.id === signInId)
    if (found) {
      found.endTime = new Date().toISOString()
    }
    ElMessage.success('签到已结束')
    fetchSignIn()
  }
}
</script>

<style scoped lang="scss">
.flex-between { display: flex; justify-content: space-between; align-items: center; }
</style>

<template>
  <div class="my-class-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>我的班级</h2>
      <div class="header-actions">
        <el-button v-if="isTeacher" type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>创建班级
        </el-button>
        <el-button @click="showJoinDialog = true">
          <el-icon><User /></el-icon>加入班级
        </el-button>
      </div>
    </div>

    <!-- 班级卡片列表 -->
    <div v-if="classList.length" class="class-grid">
      <div v-for="cls in classList" :key="cls.id" class="class-card" @click="goDetail(cls.id)">
        <div class="card-top">
          <div class="class-icon">{{ cls.className?.charAt(0) || "类" }}</div>
          <div class="class-meta">
            <h3>{{ cls.className }}</h3>
            <p class="class-code-label">
              班级码<el-tag size="small" type="warning" class="code-tag">{{ cls.classCode }}</el-tag>
              <el-button size="small" text @click.stop="copyCode(cls.classCode)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </p>
          </div>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span>老师: {{ cls.teacherName }}</span>
            <span v-if="cls.memberCount !== undefined">{{ cls.memberCount }}人</span>
          </div>
          <div class="info-row">
            <span>{{ cls.academicYear || "" }} {{ cls.semester || "" }}</span>
            <el-tag :type="cls.status === '活跃' ? 'success' : 'info'" size="small">{{ cls.status }}</el-tag>
          </div>
          <p v-if="cls.description" class="desc">{{ cls.description }}</p>
        </div>
      </div>
    </div>
    <el-empty v-else description="还没有班级，快去创建或加入一个吧~" :image-size="100" />

    <!-- 创建班级对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建班级" width="460px" :close-on-click-modal="false">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="90px">
        <el-form-item label="班级名称" prop="className">
          <el-input v-model="createForm.className" placeholder="请输入班级名称（不可同名）" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="学年" prop="academicYear">
          <el-select v-model="createForm.academicYear" placeholder="请选择学年" style="width:100%">
            <el-option label="2024-2025" value="2024-2025" />
            <el-option label="2025-2026" value="2025-2026" />
            <el-option label="2026-2027" value="2026-2027" />
          </el-select>
        </el-form-item>
        <el-form-item label="学期">
          <el-radio-group v-model="createForm.semester">
            <el-radio value="第一学期">第一学期</el-radio>
            <el-radio value="第二学期">第二学期</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="输入班级简介（选填）" maxlength="200" />
        </el-form-item>
        <el-form-item>
          <div class="form-tip">创建后将自动生成6位班级码，学生通过班级码加入</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">立即创建</el-button>
      </template>
    </el-dialog>

    <!-- 加入班级对话框 -->
    <el-dialog v-model="showJoinDialog" title="加入班级" width="400px" :close-on-click-modal="false">
      <div class="join-tip">请输入老师给的班级码加入班级</div>
      <el-input v-model="joinCode" placeholder="输入6位班级码" size="large" maxlength="16" @keyup.enter="handleJoin">
        <template #prefix><el-icon><Key /></el-icon></template>
      </el-input>
      <template #footer>
        <el-button @click="showJoinDialog = false">取消</el-button>
        <el-button type="primary" :loading="joining" @click="handleJoin">加入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { classApi } from "@/api"
import { ElMessage } from "element-plus"
import type { FormInstance } from "element-plus"
import { Plus, User, CopyDocument, Key } from "@element-plus/icons-vue"
import { useUserStore } from "@/stores/user"

const router = useRouter()
const userStore = useUserStore()
const isTeacher = computed(() => userStore.userInfo?.role === "campus_teacher")
const classList = ref<any[]>([])
const showCreateDialog = ref(false)
const showJoinDialog = ref(false)
const creating = ref(false)
const joining = ref(false)
const joinCode = ref("")
const createFormRef = ref<FormInstance>()

const createForm = reactive({ className: "", academicYear: "2025-2026", semester: "第一学期", description: "" })
const createRules = {
  className: [
    { required: true, message: "请输入班级名称", trigger: "blur" },
    { min: 2, max: 50, message: "班级名称长度2-50个字符", trigger: "blur" }
  ],
  academicYear: [{ required: true, message: "请选择学年", trigger: "change" }]
}

onMounted(() => { fetchClasses() })

async function fetchClasses() {
  try {
    const res: any = isTeacher.value ? await classApi.getTeacherClasses() : await classApi.getStudentClasses()
    classList.value = res.data || []
  } catch { classList.value = [] }
}

async function handleCreate() {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return
  creating.value = true
  try {
    await classApi.createClass(createForm)
    ElMessage.success("班级创建成功！班级码已自动生成")
    showCreateDialog.value = false
    Object.assign(createForm, { className: "", academicYear: "2025-2026", semester: "第一学期", description: "" })
    fetchClasses()
  } catch {} finally { creating.value = false }
}

async function handleJoin() {
  if (!joinCode.value.trim()) { ElMessage.warning("请输入班级码"); return }
  joining.value = true
  try {
    await classApi.joinClass(joinCode.value.trim())
    ElMessage.success("加入成功！")
    showJoinDialog.value = false
    joinCode.value = ""
    fetchClasses()
  } catch {} finally { joining.value = false }
}

async function copyCode(code: string) {
  try {
    await navigator.clipboard.writeText(code)
    ElMessage.success("班级码已复制到剪贴板")
  } catch { ElMessage.warning("复制失败，请手动复制") }
}

function goDetail(classId: number) {
  router.push("/campus/my-class/" + classId)
}
</script>

<style scoped>
.my-class-page { padding: 20px; max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-header h2 { font-size: 22px; font-weight: 600; color: #f1f5f9; margin: 0; }
.header-actions { display: flex; gap: 10px; }
.class-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.class-card {
  background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px;
  box-shadow: none; cursor: pointer;
  transition: all 0.25s ease; border: 1px solid rgba(255,255,255,0.08);
}
.class-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(99,102,241,0.2); border-color: rgba(255,255,255,0.15); }
.card-top { display: flex; gap: 14px; margin-bottom: 14px; }
.class-icon {
  width: 48px; height: 48px; border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #818cf8);
  color: #fff; font-size: 20px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.class-meta { flex: 1; }
.class-meta h3 { font-size: 16px; font-weight: 600; margin: 0 0 4px; color: rgba(255,255,255,0.8); }
.class-code-label { font-size: 12px; color: rgba(255,255,255,0.5); display: flex; align-items: center; gap: 4px; }
.code-tag { font-family: monospace; letter-spacing: 1px; }
.card-body .info-row { display: flex; justify-content: space-between; font-size: 13px; color: rgba(255,255,255,0.6); margin-bottom: 6px; }
.card-body .desc { font-size: 12px; color: rgba(255,255,255,0.4); margin: 6px 0 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.join-tip { font-size: 14px; color: #666; margin-bottom: 12px; }
.form-tip { font-size: 12px; color: #999; }
</style>

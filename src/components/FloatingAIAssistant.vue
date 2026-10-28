<template>
  <div class="floating-ai">
    <!-- 悬浮按钮 -->
    <button class="ai-fab" @click="togglePanel" :class="{ active: visible }">
      <el-icon v-if="!visible" :size="22"><ChatLineSquare /></el-icon>
      <el-icon v-else :size="22"><Close /></el-icon>
    </button>

    <!-- 对话面板 -->
    <transition name="ai-slide-up">
      <div v-if="visible" class="ai-panel">
        <div class="ai-panel-header">
          <div class="ai-panel-title">
            <el-icon><MagicStick /></el-icon>
            <span>AI 助手</span>
          </div>
          <div class="ai-panel-context">{{ contextLabel }}</div>
          <button class="ai-panel-close" @click="visible = false">
            <el-icon><Close /></el-icon>
          </button>
        </div>

        <div class="ai-messages" ref="msgContainer">
          <div v-if="messages.length === 0" class="ai-welcome">
            <el-icon :size="32" color="#818cf8"><MagicStick /></el-icon>
            <p>你好！我是 AniMed AI 助手</p>
            <p class="ai-welcome-hint">我可以帮你解答关于平台功能、实验仪器、课题信息等问题</p>
            <div class="ai-quick-questions">
              <button v-for="q in quickQuestions" :key="q" class="ai-quick-btn" @click="ask(q)">{{ q }}</button>
            </div>
          </div>
          <div v-for="(msg, i) in messages" :key="i" :class="['ai-msg', msg.role]">
            <div class="ai-msg-avatar">
              <el-icon v-if="msg.role === 'assistant'" :size="16"><MagicStick /></el-icon>
              <el-icon v-else :size="16"><User /></el-icon>
            </div>
            <div class="ai-msg-content">
              <div class="ai-msg-text">{{ msg.content }}</div>
            </div>
          </div>
          <div v-if="loading" class="ai-msg assistant">
            <div class="ai-msg-avatar"><el-icon :size="16"><MagicStick /></el-icon></div>
            <div class="ai-msg-content">
              <div class="ai-typing"><span></span><span></span><span></span></div>
            </div>
          </div>
        </div>

        <div class="ai-input-bar">
          <el-input
            v-model="inputText"
            placeholder="输入你的问题..."
            :disabled="loading"
            @keyup.enter="sendMessage"
          >
            <template #append>
              <el-button :loading="loading" @click="sendMessage" :icon="Promotion" />
            </template>
          </el-input>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from "vue"
import { useRoute } from "vue-router"
import { ElMessage } from "element-plus"
import { ChatLineSquare, Close, MagicStick, User, Promotion } from "@element-plus/icons-vue"

const route = useRoute()
const visible = ref(false)
const inputText = ref("")
const loading = ref(false)
const messages = ref<{ role: string; content: string }[]>([])
const msgContainer = ref<HTMLElement | null>(null)

// 根据当前路由生成上下文标签
const contextLabel = computed(() => {
  const path = route.path
  if (path.includes("/dashboard")) return "首页"
  if (path.includes("/data/clean")) return "数据清洗"
  if (path.includes("/data/upload")) return "数据上传"
  if (path.includes("/data")) return "数据管理"
  if (path.includes("/analysis/library")) return "分析库"
  if (path.includes("/analysis")) return "数据分析"
  if (path.includes("/knowledge")) return "知识库"
  if (path.includes("/chat")) return "师生沟通"
  if (path.includes("/my-class")) return "我的班级"
  if (path.includes("/submission")) return "课题提交"
  if (path.includes("/lab-equipment") || path.includes("/equipment")) return "实验仪器"
  if (path.includes("/my-lab-reservations")) return "我的预约"
  return "平台助手"
})

// 根据角色选择 agent 端点
const agentEndpoint = computed(() => {
  const role = localStorage.getItem("role") || "student"
  if (role === "campus_teacher") return "agentTeacher"
  return "agentStudent"
})

// 快捷问题
const quickQuestions = computed(() => {
  const path = route.path
  if (path.includes("/dashboard")) {
    return ["查看我的预约", "查看待完成课题", "查看实验仪器"]
  }
  if (path.includes("/data")) {
    return ["如何上传数据", "如何清洗数据", "数据分析有哪些方法"]
  }
  if (path.includes("/analysis")) {
    return ["如何新建分析", "分析报告怎么看", "分析库是什么"]
  }
  if (path.includes("/knowledge")) {
    return ["如何上传知识库文档", "如何搜索知识", "支持哪些文件格式"]
  }
  if (path.includes("/my-class")) {
    return ["查看班级成员", "查看作业", "查看签到记录"]
  }
  if (path.includes("/submission")) {
    return ["如何确认课题", "如何提交成果", "查看我的课题"]
  }
  if (path.includes("/lab-equipment") || path.includes("/equipment")) {
    return ["推荐实验仪器", "查看可用仪器", "如何预约仪器"]
  }
  return ["查看平台概览", "如何使用平台", "联系管理员"]
})

function togglePanel() {
  visible.value = !visible.value
}

async function ask(question: string) {
  inputText.value = question
  await sendMessage()
}

async function sendMessage() {
  if (!inputText.value.trim() || loading.value) return
  const text = inputText.value.trim()
  inputText.value = ''
  messages.value.push({ role: 'user', content: text })
  loading.value = true
  await nextTick()
  scrollToBottom()
  try {
    // Try to handle known intents with real data first
    const dataReply = await handleIntent(text)
    if (dataReply) {
      messages.value.push({ role: 'assistant', content: dataReply })
      return
    }
    // Fall back to backend AI agent
    const { analysisApi } = await import('@/api')
    const agentFn = agentEndpoint.value === 'agentTeacher'
      ? analysisApi.agentTeacher
      : analysisApi.agentStudent
    const res: any = await agentFn({ message: text })
    const reply = res.data?.content || res.data || '抱歉，暂时无法回答，请稍后再试。'
    messages.value.push({ role: 'assistant', content: reply })
  } catch (e: any) {
    messages.value.push({ role: 'assistant', content: '抱歉，服务暂时不可用，请稍后再试。' })
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// Intent-based action handlers that call real APIs to return real data
async function handleIntent(text: string): Promise<string | null> {
  const { labApi, submissionApi } = await import('@/api')

  // 查看我的预约
  if (/查看\s*我\s*的\s*预约|我的预约|预约记录/.test(text)) {
    try {
      const res: any = await labApi.getMyReservations()
      const list = res.data || res
      if (!list || (Array.isArray(list) && list.length === 0)) {
        return '你目前没有预约记录。如果需要预约实验仪器，可以前往「实验仪器预约」页面操作。'
      }
      const items = Array.isArray(list) ? list : list.records || list.rows || []
      if (items.length === 0) return '你目前没有预约记录。'
      let reply = '📋 你的预约记录如下：\n\n'
      items.slice(0, 10).forEach((r: any, i: number) => {
        const statusMap: Record<string, string> = { pending: '待审批', approved: '已通过', rejected: '已拒绝', in_use: '使用中', completed: '已完成', cancelled: '已取消' }
        reply += `${i + 1}. ${r.equipmentName || r.equipment?.name || '仪器#' + r.equipmentId}`
        reply += ` | ${r.date || ''} ${r.slot || r.timeSlot || ''}`
        reply += ` | ${statusMap[r.status] || r.status}\n`
      })
      if (items.length > 10) reply += `\n...还有 ${items.length - 10} 条记录`
      reply += '\n\n你可以点击导航栏「我的预约」查看详情。'
      return reply
    } catch {
      return '查询预约记录失败，请稍后再试或前往「我的预约」页面查看。'
    }
  }

  // 查看待完成课题 / 我的课题
  if (/查看.*课题|我的课题|待完成课题|课题进度/.test(text)) {
    try {
      const res: any = await submissionApi.getConfirmedTopics()
      const list = res.data || res
      const items = Array.isArray(list) ? list : (list.records || list.rows || [])
      if (items.length === 0) return '你目前没有待完成的课题。'
      let reply = '📚 你的课题列表：\n\n'
      items.slice(0, 10).forEach((t: any, i: number) => {
        reply += `${i + 1}. ${t.title || t.topicName || '课题#' + t.id}`
        if (t.status !== undefined) {
          const sMap: Record<string, string> = { '0': '未提交', '1': '已提交', '2': '已通过', '3': '被打回' }
          reply += ` | ${sMap[String(t.status)] || t.status}`
        }
        reply += '\n'
      })
      if (items.length > 10) reply += `\n...还有 ${items.length - 10} 个课题`
      return reply
    } catch {
      return '查询课题信息失败，请稍后再试或前往「课题提交」页面查看。'
    }
  }

  // 查看实验仪器列表
  if (/查看.*仪器|实验仪器|仪器列表/.test(text)) {
    try {
      const res: any = await labApi.getEquipmentList()
      const list = res.data || res
      const items = Array.isArray(list) ? list : (list.records || list.rows || [])
      if (items.length === 0) return '目前系统中没有可用仪器。'
      let reply = '🔬 仪器列表：\n\n'
      items.slice(0, 15).forEach((e: any, i: number) => {
        const statusText = e.status === 'normal' ? '可预约' : (e.status === 'maintenance' ? '维修中' : e.status)
        reply += `${i + 1}. ${e.name || e.equipmentName || '仪器#' + e.id} — ${statusText}\n`
      })
      if (items.length > 15) reply += `\n...共 ${items.length} 台仪器`
      return reply
    } catch {
      return '查询仪器列表失败，请稍后再试或前往「实验仪器预约」页面查看。'
    }
  }

  return null // not a known intent, fall back to AI agent
}

function scrollToBottom() {
  nextTick(() => {
    if (msgContainer.value) {
      msgContainer.value.scrollTop = msgContainer.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.floating-ai {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* 悬浮按钮 */
.ai-fab {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: none;
  background: #6366f1;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
  transition: all 0.3s ease;
  position: relative;
}
.ai-fab:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 28px rgba(99, 102, 241, 0.5);
}
.ai-fab.active {
  background: #4f46e5;
  transform: scale(0.95);
}

/* 对话面板 */
.ai-panel {
  position: absolute;
  bottom: 64px;
  right: 0;
  width: 380px;
  height: 520px;
  background: rgba(15, 15, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(16px);
}
.ai-panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(99, 102, 241, 0.1);
}
.ai-panel-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 600;
  color: #e2e8f0;
}
.ai-panel-context {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.06);
  padding: 2px 8px;
  border-radius: 10px;
  margin-left: auto;
}
.ai-panel-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 4px;
}
.ai-panel-close:hover { color: #fff; }

/* 消息区域 */
.ai-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.ai-messages::-webkit-scrollbar { width: 4px; }
.ai-messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

/* 欢迎界面 */
.ai-welcome {
  text-align: center;
  padding: 32px 16px;
  color: #e2e8f0;
}
.ai-welcome p { margin: 8px 0; font-size: 14px; }
.ai-welcome-hint { font-size: 12px !important; color: rgba(255,255,255,0.4); }
.ai-quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 16px;
}
.ai-quick-btn {
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.65);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.ai-quick-btn:hover {
  background: rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.3);
  color: #818cf8;
}

/* 消息气泡 */
.ai-msg {
  display: flex;
  gap: 8px;
  max-width: 100%;
}
.ai-msg.user { flex-direction: row-reverse; }
.ai-msg-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(99, 102, 241, 0.15);
  color: #818cf8;
}
.ai-msg.user .ai-msg-avatar { background: rgba(255, 255, 255, 0.08); color: #94a3b8; }
.ai-msg-content {
  max-width: 80%;
}
.ai-msg-text {
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.5;
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
.ai-msg.user .ai-msg-text {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.2);
}

/* 打字动画 */
.ai-typing {
  display: flex;
  gap: 4px;
  padding: 14px;
  align-items: center;
}
.ai-typing span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  animation: typing 1.2s infinite;
}
.ai-typing span:nth-child(2) { animation-delay: 0.2s; }
.ai-typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
  30% { opacity: 1; transform: translateY(-4px); }
}

/* 输入区域 */
.ai-input-bar {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.ai-input-bar :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  box-shadow: none !important;
}
.ai-input-bar :deep(.el-input__inner) {
  color: #e2e8f0 !important;
  font-size: 13px;
}
.ai-input-bar :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.3);
}
.ai-input-bar :deep(.el-input-group__append) {
  background: transparent !important;
  border: none !important;
}
.ai-input-bar :deep(.el-button) {
  background: #6366f1 !important;
  border-color: #6366f1 !important;
  color: #fff !important;
}
.ai-input-bar :deep(.el-button:hover) {
  background: #4f46e5 !important;
}

/* 过渡动画 */
.ai-slide-up-enter-active,
.ai-slide-up-leave-active {
  transition: all 0.25s ease;
}
.ai-slide-up-enter-from,
.ai-slide-up-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>


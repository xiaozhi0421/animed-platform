<template>
  <div class="ai-chat page-container">
    <div class="chat-container">
      <!-- Agent side panel -->
      <div class="agent-sidebar">
        <div class="sidebar-header">
          <div class="sidebar-logo">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
          </div>
          <span class="sidebar-title">AI 助手</span>
        </div>
        <div class="agent-list">
          <div v-for="agent in agents" :key="agent.value" :class="['agent-card', { active: activeAgent === agent.value }]" @click="switchAgent(agent.value)">
            <div class="agent-card-icon" :style="{ background: agent.gradient }">
              <el-icon :size="18" color="#fff"><component :is="agent.icon" /></el-icon>
            </div>
            <div class="agent-card-info">
              <div class="agent-card-name">{{ agent.label }}</div>
              <div class="agent-card-desc">{{ agent.desc }}</div>
            </div>
            <div v-if="activeAgent === agent.value" class="agent-card-indicator"></div>
          </div>
        </div>
        <div class="sidebar-footer">
          <span class="footer-text">AniMed AI Platform</span>
        </div>
      </div>
      <!-- Main chat area -->
      <div class="chat-main">
        <div class="chat-header">
          <div class="header-left">
            <div class="header-avatar" :style="{ background: currentAgent?.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }">
              <el-icon :size="20" color="#fff"><component :is="currentAgent?.icon || ChatDotSquare" /></el-icon>
            </div>
            <div class="header-info">
              <div class="header-title">{{ currentAgent?.label || 'AI 助手' }}</div>
              <div class="header-status"><span class="status-dot"></span>在线 {{ messages.length }}条消息</div>
            </div>
          </div>
          <div class="header-actions" v-if="messages.length">
            <el-tooltip content="清空对话">
              <el-button text circle @click="clearMessages" class="header-action-btn"><el-icon><Delete /></el-icon></el-button>
            </el-tooltip>
          </div>
        </div>
        <div class="messages" ref="messagesRef">
          <!-- Welcome screen -->
          <div v-if="!messages.length && !thinking" class="welcome">
            <div class="welcome-bg-shapes">
              <div class="shape s1"></div><div class="shape s2"></div><div class="shape s3"></div>
            </div>
            <div class="welcome-icon-wrapper">
              <div class="welcome-icon-ring"></div>
              <div class="welcome-icon" :style="{ background: currentAgent?.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }">
                <el-icon :size="32" color="#fff"><component :is="currentAgent?.icon || ChatDotSquare" /></el-icon>
              </div>
            </div>
            <h2 class="welcome-title">{{ currentAgent?.label || 'AniMed AI 助手' }}</h2>
            <p class="welcome-desc">{{ currentAgent?.desc || '请选择一个智能体开始对话' }}</p>
            <div class="suggestions">
              <div v-for="(q, i) in currentAgent?.questions || []" :key="i" class="suggestion-chip" @click="askQuestion(q)">
                <el-icon :size="14"><ChatDotRound /></el-icon>
                <span>{{ q }}</span>
              </div>
            </div>
          </div>
          <!-- Messages -->
          <div v-for="msg in messages" :key="msg.id" :class="['message-row', msg.role]">
            <div class="message-avatar">
              <div v-if="msg.role === 'user'" class="user-avatar">我</div>
              <div v-else class="ai-avatar" :style="{ background: currentAgent?.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }">
                <el-icon :size="16" color="#fff"><component :is="currentAgent?.icon || ChatDotSquare" /></el-icon>
              </div>
            </div>
            <div class="message-content">
              <div class="message-meta">
                <span class="message-sender">{{ msg.role === 'user' ? '我' : currentAgent?.label || 'AI' }}</span>
                <span class="message-time">{{ msg.time }}</span>
              </div>
              <div class="message-bubble" v-html="renderContent(msg.content)"></div>
            </div>
          </div>
          <!-- Thinking indicator -->
          <div v-if="thinking" class="message-row assistant">
            <div class="message-avatar">
              <div class="ai-avatar" :style="{ background: currentAgent?.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }">
                <el-icon :size="16" color="#fff"><component :is="currentAgent?.icon || ChatDotSquare" /></el-icon>
              </div>
            </div>
            <div class="message-content">
              <div class="message-meta">
                <span class="message-sender">{{ currentAgent?.label || 'AI' }}</span>
                <span class="message-time">{{ formatTime() }}</span>
              </div>
              <div class="message-bubble thinking-bubble">
                <div class="thinking-bar" v-if="!streamingText">
                  <span class="dot-pulse"></span>
                  <span class="dot-pulse"></span>
                  <span class="dot-pulse"></span>
                </div>
                <span v-if="streamingText" v-html="renderContent(streamingText)"></span>
                <span v-if="streamingText" class="cursor-blink">|</span>
              </div>
            </div>
          </div>
        </div>
        <div class="input-area">
          <div class="input-wrapper">
            <el-input
              v-model="inputText"
              type="textarea"
              :rows="1"
              :placeholder="'向 ' + (currentAgent?.label || 'AI助手') + ' 提问...'"
              @keydown.enter.ctrl="sendMessage"
              @keydown.enter.exact.prevent="sendMessage"
              :autosize="{ minRows: 1, maxRows: 4 }"
            />
            <el-button
              type="primary"
              :disabled="!inputText.trim() || thinking"
              @click="sendMessage"
              :loading="thinking"
              class="send-btn"
              circle
            >
              <el-icon v-if="!thinking" :size="18"><Position /></el-icon>
            </el-button>
          </div>
          <div class="input-tip">
            <span>Enter 发送 · Ctrl+Enter 换行</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from "vue"
import { analysisApi } from "@/api"
import { useUserStore } from "@/stores/user"
import { ChatDotSquare, User, Promotion, Monitor, Tickets, Connection, ChatDotRound, Delete, Position } from "@element-plus/icons-vue"

const messagesRef = ref<HTMLElement>()
const inputText = ref("")
const thinking = ref(false)
const streamingText = ref("")
const messages = ref<{ id: number; role: string; content: string; time: string }[]>([])
const activeAgent = ref<string>("general")
let msgIdCounter = 0

const userStore = useUserStore()

const allAgents = [
    {
      value: "general",
      label: "通用AI",
      icon: ChatDotSquare,
      desc: "校园平台通用智能助手",
      gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      role: "all",
      questions: ["如何预约实验仪器", "有哪些实验室可用", "有哪些课程可以选择"]
    },
    {
      value: "student",
      label: "学生助手",
      icon: User,
      desc: "面向学生 · 仪器推荐与预约",
      gradient: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
      role: "campus_student",
      questions: ["推荐适合PCR的仪器", "分子生物学实验室有什么仪器", "我的课题审阅进度"]
    },
    {
      value: "teacher",
      label: "教师助手",
      icon: Promotion,
      desc: "面向教师 · 课题审阅与课程管理",
      gradient: "linear-gradient(135deg, #f6d365 0%, #fda085 100%)",
      role: "campus_teacher",
      questions: ["待审阅的课题有哪些", "有哪些课程信息", "查看实验室仪器列表"]
    },
    {
      value: "admin",
      label: "管理员助手",
      icon: Monitor,
      desc: "面向管理员 · 全局数据概览",
      gradient: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
      role: "campus_admin",
      questions: ["系统整体数据概览", "维修工单情况", "所有预约记录"]
    },
    {
      value: "equipment-recommend",
      label: "仪器推荐",
      icon: Tickets,
      desc: "仪器推荐专家 · 根据需求推荐仪器",
      gradient: "linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)",
      role: "all",
      questions: ["推荐适合剖离实验的仪器", "最新型号的显微镜", "比较不同仪器特点"]
    },
    {
      value: "topic-review",
      label: "课题审阅",
      icon: Connection,
      desc: "课题审阅助手 · 审阅建议与统计",
      gradient: "linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)",
      role: "all",
      questions: ["待审阅课题列表", "已通过课题统计", "按导师查询课题"]
    },
  ];

const agents = computed(() => {
  const role = userStore.userRole;
  return allAgents.filter(a => a.role === "all" || a.role === role);
})
const currentAgent = computed(() => agents.value.find(a => a.value === activeAgent.value))

function switchAgent(value: string) {
  activeAgent.value = value
  messages.value = []
  inputText.value = ""
  streamingText.value = ""
}

function clearMessages() {
  messages.value = []
  streamingText.value = ""
}

function formatTime() {
  const d = new Date()
  return String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0')
}

function renderContent(text: string) {
  if (!text) return ""
  const escaped = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  let html = escaped
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\`([^\`]+)\`/g, "<code>$1</code>")
    .replace(/\n/g, "<br>")
  return html
}

async function askQuestion(q: string) {
  inputText.value = q
  await sendMessage()
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || thinking.value) return
  inputText.value = ""

  msgIdCounter++
  messages.value.push({
    id: msgIdCounter,
    role: "user",
    content: text,
    time: formatTime()
  })
  scrollToBottom()

  thinking.value = true
  streamingText.value = ""

  try {
    const agentMap: Record<string, string> = {
      general: 'agentGeneral',
      student: 'agentStudent',
      teacher: 'agentTeacher',
      admin: 'agentAdmin',
      'equipment-recommend': 'agentEquipmentRecommend',
      'topic-review': 'agentTopicReview'
    }
    const key = agentMap[activeAgent.value] || 'chat'
    const apiFn = key === 'chat'
      ? (data: any) => analysisApi.chat(data)
      : (data: any) => (analysisApi as any)[key](data)

    const res = await apiFn({ message: text })
    const reply = res?.data?.reply || res?.data?.content || res?.data?.result || res?.data?.response || JSON.stringify(res?.data || '已收到您的消息')
    msgIdCounter++
    messages.value.push({
      id: msgIdCounter,
      role: "assistant",
      content: reply,
      time: formatTime()
    })
    scrollToBottom()
  } catch (e: any) {
    const errMsg = e?.response?.data?.message || e?.message || '请求失败'
    msgIdCounter++
    messages.value.push({
      id: msgIdCounter,
      role: "assistant",
      content: '抱歉，发生了一些错误: ' + errMsg,
      time: formatTime()
    })
  } finally {
    thinking.value = false
    streamingText.value = ""
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      setTimeout(() => {
        messagesRef.value!.scrollTo({ top: messagesRef.value!.scrollHeight, behavior: 'smooth' })
      }, 80)
    }
  })
}

onMounted(() => {
  // Ready
})
</script>

<style scoped lang="scss">
.ai-chat {
  height: calc(100vh - 80px);
  padding: 12px;
  background: rgba(255,255,255,0.03);
}
.chat-container {
  display: flex;
  height: 100%;
  background: rgba(255,255,255,0.04);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}
/* Agent Sidebar */
.agent-sidebar {
  width: 240px;
  min-width: 240px;
  background: rgba(255,255,255,0.03);
  display: flex;
  flex-direction: column;
  border-right: 1px solid #eef0f4;
}
.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 18px 16px;
  .sidebar-logo {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    color: #fff;
  }
  .sidebar-title {
    font-size: 16px;
    font-weight: 600;
    color: #1a1a2e;
  }
}
.agent-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 10px;
  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }
}
.agent-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 10px;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
  &:hover { background: rgba(255,255,255,0.08); }
  &.active {
    background: rgba(255,255,255,0.04);
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
}
.agent-card-icon {
  width: 36px; height: 36px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.agent-card-info {
  flex: 1;
  min-width: 0;
  .agent-card-name {
    font-size: 13px;
    font-weight: 500;
    color: #1a1a2e;
    line-height: 1.4;
  }
  .agent-card-desc {
    font-size: 11px;
    color: rgba(255,255,255,0.4);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.3;
    margin-top: 1px;
  }
}
.agent-card-indicator {
  width: 4px; height: 24px;
  background: #667eea;
  border-radius: 4px;
  position: absolute;
  right: -10px;
  top: 50%;
  transform: translateY(-50%);
}
.sidebar-footer {
  padding: 14px 18px;
  border-top: 1px solid #eef0f4;
  .footer-text { font-size: 11px; color: rgba(255,255,255,0.35); }
}
/* Chat Main */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: rgba(255,255,255,0.03);
}
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  background: rgba(255,255,255,0.04);
  border-bottom: 1px solid #eef0f4;
  .header-left { display: flex; align-items: center; gap: 12px; }
  .header-avatar {
    width: 40px; height: 40px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
  }
  .header-info {
    .header-title { font-size: 16px; font-weight: 600; color: #1a1a2e; }
    .header-status {
      font-size: 12px; color: rgba(255,255,255,0.4);
      display: flex; align-items: center; gap: 5px;
      margin-top: 2px;
    }
  }
  .header-action-btn { color: rgba(255,255,255,0.4); &:hover { color: #818cf8; background: rgba(255,255,255,0.04); } }
}
.status-dot {
  width: 6px; height: 6px;
  background: #52c41a;
  border-radius: 50%;
  display: inline-block;
}
/* Messages */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
  &::-webkit-scrollbar { width: 6px; }
  &::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }
  &::-webkit-scrollbar-track { background: transparent; }
}
/* Welcome Screen */
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  position: relative;
  overflow: hidden;
  padding: 40px 20px;
}
.welcome-bg-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
  .shape {
    position: absolute;
    border-radius: 50%;
    opacity: 0.06;
  }
  .s1 { width: 300px; height: 300px; background: #667eea; top: -80px; right: -60px; }
  .s2 { width: 200px; height: 200px; background: rgba(118,75,162,0.3); bottom: -40px; left: -40px; }
  .s3 { width: 150px; height: 150px; background: #43e97b; bottom: 30%; right: 10%; }
}
.welcome-icon-wrapper {
  position: relative;
  margin-bottom: 20px;
}
.welcome-icon-ring {
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  border: 2px solid rgba(102, 126, 234, 0.2);
  animation: ring-pulse 2s ease-in-out infinite;
}
@keyframes ring-pulse {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.15); opacity: 0.2; }
}
.welcome-icon {
  width: 72px; height: 72px;
  border-radius: 20px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25);
}
.welcome-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin: 0 0 8px; }
.welcome-desc { font-size: 14px; color: rgba(255,255,255,0.4); margin: 0 0 28px; text-align: center; }
.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 500px;
}
.suggestion-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 20px;
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  font-size: 13px;
  color: rgba(255,255,255,0.7) !important;
  cursor: pointer;
  transition: all 0.2s ease;
  &:hover {
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #818cf8 !important;
    background: rgba(255,255,255,0.05) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.12);
  }
}
/* Message Rows */
.message-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: msg-fade-in 0.3s ease;
  &.user {
    flex-direction: row-reverse;
    .message-meta { justify-content: flex-end; }
    .message-bubble {
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      color: #fff;
      border-top-right-radius: 4px;
    }
  }
}
@keyframes msg-fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.message-avatar { flex-shrink: 0; }
.user-avatar {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 600; color: #fff;
}
.ai-avatar {
  width: 36px; height: 36px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
}
.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 4px;
  .message-sender { font-size: 12px; font-weight: 500; color: rgba(255,255,255,0.6); }
  .message-time { font-size: 11px; color: rgba(255,255,255,0.35); }
}
.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  border-top-left-radius: 4px;
  background: rgba(255,255,255,0.04);
  color: rgba(255,255,255,0.85);
  border: 1px solid rgba(255,255,255,0.08);
  line-height: 1.7;
  font-size: 14px;
  word-break: break-word;
  box-shadow: 0 1px 4px rgba(0,0,0,0.02);
  :deep(code) {
    background: rgba(255,255,255,0.04);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-family: 'SF Mono', 'Fira Code', monospace;
    color: #f87171;
  }
  :deep(strong) { font-weight: 600; }
}
/* Thinking Indicator */
.thinking-bubble {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  min-height: 40px;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.thinking-bar { display: flex; gap: 4px; padding: 4px 0; }
.dot-pulse {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  animation: dot-pulse 1.4s ease-in-out infinite both;
  &:nth-child(1) { animation-delay: 0s; }
  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}
@keyframes dot-pulse {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
.cursor-blink {
  animation: blink-cursor 0.7s step-end infinite;
  color: #818cf8;
  font-weight: 300;
}
@keyframes blink-cursor { 50% { opacity: 0; } }
/* Input Area */
.input-area {
  padding: 16px 24px 20px;
  background: rgba(255,255,255,0.04);
  border-top: 1px solid #eef0f4;
}
.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  :deep(.el-textarea__inner) {
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.12);
    padding: 10px 14px;
    font-size: 14px;
    line-height: 1.6;
    resize: none;
    transition: all 0.2s;
    box-shadow: none;
    &:focus {
      border-color: #818cf8;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
  }
}
.send-btn {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  flex-shrink: 0;
  margin-bottom: 2px;
  transition: all 0.2s;
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 14px rgba(102, 126, 234, 0.35);
  }
  &:disabled { background: rgba(255,255,255,0.15); }
}
.input-tip {
  display: flex;
  justify-content: flex-end;
  margin-top: 6px;
  padding: 0 4px;
  span { font-size: 11px; color: rgba(255,255,255,0.3); }
}
</style>

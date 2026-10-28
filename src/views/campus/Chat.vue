<template>
  <div class="chat-page page-container">
    <el-card class="chat-card">
      <div class="chat-layout">
        <div class="conversation-list">
          <div class="list-header">
            <el-radio-group v-model="listTab" size="small" style="width: 100%;">
              <el-radio-button value="chats">会话</el-radio-button>
              <el-radio-button value="teachers">老师</el-radio-button>
              <el-radio-button value="students">学生</el-radio-button>
            </el-radio-group>
          </div>
          <div v-if="listTab === 'chats'" class="list-body">
            <div v-for="conv in chatStore.conversations" :key="conv.id"
              :class="['conv-item', { active: chatStore.currentConversation?.id === conv.id }]"
              @click="selectConversation(conv)">
              <el-avatar :size="40" :src="getConvAvatar(conv)" style="flex-shrink: 0;">{{ conv.name?.charAt(0) || '?'  }}</el-avatar>
              <div class="conv-info">
                <div class="conv-name">{{ getConvDisplayName(conv) }}</div>
                <div class="conv-last text-ellipsis">{{ conv.lastMessage || '暂无消息' }}</div>
              </div>
              <el-badge v-if="conv.unreadCount > 0" :value="conv.unreadCount" :max="99" />
              <el-icon class="conv-delete-btn" title="删除\u4f1a\u8bdd" @click.stop="confirmDeleteConv(conv)"><Delete /></el-icon>
            </div>
            <el-empty v-if="!chatStore.conversations.length" description="暂无会话" :image-size="60" />
          </div>
          <div v-if="listTab === 'teachers'" class="list-body">
            <el-input v-model="teacherSearch" placeholder="搜索老师" clearable size="small" style="margin: 8px;" />
            <div v-for="teacher in filteredTeachers" :key="teacher.id" class="conv-item" @click="startChatWithTeacher(teacher)">
              <el-avatar :size="40" :src="teacher.avatar" style="background: #409eff; flex-shrink: 0;">{{ teacher.name?.charAt(0) }}</el-avatar>
              <div class="conv-info">
                <div class="conv-name">{{ teacher.name }}</div>
                <div class="conv-last">{{ teacher.specialty || teacher.title || '在线老师' }}</div>
              </div>
              <el-icon color="#0d7377"><ChatLineSquare /></el-icon>
            </div>
            <el-empty v-if="!filteredTeachers.length" description="暂无老师" :image-size="60" />
          </div>
          <div v-else-if="listTab === 'students'" class="list-body">
            <el-input v-model="studentSearch" placeholder="搜索学生" clearable size="small" style="margin: 8px;" />
            <div v-for="s in filteredStudents" :key="s.id" class="conv-item" @click="startChatWithTeacher(s)">
              <el-avatar :size="40" :src="s.avatar" style="background: #67c23a; flex-shrink: 0;">{{ s.name?.charAt(0) }}</el-avatar>
              <div class="conv-info">
                <div class="conv-name">{{ s.name }}</div>
                <div class="conv-last">{{ s.username || '同学' }}</div>
              </div>
              <el-icon color="#67c23a"><ChatLineSquare /></el-icon>
            </div>
            <el-empty v-if="!filteredStudents.length" description="暂无学生" :image-size="60" />
          </div>
        </div>
        <div class="chat-area">
          <div v-if="chatStore.currentConversation" class="chat-main">
            <div class="chat-header">
              <div style="display:flex;align-items:center;gap:8px;flex:1">
                <span>{{ getConvDisplayName(chatStore.currentConversation) }}</span>
                <el-tag size="small" type="success">在线</el-tag>
              </div>
              <div style="display:flex;gap:8px">
                <button class="action-btn" title="语音通话" @click="startVoiceCall">
                  <el-icon :size="18"><Phone /></el-icon><span>语音</span>
                </button>
                <button class="action-btn" title="视频通话" @click="startVideoCall">
                  <el-icon :size="18"><VideoCamera /></el-icon><span>视频</span>
                </button>
              </div>
            </div>
            <div class="messages" ref="messagesRef">
              <div v-for="msg in chatStore.messages" :key="msg.id" :class="['msg-row', msg.senderId === userId ? 'self' : 'other']">
                <el-avatar v-if="msg.senderId !== userId" :size="36" :src="msg.senderAvatar" style="background: #409eff; flex-shrink: 0;">{{ (msg.senderName || '?').charAt(0) }}</el-avatar>
                <div class="msg-bubble">
                  <div v-if="msg.messageType === 'text'" class="msg-content">{{ msg.content }}</div>
                  <div v-else-if="msg.messageType === 'image'" class="msg-content">
                    <img :src="msg.content" class="msg-img" @click="previewImage(msg.content)" />
                  </div>
                  <div v-else-if="msg.messageType === 'file'" class="file-msg" @click="downloadFile(msg)">
                    <el-icon :size="24"><Folder /></el-icon>
                    <div class="file-info">
                      <span class="file-name">{{ msg.fileName || '文件' }}</span>
                      <span class="file-size">{{ formatFileSize(msg.fileSize) }}</span>
                    </div>
                    <el-icon class="download-icon"><Download /></el-icon>
                  </div>
                  <div v-else-if="msg.messageType === 'voice'" class="msg-content voice-msg">
                    <el-icon><Microphone /></el-icon><span>{{ msg.duration || 0 }}"</span>
                  </div>
                  <div v-else class="msg-content">{{ msg.content }}</div>
                  <div class="msg-time">{{ formatTime(msg.createTime) }}</div>
                </div>
                <el-avatar v-if="msg.senderId === userId" :size="36" :src="userStore.userInfo?.avatar" style="background: #409eff; flex-shrink: 0;">{{ (msg.senderName || '?').charAt(0) }}</el-avatar>
              </div>
            </div>
            <div class="input-area">
              <div class="input-toolbar">
                <input ref="imageInputRef" type="file" accept="image/*" style="display:none" @change="onImageSelected" />
                <input ref="fileInputRef" type="file" style="display:none" @change="onFileSelected" />
                <button class="tool-btn" title="图片" :disabled="uploading" @click="triggerImageUpload"><el-icon><Picture /></el-icon></button>
                <button class="tool-btn" title="文件" :disabled="uploading" @click="triggerFileUpload"><el-icon><Folder /></el-icon></button>
                <span v-if="uploading" class="uploading-hint">上传中..</span>
              </div>
              <div class="input-row">
                <el-input v-model="inputText" type="textarea" :rows="2" placeholder="输入消息..." resize="none" @keydown.enter.exact.prevent="sendMsg" />
                <RippleButton custom-class="send-btn" ripple-color="rgba(64,158,255,0.3)" :disabled="!inputText.trim() || uploading" @click="sendMsg">发送</RippleButton>
              </div>
            </div>
          </div>
          <div v-else class="chat-empty">
            <el-icon :size="60" color="#dcdfe6"><ChatLineSquare /></el-icon>
            <p>选择一个老师开始沟通</p>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Image Preview -->
    <el-dialog v-model="showImagePreview" title="图片预览" width="auto" :close-on-click-modal="true" destroy-on-close>
      <img :src="previewUrl" style="max-width:80vw;max-height:80vh;border-radius:8px;" />
    </el-dialog>

    <!-- Incoming Call -->
    <transition name="slide-fade">
      <div v-if="incomingCall.show" class="incoming-call-overlay">
        <div class="incoming-call-card">
          <div class="call-avatar-lg" :style="{ background: getAvatarColor(incomingCall.name) }">{{ incomingCall.name?.charAt(0) || '?' }}</div>
          <div class="incoming-call-name">{{ incomingCall.name }}</div>
          <div class="incoming-call-type">{{ incomingCall.type === 'video' ? '视频通话' : '语音通话' }}</div>
          <div class="incoming-call-actions">
            <button class="call-btn reject" @click="rejectIncomingCall"><el-icon :size="28"><Close /></el-icon></button>
            <button class="call-btn accept" @click="acceptIncomingCall"><el-icon :size="28"><PhoneFilled /></el-icon></button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Delete Confirm Dialog -->
    <el-dialog v-model="showDeleteDialog" title="删除\u4f1a\u8bdd" width="360px" :close-on-click-modal="false">
      <p style="margin-bottom:16px;">确定要删除与 <strong>{{ deleteTarget?.name }}</strong> 的会话吗？</p>
      <el-checkbox v-model="deleteMessagesToo">同时删除所有聊天记录</el-checkbox>
      <template #footer>
        <el-button @click="showDeleteDialog = false">取消</el-button>
        <el-button type="danger" @click="doDeleteConv">确定删除</el-button>
      </template>
    </el-dialog>

    <!-- Call Dialog -->
    <el-dialog v-model="showCallDialog" :title="callType === 'video' ? '视频通话' : '语音通话'"
      :width="callType === 'video' ? '700px' : '400px'"
      :close-on-click-modal="false" :show-close="false" destroy-on-close class="call-dialog-wrapper">
      <div v-if="callType === 'video'" class="video-call-container">
        <div class="remote-video-container">
          <video v-if="remoteStream" ref="remoteVideoRef" autoplay playsinline class="remote-video"></video>
          <div v-else class="remote-placeholder">
            <div class="call-avatar-lg" :style="{ background: getAvatarColor(chatStore.currentConversation?.name) }">{{ chatStore.currentConversation?.name?.charAt(0) || '?' }}</div>
            <div class="call-name-text">{{ chatStore.currentConversation?.name }}</div>
            <div class="call-status-text">{{ callStateText }}</div>
          </div>
        </div>
        <div class="local-video-container">
          <video v-if="localStream" ref="localVideoRef" autoplay playsinline muted class="local-video"></video>
          <div v-else class="local-placeholder"><div class="local-avatar"><el-icon :size="40" color="#fff"><UserFilled /></el-icon></div></div>
        </div>
        <div class="call-controls">
          <button class="ctrl-btn" :class="{ active: !micEnabled }" @click="toggleMic"><el-icon :size="22"><Microphone /></el-icon></button>
          <button class="ctrl-btn" :class="{ active: !cameraEnabled }" @click="toggleCamera"><el-icon :size="22"><VideoCamera /></el-icon></button>
          <button class="ctrl-btn hangup" @click="endCall"><el-icon :size="28"><PhoneFilled /></el-icon></button>
        </div>
      </div>
      <div v-else class="voice-call-container">
        <div class="call-avatar-lg" :style="{ background: getAvatarColor(chatStore.currentConversation?.name) }">{{ chatStore.currentConversation?.name?.charAt(0) || '?' }}</div>
        <div class="call-name-text">{{ chatStore.currentConversation?.name }}</div>
        <div class="call-status-text">{{ callStateText }}</div>
        <div class="call-timer" v-if="callTimer > 0">{{ formatCallTimer(callTimer) }}</div>
        <div class="call-controls">
          <button class="ctrl-btn" :class="{ active: !micEnabled }" @click="toggleMic"><el-icon :size="22"><Microphone /></el-icon></button>
          <button class="ctrl-btn hangup" @click="endCall"><el-icon :size="28"><PhoneFilled /></el-icon></button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'
import { chatApi, fileApi } from '@/api'
import { get } from '@/utils/request'
import { ElMessage } from 'element-plus'
import RippleButton from '@/components/RippleButton.vue'
import { wsClient } from '@/utils/websocket'
import { webrtcManager, type CallType } from '@/utils/webrtc'
import dayjs from 'dayjs'

const chatStore = useChatStore()
const userStore = useUserStore()
const userId = computed(() => userStore.userInfo?.userId || userStore.userInfo?.id || 0)
const isTeacher = computed(() => userStore.userRole === 'campus_teacher')
const messagesRef = ref<HTMLElement>()
const inputText = ref('')
const listTab = ref('chats')
const teacherSearch = ref('')
const studentSearch = ref('')
const students = ref<any[]>([])
const teachers = ref<any[]>([])
const uploading = ref(false)
const showDeleteDialog = ref(false)
const deleteTarget = ref<any>(null)
const deleteMessagesToo = ref(false)
const imageInputRef = ref<HTMLInputElement>()
const fileInputRef = ref<HTMLInputElement>()
const showImagePreview = ref(false)
const previewUrl = ref('')
const showCallDialog = ref(false)
const callType = ref<CallType>('voice')
const callStateText = ref('')
const callTimer = ref(0)
const micEnabled = ref(true)
const cameraEnabled = ref(true)
const localStream = ref<MediaStream | null>(null)
const remoteStream = ref<MediaStream | null>(null)
const localVideoRef = ref<HTMLVideoElement>()
const remoteVideoRef = ref<HTMLVideoElement>()
let callTimerInterval: any = null
const incomingCall = ref<{ show: boolean; fromId: number; conversationId: number; type: CallType; name: string }>({ show: false, fromId: 0, conversationId: 0, type: 'voice', name: '' })
const sentMsgIds = new Set<number>()

onMounted(() => {
  chatStore.fetchConversations()
  fetchTeachers()
  if (userId.value) {
    webrtcManager.init(userId.value)
    webrtcManager.setCallbacks({
      onIncomingCall: (fromId, type, conversationId) => {
        const conv = chatStore.conversations.find((c: any) => c.id === conversationId)
        incomingCall.value = { show: true, fromId, conversationId, type, name: conv?.name || `用户${fromId}` }
      },
      onCallEnded: () => { incomingCall.value.show = false; stopCallTimer(); remoteStream.value = null; localStream.value = null; showCallDialog.value = false }
    })
    wsClient.connect(userId.value)
    wsClient.on('message', (data) => {
      if (sentMsgIds.has(data.id)) { sentMsgIds.delete(data.id); return }
      chatStore.addMessage(data)
      nextTick(() => { if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight })
    })
    wsClient.on('*', () => { chatStore.fetchConversations() })
  }
})

async function fetchTeachers() {
  try {
    const res1: any = await get('/user/campus/teacher/list', { pageNum: 1, pageSize: 100 })
    const data1 = res1.data
    teachers.value = (data1?.records || data1 || []).map((d: any) => ({ id: d.id, name: d.realName || d.name || '老师', username: d.username || '', title: d.title || '', specialty: d.specialty || d.department || '', avatar: d.avatar || '' }))
  } catch { teachers.value = [] }
  try {
    const res2: any = await get('/user/campus/student/list', { pageNum: 1, pageSize: 100 })
    const data2 = res2.data
    students.value = (data2?.records || data2 || []).map((d: any) => ({ id: d.id, name: d.realName || d.name || '学生', username: d.username || '', title: d.title || '', specialty: d.specialty || d.department || '', avatar: d.avatar || '' }))
  } catch { students.value = [] }
}

const contactMap = computed(() => {
  const map: Record<number, any> = {}
  ;[...teachers.value, ...students.value].forEach(c => { map[c.id] = c })
  return map
})

const filteredTeachers = computed(() => {
  if (!teacherSearch.value) return teachers.value
  const kw = teacherSearch.value.toLowerCase()
  return teachers.value.filter((d: any) => (d.realName || d.name || '').toLowerCase().includes(kw) || (d.department || '').toLowerCase().includes(kw) || (d.title || '').toLowerCase().includes(kw))
})

const filteredStudents = computed(() => {
  if (!studentSearch.value) return students.value
  const kw = studentSearch.value.toLowerCase()
  return students.value.filter((d: any) => (d.realName || d.name || '').toLowerCase().includes(kw) || (d.username || '').toLowerCase().includes(kw))
})

async function selectConversation(conv: any) {
  chatStore.currentConversation = conv
  await chatStore.fetchMessages(conv.id)
  await chatStore.markAsRead(conv.id)
  conv.unreadCount = 0
  await chatStore.fetchConversations()
  nextTick(() => { if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight })
}

async function startChatWithTeacher(teacher: any) {
  const existing = chatStore.conversations.find((c: any) => c.name === teacher.name || (c.memberIds && c.memberIds.includes(teacher.id)))
  if (existing) { await selectConversation(existing); listTab.value = 'chats'; return }
  try {
    await chatApi.createConversation({ type: 'private', memberIds: [teacher.id], name: teacher.name })
    await chatStore.fetchConversations()
    const conv = chatStore.conversations.find((c: any) => c.name === teacher.name)
    if (conv) await selectConversation(conv)
    listTab.value = 'chats'
  } catch { ElMessage.error('创建会话失败') }
}

async function sendMsg() {
  if (!inputText.value.trim() || !chatStore.currentConversation) return
  const text = inputText.value.trim()
  inputText.value = ''
  try {
    const sentMsg = await chatStore.sendMessage({ conversationId: chatStore.currentConversation.id, messageType: 'text', content: text })
    if (sentMsg && sentMsg.id) { sentMsgIds.add(sentMsg.id); chatStore.addMessage(sentMsg); nextTick(() => { if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight }) }
  } catch { ElMessage.error('发送失败') }
}

function triggerImageUpload() { imageInputRef.value?.click() }
function triggerFileUpload() { fileInputRef.value?.click() }
async function onImageSelected(e: Event) { const input=e.target as HTMLInputElement; const file=input?.files?.[0]; if(!file) return; await uploadAndSend(file,'image'); input.value='' }
async function onFileSelected(e: Event) { const input=e.target as HTMLInputElement; const file=input?.files?.[0]; if(!file) return; await uploadAndSend(file,'file'); input.value='' }
async function uploadAndSend(file: File, messageType: string) {
  if (!chatStore.currentConversation) return
  uploading.value = true
  try {
    const formData = new FormData(); formData.append('file', file)
    const res: any = await fileApi.upload(formData)
    const fileData = res.data
    if (!fileData?.url) { ElMessage.error('上传失败'); return }
    const sentMsg = await chatStore.sendMessage({ conversationId: chatStore.currentConversation.id, messageType, content: fileData.url, fileName: fileData.originalName || file.name, fileSize: fileData.fileSize || file.size })
    if (sentMsg?.id) { sentMsgIds.add(sentMsg.id); chatStore.addMessage(sentMsg); nextTick(() => { if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight }) }
    await chatStore.fetchConversations()
  } catch { ElMessage.error('上传发送失败') } finally { uploading.value = false }
}
function previewImage(url: string) { previewUrl.value = url; showImagePreview.value = true }
function downloadFile(msg: any) { window.open(msg.content, '_blank') }
function formatTime(time: any) { if (!time) return ''; return dayjs(time).format('HH:mm') }
function formatFileSize(bytes: number) { if (!bytes) return ''; if (bytes<1024) return bytes+' B'; if (bytes<1024*1024) return (bytes/1024).toFixed(1)+' KB'; return (bytes/1024/1024).toFixed(1)+' MB' }
function formatCallTimer(seconds: number) { return `${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}` }

function confirmDeleteConv(conv: any) {
  deleteTarget.value = conv
  deleteMessagesToo.value = false
  showDeleteDialog.value = true
}

async function doDeleteConv() {
  if (!deleteTarget.value) return
  try {
    await chatApi.deleteConversation(deleteTarget.value.id, deleteMessagesToo.value)
    await chatStore.fetchConversations()
    if (chatStore.currentConversation?.id === deleteTarget.value.id) {
      chatStore.$patch({ currentConversation: null })
      chatStore.$patch({ messages: [] })
    }
    showDeleteDialog.value = false
    deleteTarget.value = null
    ElMessage.success('\u5df2\u5220\u9664')
  } catch (e: any) { ElMessage.error(e?.response?.data?.msg || e?.message || '删除失败') }
}

function getConvDisplayName(conv: any) {
  if (!conv) return '师生沟通'
  // 对于私聊对话，始终显示对方参与者的名字
  if (conv.type === 'private' && conv.members?.length && contactMap.value) {
    const otherMember = conv.members.find((m: any) => m.userId !== userId.value)
    if (otherMember && contactMap.value[otherMember.userId]) {
      return contactMap.value[otherMember.userId].name
    }
  }
  return conv.name || '师生沟通'
}

function getConvAvatar(conv: any) {
    if (conv.avatar) return conv.avatar
    if (conv.type === 'private' || conv.type === 'single') {
      const other = conv.members?.find((m: any) => m.userId !== userId.value)
      if (other && contactMap.value?.[other.userId]?.avatar) return contactMap.value[other.userId].avatar
    }
    return ''
  }
function getAvatarColor(name: string) { const clrs=['#409eff','#67c23a','#e6a23c','#f56c6c','#909399','#0d7377','#9b59b6','#1abc9c']; let h=0; for(let i=0;i<(name||'').length;i++) h=name.charCodeAt(i)+((h<<5)-h); return clrs[Math.abs(h)%clrs.length] }

async function startVoiceCall() { if(!chatStore.currentConversation) return; callType.value='voice'; await initCall('voice') }
async function startVideoCall() { if(!chatStore.currentConversation) return; callType.value='video'; await initCall('video') }
async function initCall(type: CallType) {
  callType.value=type; showCallDialog.value=true; callStateText.value='正在呼叫...'; callTimer.value=0; micEnabled.value=true; cameraEnabled.value=true
  webrtcManager.setCallbacks({
    onRemoteStream: (s)=>{ remoteStream.value=s; nextTick(()=>{ if(remoteVideoRef.value) remoteVideoRef.value.srcObject=s }) },
    onCallStateChange: (s)=>{ if(s==='connected'){ callStateText.value='通话中'; startCallTimer() } else if(s==='calling'){ callStateText.value='正在呼叫...' } },
    onCallEnded: ()=>{ stopCallTimer(); remoteStream.value=null; localStream.value=null; showCallDialog.value=false; callStateText.value='' },
    onError: (e)=>{ ElMessage.error(e); showCallDialog.value=false }
  })
  await webrtcManager.startCall(chatStore.currentConversation.id, type)
  localStream.value=webrtcManager.getLocalStream()
  nextTick(()=>{ if(localVideoRef.value&&localStream.value) localVideoRef.value.srcObject=localStream.value })
}
function acceptIncomingCall() { const d=incomingCall.value; d.show=false; callType.value=d.type; showCallDialog.value=true; callStateText.value='连接中..'; callTimer.value=0; micEnabled.value=true; cameraEnabled.value=true
  webrtcManager.setCallbacks({
    onRemoteStream: (s)=>{ remoteStream.value=s; nextTick(()=>{ if(remoteVideoRef.value) remoteVideoRef.value.srcObject=s }) },
    onCallStateChange: (s)=>{ if(s==='connected'){ callStateText.value='通话中'; startCallTimer() } },
    onCallEnded: ()=>{ stopCallTimer(); remoteStream.value=null; localStream.value=null; showCallDialog.value=false; callStateText.value='' },
    onError: (e)=>{ ElMessage.error(e); showCallDialog.value=false }
  })
  webrtcManager.acceptCall(d.conversationId, d.type)
  localStream.value=webrtcManager.getLocalStream()
  nextTick(()=>{ if(localVideoRef.value&&localStream.value) localVideoRef.value.srcObject=localStream.value })
}
function rejectIncomingCall() { webrtcManager.rejectCall(incomingCall.value.conversationId); incomingCall.value.show=false }
function endCall() { webrtcManager.endCall(); stopCallTimer(); remoteStream.value=null; localStream.value=null; showCallDialog.value=false }
function toggleMic() { micEnabled.value=webrtcManager.toggleMute() }
function toggleCamera() { cameraEnabled.value=webrtcManager.toggleVideo() }
function startCallTimer() { callTimer.value=0; callTimerInterval=setInterval(()=>{ callTimer.value++ },1000) }
function stopCallTimer() { if(callTimerInterval){ clearInterval(callTimerInterval); callTimerInterval=null } }
</script>

<style scoped lang="scss">
.chat-card { height: calc(100vh - 140px); :deep(.el-card__body) { height: 100%; padding: 0; } }
.chat-layout { display: flex; height: 100%; }
.conversation-list { width: 280px; border-right: 1px solid rgba(255,255,255,0.06); display: flex; flex-direction: column; .list-header { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.06); } .list-body { flex: 1; overflow-y: auto; }
  .conv-item { padding: 12px 16px; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.04); display: flex; align-items: center; gap: 10px;
    &:hover, &.active { background: rgba(99,102,241,0.15); } .conv-info { flex: 1; overflow: hidden; } .conv-name { font-size: 14px; font-weight: 500; } .conv-last { font-size: 12px; color: rgba(255,255,255,0.35); margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; } } }
.chat-area { flex: 1; display: flex; flex-direction: column; }
.chat-main { display: flex; flex-direction: column; height: 100%; }
.chat-header { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.06); display: flex; align-items: center; justify-content: space-between; font-weight: 500; }
.action-btn { display:inline-flex;flex-direction:column;align-items:center;gap:1px;padding:4px 10px;border:1px solid rgba(255,255,255,0.06);border-radius:6px;background:transparent;cursor:pointer;color:rgba(255,255,255,0.45);font-size:10px;transition:all 0.2s; }
.action-btn:hover { background:rgba(99,102,241,0.15);border-color:#818cf8;color:#818cf8; }
.messages { flex:1; overflow-y:auto; padding:16px; background:transparent; .msg-row { display:flex; margin-bottom:16px; align-items:flex-start; gap:8px; } .msg-row.self { flex-direction:row-reverse; } .msg-bubble { max-width:60%; } .msg-content { padding:10px 14px; border-radius:12px; font-size:14px; line-height:1.5; word-break:break-word; } .msg-row.other .msg-content { background:rgba(255,255,255,0.04); color:rgba(255,255,255,0.85); border-top-left-radius:4px; } .msg-row.self .msg-content { background:#6366f1; color:rgba(0,0,0,0.9); border-top-right-radius:4px; } .msg-time { font-size:11px; color:rgba(255,255,255,0.35); margin-top:4px; } .msg-row.self .msg-time { text-align:right; } .msg-img { max-width:200px; border-radius:8px; cursor:pointer; transition:transform 0.2s; } .msg-img:hover { transform:scale(1.05); } .file-msg { display:flex; align-items:center; gap:8px; cursor:pointer; padding:4px 0; } .file-info { flex:1; display:flex; flex-direction:column; gap:2px; } .file-name { font-size:13px; font-weight:500; color:#818cf8; } .file-size { font-size:11px; color:rgba(255,255,255,0.35); } .download-icon { color:#818cf8; opacity:0.6; } .voice-msg { display:flex; align-items:center; gap:6px; } }
.input-area { padding:12px 16px; border-top:1px solid rgba(255,255,255,0.06); background:rgba(255,255,255,0.04); }
.input-toolbar { display:flex; gap:8px; align-items:center; margin-bottom:8px; }
.tool-btn { width:32px; height:32px; border-radius:8px; border:1px solid rgba(255,255,255,0.06); background:transparent; cursor:pointer; display:flex; align-items:center; justify-content:center; color:rgba(255,255,255,0.45); transition:all 0.2s; }
.tool-btn:hover { background:rgba(255,255,255,0.08); color:#818cf8; }
.tool-btn:disabled { opacity:0.4; cursor:not-allowed; }
.uploading-hint { font-size:12px; color:rgba(255,255,255,0.35); }
.input-row { display:flex; gap:8px; }
:deep(.send-btn) { margin-top:8px; background:#409eff; color:rgba(0,0,0,0.9); border-color:#409eff; &:hover { border-color:#66b1ff; color:#66b1ff; } } :deep(.send-btn.is-disabled) { opacity:0.5; }
.chat-empty { flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; color:rgba(255,255,255,0.35); p { margin-top:12px; } }
.incoming-call-overlay { position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);z-index:9999;display:flex;align-items:center;justify-content:center; }
.incoming-call-card { background:#1a1a2e;border-radius:20px;padding:40px 60px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.5);animation:callPulse 1.5s ease-in-out infinite; }
@keyframes callPulse { 0%,100%{box-shadow:0 20px 60px rgba(0,0,0,0.5)} 50%{box-shadow:0 20px 60px rgba(64,158,255,0.3)} }
.call-avatar-lg { width:80px;height:80px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:rgba(0,0,0,0.9);font-size:32px;font-weight:700;margin:0 auto 16px; }
.incoming-call-name { font-size:22px;font-weight:600;color:rgba(0,0,0,0.9);margin-bottom:8px; }
.incoming-call-type { font-size:14px;color:rgba(255,255,255,0.6);margin-bottom:24px; }
.incoming-call-actions { display:flex;gap:40px;justify-content:center; }
.call-btn.reject { width:56px;height:56px;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;background:#f56c6c;color:rgba(0,0,0,0.9); }
.call-btn.reject:hover { transform:scale(1.1);box-shadow:0 4px 16px rgba(245,108,108,0.4); }
.call-btn.accept { width:56px;height:56px;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;background:#67c23a;color:rgba(0,0,0,0.9); }
.call-btn.accept:hover { transform:scale(1.1);box-shadow:0 4px 16px rgba(103,194,58,0.4); }
.call-dialog-wrapper :deep(.el-dialog__header) { display:none; }
.video-call-container { position:relative;height:450px;background:#1a1a2e;border-radius:12px;overflow:hidden; }
.remote-video-container { width:100%;height:100%; } .remote-video { width:100%;height:100%;object-fit:cover; }
.remote-placeholder { display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:12px; }
.call-name-text { font-size:18px;font-weight:600;color:rgba(0,0,0,0.9); } .call-status-text { font-size:14px;color:rgba(255,255,255,0.6); } .call-timer { font-size:14px;color:rgba(255,255,255,0.6);margin-top:-8px; }
.local-video-container { position:absolute;bottom:80px;right:16px;width:140px;height:180px;border-radius:12px;overflow:hidden;border:2px solid rgba(255,255,255,0.3);background:#2d2d5e; }
.local-video { width:100%;height:100%;object-fit:cover; } .local-placeholder { width:100%;height:100%;display:flex;align-items:center;justify-content:center; }
.voice-call-container { display:flex;flex-direction:column;align-items:center;gap:16px;padding:40px 20px;position:relative;min-height:320px; }
.call-controls { position:absolute;bottom:16px;left:50%;transform:translateX(-50%);display:flex;gap:16px; }
.voice-call-container .call-controls { position:relative;bottom:auto;left:auto;transform:none;margin-top:20px; }
.ctrl-btn { width:48px;height:48px;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.2);color:rgba(0,0,0,0.9);transition:all 0.2s;backdrop-filter:blur(4px); }
.ctrl-btn:hover { background:rgba(255,255,255,0.3); } .ctrl-btn.active { background:#f56c6c; } .ctrl-btn.hangup { width:56px;height:56px;background:#f56c6c; }
.ctrl-btn.hangup:hover { transform:scale(1.1);box-shadow:0 4px 16px rgba(245,108,108,0.4); }
.slide-fade-enter-active { transition:all 0.3s ease-out; } .slide-fade-leave-active { transition:all 0.2s ease-in; }
.slide-fade-enter-from { transform:translateY(-20px);opacity:0; } .slide-fade-leave-to { transform:translateY(20px);opacity:0; }
.conv-item { position: relative; }
.conv-delete-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255,255,255,0.3);
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
  font-size: 14px;
}
.conv-item:hover .conv-delete-btn {
  opacity: 1;
  color: #f56c6c;
}
.conv-delete-btn:hover {
  transform: translateY(-50%) scale(1.2);
}
</style>
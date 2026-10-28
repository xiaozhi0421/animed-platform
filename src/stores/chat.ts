import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatApi } from '@/api'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref<any[]>([])
  const currentConversation = ref<any>(null)
  const messages = ref<any[]>([])
  const unreadCount = ref(0)
  const api = ref(chatApi)

  function setApi(apiModule: any) {
    api.value = apiModule
  }

  async function fetchConversations() {
    const res: any = await api.value.getConversations()
    conversations.value = res.data || []
  }

  async function fetchMessages(conversationId: number, lastMessageId?: number) {
    const res: any = await api.value.getMessages({ conversationId, lastMessageId, pageSize: 30 })
    if (lastMessageId) {
      messages.value = [...(res.data || []), ...messages.value]
    } else {
      messages.value = res.data || []
    }
  }

  async function sendMessage(data: { conversationId: number; messageType: string; content: string }) {
    const res: any = await api.value.sendMessage(data)
    return res.data
  }

  async function fetchUnreadCount() {
    const res: any = await api.value.getUnreadCount()
    unreadCount.value = res.data || 0
  }

  async function markAsRead(conversationId: number) {
    await api.value.markAsRead(conversationId)
    await fetchUnreadCount()
  }

  function addMessage(msg: any) {
    if (currentConversation.value && msg.conversationId === currentConversation.value.id) {
      const exists = messages.value.some(m => m.id === msg.id)
      if (!exists) {
        messages.value.push(msg)
      }
    }
  }

  return { conversations, currentConversation, messages, unreadCount, api, setApi, fetchConversations, fetchMessages, sendMessage, fetchUnreadCount, markAsRead, addMessage }
})
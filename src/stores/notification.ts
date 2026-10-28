import { defineStore } from 'pinia'
import { ref } from 'vue'
import { notificationApi } from '@/api'

export const useNotificationStore = defineStore('notification', () => {
  const unreadCount = ref(0)

  async function fetchUnreadCount() {
    try {
      // Use a short timeout so failed requests don't hang
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 3000)
      const res: any = await notificationApi.getUnreadCount()
      clearTimeout(timeout)
      unreadCount.value = res.data || 0
    } catch (e) {
      // Notification service not available, silently ignore
      unreadCount.value = 0
    }
  }

  async function markAllAsRead() {
    await notificationApi.markAllAsRead()
    unreadCount.value = 0
  }

  function increment() {
    unreadCount.value++
  }

  return { unreadCount, fetchUnreadCount, markAllAsRead, increment }
})

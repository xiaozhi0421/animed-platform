type MessageHandler = (data: any) => void

class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string = ''
  private reconnectCount = 0
  private maxReconnect = 5
  private reconnectTimer: any = null
  private handlers: Map<string, MessageHandler[]> = new Map()
  private heartbeatTimer: any = null

  connect(userId: number) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    this.url = `${protocol}//${window.location.host}/ws`
    this.ws = new WebSocket(this.url)

    this.ws.onopen = () => {
      this.reconnectCount = 0
      this.send({ type: 'auth', fromId: userId })
      this.startHeartbeat()
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        const handlers = this.handlers.get(data.type) || []
        handlers.forEach(handler => handler(data))
        const allHandlers = this.handlers.get('*') || []
        allHandlers.forEach(handler => handler(data))
      } catch (e) {
        console.error('WebSocket消息解析失败', e)
      }
    }

    this.ws.onclose = () => {
      this.stopHeartbeat()
      this.tryReconnect(userId)
    }

    this.ws.onerror = () => {
      this.stopHeartbeat()
    }
  }

  disconnect() {
    this.stopHeartbeat()
    clearTimeout(this.reconnectTimer)
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  on(type: string, handler: MessageHandler) {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, [])
    }
    this.handlers.get(type)!.push(handler)
  }

  off(type: string, handler: MessageHandler) {
    const handlers = this.handlers.get(type)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) handlers.splice(index, 1)
    }
  }

  private tryReconnect(userId: number) {
    if (this.reconnectCount >= this.maxReconnect) return
    this.reconnectTimer = setTimeout(() => {
      this.reconnectCount++
      this.connect(userId)
    }, 3000 * this.reconnectCount)
  }

  private startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'ping' })
    }, 30000)
  }

  private stopHeartbeat() {
    clearInterval(this.heartbeatTimer)
  }
}

export const wsClient = new WebSocketClient()

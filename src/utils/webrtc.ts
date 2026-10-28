import { wsClient } from './websocket'

export type CallType = 'voice' | 'video'
export type CallState = 'idle' | 'calling' | 'ringing' | 'connected' | 'ended'

export interface CallEventCallbacks {
  onRemoteStream?: (stream: MediaStream) => void
  onCallStateChange?: (state: CallState) => void
  onIncomingCall?: (fromId: number, callType: CallType, conversationId: number) => void
  onCallEnded?: (fromId?: number) => void
  onError?: (error: string) => void
}

class WebRTCManager {
  private pc: RTCPeerConnection | null = null
  private localStream: MediaStream | null = null
  private remoteStream: MediaStream | null = null
  private callState: CallState = 'idle'
  private callbacks: CallEventCallbacks = {}
  private userId: number = 0
  private currentConvId: number = 0
  private stunServers: RTCConfiguration = {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' }
    ]
  }

  init(userId: number) {
    this.userId = userId
    // Listen for call signaling messages
    wsClient.on('call_start', (data: any) => {
      if (data.fromId === this.userId) return
      this.currentConvId = data.conversationId
      this.callbacks.onIncomingCall?.(data.fromId, data.extra || 'voice', data.conversationId)
    })
    wsClient.on('call_offer', (data: any) => {
      if (data.fromId === this.userId) return
      this.handleOffer(data)
    })
    wsClient.on('call_answer', (data: any) => {
      if (data.fromId === this.userId) return
      this.handleAnswer(data)
    })
    wsClient.on('call_ice', (data: any) => {
      if (data.fromId === this.userId) return
      this.handleIceCandidate(data)
    })
    wsClient.on('call_end', (data: any) => {
      this.handleRemoteEnd(data)
    })
    wsClient.on('call_accept', (data: any) => {
      if (data.fromId === this.userId) return
      this.callState = 'connected'
      this.callbacks.onCallStateChange?.('connected')
    })
    wsClient.on('call_reject', (data: any) => {
      if (data.fromId === this.userId) return
      this.cleanup()
      this.callbacks.onCallEnded?.(data.fromId)
      this.callbacks.onError?.('对方拒绝了通话')
    })
  }

  setCallbacks(cb: CallEventCallbacks) {
    this.callbacks = cb
  }

  getState(): CallState { return this.callState }
  getRemoteStream(): MediaStream | null { return this.remoteStream }
  getLocalStream(): MediaStream | null { return this.localStream }

  async startCall(conversationId: number, callType: CallType) {
    this.currentConvId = conversationId
    this.callState = 'calling'
    this.callbacks.onCallStateChange?.('calling')

    try {
      const constraints: MediaStreamConstraints = {
        audio: true,
        video: callType === 'video'
      }
      this.localStream = await navigator.mediaDevices.getUserMedia(constraints)
      this.pc = new RTCPeerConnection(this.stunServers)

      // Add local tracks
      this.localStream.getTracks().forEach(track => {
        this.pc!.addTrack(track, this.localStream!)
      })

      // Handle remote stream
      this.pc.ontrack = (event) => {
        this.remoteStream = event.streams[0]
        this.callbacks.onRemoteStream?.(event.streams[0])
      }

      // ICE candidates
      this.pc.onicecandidate = (event) => {
        if (event.candidate) {
          wsClient.send({
            type: 'call_ice',
            conversationId,
            content: JSON.stringify(event.candidate)
          })
        }
      }

      // Create offer
      const offer = await this.pc.createOffer()
      await this.pc.setLocalDescription(offer)
      wsClient.send({
        type: 'call_offer',
        conversationId,
        content: JSON.stringify(offer)
      })

      // Notify the other side
      wsClient.send({
        type: 'call_start',
        conversationId,
        extra: callType
      })

    } catch (e: any) {
      this.cleanup()
      this.callbacks.onError?.('无法访问麦克风/摄像头: ' + e.message)
    }
  }

  async acceptCall(conversationId: number, callType: CallType) {
    this.currentConvId = conversationId
    this.callState = 'connected'
    this.callbacks.onCallStateChange?.('connected')

    try {
      const constraints: MediaStreamConstraints = {
        audio: true,
        video: callType === 'video'
      }
      this.localStream = await navigator.mediaDevices.getUserMedia(constraints)
      this.pc = new RTCPeerConnection(this.stunServers)

      this.localStream.getTracks().forEach(track => {
        this.pc!.addTrack(track, this.localStream!)
      })

      this.pc.ontrack = (event) => {
        this.remoteStream = event.streams[0]
        this.callbacks.onRemoteStream?.(event.streams[0])
      }

      this.pc.onicecandidate = (event) => {
        if (event.candidate) {
          wsClient.send({
            type: 'call_ice',
            conversationId,
            content: JSON.stringify(event.candidate)
          })
        }
      }

    } catch (e: any) {
      this.cleanup()
      this.callbacks.onError?.('无法访问麦克风/摄像头: ' + e.message)
    }
  }

  private async handleOffer(data: any) {
    // Will be handled when acceptCall is triggered
    // Store offer for later use
    if (this.pc && data.content) {
      try {
        const offer = JSON.parse(data.content)
        await this.pc.setRemoteDescription(new RTCSessionDescription(offer))
        const answer = await this.pc.createAnswer()
        await this.pc.setLocalDescription(answer)
        wsClient.send({
          type: 'call_answer',
          conversationId: data.conversationId,
          content: JSON.stringify(answer)
        })
        wsClient.send({ type: 'call_accept', conversationId: data.conversationId })
      } catch (e) {
        console.error('Failed to handle offer', e)
      }
    }
  }

  private async handleAnswer(data: any) {
    if (this.pc && data.content) {
      try {
        const answer = JSON.parse(data.content)
        await this.pc.setRemoteDescription(new RTCSessionDescription(answer))
        this.callState = 'connected'
        this.callbacks.onCallStateChange?.('connected')
      } catch (e) {
        console.error('Failed to handle answer', e)
      }
    }
  }

  private async handleIceCandidate(data: any) {
    if (this.pc && data.content) {
      try {
        const candidate = JSON.parse(data.content)
        await this.pc.addIceCandidate(new RTCIceCandidate(candidate))
      } catch (e) {
        console.error('Failed to add ICE candidate', e)
      }
    }
  }

  private handleRemoteEnd(data: any) {
    this.cleanup()
    this.callbacks.onCallEnded?.(data.fromId)
  }

  toggleMute() {
    if (this.localStream) {
      const audioTrack = this.localStream.getAudioTracks()[0]
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled
        return audioTrack.enabled
      }
    }
    return true
  }

  toggleVideo() {
    if (this.localStream) {
      const videoTrack = this.localStream.getVideoTracks()[0]
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled
        return videoTrack.enabled
      }
    }
    return true
  }

  endCall() {
    if (this.currentConvId) {
      wsClient.send({ type: 'call_end', conversationId: this.currentConvId })
    }
    this.cleanup()
    this.callbacks.onCallEnded?.()
  }

  rejectCall(conversationId: number) {
    wsClient.send({ type: 'call_reject', conversationId })
    this.cleanup()
  }

  private cleanup() {
    if (this.localStream) {
      this.localStream.getTracks().forEach(t => t.stop())
      this.localStream = null
    }
    if (this.pc) {
      this.pc.close()
      this.pc = null
    }
    this.remoteStream = null
    this.callState = 'idle'
  }
}

export const webrtcManager = new WebRTCManager()
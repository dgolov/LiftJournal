const WS_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api')
  .replace(/^http/, 'ws')
  .replace(/\/api$/, '')

const TOKEN_KEY = 'gym_auth_token'

class WsClient {
  constructor() {
    this._ws = null
    this._reconnectDelay = 1000
    this._maxDelay = 30000
    this._pingTimer = null
    this._stopped = false
    this._onNotification = null
  }

  onNotification(fn) {
    this._onNotification = fn
  }

  connect() {
    this._stopped = false
    this._tryConnect()
  }

  disconnect() {
    this._stopped = true
    clearInterval(this._pingTimer)
    if (this._ws) {
      this._ws.onclose = null
      this._ws.close()
      this._ws = null
    }
  }

  _tryConnect() {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token || this._stopped) return

    const url = `${WS_BASE}/api/ws?token=${encodeURIComponent(token)}`
    const ws = new WebSocket(url)
    this._ws = ws

    ws.onopen = () => {
      this._reconnectDelay = 1000
      this._startPing()
    }

    ws.onmessage = (e) => {
      if (e.data === 'pong') return
      try {
        const msg = JSON.parse(e.data)
        if (msg.event === 'notification' && this._onNotification) {
          this._onNotification(msg.data)
        }
      } catch { /* ignore malformed */ }
    }

    ws.onclose = () => {
      clearInterval(this._pingTimer)
      if (!this._stopped) this._scheduleReconnect()
    }

    ws.onerror = () => {
      ws.close()
    }
  }

  _startPing() {
    clearInterval(this._pingTimer)
    this._pingTimer = setInterval(() => {
      if (this._ws?.readyState === WebSocket.OPEN) {
        this._ws.send('ping')
      }
    }, 25000)
  }

  _scheduleReconnect() {
    setTimeout(() => this._tryConnect(), this._reconnectDelay)
    this._reconnectDelay = Math.min(this._reconnectDelay * 2, this._maxDelay)
  }
}

export const wsClient = new WsClient()

import { useEffect, useRef, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const STATUS_LABELS = {
  thinking: 'Thinking',
  calling_tools: 'Checking records',
  answering: 'Writing',
}

function makeId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export default function ChatWidget({ examplePrompts = [] }) {
  const [messages, setMessages] = useState([
    { id: makeId(), role: 'assistant', text: 'How can I help you today?' },
  ])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [status, setStatus] = useState('')
  const [conversationId, setConversationId] = useState(null)
  const listRef = useRef(null)

  useEffect(() => {
    const el = listRef.current
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  }, [messages, status])

  const send = async (textOverride) => {
    const text = (textOverride !== undefined ? textOverride : input).trim()
    if (!text || busy) {
      return
    }
    setInput('')
    setBusy(true)
    setStatus('thinking')
    const userMessage = { id: makeId(), role: 'user', text }
    setMessages((prev) => [...prev, userMessage])
    const assistantId = makeId()
    setMessages((prev) => [...prev, { id: assistantId, role: 'assistant', text: '' }])
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, conversation_id: conversationId }),
      })
      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`)
      }
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let assistantText = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          break
        }
        buffer += decoder.decode(value, { stream: true })
        const blocks = buffer.split('\n\n')
        buffer = blocks.pop() || ''
        for (const block of blocks) {
          for (const line of block.split('\n')) {
            if (!line.startsWith('data:')) {
              continue
            }
            const payload = line.slice(5).trim()
            if (!payload) {
              continue
            }
            let event
            try {
              event = JSON.parse(payload)
            } catch {
              continue
            }
            if (event.type === 'status') {
              setStatus(event.state || '')
            } else if (event.type === 'token') {
              assistantText += event.text
              setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, text: assistantText } : m)))
            } else if (event.type === 'done') {
              if (event.conversation_id) {
                setConversationId(event.conversation_id)
              }
            } else if (event.type === 'error') {
              assistantText = event.text
              setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, text: event.text } : m)))
            }
          }
        }
      }
      setMessages((prev) => prev.map((m) => (m.id === assistantId && !m.text ? { ...m, text: 'The assistant returned an empty reply. Please try again.' } : m)))
    } catch {
      setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, text: 'Something went wrong while contacting support. Please try again.' } : m)))
    } finally {
      setBusy(false)
      setStatus('')
    }
  }

  const onKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      send()
    }
  }

  return (
    <div className="chat-widget">
      <div className="chat-messages" ref={listRef} role="log" aria-live="polite">
        {messages.map((message) => (
          <div key={message.id} className={`message-row ${message.role}`}>
            <div className="message-bubble">{message.text}</div>
          </div>
        ))}
        {status ? (
          <div className="message-row assistant">
            <div className="message-bubble status-bubble">{STATUS_LABELS[status] || 'Working'}</div>
          </div>
        ) : null}
      </div>
      {examplePrompts.length > 0 ? (
        <div className="prompt-row">
          {examplePrompts.map((prompt) => (
            <button key={prompt} type="button" className="prompt-button" onClick={() => send(prompt)} disabled={busy}>
              {prompt}
            </button>
          ))}
        </div>
      ) : null}
      <div className="chat-composer">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={onKeyDown}
          rows={2}
          placeholder="Type your question here"
          disabled={busy}
          aria-label="Message"
        />
        <button type="button" className="button" onClick={() => send()} disabled={busy}>
          Send
        </button>
      </div>
    </div>
  )
}

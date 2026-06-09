import { useState, useRef, useEffect } from "react"

export default function ChatPanel({ sessionId }) {
  const [messages, setMessages] = useState([
    {
      role:    "assistant",
      content: "Hi! I've analyzed both videos. Ask me anything — engagement rates, hook comparison, content strategy, or improvement suggestions.",
      sources: [],
    },
  ])
  const [input, setInput]     = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef             = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: "user", content: input, sources: [] }
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setLoading(true)

    // Add empty assistant message to stream into
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "", sources: [] },
    ])

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({
          session_id: sessionId,
          message:    input,
        }),
      })

      const reader  = res.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text  = decoder.decode(value)
        const lines = text.split("\n")

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          try {
            const data = JSON.parse(line.slice(6))

            if (data.type === "token") {
              setMessages((prev) => {
                const updated = [...prev]
                updated[updated.length - 1].content += data.content
                return updated
              })
            }

            if (data.type === "sources") {
              setMessages((prev) => {
                const updated = [...prev]
                updated[updated.length - 1].sources = data.content
                return updated
              })
            }
          } catch {}
        }
      }
    } catch (e) {
      setMessages((prev) => {
        const updated = [...prev]
        updated[updated.length - 1].content = "Error: " + e.message
        return updated
      })
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="chat-panel">
      <h3>💬 Ask About These Videos</h3>

      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources">
                <p className="sources-title">Sources:</p>
                {msg.sources.map((s, j) => (
                  <div key={j} className="source-chip">
                    📎 Video {s.video_id} — {s.text.slice(0, 80)}...
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-content typing">thinking...</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask anything about the videos... (Enter to send)"
          rows={2}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  )
}
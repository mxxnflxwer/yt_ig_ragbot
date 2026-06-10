import { useState } from "react"
import UrlInput from "./components/UrlInput"
import VideoCard from "./components/VideoCard"
import ChatPanel from "./components/ChatPanel"
import "./App.css"

function App() {
  const [sessionId, setSessionId] = useState(null)
  const [videoA, setVideoA]       = useState(null)
  const [videoB, setVideoB]       = useState(null)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)

  const handleIngest = async (urlA, urlB) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("http://localhost:8000/api/ingest", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ url_a: urlA, url_b: urlB }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || "Ingest failed")
      }
      const data = await res.json()
      setSessionId(data.session_id)
      setVideoA(data.video_a)
      setVideoB(data.video_b)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🎬 RAG Video Analyst</h1>
        <p>Compare any two videos with AI</p>
      </header>

      {!sessionId && (
        <UrlInput onIngest={handleIngest} loading={loading} error={error} />
      )}

      {sessionId && (
        <>
          <div className="video-cards">
            <VideoCard video={videoA} label={`Video A — ${videoA?.platform}`} />
            <VideoCard video={videoB} label={`Video B — ${videoB?.platform}`} />
          </div>
          <ChatPanel sessionId={sessionId} />
        </>
      )}
    </div>
  )
}

export default App
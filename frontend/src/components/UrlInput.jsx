import { useState } from "react"

export default function UrlInput({ onIngest, loading, error }) {
  const [urlA, setUrlA] = useState("")
  const [urlB, setUrlB] = useState("")

  const handleSubmit = () => {
    if (!urlA || !urlB) return
    onIngest(urlA, urlB)
  }

  return (
    <div className="url-input-container">
      <h2>Enter Two Video URLs</h2>
      <p className="url-hint">Supports YouTube vs YouTube, Instagram vs Instagram, or YouTube vs Instagram</p>
      <div className="url-inputs">
        <input
          type="text"
          placeholder="Video A — YouTube or Instagram Reel URL"
          value={urlA}
          onChange={(e) => setUrlA(e.target.value)}
          className="url-field"
        />
        <input
          type="text"
          placeholder="Video B — YouTube or Instagram Reel URL"
          value={urlB}
          onChange={(e) => setUrlB(e.target.value)}
          className="url-field"
        />
      </div>
      <button
        onClick={handleSubmit}
        disabled={loading || !urlA || !urlB}
        className="analyze-btn"
      >
        {loading ? "Analyzing... (this may take a minute)" : "Analyze Videos"}
      </button>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
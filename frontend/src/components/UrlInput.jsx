import { useState } from "react"

export default function UrlInput({ onIngest, loading, error }) {
  const [youtubeUrl, setYoutubeUrl]     = useState("")
  const [instagramUrl, setInstagramUrl] = useState("")

  const handleSubmit = () => {
    if (!youtubeUrl || !instagramUrl) return
    onIngest(youtubeUrl, instagramUrl)
  }

  return (
    <div className="url-input-container">
      <h2>Enter Video URLs</h2>
      <div className="url-inputs">
        <input
          type="text"
          placeholder="YouTube URL"
          value={youtubeUrl}
          onChange={(e) => setYoutubeUrl(e.target.value)}
          className="url-field"
        />
        <input
          type="text"
          placeholder="Instagram Reel URL"
          value={instagramUrl}
          onChange={(e) => setInstagramUrl(e.target.value)}
          className="url-field"
        />
      </div>
      <button
        onClick={handleSubmit}
        disabled={loading || !youtubeUrl || !instagramUrl}
        className="analyze-btn"
      >
        {loading ? "Analyzing... (this may take a minute)" : "Analyze Videos"}
      </button>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
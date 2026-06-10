export default function VideoCard({ video, label }) {
  if (!video) return null

  return (
    <div className="video-card">
      <h3>{label}</h3>
      <div className="video-meta">
        <p><strong>Title</strong>: {video.title}</p>
        <p><strong>Creator</strong>: {video.creator_name}</p>
        <p>
          <strong>{video.platform === "youtube" ? "Subscribers" : "Followers"}</strong>:{" "}
          {video.follower_count != null ? video.follower_count.toLocaleString() : "N/A"}
        </p>
        <p><strong>Platform</strong>: {video.platform}</p>
        <p><strong>Upload Date</strong>: {video.upload_date}</p>
        <p><strong>Duration</strong>: {video.duration_seconds}s</p>
      </div>

      <div className="video-stats">
        <div className="stat">
          <span className="stat-value">{video.views.toLocaleString()}</span>
          <span className="stat-label">Views</span>
        </div>
        <div className="stat">
          <span className="stat-value">{video.likes.toLocaleString()}</span>
          <span className="stat-label">Likes</span>
        </div>
        <div className="stat">
          <span className="stat-value">{video.comments.toLocaleString()}</span>
          <span className="stat-label">Comments</span>
        </div>
        <div className="stat highlight">
          <span className="stat-value">{video.engagement_rate}%</span>
          <span className="stat-label">Engagement</span>
        </div>
      </div>

      {video.hashtags.length > 0 && (
        <div className="hashtags">
          {video.hashtags.slice(0, 5).map((tag, i) => (
            <span key={i} className="tag">{tag}</span>
          ))}
        </div>
      )}

      <p className="chunks">
        📦 {video.transcript_chunks} transcript chunks indexed
      </p>
    </div>
  )
}
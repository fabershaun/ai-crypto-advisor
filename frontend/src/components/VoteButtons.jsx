import api from '../services/api'

function VoteButtons({ contentType, contentId, vote, onVote }) {
  const handleVote = async (value) => {
    try {
      await api.post('/votes', {
        content_type: contentType,
        content_id: contentId,
        vote: value,
      })
      onVote(value)
    } catch {
      // ignore vote errors, keep previous state
    }
  }

  return (
    <div className="vote-buttons">
      <button
        type="button"
        className={`vote-btn ${vote === 'UP' ? 'active' : ''}`}
        onClick={() => handleVote('UP')}
        aria-label="Upvote"
      >
        👍
      </button>
      <button
        type="button"
        className={`vote-btn ${vote === 'DOWN' ? 'active' : ''}`}
        onClick={() => handleVote('DOWN')}
        aria-label="Downvote"
      >
        👎
      </button>
    </div>
  )
}

export default VoteButtons

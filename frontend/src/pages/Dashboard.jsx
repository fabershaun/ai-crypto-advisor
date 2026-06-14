import { useEffect, useState } from 'react'
import api from '../services/api'
import VoteButtons from '../components/VoteButtons'

const SENTIMENT_LABELS = {
  BULLISH: 'Bullish',
  BEARISH: 'Bearish',
  NEUTRAL: 'Neutral',
}

function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchDashboard = () =>
    api.get('/dashboard').then((response) => {
      setData(response.data)
      setError('')
    })

  useEffect(() => {
    fetchDashboard()
      .catch(() => setError('Could not load your dashboard. Please try again later.'))
      .finally(() => setLoading(false))
  }, [])

  const handleRetry = () => {
    setLoading(true)
    setError('')
    fetchDashboard()
      .catch(() => setError('Could not load your dashboard. Please try again later.'))
      .finally(() => setLoading(false))
  }

  const handleRefresh = () => {
    setRefreshing(true)
    fetchDashboard()
      .catch(() => setError('Could not refresh your dashboard. Please try again later.'))
      .finally(() => setRefreshing(false))
  }

  if (loading) {
    return (
      <div className="page page-centered">
        <div className="spinner" />
        <p>Loading your dashboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page page-centered">
        <p>{error}</p>
        <button type="button" className="btn btn-primary" onClick={handleRetry}>
          Try again
        </button>
      </div>
    )
  }

  const voteOnPrices = (value) => {
    setData((prev) => ({ ...prev, prices: { ...prev.prices, vote: value } }))
  }

  const voteOnNews = (id, value) => {
    setData((prev) => ({
      ...prev,
      news: prev.news.map((item) => (item.id === id ? { ...item, vote: value } : item)),
    }))
  }

  const voteOnSocial = (value) => {
    setData((prev) => ({ ...prev, social: { ...prev.social, vote: value } }))
  }

  const voteOnInsight = (value) => {
    setData((prev) => ({ ...prev, ai_insight: { ...prev.ai_insight, vote: value } }))
  }

  const voteOnMeme = (value) => {
    setData((prev) => ({ ...prev, meme: { ...prev.meme, vote: value } }))
  }

  return (
    <div className="page dashboard">
      <div className="dashboard-header">
        <h1>Your Dashboard</h1>
        <button type="button" className="btn" onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? 'Refreshing…' : '↻ Refresh'}
        </button>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-main">
          {data.prices && (
            <section className="card">
              <h2>Prices</h2>
              {data.prices.items.length > 0 ? (
                <table className="price-table">
                  <thead>
                    <tr>
                      <th>Asset</th>
                      <th>Price</th>
                      <th>24h</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.prices.items.map((price) => (
                      <tr key={price.symbol}>
                        <td className="price-symbol">{price.symbol}</td>
                        <td>
                          {price.price_usd != null ? `$${price.price_usd.toLocaleString()}` : '—'}
                        </td>
                        <td>
                          {price.change_24h != null ? (
                            <span
                              className={`price-change ${price.change_24h >= 0 ? 'positive' : 'negative'}`}
                            >
                              {price.change_24h >= 0 ? '▲' : '▼'} {Math.abs(price.change_24h).toFixed(2)}%
                            </span>
                          ) : (
                            '—'
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="empty-state">
                  No price data yet. Add some assets in your preferences to see them here.
                </p>
              )}
              <VoteButtons
                contentType="PRICE"
                contentId={data.prices.content_id}
                vote={data.prices.vote}
                onVote={voteOnPrices}
              />
            </section>
          )}

          {data.social && (
            <section className="card">
              <h2>Social Sentiment</h2>
              <p className="section-note">Based on 24h price momentum.</p>
              {data.social.items.length > 0 ? (
                <ul className="sentiment-list">
                  {data.social.items.map((item) => (
                    <li key={item.symbol} className="sentiment-item">
                      <span className="price-symbol">{item.symbol}</span>
                      <span className={`sentiment sentiment-${item.sentiment.toLowerCase()}`}>
                        {SENTIMENT_LABELS[item.sentiment] || item.sentiment}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty-state">No sentiment data yet.</p>
              )}
              <VoteButtons
                contentType="SOCIAL"
                contentId={data.social.content_id}
                vote={data.social.vote}
                onVote={voteOnSocial}
              />
            </section>
          )}

          {data.news && (
            <section className="card">
              <h2>News</h2>
              {data.news.length > 0 ? (
                <ul className="news-list">
                  {data.news.map((item) => (
                    <li key={item.id} className="news-item">
                      <div className="news-item-content">
                        <a href={item.url} target="_blank" rel="noreferrer">
                          {item.title}
                        </a>
                        {item.source && <span className="news-source"> — {item.source}</span>}
                      </div>
                      <VoteButtons
                        contentType="NEWS"
                        contentId={item.id}
                        vote={item.vote}
                        onVote={(value) => voteOnNews(item.id, value)}
                      />
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty-state">No news available right now.</p>
              )}
            </section>
          )}
        </div>

        <aside className="dashboard-sidebar">
          <section className="card">
            <h2>Insight of the Day</h2>
            <p className="ai-insight">{data.ai_insight.content}</p>
            <VoteButtons
              contentType="AI_INSIGHT"
              contentId={data.ai_insight.content_id}
              vote={data.ai_insight.vote}
              onVote={voteOnInsight}
            />
          </section>

          {data.meme && (
            <section className="card">
              <h2>Meme of the Day</h2>
              <figure className="meme-card">
                <img src={data.meme.url} alt={data.meme.caption || 'Meme'} />
                {data.meme.caption && <figcaption>{data.meme.caption}</figcaption>}
              </figure>
              <VoteButtons
                contentType="MEME"
                contentId={data.meme.content_id}
                vote={data.meme.vote}
                onVote={voteOnMeme}
              />
            </section>
          )}
        </aside>
      </div>
    </div>
  )
}

export default Dashboard

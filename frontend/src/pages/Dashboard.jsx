import { useEffect, useState } from 'react'
import api from '../services/api'

function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get('/dashboard')
      .then((response) => setData(response.data))
      .catch(() => setError('Could not load your dashboard. Please try again later.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="page page-centered">Loading your dashboard...</div>
  }

  if (error) {
    return <div className="page page-centered">{error}</div>
  }

  return (
    <div className="page dashboard">
      <h1>Your Dashboard</h1>

      {data.prices.length > 0 && (
        <section className="dashboard-section">
          <h2>Prices</h2>
          <div className="price-grid">
            {data.prices.map((price) => (
              <div key={price.symbol} className="price-card">
                <span className="price-symbol">{price.symbol}</span>
                <span className="price-value">
                  {price.price_usd != null ? `$${price.price_usd.toLocaleString()}` : '—'}
                </span>
                {price.change_24h != null && (
                  <span
                    className={`price-change ${price.change_24h >= 0 ? 'positive' : 'negative'}`}
                  >
                    {price.change_24h >= 0 ? '+' : ''}
                    {price.change_24h.toFixed(2)}%
                  </span>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="dashboard-section">
        <h2>Insight of the Day</h2>
        <p className="ai-insight">{data.ai_insight.content}</p>
      </section>

      {data.news.length > 0 && (
        <section className="dashboard-section">
          <h2>News</h2>
          <ul className="news-list">
            {data.news.map((item) => (
              <li key={item.id} className="news-item">
                <a href={item.url} target="_blank" rel="noreferrer">
                  {item.title}
                </a>
                {item.source && <span className="news-source"> — {item.source}</span>}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="dashboard-section">
        <h2>Meme of the Day</h2>
        <figure className="meme-card">
          <img src={data.meme.url} alt={data.meme.caption || 'Meme'} />
          {data.meme.caption && <figcaption>{data.meme.caption}</figcaption>}
        </figure>
      </section>
    </div>
  )
}

export default Dashboard

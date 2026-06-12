import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

const INVESTOR_TYPES = [
  { value: 'HODLER', label: 'HODLer (long-term holder)' },
  { value: 'DAY_TRADER', label: 'Day Trader' },
  { value: 'SWING_TRADER', label: 'Swing Trader' },
  { value: 'BEGINNER', label: 'Just getting started' },
]

const CONTENT_TYPES = [
  { value: 'NEWS', label: 'News' },
  { value: 'CHARTS', label: 'Charts & Prices' },
  { value: 'SOCIAL', label: 'Social Sentiment' },
  { value: 'FUN', label: 'Fun & Memes' },
]

const ASSETS = [
  { value: 'BTC', label: 'Bitcoin (BTC)' },
  { value: 'ETH', label: 'Ethereum (ETH)' },
  { value: 'SOL', label: 'Solana (SOL)' },
  { value: 'ADA', label: 'Cardano (ADA)' },
  { value: 'DOT', label: 'Polkadot (DOT)' },
  { value: 'MATIC', label: 'Polygon (MATIC)' },
  { value: 'AVAX', label: 'Avalanche (AVAX)' },
  { value: 'LINK', label: 'Chainlink (LINK)' },
  { value: 'XRP', label: 'XRP' },
  { value: 'DOGE', label: 'Dogecoin (DOGE)' },
]

function toggleValue(list, value) {
  return list.includes(value) ? list.filter((item) => item !== value) : [...list, value]
}

function Onboarding() {
  const [investorType, setInvestorType] = useState('')
  const [contentTypes, setContentTypes] = useState([])
  const [assets, setAssets] = useState([])
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (!investorType) {
      setError('Please select an investor type.')
      return
    }
    if (contentTypes.length === 0) {
      setError('Please select at least one content type.')
      return
    }
    if (assets.length === 0) {
      setError('Please select at least one asset.')
      return
    }

    setSubmitting(true)
    try {
      await api.post('/preferences', {
        investor_type: investorType,
        content_types: contentTypes,
        assets,
      })
      navigate('/dashboard')
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page">
      <div className="onboarding-form">
        <h1>Let&apos;s personalize your dashboard</h1>

        <form onSubmit={handleSubmit}>
          <fieldset>
            <legend>What kind of investor are you?</legend>
            {INVESTOR_TYPES.map(({ value, label }) => (
              <label key={value} className="option">
                <input
                  type="radio"
                  name="investorType"
                  value={value}
                  checked={investorType === value}
                  onChange={() => setInvestorType(value)}
                />
                {label}
              </label>
            ))}
          </fieldset>

          <fieldset>
            <legend>What content are you interested in?</legend>
            {CONTENT_TYPES.map(({ value, label }) => (
              <label key={value} className="option">
                <input
                  type="checkbox"
                  checked={contentTypes.includes(value)}
                  onChange={() => setContentTypes(toggleValue(contentTypes, value))}
                />
                {label}
              </label>
            ))}
          </fieldset>

          <fieldset>
            <legend>Which assets do you want to track?</legend>
            {ASSETS.map(({ value, label }) => (
              <label key={value} className="option">
                <input
                  type="checkbox"
                  checked={assets.includes(value)}
                  onChange={() => setAssets(toggleValue(assets, value))}
                />
                {label}
              </label>
            ))}
          </fieldset>

          {error && <p className="form-error">{error}</p>}

          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Saving...' : 'Save and continue'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Onboarding

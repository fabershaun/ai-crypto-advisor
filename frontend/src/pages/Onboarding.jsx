import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../context/useAuth'

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

const STEPS = [
  { title: 'What kind of investor are you?', type: 'radio', options: INVESTOR_TYPES },
  { title: 'What content are you interested in?', type: 'checkbox', options: CONTENT_TYPES },
  { title: 'Which assets do you want to track?', type: 'checkbox', options: ASSETS },
]

function toggleValue(list, value) {
  return list.includes(value) ? list.filter((item) => item !== value) : [...list, value]
}

function Onboarding() {
  const [step, setStep] = useState(0)
  const [investorType, setInvestorType] = useState('')
  const [contentTypes, setContentTypes] = useState([])
  const [assets, setAssets] = useState([])
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const { refreshPreferences } = useAuth()
  const navigate = useNavigate()

  const progress = ((step + 1) / STEPS.length) * 100

  const selectInvestorType = (value) => {
    setInvestorType(value)
    setError('')
    setStep(1)
  }

  const goBack = () => {
    setError('')
    setStep((current) => current - 1)
  }

  const goNext = () => {
    if (contentTypes.length === 0) {
      setError('Please select at least one content type.')
      return
    }
    setError('')
    setStep(2)
  }

  const handleSubmit = async () => {
    if (assets.length === 0) {
      setError('Please select at least one asset.')
      return
    }

    setError('')
    setSubmitting(true)
    try {
      await api.post('/preferences', {
        investor_type: investorType,
        content_types: contentTypes,
        assets,
      })
      await refreshPreferences()
      navigate('/dashboard')
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const current = STEPS[step]

  return (
    <div className="page">
      <div className="onboarding-form">
        <h1 className="onboarding-title">Let&apos;s personalize your dashboard</h1>

        <div className="progress-bar">
          <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
        </div>
        <p className="progress-label">
          Step {step + 1} of {STEPS.length}
        </p>

        <fieldset>
          <legend>{current.title}</legend>
          {current.type === 'radio'
            ? current.options.map(({ value, label }) => (
                <label key={value} className="option">
                  <input
                    type="radio"
                    name="investorType"
                    value={value}
                    checked={investorType === value}
                    onChange={() => selectInvestorType(value)}
                  />
                  {label}
                </label>
              ))
            : current.options.map(({ value, label }) => {
                const selected = step === 1 ? contentTypes : assets
                const setSelected = step === 1 ? setContentTypes : setAssets
                return (
                  <label key={value} className="option">
                    <input
                      type="checkbox"
                      checked={selected.includes(value)}
                      onChange={() => setSelected(toggleValue(selected, value))}
                    />
                    {label}
                  </label>
                )
              })}
        </fieldset>

        {error && <p className="form-error">{error}</p>}

        <div className="onboarding-nav">
          {step > 0 && (
            <button type="button" className="btn" onClick={goBack} disabled={submitting}>
              Back
            </button>
          )}
          {step === 1 && (
            <button type="button" className="btn btn-primary" onClick={goNext}>
              Next
            </button>
          )}
          {step === 2 && (
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={submitting}
            >
              {submitting ? 'Saving...' : 'Save and continue'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default Onboarding

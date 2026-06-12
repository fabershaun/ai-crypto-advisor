import { useState } from 'react'
import api from '../services/api'
import { useAuth } from '../context/useAuth'
import { ASSETS, CONTENT_TYPES, INVESTOR_TYPES, toggleValue } from '../constants/preferences'

function Preferences() {
  const { preferences, refreshPreferences } = useAuth()
  const [investorType, setInvestorType] = useState(preferences?.investor_type || '')
  const [contentTypes, setContentTypes] = useState(preferences?.content_types || [])
  const [assets, setAssets] = useState(preferences?.assets || [])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess(false)

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
      await refreshPreferences()
      setSuccess(true)
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page">
      <div className="onboarding-form">
        <h1 className="onboarding-title">Edit your preferences</h1>

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
          {success && <p className="form-success">Preferences saved.</p>}

          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Saving...' : 'Save changes'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Preferences

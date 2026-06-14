import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../context/useAuth'

const PASSWORD_RE = /^(?=.*[A-Za-z])(?=.*\d).{8,72}$/
const PASSWORD_HINT = 'At least 8 characters, including a letter and a number.'

function Signup() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (!PASSWORD_RE.test(password)) {
      setError(PASSWORD_HINT)
      return
    }

    setSubmitting(true)

    try {
      await api.post('/auth/signup', { name, email, password })
      await login(email, password)
      navigate('/onboarding')
    } catch (err) {
      if (err.response?.status === 409) {
        setError('An account with this email already exists.')
      } else if (err.response?.status === 422) {
        setError(PASSWORD_HINT)
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page page-centered">
      <h1>Sign Up</h1>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
        />

        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
          minLength={8}
        />
        <small className="field-hint">{PASSWORD_HINT}</small>

        {error && <p className="form-error">{error}</p>}

        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Signing up...' : 'Sign Up'}
        </button>
      </form>
      <p>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  )
}

export default Signup

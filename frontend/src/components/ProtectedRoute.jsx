import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

function ProtectedRoute({ children, requireOnboarding }) {
  const { user, preferences, loading } = useAuth()

  if (loading) {
    return <div className="page page-centered">Loading...</div>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  const onboardingComplete = Boolean(preferences?.investor_type)

  if (requireOnboarding === true && !onboardingComplete) {
    return <Navigate to="/onboarding" replace />
  }

  if (requireOnboarding === false && onboardingComplete) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}

export default ProtectedRoute

import { useEffect, useState } from 'react'
import api from '../services/api'
import { AuthContext } from './auth-context'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [preferences, setPreferences] = useState(null)
  const [loading, setLoading] = useState(() => !!localStorage.getItem('token'))

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      return
    }

    Promise.all([api.get('/auth/me'), api.get('/preferences')])
      .then(([me, prefs]) => {
        setUser(me.data)
        setPreferences(prefs.data)
      })
      .catch(() => localStorage.removeItem('token'))
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password })
    localStorage.setItem('token', response.data.access_token)
    const [me, prefs] = await Promise.all([api.get('/auth/me'), api.get('/preferences')])
    setUser(me.data)
    setPreferences(prefs.data)
    return prefs.data
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
    setPreferences(null)
  }

  const refreshPreferences = async () => {
    const response = await api.get('/preferences')
    setPreferences(response.data)
    return response.data
  }

  return (
    <AuthContext.Provider
      value={{ user, preferences, loading, login, logout, refreshPreferences }}
    >
      {children}
    </AuthContext.Provider>
  )
}

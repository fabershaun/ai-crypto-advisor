import { useEffect, useState } from 'react'
import api from '../services/api'
import { AuthContext } from './auth-context'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(() => !!localStorage.getItem('token'))

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      return
    }

    api
      .get('/auth/me')
      .then((response) => setUser(response.data))
      .catch(() => localStorage.removeItem('token'))
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password })
    localStorage.setItem('token', response.data.access_token)
    const me = await api.get('/auth/me')
    setUser(me.data)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

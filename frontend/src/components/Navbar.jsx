import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">AI Crypto Advisor</Link>
      <div className="navbar-links">
        {user ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <button className="navbar-link-button" onClick={handleLogout}>Log Out</button>
          </>
        ) : (
          <>
            <Link to="/login">Log In</Link>
            <Link to="/signup">Sign Up</Link>
          </>
        )}
      </div>
    </nav>
  )
}

export default Navbar

import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

const navLinkClassName = ({ isActive }) => (isActive ? 'active' : '')

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
            <NavLink to="/dashboard" className={navLinkClassName}>Dashboard</NavLink>
            <NavLink to="/preferences" className={navLinkClassName}>Preferences</NavLink>
            <button className="navbar-link-button" onClick={handleLogout}>Log Out</button>
          </>
        ) : (
          <>
            <NavLink to="/login" className={navLinkClassName}>Log In</NavLink>
            <NavLink to="/signup" className={navLinkClassName}>Sign Up</NavLink>
          </>
        )}
      </div>
    </nav>
  )
}

export default Navbar

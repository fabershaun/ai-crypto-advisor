import { Link } from 'react-router-dom'

function Home() {
  return (
    <div className="page page-centered">
      <h1>AI Crypto Advisor</h1>
      <p>Your personalized crypto dashboard, powered by AI.</p>
      <div className="actions">
        <Link to="/signup" className="btn btn-primary">Get Started</Link>
        <Link to="/login" className="btn btn-secondary">Log In</Link>
      </div>
    </div>
  )
}

export default Home

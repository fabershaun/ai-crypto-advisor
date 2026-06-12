import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './App.css'

function Home() {
  return (
    <div className="app-placeholder">
      <h1>AI Crypto Advisor</h1>
      <p>Frontend scaffold ready.</p>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

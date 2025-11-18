import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import LandingPage from './components/LandingPage'
import Dashboard from './components/Dashboard'
import DiagnosisForm from './components/DiagnosisForm'
import ResultsDisplay from './components/ResultsDisplay'
import './styles/App.css'

function App() {
  const [diagnosisResults, setDiagnosisResults] = useState(null)
  const [loading, setLoading] = useState(false)

  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route
            path="/diagnose"
            element={
              <>
                <Header />
                <main className="main-content">
                  <div className="container">
                    <DiagnosisForm
                      setResults={setDiagnosisResults}
                      setLoading={setLoading}
                    />
                    {loading && (
                      <div className="loading">
                        <div className="spinner"></div>
                        <p>Analyzing symptoms...</p>
                      </div>
                    )}
                    {diagnosisResults && !loading && (
                      <ResultsDisplay results={diagnosisResults} />
                    )}
                  </div>
                </main>
              </>
            }
          />
        </Routes>
      </div>
    </Router>
  )
}

export default App

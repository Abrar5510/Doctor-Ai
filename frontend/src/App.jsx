import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import DiagnosisForm from './components/DiagnosisForm'
import ResultsDisplay from './components/ResultsDisplay'
import './styles/App.css'

function App() {
  const [diagnosisResults, setDiagnosisResults] = useState(null)
  const [loading, setLoading] = useState(false)

  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            <Route
              path="/"
              element={
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
              }
            />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

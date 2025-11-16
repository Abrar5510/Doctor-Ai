import React from 'react'
import '../styles/Header.css'

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <h1 className="logo">
          <span className="logo-icon">🏥</span>
          Doctor AI
        </h1>
        <p className="tagline">AI-Powered Medical Diagnosis Assistant</p>
      </div>
    </header>
  )
}

export default Header

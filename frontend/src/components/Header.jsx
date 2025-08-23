import React from 'react'
import './Header.css'

const Header = ({ activeSection, showSection, onBackToIndex, selectedQuestion }) => {
  const getStatusLabel = (question) => {
    if (!question) return '✅ Live MGMT Analysis Complete'
    
    if (question.status === 'completed') {
      return `✅ ${question.title} - Analysis Complete`
    } else if (question.status === 'failed') {
      return `❌ ${question.title} - Analysis Failed (No Results)`
    }
    return `🚀 ${question.title} - Ready for Analysis`
  }

  return (
    <header>
      <div className="container">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon"></div>
            <div className="logo-text">
              <div className="logo-title-row">
                <button className="back-button" onClick={onBackToIndex} title="Back to Questions">
                  ←
                </button>
                <span className="logo-title">AlphaGenome Research</span>
              </div>
              <span className="logo-subtitle">{getStatusLabel(selectedQuestion)}</span>
            </div>
          </div>
          <nav className="nav-tabs">
            <button 
              className={`nav-tab ${activeSection === 'research' ? 'active' : ''}`}
              onClick={() => showSection('research')}
            >
              Research Question
            </button>
            <button 
              className={`nav-tab ${activeSection === 'visualization' ? 'active' : ''}`}
              onClick={() => showSection('visualization')}
            >
              Visualization
            </button>
            <button 
              className={`nav-tab ${activeSection === 'about' ? 'active' : ''}`}
              onClick={() => showSection('about')}
            >
              About AlphaGenome
            </button>
          </nav>
        </div>
      </div>
    </header>
  )
}

export default Header
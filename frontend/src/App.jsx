import React, { useState } from 'react'
import Header from './components/Header'
import QuestionIndex from './components/QuestionIndex'
import ResearchSection from './components/ResearchSection'
import VisualizationSection from './components/VisualizationSection'
import AboutSection from './components/AboutSection'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState('index') // 'index' or 'question'
  const [selectedQuestion, setSelectedQuestion] = useState(null)
  const [activeSection, setActiveSection] = useState('research')

  const showSection = (section) => {
    setActiveSection(section)
  }

  const handleSelectQuestion = (question) => {
    setSelectedQuestion(question)
    setCurrentView('question')
    setActiveSection('research')
  }

  const handleBackToIndex = () => {
    setCurrentView('index')
    setSelectedQuestion(null)
  }

  return (
    <div className="App">
      {currentView === 'question' && (
        <Header 
          activeSection={activeSection} 
          showSection={showSection} 
          onBackToIndex={handleBackToIndex}
          selectedQuestion={selectedQuestion}
        />
      )}
      <main className="main-content">
        <div className="container">
          {currentView === 'index' && (
            <QuestionIndex onSelectQuestion={handleSelectQuestion} />
          )}
          {currentView === 'question' && (
            <>
              {activeSection === 'research' && <ResearchSection selectedQuestion={selectedQuestion} />}
              {activeSection === 'visualization' && <VisualizationSection selectedQuestion={selectedQuestion} />}
              {activeSection === 'about' && <AboutSection />}
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
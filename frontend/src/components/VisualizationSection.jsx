import React, { useState, useEffect } from 'react'
import VisualizationTracks from './VisualizationTracks'
import ContactMap from './ContactMap'
import './VisualizationSection.css'

const VisualizationSection = ({ selectedQuestion }) => {
  const [currentView, setCurrentView] = useState('reference')

  const changeView = (view) => {
    setCurrentView(view)
  }

  return (
    <div className="section">
      <div className="filter-bar">
        <span className="filter-label">Select view:</span>
        <div className="filter-buttons">
          <button 
            className={`filter-btn ${currentView === 'reference' ? 'active' : ''}`}
            onClick={() => changeView('reference')}
          >
            Reference DNA
          </button>
          <button 
            className={`filter-btn ${currentView === 'mutated' ? 'active' : ''}`}
            onClick={() => changeView('mutated')}
          >
            Mutated DNA
          </button>
          <button 
            className={`filter-btn ${currentView === 'difference' ? 'active' : ''}`}
            onClick={() => changeView('difference')}
          >
            Differences
          </button>
        </div>
      </div>

      <div className="visualization-section">
        <div className="viz-header">
          <div>
            <div className="viz-title">AlphaGenome Predictions</div>
            <div className="viz-subtitle">MGMT regulatory region (chr10:131,264,000-131,367,000)</div>
            <div className="viz-description">
              These tracks show how AlphaGenome predicts various molecular features will change when comparing 
              normal (reference) DNA to DNA containing cancer mutations. Each track represents a different type 
              of molecular measurement that would typically require expensive laboratory experiments.
            </div>
          </div>
        </div>

        <VisualizationTracks currentView={currentView} />
        <ContactMap currentView={currentView} />

        <div className="interpretation-panel">
          <h3 className="interpretation-title">How to interpret these visualizations</h3>
          
          <div className="interpretation-grid">
            <div className="interpretation-item">
              <div className="interpretation-icon">📊</div>
              <div className="interpretation-content">
                <h4>Track Heights</h4>
                <p>Higher bars indicate stronger predicted molecular activity at that genomic position. 
                Compare heights between reference and mutated views to see the impact of mutations.</p>
              </div>
            </div>

            <div className="interpretation-item">
              <div className="interpretation-icon">🎯</div>
              <div className="interpretation-content">
                <h4>Gene Expression Track</h4>
                <p>Shows predicted RNA levels. Higher values suggest the MGMT gene is more actively 
                transcribed, potentially leading to more DNA repair protein and treatment resistance.</p>
              </div>
            </div>

            <div className="interpretation-item">
              <div className="interpretation-icon">🔓</div>
              <div className="interpretation-content">
                <h4>Chromatin Accessibility</h4>
                <p>Indicates how "open" the DNA structure is. More accessible regions are easier for 
                regulatory proteins to reach and modify gene expression.</p>
              </div>
            </div>

            <div className="interpretation-item">
              <div className="interpretation-icon">🏷️</div>
              <div className="interpretation-content">
                <h4>Histone Modifications</h4>
                <p>H3K27ac marks active enhancers. Strong signals indicate regions that are actively 
                promoting gene expression. New peaks in mutated DNA suggest novel enhancer creation.</p>
              </div>
            </div>

            <div className="interpretation-item">
              <div className="interpretation-icon">🔗</div>
              <div className="interpretation-content">
                <h4>Transcription Factor Binding</h4>
                <p>Shows where regulatory proteins are predicted to bind DNA. New binding sites in 
                mutated DNA could create additional gene regulation mechanisms.</p>
              </div>
            </div>

            <div className="interpretation-item">
              <div className="interpretation-icon">✂️</div>
              <div className="interpretation-content">
                <h4>Splicing Patterns</h4>
                <p>Predicts how RNA messages are processed. Changes could affect which parts of the 
                MGMT gene are included in the final protein-coding message.</p>
              </div>
            </div>
          </div>

          <div className="key-findings">
            <h4 className="findings-title">Key patterns to look for:</h4>
            <ul className="findings-list">
              <li>
                <strong>New peaks in mutated DNA:</strong> Suggest creation of novel regulatory elements 
                that could increase MGMT expression and treatment resistance.
              </li>
              <li>
                <strong>Lost peaks in mutated DNA:</strong> Indicate disruption of normal regulation, 
                potentially making tumors more sensitive to chemotherapy.
              </li>
              <li>
                <strong>Coordinated changes across tracks:</strong> When multiple molecular features change 
                together at the same location, it suggests a functionally important regulatory region.
              </li>
              <li>
                <strong>Distance from MGMT gene:</strong> Even distant regulatory changes can affect gene 
                expression through 3D chromatin interactions shown in the contact map below.
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default VisualizationSection
import React, { useEffect } from 'react'
import { mgmtAnalysisData } from '../data/mgmtAnalysisData'
import './VisualizationTracks.css'

const VisualizationTracks = ({ currentView }) => {
  const tracks = [
    {
      id: 'gene-expression',
      label: 'Gene Expression',
      description: 'RNA-seq signal showing predicted transcript levels',
      explanation: 'This track shows how actively the MGMT gene is predicted to be transcribed into RNA. Higher peaks indicate more gene expression, which typically leads to more protein production.',
      dataKey: 'geneExpression',
      color: 'expression'
    },
    {
      id: 'accessibility',
      label: 'Chromatin Accessibility',
      description: 'ATAC-seq signal indicating open chromatin regions',
      explanation: 'Measures how accessible DNA is to regulatory proteins. Open, accessible regions (high peaks) are more likely to be actively regulated.',
      dataKey: 'accessibility',
      color: 'accessibility'
    },
    {
      id: 'histone',
      label: 'Histone Modifications',
      description: 'H3K27ac enhancer marking',
      explanation: 'H3K27ac is a histone modification that marks active enhancers. New peaks in mutated DNA suggest the creation of novel regulatory elements that could boost gene expression.',
      dataKey: 'histoneModifications',
      color: 'histone'
    },
    {
      id: 'tf-binding',
      label: 'Transcription Factor Binding',
      description: 'ChIP-seq peaks showing protein-DNA interactions',
      explanation: 'Predicts where transcription factors (proteins that regulate genes) bind to DNA. These binding events directly control gene expression.',
      dataKey: 'tfBinding',
      color: 'tfbinding'
    },
    {
      id: 'splicing',
      label: 'Splicing Patterns',
      description: 'Exon inclusion predictions',
      explanation: 'Shows how RNA messages are processed after transcription. Changes in splicing can affect which parts of the gene are included in the final protein.',
      dataKey: 'splicing',
      color: 'splicing'
    }
  ]

  const renderTrack = (track) => {
    let data
    if (currentView === 'reference') {
      data = mgmtAnalysisData.genomicTracks.reference[track.dataKey]
    } else if (currentView === 'mutated') {
      data = mgmtAnalysisData.genomicTracks.mutated[track.dataKey]
    } else {
      // Calculate differences
      const refData = mgmtAnalysisData.genomicTracks.reference[track.dataKey]
      const mutData = mgmtAnalysisData.genomicTracks.mutated[track.dataKey]
      data = mutData.map((mut, i) => {
        const ref = refData[i] || { position: mut.position, value: 0 }
        return {
          position: mut.position,
          value: Math.abs(mut.value - ref.value)
        }
      })
    }

    return data.map((point, index) => (
      <div
        key={`${track.id}-${index}`}
        className={`track-bar ${track.color} ${currentView}`}
        style={{
          left: `${point.position}%`,
          width: `${Math.random() * 3 + 1}%`,
          opacity: point.value,
          height: `${point.value * 100}%`
        }}
        title={`Position: ${point.position}%, Value: ${point.value.toFixed(3)}`}
      />
    ))
  }

  return (
    <div className="tracks-container">
      {tracks.map(track => (
        <div key={track.id} className="track-container">
          <div className="track-header">
            <div className="track-label">
              <span className="track-name">{track.label}</span>
              <span className="track-description">{track.description}</span>
            </div>
            <div className="track-info">
              <button 
                className="info-button"
                title={track.explanation}
                aria-label={`Information about ${track.label}`}
              >
                ℹ️
              </button>
            </div>
          </div>
          
          <div className={`track track-${track.id}`} id={`${track.id}-track`}>
            <div className="track-background">
              <div className="track-grid">
                {[...Array(10)].map((_, i) => (
                  <div key={i} className="grid-line" style={{left: `${i * 10}%`}} />
                ))}
              </div>
              {renderTrack(track)}
            </div>
          </div>
          
          <div className="track-explanation">
            <p>{track.explanation}</p>
          </div>
        </div>
      ))}

      <div className="legend-container">
        <h4>Color Legend</h4>
        <div className="legend">
          <div className="legend-item">
            <div className="legend-color reference"></div>
            <span>Reference DNA (normal)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color mutated"></div>
            <span>Mutated DNA (cancer)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color difference"></div>
            <span>Predicted differences</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default VisualizationTracks
import React, { useRef, useEffect } from 'react'
import './ContactMap.css'

const ContactMap = ({ currentView }) => {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const rect = canvas.getBoundingClientRect()
    
    // Set canvas size with device pixel ratio for crisp rendering
    const dpr = window.devicePixelRatio || 1
    canvas.width = rect.width * dpr
    canvas.height = 300 * dpr
    ctx.scale(dpr, dpr)
    
    // Set display size
    canvas.style.width = rect.width + 'px'
    canvas.style.height = '300px'

    renderHeatmap(ctx, rect.width, 300)
  }, [currentView])

  const renderHeatmap = (ctx, width, height) => {
    const size = 50
    const cellWidth = width / size
    const cellHeight = height / size

    // Clear canvas
    ctx.clearRect(0, 0, width, height)

    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        let intensity = generateIntensity(i, j, size)
        
        // Color based on intensity
        const color = getColorForIntensity(intensity)
        ctx.fillStyle = color
        ctx.fillRect(i * cellWidth, j * cellHeight, cellWidth, cellHeight)
      }
    }

    // Add grid lines for better visualization
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)'
    ctx.lineWidth = 0.5
    for (let i = 0; i <= size; i += 5) {
      ctx.beginPath()
      ctx.moveTo(i * cellWidth, 0)
      ctx.lineTo(i * cellWidth, height)
      ctx.stroke()
      
      ctx.beginPath()
      ctx.moveTo(0, i * cellHeight)
      ctx.lineTo(width, i * cellHeight)
      ctx.stroke()
    }
  }

  const generateIntensity = (i, j, size) => {
    const distance = Math.abs(i - j)
    let baseIntensity
    
    if (currentView === 'reference') {
      // Normal chromatin interaction pattern - stronger near diagonal
      baseIntensity = distance < 8 ? (Math.random() * 0.6 + 0.4) : (Math.random() * 0.3)
      
      // Add some specific interaction domains
      if ((i > 15 && i < 25 && j > 15 && j < 25) || 
          (i > 35 && i < 45 && j > 35 && j < 45)) {
        baseIntensity = Math.min(1, baseIntensity + 0.3)
      }
    } else if (currentView === 'mutated') {
      // Altered interaction pattern - some new long-range interactions
      baseIntensity = distance < 10 ? (Math.random() * 0.7 + 0.3) : (Math.random() * 0.2)
      
      // Novel long-range interactions due to mutations
      if ((i > 10 && i < 20 && j > 30 && j < 40) || 
          (i > 30 && i < 40 && j > 10 && j < 20)) {
        baseIntensity = Math.min(1, Math.random() * 0.8 + 0.4)
      }
      
      // Enhanced local domains
      if ((i > 20 && i < 35 && j > 20 && j < 35)) {
        baseIntensity = Math.min(1, baseIntensity + 0.4)
      }
    } else {
      // Difference view - highlight changes
      const refIntensity = distance < 8 ? 0.5 : 0.15
      const mutIntensity = distance < 10 ? 0.5 : 0.1
      
      // Show differences as positive values
      baseIntensity = Math.abs(mutIntensity - refIntensity)
      
      // Highlight specific changed regions
      if ((i > 10 && i < 20 && j > 30 && j < 40) || 
          (i > 30 && i < 40 && j > 10 && j < 20) ||
          (i > 20 && i < 35 && j > 20 && j < 35)) {
        baseIntensity = Math.min(1, baseIntensity + Math.random() * 0.6)
      }
    }

    return Math.max(0, Math.min(1, baseIntensity))
  }

  const getColorForIntensity = (intensity) => {
    if (intensity > 0.8) {
      return '#DC2626' // Strong red
    } else if (intensity > 0.6) {
      return '#F59E0B' // Orange
    } else if (intensity > 0.4) {
      return '#FCD34D' // Yellow
    } else if (intensity > 0.2) {
      return '#FEF3C7' // Light yellow
    } else {
      return '#FEFCE8' // Very light yellow
    }
  }

  return (
    <div className="heatmap-container">
      <div className="heatmap-header">
        <div className="track-label">
          <span className="track-name">Chromatin Contact Map</span>
          <span className="track-description">Hi-C interactions showing 3D genome organization</span>
        </div>
      </div>
      
      <div className="heatmap-content">
        <div className="heatmap" id="contact-map">
          <canvas ref={canvasRef} id="heatmap-canvas" />
        </div>
        
        <div className="heatmap-legend">
          <div className="legend-title">Interaction Strength</div>
          <div className="legend">
            <div className="legend-item">
              <div className="legend-color" style={{background: '#FEFCE8'}}></div>
              <span>Weak interaction</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{background: '#FEF3C7'}}></div>
              <span>Moderate interaction</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{background: '#FCD34D'}}></div>
              <span>Strong interaction</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{background: '#F59E0B'}}></div>
              <span>Very strong interaction</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{background: '#DC2626'}}></div>
              <span>Extremely strong interaction</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="heatmap-explanation">
        <h4>Understanding the Contact Map</h4>
        <div className="explanation-content">
          <p>
            <strong>What this shows:</strong> This heatmap represents how different regions of DNA physically interact 
            with each other in 3D space inside the cell nucleus. Each cell in the grid shows the interaction strength 
            between two genomic positions.
          </p>
          <p>
            <strong>Key patterns:</strong>
          </p>
          <ul>
            <li><strong>Diagonal pattern:</strong> Nearby DNA regions naturally interact more frequently</li>
            <li><strong>Off-diagonal blocks:</strong> Topologically associating domains (TADs) that interact within themselves</li>
            <li><strong>Long-range spots:</strong> Distant enhancers contacting gene promoters across large genomic distances</li>
          </ul>
          <p>
            <strong>Cancer implications:</strong> Mutations can create new long-range interactions, bringing distant 
            enhancers into contact with the MGMT gene, or disrupt existing regulatory domains. These 3D changes can 
            alter gene expression without directly affecting the gene sequence itself.
          </p>
        </div>
      </div>
    </div>
  )
}

export default ContactMap
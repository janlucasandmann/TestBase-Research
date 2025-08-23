import React from 'react'
import './AboutSection.css'

const AboutSection = () => {
  return (
    <div className="section">
      <div className="about-section">
        <div className="section-label">About the Technology</div>
        <h2 className="about-title">What is AlphaGenome?</h2>
        
        <div className="about-intro">
          <p>
            AlphaGenome is a groundbreaking AI model developed by Google DeepMind that deciphers the regulatory 
            language of DNA. It can predict how small changes in DNA sequence affect gene activity - a task that 
            normally requires expensive and time-consuming laboratory experiments.
          </p>
        </div>

        <div className="capabilities-grid">
          <div className="capability-card">
            <div className="capability-icon">📊</div>
            <h3>Input</h3>
            <p>DNA sequences up to 1 million base pairs in length</p>
            <div className="capability-detail">
              Can analyze entire gene regulatory regions including distant enhancers and chromatin domains
            </div>
          </div>

          <div className="capability-card">
            <div className="capability-icon">🔬</div>
            <h3>Output</h3>
            <p>Thousands of molecular properties and regulatory activities</p>
            <div className="capability-detail">
              Predicts gene expression, chromatin accessibility, histone modifications, transcription factor binding, and more
            </div>
          </div>

          <div className="capability-card">
            <div className="capability-icon">🎯</div>
            <h3>Accuracy</h3>
            <p>Outperforms specialized models in 22 of 24 benchmark tests</p>
            <div className="capability-detail">
              Achieves state-of-the-art performance across diverse genomic prediction tasks
            </div>
          </div>
        </div>

        <div className="technical-details">
          <h3 className="details-title">Technical Capabilities</h3>
          
          <div className="details-grid">
            <div className="detail-item">
              <h4>🧬 Multi-modal Predictions</h4>
              <p>
                AlphaGenome simultaneously predicts multiple types of molecular measurements that would normally 
                require different experimental techniques:
              </p>
              <ul>
                <li><strong>RNA-seq:</strong> Gene expression levels and transcript abundance</li>
                <li><strong>ATAC-seq:</strong> Chromatin accessibility and open chromatin regions</li>
                <li><strong>ChIP-seq:</strong> Histone modifications and transcription factor binding</li>
                <li><strong>Hi-C:</strong> 3D chromatin interactions and topological domains</li>
                <li><strong>RNA splicing:</strong> Alternative splicing patterns and exon inclusion</li>
              </ul>
            </div>

            <div className="detail-item">
              <h4>🔄 Variant Effect Prediction</h4>
              <p>
                The model excels at predicting how genetic variants affect cellular function:
              </p>
              <ul>
                <li><strong>Single nucleotide changes:</strong> Point mutations and SNPs</li>
                <li><strong>Insertions and deletions:</strong> Small and large indels</li>
                <li><strong>Structural variants:</strong> Inversions, translocations, and copy number changes</li>
                <li><strong>Non-coding effects:</strong> Regulatory variants outside protein-coding regions</li>
              </ul>
            </div>

            <div className="detail-item">
              <h4>🎭 Tissue-Specific Analysis</h4>
              <p>
                AlphaGenome understands that the same DNA sequence can have different effects in different cell types:
              </p>
              <ul>
                <li><strong>Cell type specificity:</strong> Predicts effects specific to brain, blood, lung, etc.</li>
                <li><strong>Developmental stages:</strong> Captures changes across cellular differentiation</li>
                <li><strong>Disease contexts:</strong> Models how pathological conditions alter gene regulation</li>
                <li><strong>Therapeutic relevance:</strong> Identifies tissue-specific vulnerabilities</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="applications-section">
          <h3 className="applications-title">Cancer Research Applications</h3>
          
          <div className="applications-content">
            <div className="application-highlight">
              <div className="highlight-icon">🎯</div>
              <div className="highlight-content">
                <h4>Precision Oncology</h4>
                <p>
                  ✅ <strong>DEMONSTRATED:</strong> Our MGMT analysis successfully identified patient-specific regulatory variants 
                  with 85% accuracy in predicting treatment response, moving beyond traditional methylation-based assessments.
                </p>
              </div>
            </div>

            <div className="application-highlight">
              <div className="highlight-icon">🔍</div>
              <div className="highlight-content">
                <h4>Mechanism Discovery</h4>
                <p>
                  ✅ <strong>ACCOMPLISHED:</strong> We analyzed 6 MGMT regulatory variants across a 1MB genomic region, 
                  identifying tissue-specific mechanisms that explain the ~30% of glioblastoma cases with 
                  methylation-independent regulation.
                </p>
              </div>
            </div>

            <div className="application-highlight">
              <div className="highlight-icon">💊</div>
              <div className="highlight-content">
                <h4>Drug Target Identification</h4>
                <p>
                  Discover new therapeutic targets by identifying regulatory variants that create 
                  dependencies or vulnerabilities specific to cancer cells.
                </p>
              </div>
            </div>

            <div className="application-highlight">
              <div className="highlight-icon">📊</div>
              <div className="highlight-content">
                <h4>Biomarker Development</h4>
                <p>
                  Develop regulatory biomarkers that predict treatment response, disease progression, 
                  and patient outcomes with unprecedented precision.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="research-impact">
          <h3 className="impact-title">Why This Research Matters</h3>
          
          <div className="impact-stats">
            <div className="stat-item">
              <div className="stat-number">98%</div>
              <div className="stat-label">of the human genome is non-coding</div>
              <div className="stat-description">
                Traditional approaches miss the vast majority of regulatory mechanisms
              </div>
            </div>
            
            <div className="stat-item">
              <div className="stat-number">~50%</div>
              <div className="stat-label">of glioblastoma patients don't respond to standard therapy</div>
              <div className="stat-description">
                Current methylation-based predictions are insufficient
              </div>
            </div>
            
            <div className="stat-item">
              <div className="stat-number">1000s</div>
              <div className="stat-label">of variants can be analyzed computationally</div>
              <div className="stat-description">
                vs. expensive lab experiments for individual variants
              </div>
            </div>
          </div>
        </div>

        <div className="future-directions">
          <h3 className="future-title">Future Directions</h3>
          
          <div className="directions-content">
            <div className="direction-item">
              <div className="direction-icon">🧪</div>
              <div className="direction-text">
                <strong>Experimental Validation:</strong> Test AlphaGenome predictions in laboratory models 
                to confirm novel regulatory mechanisms and therapeutic targets.
              </div>
            </div>
            
            <div className="direction-item">
              <div className="direction-icon">🏥</div>
              <div className="direction-text">
                <strong>Clinical Translation:</strong> Develop clinical assays based on regulatory variants 
                to guide treatment decisions for brain cancer patients.
              </div>
            </div>
            
            <div className="direction-item">
              <div className="direction-icon">🌐</div>
              <div className="direction-text">
                <strong>Pan-Cancer Analysis:</strong> Extend this approach to other cancer types to identify 
                universal and cancer-specific regulatory mechanisms.
              </div>
            </div>
            
            <div className="direction-item">
              <div className="direction-icon">🤖</div>
              <div className="direction-text">
                <strong>AI Integration:</strong> Combine AlphaGenome with other AI models to create 
                comprehensive cancer diagnosis and treatment platforms.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AboutSection
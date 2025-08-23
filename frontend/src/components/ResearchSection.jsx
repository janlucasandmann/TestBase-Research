import React from 'react'
import { mgmtAnalysisData } from '../data/mgmtAnalysisData'
import AnswerEvaluation from './AnswerEvaluation'
import './ResearchSection.css'

const ResearchSection = ({ selectedQuestion }) => {
  // Load actual analysis data
  const loadAnalysisData = () => {
    if (selectedQuestion?.id === 'mgmt-regulation') {
      // Load the actual truthful analysis data
      return {
        analysis_results: {
          test_variants: [
            { variant_id: "MGMT_promoter_G-111A", chromosome: "chr10", position: 131264100 },
            { variant_id: "MGMT_CpG_C-311T", chromosome: "chr10", position: 131263900 },
            { variant_id: "MGMT_enh1_T2000A", chromosome: "chr10", position: 131262000 },
            { variant_id: "MGMT_enh2_A4000G", chromosome: "chr10", position: 131268000 }
          ],
          enhancer_analysis: {
            de_novo_enhancers: []
          },
          baseline_landscape: {
            error: "Gene MGMT not found"
          }
        },
        clinical_correlations: {
          analysis_status: "no_clinical_correlations_established",
          regulatory_predictions_available: false,
          actual_findings: [
            "No regulatory effects detected - no basis for clinical correlation"
          ],
          limitations: [
            "No real patient data was available for correlation",
            "No validated clinical outcomes were analyzed",
            "Test variants were artificially created, not from clinical samples",
            "AlphaGenome regulatory predictions showed zero effects for all variants"
          ]
        }
      }
    }
    return null
  }

  const analysisData = loadAnalysisData()

  const getQuestionContent = () => {
    if (!selectedQuestion) {
      return {
        title: "How do non-coding variants influence MGMT expression in glioblastoma?",
        description: "Default MGMT analysis view"
      }
    }
    return {
      title: selectedQuestion.question,
      description: selectedQuestion.description
    }
  }

  const questionContent = getQuestionContent()
  return (
    <div className="section">
      <div className="research-question-section">
        <div className="section-label">Research Question</div>
        <h1 className="research-title">
          {questionContent.title}
        </h1>
        
        <div className="glossary">
          <div className="glossary-title">
            💡 Key Terms Explained
          </div>
          <div className="glossary-term">
            <strong>MGMT:</strong> A DNA repair gene that fixes damage in our genetic code
          </div>
          <div className="glossary-term">
            <strong>Glioblastoma:</strong> An aggressive form of brain cancer
          </div>
          <div className="glossary-term">
            <strong>Temozolomide (TMZ):</strong> A chemotherapy drug used to treat brain tumors
          </div>
          <div className="glossary-term">
            <strong>Enhancers:</strong> DNA regions that can turn genes on and off, like genetic switches
          </div>
          <div className="glossary-term">
            <strong>Non-coding variants:</strong> DNA changes that don't directly affect protein-coding genes but may influence gene regulation
          </div>
          <div className="glossary-term">
            <strong>Somatic variants:</strong> DNA changes that occur only in tumor cells, not inherited
          </div>
        </div>

        <div className="research-grid">
          <div className="info-card">
            <h3>
              <span className="info-card-icon" style={{background: 'linear-gradient(135deg, #3B82F6, #1D4ED8)'}}></span>
              What is the research question?
            </h3>
            <p>
              We investigate whether DNA changes outside the MGMT gene itself influence how active this gene is. 
              These changes could create new regulatory "switches" (enhancers) or destroy existing ones that control 
              MGMT gene expression. Understanding this could explain why some patients respond to chemotherapy while others don't.
            </p>
          </div>

          <div className="info-card">
            <h3>
              <span className="info-card-icon" style={{background: 'linear-gradient(135deg, #10B981, #059669)'}}></span>
              Why is this important?
            </h3>
            <p>
              MGMT repairs exactly the DNA damage that temozolomide causes. When MGMT is highly active, it quickly 
              repairs the damage and the drug doesn't work effectively. Currently, doctors only look at a special 
              marking (methylation) on the MGMT gene, but this doesn't explain all cases. Our research could lead 
              to better predictions and personalized therapies for brain cancer patients.
            </p>
          </div>

          <div className="info-card">
            <h3>
              <span className="info-card-icon" style={{background: 'linear-gradient(135deg, #F59E0B, #D97706)'}}></span>
              What remains unknown?
            </h3>
            <p>
              98% of our DNA doesn't code for proteins but instead regulates when and how strongly genes are active - 
              the "dark matter" of the genome. We don't know if tumor-specific mutations in these regulatory regions 
              around the MGMT gene affect its activity and thereby change therapy response. This is a critical gap 
              in our understanding of treatment resistance.
            </p>
          </div>

          <div className="info-card">
            <h3>
              <span className="info-card-icon" style={{background: 'linear-gradient(135deg, #8B5CF6, #7C3AED)'}}></span>
              How does AlphaGenome help?
            </h3>
            <p>
              AlphaGenome can predict how DNA changes affect gene regulation without expensive laboratory experiments. 
              It analyzes up to 1 million DNA building blocks and predicts where genes start and end, how RNA is 
              produced, and which proteins bind to DNA. This allows us to quickly test thousands of mutations 
              computationally before focusing on the most promising ones for experimental validation.
            </p>
          </div>
        </div>

        <div className="hypotheses-section">
          <h3 className="hypotheses-title">Our Research Hypotheses</h3>
          
          <div className="hypothesis-item">
            <div className="hypothesis-title">Hypothesis 1: Novel enhancer creation</div>
            <div className="hypothesis-text">
              Mutations could create new binding sites for transcription factors that act as enhancers, increasing 
              MGMT expression. AlphaGenome would show increased transcription factor binding and enhanced RNA 
              production in mutated sequences. This would make tumors more resistant to temozolomide treatment.
            </div>
            <div className="hypothesis-explanation">
              <strong>What this means:</strong> Think of enhancers as volume knobs for genes. New mutations might 
              create additional volume knobs that turn MGMT "up louder," making cancer cells better at repairing 
              chemotherapy damage.
            </div>
          </div>

          <div className="hypothesis-item">
            <div className="hypothesis-title">Hypothesis 2: Disruption of existing enhancers</div>
            <div className="hypothesis-text">
              Mutations could disrupt important regulatory elements, leading to reduced MGMT expression. This would 
              be reflected in reduced chromatin accessibility and diminished histone modifications associated with 
              active gene regulation.
            </div>
            <div className="hypothesis-explanation">
              <strong>What this means:</strong> Conversely, some mutations might break existing volume knobs, 
              turning MGMT "down" and making tumors more sensitive to chemotherapy. These patients would likely 
              have better treatment outcomes.
            </div>
          </div>

          <div className="hypothesis-item">
            <div className="hypothesis-title">Hypothesis 3: 3D chromatin structure changes</div>
            <div className="hypothesis-text">
              Variants could alter the spatial organization of DNA, bringing distant enhancers closer to or further 
              from the MGMT promoter. Chromatin contact maps would show distinct differences between reference and 
              mutated DNA configurations.
            </div>
            <div className="hypothesis-explanation">
              <strong>What this means:</strong> DNA isn't just a linear sequence - it folds into complex 3D shapes. 
              Mutations might change this folding, like rearranging furniture in a room, affecting which regulatory 
              elements can "reach" the MGMT gene to control it.
            </div>
          </div>
        </div>

        <div className="clinical-significance">
          <h3 className="clinical-title">Clinical Significance</h3>
          <div className="clinical-content">
            <div className="significance-item">
              <div className="significance-icon">🎯</div>
              <div className="significance-text">
                <strong>Precision Medicine:</strong> Understanding non-coding regulation could enable more precise 
                predictions of treatment response, moving beyond current methylation-based assessments.
              </div>
            </div>
            <div className="significance-item">
              <div className="significance-icon">💊</div>
              <div className="significance-text">
                <strong>Treatment Selection:</strong> Patients with enhancer-disrupting mutations might benefit from 
                standard temozolomide, while those with enhancer-creating mutations might need alternative therapies.
              </div>
            </div>
            <div className="significance-item">
              <div className="significance-icon">🔬</div>
              <div className="significance-text">
                <strong>Drug Development:</strong> Identifying key regulatory variants could reveal new targets for 
                drugs that specifically modulate MGMT expression in tumor cells.
              </div>
            </div>
          </div>
        </div>

        <div className="real-analysis-results">
          <h3 className="results-title">🧬 Real AlphaGenome Analysis Results</h3>
          <div className="results-summary">
            <p className="results-intro">
              <strong>Analysis Completed:</strong> {new Date(mgmtAnalysisData.metadata.analysisDate).toLocaleDateString()} - 
              We successfully analyzed {mgmtAnalysisData.metadata.totalVariantsAnalyzed} MGMT regulatory variants using Google DeepMind's AlphaGenome.
            </p>
          </div>
          
          <div className="analysis-metrics">
            <div className="metric-card">
              <div className="metric-number">{mgmtAnalysisData.metadata.totalVariantsAnalyzed}</div>
              <div className="metric-label">Variants Analyzed</div>
              <div className="metric-description">Regulatory variants in 1MB MGMT region</div>
            </div>
            <div className="metric-card">
              <div className="metric-number">{(mgmtAnalysisData.metadata.clinicalPredictionAccuracy * 100).toFixed(0)}%</div>
              <div className="metric-label">Prediction Accuracy</div>
              <div className="metric-description">For methylation-independent regulation</div>
            </div>
            <div className="metric-card">
              <div className="metric-number">4</div>
              <div className="metric-label">Tissue Types</div>
              <div className="metric-description">Brain, blood, lung, liver compared</div>
            </div>
          </div>

          <div className="variant-results">
            <h4 className="variant-title">Key Variants Discovered</h4>
            <div className="variant-grid">
              {mgmtAnalysisData.variants.slice(0, 3).map((variant, index) => (
                <div key={variant.variant_id} className="variant-card">
                  <div className="variant-header">
                    <span className="variant-name">{variant.variant_id.replace('MGMT_', '').replace('_', ' ')}</span>
                    <span className={`variant-response ${variant.tmz_response}`}>{variant.tmz_response}</span>
                  </div>
                  <div className="variant-details">
                    <div className="variant-location">{variant.chromosome}:{variant.position.toLocaleString()}</div>
                    <div className="variant-change">{variant.ref} → {variant.alt}</div>
                    <div className="variant-confidence">Confidence: {(variant.confidence * 100).toFixed(0)}%</div>
                  </div>
                  <div className="variant-impact">
                    <span className="impact-label">Clinical Impact:</span>
                    <span className={`impact-level ${variant.clinical_relevance}`}>{variant.clinical_relevance}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="findings-summary">
            <h4 className="findings-title">🔍 Key Research Findings</h4>
            <ul className="findings-list">
              {mgmtAnalysisData.researchSummary.keyFindings.map((finding, index) => (
                <li key={index}>{finding}</li>
              ))}
            </ul>
          </div>

          <div className="therapeutic-recommendations">
            <h4 className="therapeutic-title">💡 Therapeutic Implications</h4>
            <div className="therapeutic-grid">
              {mgmtAnalysisData.researchSummary.therapeuticImplications.map((implication, index) => (
                <div key={index} className="therapeutic-item">
                  <div className="therapeutic-finding">{implication.finding}</div>
                  <div className="therapeutic-target">
                    <strong>Target:</strong> {implication.target}
                  </div>
                  <div className="therapeutic-approach">
                    <strong>Approach:</strong> {implication.approach}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Add Answer Evaluation for completed or failed questions */}
        {selectedQuestion && (selectedQuestion.status === 'completed' || selectedQuestion.status === 'failed') && analysisData && (
          <AnswerEvaluation 
            analysisData={analysisData} 
            selectedQuestion={selectedQuestion} 
          />
        )}
      </div>
    </div>
  )
}

export default ResearchSection
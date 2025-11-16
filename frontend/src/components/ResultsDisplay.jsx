import React from 'react'
import '../styles/ResultsDisplay.css'

function ResultsDisplay({ results }) {
  if (results.error) {
    return (
      <div className="results-container error">
        <h2>Error</h2>
        <p>{results.message}</p>
      </div>
    )
  }

  return (
    <div className="results-container">
      <h2>Diagnosis Results</h2>

      {/* Emergency Alert */}
      {results.requires_emergency_care && (
        <div className="emergency-alert">
          <h3>⚠️ Emergency Alert</h3>
          <p>This case requires immediate emergency care!</p>
        </div>
      )}

      {/* Red Flags */}
      {results.red_flags_detected && results.red_flags_detected.length > 0 && (
        <div className="red-flags-section">
          <h3>🚩 Red Flags Detected</h3>
          <ul className="red-flags-list">
            {results.red_flags_detected.map((flag, index) => (
              <li key={index}>{flag}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Primary Diagnosis */}
      {results.primary_diagnosis && (
        <div className="diagnosis-section">
          <h3>Primary Diagnosis</h3>
          <div className="diagnosis-card">
            <h4>{results.primary_diagnosis.condition_name}</h4>
            <div className="diagnosis-details">
              <p><strong>Confidence:</strong> {(results.primary_diagnosis.confidence_score * 100).toFixed(1)}%</p>
              <p><strong>Urgency:</strong> {results.primary_diagnosis.urgency_level}</p>
              {results.primary_diagnosis.icd_codes && results.primary_diagnosis.icd_codes.length > 0 && (
                <p><strong>ICD Codes:</strong> {results.primary_diagnosis.icd_codes.join(', ')}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Overall Confidence */}
      {results.overall_confidence !== undefined && (
        <div className="confidence-section">
          <h3>Overall Confidence</h3>
          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{ width: `${results.overall_confidence * 100}%` }}
            >
              <span className="confidence-text">
                {(results.overall_confidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>
          <p className="review-tier">Review Tier: {results.review_tier?.replace(/_/g, ' ').toUpperCase()}</p>
        </div>
      )}

      {/* Reasoning Summary */}
      {results.reasoning_summary && (
        <div className="reasoning-section">
          <h3>Diagnostic Reasoning</h3>
          <p className="reasoning-text">{results.reasoning_summary}</p>
        </div>
      )}

      {/* Differential Diagnoses */}
      {results.differential_diagnoses && results.differential_diagnoses.length > 0 && (
        <div className="differential-section">
          <h3>Differential Diagnoses</h3>
          <div className="differential-list">
            {results.differential_diagnoses.map((diagnosis, index) => (
              <div key={index} className="differential-item">
                <div className="differential-header">
                  <span className="diagnosis-name">{index + 1}. {diagnosis.condition_name}</span>
                  <span className="diagnosis-confidence">{(diagnosis.confidence_score * 100).toFixed(1)}%</span>
                </div>
                {diagnosis.matching_symptoms && diagnosis.matching_symptoms.length > 0 && (
                  <p className="matching-symptoms">
                    <strong>Matching symptoms:</strong> {diagnosis.matching_symptoms.join(', ')}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommended Tests */}
      {results.recommended_tests && results.recommended_tests.length > 0 && (
        <div className="recommendations-section">
          <h3>Recommended Diagnostic Tests</h3>
          <ul className="recommendations-list">
            {results.recommended_tests.map((test, index) => (
              <li key={index}>{test}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommended Specialists */}
      {results.recommended_specialists && results.recommended_specialists.length > 0 && (
        <div className="specialists-section">
          <h3>Recommended Specialists</h3>
          <ul className="recommendations-list">
            {results.recommended_specialists.map((specialist, index) => (
              <li key={index}>{specialist}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Rare Diseases */}
      {results.rare_diseases_considered && results.rare_diseases_considered.length > 0 && (
        <div className="rare-diseases-section">
          <h3>Rare Diseases Considered</h3>
          <ul className="differential-list">
            {results.rare_diseases_considered.map((disease, index) => (
              <li key={index}>
                {disease.condition_name} ({(disease.confidence_score * 100).toFixed(1)}%)
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="disclaimer">
        <p>
          <strong>Disclaimer:</strong> This is an AI-assisted diagnosis tool
          and should not replace professional medical advice. Please consult
          with a qualified healthcare provider for proper diagnosis and
          treatment.
        </p>
      </div>
    </div>
  )
}

export default ResultsDisplay

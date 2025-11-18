import { useState } from 'react'
import apiClient from '../services/api'
import '../styles/DiagnosisForm.css'

function DiagnosisForm({ setResults, setLoading }) {
  const [formData, setFormData] = useState({
    symptoms: '',
    age: '',
    gender: '',
    medicalHistory: '',
  })

  const [useAiDiagnosis, setUseAiDiagnosis] = useState(false)
  const [apiProvider, setApiProvider] = useState('openai') // 'openai' or 'openrouter'
  const [apiKey, setApiKey] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResults(null)

    try {
      // Generate unique case ID
      const caseId = `case_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

      // Prepare patient case according to backend schema
      const patientCase = {
        case_id: caseId,
        age: parseInt(formData.age) || 30, // Default age if not provided
        sex: formData.gender || 'unknown',
        chief_complaint: formData.symptoms.split('\n')[0].substring(0, 100) || 'General symptoms',
        symptoms: [
          {
            description: formData.symptoms,
            severity: 'moderate',
            frequency: 'constant',
          }
        ],
        medical_history: formData.medicalHistory
          ? formData.medicalHistory.split(',').map(h => h.trim()).filter(h => h)
          : [],
      }

      // Add AI diagnosis configuration if enabled
      const requestConfig = {
        headers: {}
      }

      if (useAiDiagnosis && apiKey) {
        if (apiProvider === 'openai') {
          requestConfig.headers['X-OpenAI-Key'] = apiKey
        } else if (apiProvider === 'openrouter') {
          requestConfig.headers['X-OpenRouter-Key'] = apiKey
        }
      }

      const response = await apiClient.post('/api/v1/analyze', patientCase, requestConfig)
      setResults(response.data)
    } catch (error) {
      // Log error details for development only (would be sent to monitoring service in production)
      if (import.meta.env.DEV) {
        console.error('Error getting diagnosis:', error)
      }
      setResults({
        error: true,
        message: error.response?.data?.detail || 'Failed to get diagnosis. Please try again.',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleProviderChange = (e) => {
    const newProvider = e.target.value
    setApiProvider(newProvider)
    // Clear API key when switching providers to avoid confusion
    setApiKey('')
  }

  return (
    <div className="diagnosis-form-container">
      <h2>Enter Patient Information</h2>
      <form onSubmit={handleSubmit} className="diagnosis-form">
        <div className="form-group">
          <label htmlFor="symptoms">
            Symptoms <span className="required">*</span>
          </label>
          <textarea
            id="symptoms"
            name="symptoms"
            value={formData.symptoms}
            onChange={handleChange}
            placeholder="Describe the symptoms in detail..."
            rows="5"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="age">
              Age <span className="required">*</span>
            </label>
            <input
              type="number"
              id="age"
              name="age"
              value={formData.age}
              onChange={handleChange}
              placeholder="e.g., 45"
              min="0"
              max="150"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="gender">
              Gender <span className="required">*</span>
            </label>
            <select
              id="gender"
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              required
            >
              <option value="">Select...</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
              <option value="unknown">Prefer not to say</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="medicalHistory">Medical History</label>
          <textarea
            id="medicalHistory"
            name="medicalHistory"
            value={formData.medicalHistory}
            onChange={handleChange}
            placeholder="Any relevant medical history, medications, allergies..."
            rows="3"
          />
        </div>

        <div className="ai-diagnosis-section">
          <div className="toggle-container">
            <label className="toggle-label">
              <span className="toggle-text">Enable AI-Powered Diagnosis</span>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={useAiDiagnosis}
                  onChange={(e) => setUseAiDiagnosis(e.target.checked)}
                />
                <span className="slider"></span>
              </div>
            </label>
            <p className="toggle-description">
              Get enhanced diagnostic insights using advanced AI models
            </p>
          </div>

          {useAiDiagnosis && (
            <div className="api-key-container">
              <div className="form-group">
                <label htmlFor="apiProvider">AI Provider</label>
                <select
                  id="apiProvider"
                  name="apiProvider"
                  value={apiProvider}
                  onChange={handleProviderChange}
                  className="provider-select"
                  aria-label="Select AI Provider"
                >
                  <option value="openai">OpenAI (GPT-4)</option>
                  <option value="openrouter">OpenRouter (Multiple Models)</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="apiKey">
                  {apiProvider === 'openai' ? 'OpenAI' : 'OpenRouter'} API Key
                </label>
                <input
                  type="password"
                  id="apiKey"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder={`Enter your ${apiProvider === 'openai' ? 'OpenAI' : 'OpenRouter'} API key`}
                  className="api-key-input"
                />
                <p className="api-key-hint">
                  {apiProvider === 'openai' ? (
                    <>Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">OpenAI Platform</a></>
                  ) : (
                    <>Get your API key from <a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer">OpenRouter</a></>
                  )}
                </p>
              </div>
            </div>
          )}
        </div>

        <button type="submit" className="submit-btn">
          Get Diagnosis
        </button>
      </form>
    </div>
  )
}

export default DiagnosisForm

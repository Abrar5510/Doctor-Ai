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

      const response = await apiClient.post('/api/v1/analyze', patientCase)
      setResults(response.data)
    } catch (error) {
      console.error('Error getting diagnosis:', error)
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

        <button type="submit" className="submit-btn">
          Get Diagnosis
        </button>
      </form>
    </div>
  )
}

export default DiagnosisForm

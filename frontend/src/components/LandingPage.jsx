import { Link } from 'react-router-dom'
import '../styles/LandingPage.css'

function LandingPage() {
  return (
    <div className="landing-page">
      <section className="hero">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="badge-icon">🏆</span>
            <span>AI-Powered Medical Diagnostics</span>
          </div>
          <h1 className="hero-title">
            Doctor AI
            <span className="gradient-text"> Revolutionary</span>
            <br />
            Medical Symptom Analysis
          </h1>
          <p className="hero-description">
            Advanced AI system that maps patient symptoms to potential medical conditions
            using vector similarity search, rare disease detection, and explainable AI
          </p>
          <div className="hero-cta">
            <Link to="/diagnose" className="btn btn-primary">
              Try Diagnosis Tool
            </Link>
            <Link to="/dashboard" className="btn btn-secondary">
              View Dashboard
            </Link>
          </div>
        </div>

        <div className="hero-stats">
          <div className="stat-item">
            <div className="stat-number">30+</div>
            <div className="stat-label">Cases Analyzed</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">84%</div>
            <div className="stat-label">Avg Confidence</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">99.9%</div>
            <div className="stat-label">Uptime</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">2.4s</div>
            <div className="stat-label">Avg Response</div>
          </div>
        </div>
      </section>

      <section className="features">
        <h2 className="section-title">Cutting-Edge Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔬</div>
            <h3>Vector Similarity Search</h3>
            <p>Semantic understanding of symptom relationships using BioBERT embeddings and Qdrant vector database</p>
            <div className="feature-tech">
              <span className="tech-badge">BioBERT</span>
              <span className="tech-badge">Qdrant</span>
            </div>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🧬</div>
            <h3>Rare Disease Detection</h3>
            <p>Comprehensive orphan disease coverage using Human Phenotype Ontology (HPO) with 15,000+ phenotypes</p>
            <div className="feature-tech">
              <span className="tech-badge">HPO</span>
              <span className="tech-badge">ICD-10</span>
            </div>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Multi-Tier Review System</h3>
            <p>Confidence-based routing to appropriate care level (Automated, Primary Care, Specialist, Multi-disciplinary)</p>
            <div className="feature-tech">
              <span className="tech-badge">4 Tiers</span>
            </div>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🚨</div>
            <h3>Red Flag Detection</h3>
            <p>Immediate alerts for life-threatening symptoms requiring emergency care</p>
            <div className="feature-tech">
              <span className="tech-badge">Real-time</span>
            </div>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>Explainable AI</h3>
            <p>Complete transparency in diagnostic reasoning with confidence scores and differential diagnosis rankings</p>
            <div className="feature-tech">
              <span className="tech-badge">GPT-4</span>
            </div>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔒</div>
            <h3>HIPAA Compliant</h3>
            <p>Full audit trail, data anonymization, and secure authentication for healthcare compliance</p>
            <div className="feature-tech">
              <span className="tech-badge">Secure</span>
            </div>
          </div>
        </div>
      </section>

      <section className="tech-stack">
        <h2 className="section-title">Modern Tech Stack</h2>
        <div className="tech-categories">
          <div className="tech-category">
            <h4>Backend</h4>
            <div className="tech-tags">
              <span className="tech-tag">FastAPI</span>
              <span className="tech-tag">Python</span>
              <span className="tech-tag">PostgreSQL</span>
              <span className="tech-tag">Redis</span>
            </div>
          </div>

          <div className="tech-category">
            <h4>AI/ML</h4>
            <div className="tech-tags">
              <span className="tech-tag">Transformers</span>
              <span className="tech-tag">PyTorch</span>
              <span className="tech-tag">BioBERT</span>
              <span className="tech-tag">OpenAI GPT-4</span>
            </div>
          </div>

          <div className="tech-category">
            <h4>Vector Database</h4>
            <div className="tech-tags">
              <span className="tech-tag">Qdrant</span>
              <span className="tech-tag">HNSW</span>
            </div>
          </div>

          <div className="tech-category">
            <h4>Frontend</h4>
            <div className="tech-tags">
              <span className="tech-tag">React 18</span>
              <span className="tech-tag">Vite</span>
              <span className="tech-tag">Axios</span>
            </div>
          </div>
        </div>
      </section>

      <section className="use-cases">
        <h2 className="section-title">Use Cases</h2>
        <div className="use-cases-grid">
          <div className="use-case">
            <div className="use-case-icon">🏥</div>
            <h3>Clinical Decision Support</h3>
            <p>Assist physicians with differential diagnosis generation and clinical recommendations</p>
          </div>

          <div className="use-case">
            <div className="use-case-icon">⚡</div>
            <h3>Emergency Triage</h3>
            <p>Rapid symptom assessment and severity classification for emergency departments</p>
          </div>

          <div className="use-case">
            <div className="use-case-icon">🌐</div>
            <h3>Telemedicine</h3>
            <p>Remote patient evaluation and preliminary diagnosis for telehealth platforms</p>
          </div>

          <div className="use-case">
            <div className="use-case-icon">📚</div>
            <h3>Medical Education</h3>
            <p>Training tool for medical students to learn diagnostic reasoning patterns</p>
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to Experience AI-Powered Diagnosis?</h2>
          <p>Try our advanced diagnostic system or explore the analytics dashboard</p>
          <div className="cta-buttons">
            <Link to="/diagnose" className="btn btn-primary-large">
              Start Diagnosis
            </Link>
            <Link to="/dashboard" className="btn btn-outline-large">
              View Analytics
            </Link>
          </div>
        </div>
      </section>

      <footer className="landing-footer">
        <p>© 2024 Doctor AI - Advanced Medical Symptom Analysis</p>
        <p className="footer-disclaimer">
          This system is a Clinical Decision Support tool and does not replace physician judgment.
          All diagnoses require human review and confirmation.
        </p>
      </footer>
    </div>
  )
}

export default LandingPage

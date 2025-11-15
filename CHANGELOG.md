# Changelog

All notable changes to the Doctor-AI Medical Symptom Constellation Mapper project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive project documentation overhaul
- CONTRIBUTING.md with contribution guidelines
- CHANGELOG.md for tracking project changes
- SECURITY.md for security policy and reporting
- ARCHITECTURE.md for system architecture documentation
- TESTING.md for testing guidelines
- DEPLOYMENT.md for deployment instructions

### Changed
- Updated README.md with corrected GitHub repository URLs

## [0.2.0] - 2024

### Added
- AI Reasoning Assistant powered by Large Language Models
- Natural language explanations for diagnoses
- Intelligent follow-up question generation
- Medical report generation in multiple formats (SOAP, patient-friendly, clinical)
- Simple language explanations for patient education
- Treatment recommendations with AI assistance
- Dataset filtering and processing pipeline
- Intelligent dataset filtering for HPO and ICD-10
- Unified dataset merging with deduplication
- Automated Qdrant indexing for medical conditions
- Comprehensive medical datasets documentation

### Changed
- Enhanced diagnostic engine with AI-powered insights
- Improved confidence scoring mechanism
- Optimized vector similarity search
- Updated dataset processing to reduce size by 75% while maintaining diagnostic value

### Fixed
- Qdrant client version incompatibility issues
- Vector embedding generation performance
- Dataset download and processing edge cases

## [0.1.0] - 2024

### Added
- Initial release of Medical Symptom Constellation Mapper
- Vector similarity search using BioBERT/PubMedBERT embeddings
- Qdrant vector database integration
- FastAPI REST API with comprehensive endpoints
- Differential diagnosis generation
- Multi-tier review system (Tier 1-4 based on confidence)
- Red flag detection for life-threatening symptoms
- Rare disease detection capability
- HIPAA-compliant audit logging
- Clinical decision support features
- PostgreSQL integration for traditional data
- Redis caching layer
- Docker and Docker Compose support
- Comprehensive API documentation (Swagger/ReDoc)
- Initial medical ontology integration:
  - SNOMED CT support
  - ICD-10/11 codes
  - HPO (Human Phenotype Ontology)
  - UMLS integration
- Sample dataset with 8 medical conditions
- Automated database seeding scripts
- Basic testing infrastructure
- Environment-based configuration
- Makefile for common operations
- Quick start guide
- Qdrant setup guide with multiple installation options
- Docker deployment configuration

### API Endpoints
- `POST /api/v1/analyze` - Analyze patient symptoms
- `GET /api/v1/condition/{condition_id}` - Get condition details
- `GET /api/v1/stats` - System statistics
- `GET /health` - Health check

### Infrastructure
- Docker Compose with Qdrant, PostgreSQL, and Redis
- Automated Qdrant setup script
- Model download and caching
- Embedding generation service
- Vector store abstraction layer

### Documentation
- Comprehensive README with installation and usage instructions
- API documentation via Swagger UI and ReDoc
- Quick start guide for developers
- Qdrant setup guide with troubleshooting
- Medical disclaimer and compliance information

### Security
- Environment-based secret management
- API key support for Qdrant Cloud
- Data anonymization capabilities
- Audit trail implementation
- HIPAA compliance features

### Performance
- Query latency <2s (p95)
- Embedding generation ~500ms per case
- Vector search <100ms for 10K vectors
- Support for 100+ queries/second with scaling

---

## Version History Summary

- **v0.2.0**: AI Assistant, Dataset Processing, Enhanced Features
- **v0.1.0**: Initial Release - Core Diagnostic Engine

---

## Upgrade Guide

### Upgrading from 0.1.0 to 0.2.0

1. **Update Dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Update Environment Variables**

   Add to your `.env` file:
   ```env
   # AI Assistant (new in 0.2.0)
   OPENAI_API_KEY=your-api-key-here
   USE_LOCAL_LLM=False
   LOCAL_LLM_MODEL=llama2
   ENABLE_AI_ASSISTANT=True
   ```

3. **Download New Datasets**
   ```bash
   python scripts/download_datasets/download_all_priority.py
   ```

4. **Process and Index Datasets**
   ```bash
   python scripts/process_datasets/process_all.py
   ```

5. **Restart Services**
   ```bash
   docker-compose down
   docker-compose up -d
   python -m src.main
   ```

6. **Test New Features**
   ```bash
   python scripts/test_ai_assistant.py
   ```

---

## Breaking Changes

### v0.2.0

No breaking changes in this version. All v0.1.0 functionality remains compatible.

### v0.1.0

Initial release - no breaking changes.

---

## Deprecation Notices

### v0.2.0

- None

### Future Deprecations

- Legacy seed_data.py will be replaced with dataset processing pipeline in v0.3.0
- Direct SNOMED CT file access will be deprecated in favor of API access in v0.3.0

---

## Known Issues

### v0.2.0

- AI Assistant may occasionally generate hallucinated medical information (use with medical oversight)
- Large dataset processing can be memory-intensive (requires 8GB+ RAM)
- Qdrant collection recreation requires manual deletion if schema changes

### v0.1.0

- Model download on first run can take 5-10 minutes
- Qdrant connection issues on some Docker configurations (see troubleshooting guide)
- Limited rare disease coverage (improved in v0.2.0)

---

## Migration Guides

### Data Migration

No data migration required between versions. Vector collections are backward compatible.

### Configuration Migration

New configuration options are added with sensible defaults. Update `.env` file as needed.

---

## Contributors

Thank you to all contributors who have helped improve Doctor-AI!

- Project Lead: Abrar
- Contributors: See GitHub contributors page

---

## Feedback and Reporting

- **Bug Reports**: https://github.com/Abrar5510/Doctor-Ai/issues
- **Feature Requests**: https://github.com/Abrar5510/Doctor-Ai/discussions
- **Security Issues**: See SECURITY.md

---

**Note**: Dates in YYYY-MM-DD format. Versions follow semantic versioning (MAJOR.MINOR.PATCH).

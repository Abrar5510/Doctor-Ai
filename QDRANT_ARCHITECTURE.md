# Qdrant Database Architecture

## Overview
This document describes the Qdrant-based database architecture for Doctor-AI, replacing PostgreSQL with Qdrant as the primary database.

## Collections Structure

### 1. **users** Collection
- **Vector Field**: Embedding of user profile (username + full_name + role)
- **Vector Dimension**: 768 (BiomedNLP-PubMedBERT)
- **Payload Fields**:
  - id (integer)
  - username (string)
  - email (string)
  - hashed_password (string)
  - full_name (string)
  - role (string: admin, physician, nurse, researcher, api_user)
  - status (string: active, inactive, suspended, pending_verification)
  - is_active (boolean)
  - is_verified (boolean)
  - failed_login_attempts (integer)
  - locked_until (datetime)
  - password_changed_at (datetime)
  - password_reset_token (string)
  - password_reset_expires (datetime)
  - verification_token (string)
  - verification_expires (datetime)
  - created_at (datetime)
  - updated_at (datetime)
  - last_login_at (datetime)
  - created_by (integer)

### 2. **user_sessions** Collection
- **Vector Field**: Embedding of session metadata (user_agent + device_info)
- **Vector Dimension**: 768
- **Payload Fields**:
  - id (integer)
  - user_id (integer)
  - token_jti (string)
  - ip_address (string)
  - user_agent (string)
  - device_info (string)
  - created_at (datetime)
  - expires_at (datetime)
  - last_activity_at (datetime)
  - revoked_at (datetime)
  - is_active (boolean)

### 3. **audit_logs** Collection
- **Vector Field**: Embedding of action + description
- **Vector Dimension**: 768
- **Payload Fields**:
  - id (integer)
  - user_id (integer)
  - action (string)
  - resource_type (string)
  - resource_id (string)
  - status (string)
  - ip_address (string)
  - user_agent (string)
  - request_method (string)
  - request_path (string)
  - description (string)
  - metadata_json (string)
  - error_message (string)
  - timestamp (datetime)
  - duration_ms (integer)

### 4. **api_keys** Collection
- **Vector Field**: Embedding of key name + description
- **Vector Dimension**: 768
- **Payload Fields**:
  - id (integer)
  - user_id (integer)
  - key_hash (string)
  - key_prefix (string)
  - name (string)
  - description (string)
  - scopes (string)
  - rate_limit (integer)
  - is_active (boolean)
  - created_at (datetime)
  - expires_at (datetime)
  - last_used_at (datetime)
  - revoked_at (datetime)
  - total_requests (integer)

### 5. **patient_cases** Collection
- **Vector Field**: Embedding of chief_complaint + symptoms
- **Vector Dimension**: 768
- **Payload Fields**:
  - id (integer)
  - case_id (string)
  - user_id (integer)
  - patient_age (integer)
  - patient_sex (string)
  - patient_ethnicity (string)
  - patient_location (string)
  - chief_complaint (string)
  - symptoms_json (string)
  - medical_history_json (string)
  - family_history_json (string)
  - medications_json (string)
  - allergies_json (string)
  - top_diagnosis (string)
  - confidence_score (integer)
  - review_tier (integer)
  - has_red_flags (boolean)
  - red_flags_json (string)
  - status (string)
  - priority (string)
  - assigned_to_user_id (integer)
  - created_at (datetime)
  - updated_at (datetime)
  - reviewed_at (datetime)

### 6. **diagnosis_records** Collection
- **Vector Field**: Embedding of condition_name + matching_symptoms
- **Vector Dimension**: 768
- **Payload Fields**:
  - id (integer)
  - case_id (integer)
  - condition_id (string)
  - condition_name (string)
  - icd10_code (string)
  - snomed_code (string)
  - similarity_score (integer)
  - confidence_score (integer)
  - probability (integer)
  - rank (integer)
  - is_rare_disease (boolean)
  - urgency_level (string)
  - specialty (string)
  - matching_symptoms_json (string)
  - supporting_evidence_json (string)
  - distinguishing_features_json (string)
  - typical_age_range (string)
  - sex_predilection (string)
  - prevalence (string)
  - physician_confirmed (boolean)
  - physician_notes (string)
  - physician_id (integer)
  - reviewed_at (datetime)
  - created_at (datetime)

### 7. **system_metrics** Collection
- **Vector Field**: Embedding of metric_type + metric_name
- **Vector Dimension**: 768
- **Payload Fields**:
  - id (integer)
  - metric_type (string)
  - metric_name (string)
  - metric_value (integer)
  - metric_unit (string)
  - endpoint (string)
  - user_id (integer)
  - request_id (string)
  - metadata_json (string)
  - timestamp (datetime)

### 8. **medical_conditions** Collection (PRIMARY MEDICAL KNOWLEDGE BASE)
- **Vector Field**: Embedding of condition_name + typical_symptoms + rare_symptoms
- **Vector Dimension**: 768
- **Payload Fields**:
  - id (integer)
  - condition_id (string)
  - condition_name (string)
  - icd_codes_json (string)
  - snomed_codes_json (string)
  - typical_symptoms_json (string)
  - rare_symptoms_json (string)
  - red_flag_symptoms_json (string)
  - prevalence (integer)
  - is_rare_disease (boolean)
  - urgency_level (string)
  - temporal_pattern (string)
  - diagnostic_criteria_json (string)
  - differential_diagnoses_json (string)
  - recommended_tests_json (string)
  - specialist_referral (string)
  - distinguishing_features_json (string)
  - evidence_sources_json (string)
  - typical_age_range (string)
  - sex_predilection (string)
  - created_at (datetime)
  - updated_at (datetime)

## Data Loading Strategy

1. **CSV Files** stored in `/data/` directory
2. **Initialization Script** reads CSV and loads into Qdrant
3. **Embedding Generation** using BiomedNLP-PubMedBERT model
4. **Vector Indexing** using HNSW algorithm for fast similarity search

## Benefits of Qdrant Architecture

1. **Semantic Search**: Find similar cases, diagnoses, or conditions using vector similarity
2. **Flexible Schema**: Easy to add new fields without migrations
3. **Scalability**: Horizontal scaling for large medical datasets
4. **Rich Filtering**: Combine vector search with payload filters
5. **Performance**: Fast vector search for real-time diagnosis suggestions

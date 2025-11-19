"""
Seed script to populate PostgreSQL with medical conditions (ML-free version).

This version stores medical conditions in PostgreSQL for keyword-based search.
No ML embeddings or vector databases required.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from loguru import logger

from src.database import SessionLocal
from src.models.database import MedicalCondition
from src.models.schemas import UrgencyLevel


# Sample medical conditions for demonstration
SAMPLE_CONDITIONS = [
    {
        "condition_id": "cond_hypothyroidism",
        "condition_name": "Hypothyroidism",
        "icd_codes": ["E03.9"],
        "snomed_codes": ["40930008"],
        "prevalence": 0.05,  # 5% prevalence
        "is_rare_disease": False,
        "typical_symptoms": [
            "fatigue",
            "weight gain",
            "cold intolerance",
            "dry skin",
            "constipation",
            "hair loss",
            "depression",
            "muscle weakness"
        ],
        "rare_symptoms": ["myxedema", "hoarseness"],
        "red_flag_symptoms": ["severe myxedema", "hypothyroid coma"],
        "temporal_pattern": "Gradual onset over months to years",
        "diagnostic_criteria": [
            "Elevated TSH",
            "Low Free T4",
            "Presence of thyroid antibodies"
        ],
        "differential_diagnoses": [
            "Depression",
            "Chronic fatigue syndrome",
            "Anemia"
        ],
        "urgency_level": "routine",
        "recommended_tests": ["TSH", "Free T4", "TPO antibodies"],
        "specialist_referral": "Endocrinologist",
        "distinguishing_features": ["Delayed reflexes", "Periorbital edema"],
        "evidence_sources": [
            "American Thyroid Association Guidelines 2023",
            "PMID: 12345678"
        ],
        "typical_age_range": "40-60 years",
        "sex_predilection": "Female (9:1)"
    },
    {
        "condition_id": "cond_type2_diabetes",
        "condition_name": "Type 2 Diabetes Mellitus",
        "icd_codes": ["E11.9"],
        "snomed_codes": ["44054006"],
        "prevalence": 0.10,  # 10% prevalence
        "is_rare_disease": False,
        "typical_symptoms": [
            "increased thirst",
            "frequent urination",
            "increased hunger",
            "fatigue",
            "blurred vision",
            "slow wound healing",
            "tingling in hands or feet"
        ],
        "rare_symptoms": ["diabetic ketoacidosis in type 2"],
        "red_flag_symptoms": [
            "diabetic ketoacidosis",
            "hyperosmolar hyperglycemic state"
        ],
        "temporal_pattern": "Gradual onset, often asymptomatic initially",
        "diagnostic_criteria": [
            "Fasting glucose ≥126 mg/dL",
            "HbA1c ≥6.5%",
            "Random glucose ≥200 mg/dL with symptoms"
        ],
        "differential_diagnoses": [
            "Type 1 Diabetes",
            "MODY",
            "Secondary diabetes"
        ],
        "urgency_level": "routine",
        "recommended_tests": [
            "Fasting glucose",
            "HbA1c",
            "Lipid panel",
            "Kidney function"
        ],
        "specialist_referral": "Endocrinologist",
        "distinguishing_features": ["Acanthosis nigricans", "Central obesity"],
        "evidence_sources": ["ADA Standards of Care 2024"],
        "typical_age_range": "45+ years",
        "sex_predilection": "Equal"
    },
    {
        "condition_id": "cond_myotonic_dystrophy",
        "condition_name": "Myotonic Dystrophy Type 1",
        "icd_codes": ["G71.11"],
        "snomed_codes": ["277952003"],
        "prevalence": 0.00001,  # 1 in 100,000
        "is_rare_disease": True,
        "typical_symptoms": [
            "progressive muscle weakness",
            "myotonia",
            "delayed muscle relaxation",
            "cataracts",
            "cardiac arrhythmias",
            "frontal balding",
            "testicular atrophy",
            "excessive daytime sleepiness"
        ],
        "rare_symptoms": [
            "congenital form with respiratory failure",
            "severe cognitive impairment"
        ],
        "red_flag_symptoms": [
            "cardiac conduction defects",
            "respiratory failure"
        ],
        "temporal_pattern": "Progressive, onset typically in adolescence to adulthood",
        "diagnostic_criteria": [
            "Clinical myotonia",
            "CTG repeat expansion in DMPK gene",
            "Multisystem involvement"
        ],
        "differential_diagnoses": [
            "Myotonic Dystrophy Type 2",
            "Limb-girdle muscular dystrophy",
            "Hypothyroidism"
        ],
        "urgency_level": "urgent",
        "recommended_tests": [
            "DMPK genetic testing",
            "EMG",
            "ECG",
            "Echocardiogram",
            "Pulmonary function tests"
        ],
        "specialist_referral": "Neuromuscular specialist",
        "distinguishing_features": ["Hatchet face", "Percussion myotonia"],
        "evidence_sources": [
            "Orphanet",
            "GeneReviews: Myotonic Dystrophy Type 1"
        ],
        "typical_age_range": "20-40 years",
        "sex_predilection": "Equal"
    },
    {
        "condition_id": "cond_acute_coronary_syndrome",
        "condition_name": "Acute Coronary Syndrome",
        "icd_codes": ["I24.9"],
        "snomed_codes": ["394659003"],
        "prevalence": 0.003,  # 0.3% annual incidence
        "is_rare_disease": False,
        "typical_symptoms": [
            "chest pain",
            "chest pressure",
            "shortness of breath",
            "nausea",
            "sweating",
            "pain radiating to arm",
            "pain radiating to jaw",
            "lightheadedness"
        ],
        "rare_symptoms": ["epigastric pain only", "toothache"],
        "red_flag_symptoms": [
            "severe chest pain",
            "chest pain with ST elevation",
            "cardiogenic shock"
        ],
        "temporal_pattern": "Acute onset, symptoms typically lasting >10 minutes",
        "diagnostic_criteria": [
            "Elevated troponin",
            "ECG changes (ST elevation/depression, T wave inversion)",
            "Clinical presentation consistent with ACS"
        ],
        "differential_diagnoses": [
            "Pulmonary embolism",
            "Aortic dissection",
            "Pericarditis",
            "GERD"
        ],
        "urgency_level": "emergency",
        "recommended_tests": [
            "ECG",
            "Troponin I/T",
            "Chest X-ray",
            "Coronary angiography"
        ],
        "specialist_referral": "Cardiologist",
        "distinguishing_features": ["Levine sign", "Diaphoresis"],
        "evidence_sources": [
            "ACC/AHA Guidelines for STEMI 2023",
            "ESC Guidelines for ACS 2023"
        ],
        "typical_age_range": "55+ years",
        "sex_predilection": "Male (2:1 before age 65)"
    },
    {
        "condition_id": "cond_migraine",
        "condition_name": "Migraine with Aura",
        "icd_codes": ["G43.1"],
        "snomed_codes": ["4473006"],
        "prevalence": 0.12,  # 12% prevalence
        "is_rare_disease": False,
        "typical_symptoms": [
            "severe headache",
            "visual aura",
            "photophobia",
            "phonophobia",
            "nausea",
            "vomiting",
            "pulsating headache",
            "unilateral headache"
        ],
        "rare_symptoms": ["hemiplegic aura", "brainstem aura"],
        "red_flag_symptoms": [
            "sudden severe headache",
            "headache with fever and stiff neck",
            "new onset after age 50"
        ],
        "temporal_pattern": "Episodic, lasting 4-72 hours, often preceded by aura",
        "diagnostic_criteria": [
            "At least 5 attacks fulfilling criteria",
            "Headache lasting 4-72 hours",
            "At least 2 of: unilateral, pulsating, moderate-severe intensity, aggravated by activity",
            "At least 1 of: nausea/vomiting, photophobia and phonophobia"
        ],
        "differential_diagnoses": [
            "Tension-type headache",
            "Cluster headache",
            "Medication overuse headache",
            "Secondary headache disorders"
        ],
        "urgency_level": "routine",
        "recommended_tests": [
            "Clinical diagnosis (imaging if red flags present)",
            "MRI brain (if atypical features)"
        ],
        "specialist_referral": "Neurologist",
        "distinguishing_features": ["Aura preceding headache", "Family history"],
        "evidence_sources": [
            "International Classification of Headache Disorders-3",
            "American Headache Society Guidelines"
        ],
        "typical_age_range": "18-50 years",
        "sex_predilection": "Female (3:1)"
    }
]


def seed_medical_conditions(db: Session):
    """Populate database with sample medical conditions."""
    logger.info("Starting to seed medical conditions...")

    # Clear existing data
    logger.info("Clearing existing medical conditions...")
    db.query(MedicalCondition).delete()
    db.commit()

    # Add each condition
    for cond_data in SAMPLE_CONDITIONS:
        # Create searchable text (space-separated symptoms for simple matching)
        all_symptoms = (
            cond_data.get("typical_symptoms", []) +
            cond_data.get("rare_symptoms", []) +
            cond_data.get("red_flag_symptoms", [])
        )
        symptoms_searchable = " ".join(all_symptoms).lower()

        # Convert prevalence to integer (multiply by 1 million)
        prevalence_int = int(cond_data["prevalence"] * 1000000)

        # Create database record
        db_condition = MedicalCondition(
            condition_id=cond_data["condition_id"],
            condition_name=cond_data["condition_name"],
            icd_codes_json=json.dumps(cond_data.get("icd_codes", [])),
            snomed_codes_json=json.dumps(cond_data.get("snomed_codes", [])),
            typical_symptoms_json=json.dumps(cond_data.get("typical_symptoms", [])),
            rare_symptoms_json=json.dumps(cond_data.get("rare_symptoms", [])),
            red_flag_symptoms_json=json.dumps(cond_data.get("red_flag_symptoms", [])),
            symptoms_searchable=symptoms_searchable,
            prevalence=prevalence_int,
            is_rare_disease=cond_data.get("is_rare_disease", False),
            urgency_level=cond_data.get("urgency_level", "routine"),
            temporal_pattern=cond_data.get("temporal_pattern"),
            diagnostic_criteria_json=json.dumps(cond_data.get("diagnostic_criteria", [])),
            differential_diagnoses_json=json.dumps(cond_data.get("differential_diagnoses", [])),
            recommended_tests_json=json.dumps(cond_data.get("recommended_tests", [])),
            specialist_referral=cond_data.get("specialist_referral"),
            distinguishing_features_json=json.dumps(cond_data.get("distinguishing_features", [])),
            evidence_sources_json=json.dumps(cond_data.get("evidence_sources", [])),
            typical_age_range=cond_data.get("typical_age_range"),
            sex_predilection=cond_data.get("sex_predilection"),
        )

        db.add(db_condition)
        logger.info(f"Added: {cond_data['condition_name']}")

    # Commit all changes
    db.commit()
    logger.info(f"Successfully seeded {len(SAMPLE_CONDITIONS)} medical conditions")


def main():
    """Main entry point."""
    logger.info("="  * 60)
    logger.info("Doctor-AI Database Seeding (Lite Version - No ML)")
    logger.info("=" * 60)

    try:
        # Create database session
        db = SessionLocal()

        try:
            # Seed medical conditions
            seed_medical_conditions(db)

            logger.info("=" * 60)
            logger.info("Seeding completed successfully!")
            logger.info("=" * 60)

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise


if __name__ == "__main__":
    main()

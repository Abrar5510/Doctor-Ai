"""
Seed script to populate the vector database with sample medical conditions
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.schemas import MedicalCondition, UrgencyLevel
from src.services.embedding import EmbeddingService
from src.services.vector_store import VectorStoreService
from loguru import logger


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
        "urgency_level": UrgencyLevel.ROUTINE,
        "recommended_tests": ["TSH", "Free T4", "TPO antibodies"],
        "specialist_referral": "Endocrinologist",
        "evidence_sources": [
            "American Thyroid Association Guidelines 2023",
            "PMID: 12345678"
        ]
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
        "urgency_level": UrgencyLevel.ROUTINE,
        "recommended_tests": [
            "Fasting glucose",
            "HbA1c",
            "Lipid panel",
            "Kidney function"
        ],
        "specialist_referral": "Endocrinologist",
        "evidence_sources": ["ADA Standards of Care 2024"]
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
            "myotonia (delayed muscle relaxation)",
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
        "urgency_level": UrgencyLevel.URGENT,
        "recommended_tests": [
            "DMPK genetic testing",
            "EMG",
            "ECG",
            "Echocardiogram",
            "Pulmonary function tests"
        ],
        "specialist_referral": "Neuromuscular specialist",
        "evidence_sources": [
            "Orphanet",
            "GeneReviews: Myotonic Dystrophy Type 1"
        ]
    },
    {
        "condition_id": "cond_acute_coronary_syndrome",
        "condition_name": "Acute Coronary Syndrome",
        "icd_codes": ["I24.9"],
        "snomed_codes": ["394659003"],
        "prevalence": 0.002,
        "is_rare_disease": False,
        "typical_symptoms": [
            "chest pain",
            "pressure or tightness in chest",
            "pain radiating to arm, jaw, or back",
            "shortness of breath",
            "diaphoresis",
            "nausea",
            "lightheadedness"
        ],
        "rare_symptoms": ["silent MI in diabetics"],
        "red_flag_symptoms": [
            "severe chest pain",
            "ST elevation on ECG",
            "hemodynamic instability"
        ],
        "temporal_pattern": "Acute onset, typically lasting >15-20 minutes",
        "diagnostic_criteria": [
            "Elevated troponin",
            "ECG changes (ST elevation or depression)",
            "Clinical presentation consistent with ACS"
        ],
        "differential_diagnoses": [
            "Pulmonary embolism",
            "Aortic dissection",
            "Pericarditis",
            "GERD"
        ],
        "urgency_level": UrgencyLevel.EMERGENCY,
        "recommended_tests": [
            "ECG",
            "Troponin",
            "Chest X-ray",
            "Cardiac catheterization"
        ],
        "specialist_referral": "Cardiologist",
        "evidence_sources": [
            "ACC/AHA STEMI Guidelines 2023",
            "ESC Guidelines 2023"
        ]
    },
    {
        "condition_id": "cond_systemic_lupus",
        "condition_name": "Systemic Lupus Erythematosus",
        "icd_codes": ["M32.9"],
        "snomed_codes": ["55464009"],
        "prevalence": 0.0005,  # 0.05%
        "is_rare_disease": False,
        "typical_symptoms": [
            "malar rash",
            "photosensitivity",
            "joint pain",
            "fatigue",
            "fever",
            "kidney dysfunction",
            "oral ulcers",
            "serositis"
        ],
        "rare_symptoms": [
            "lupus nephritis",
            "CNS lupus",
            "lupus pneumonitis"
        ],
        "red_flag_symptoms": [
            "severe kidney dysfunction",
            "CNS involvement",
            "severe thrombocytopenia"
        ],
        "temporal_pattern": "Relapsing-remitting course with flares",
        "diagnostic_criteria": [
            "ANA positive",
            "Anti-dsDNA or anti-Smith antibodies",
            "Low complement (C3, C4)",
            "Meeting ACR/EULAR classification criteria"
        ],
        "differential_diagnoses": [
            "Mixed Connective Tissue Disease",
            "Rheumatoid Arthritis",
            "Drug-induced lupus",
            "Undifferentiated CTD"
        ],
        "urgency_level": UrgencyLevel.URGENT,
        "recommended_tests": [
            "ANA",
            "Anti-dsDNA",
            "Complement levels",
            "CBC",
            "Urinalysis",
            "Kidney function"
        ],
        "specialist_referral": "Rheumatologist",
        "evidence_sources": [
            "ACR/EULAR SLE Criteria 2019",
            "EULAR Recommendations 2023"
        ]
    },
    {
        "condition_id": "cond_iron_deficiency_anemia",
        "condition_name": "Iron Deficiency Anemia",
        "icd_codes": ["D50.9"],
        "snomed_codes": ["87522002"],
        "prevalence": 0.02,  # 2%
        "is_rare_disease": False,
        "typical_symptoms": [
            "fatigue",
            "weakness",
            "pale skin",
            "shortness of breath",
            "dizziness",
            "cold hands and feet",
            "brittle nails",
            "craving for ice or non-food items (pica)"
        ],
        "rare_symptoms": ["restless leg syndrome", "glossitis"],
        "red_flag_symptoms": ["severe anemia with hemodynamic instability"],
        "temporal_pattern": "Gradual onset over weeks to months",
        "diagnostic_criteria": [
            "Low hemoglobin",
            "Low ferritin",
            "Low serum iron",
            "Elevated TIBC",
            "Microcytic anemia on CBC"
        ],
        "differential_diagnoses": [
            "Thalassemia",
            "Anemia of chronic disease",
            "Sideroblastic anemia"
        ],
        "urgency_level": UrgencyLevel.ROUTINE,
        "recommended_tests": [
            "CBC",
            "Ferritin",
            "Iron studies",
            "Stool occult blood",
            "Colonoscopy if indicated"
        ],
        "specialist_referral": "Hematologist",
        "evidence_sources": ["WHO Guidelines on Iron Deficiency"]
    },
    {
        "condition_id": "cond_parkinsons",
        "condition_name": "Parkinson's Disease",
        "icd_codes": ["G20"],
        "snomed_codes": ["49049000"],
        "prevalence": 0.001,  # 0.1%
        "is_rare_disease": False,
        "typical_symptoms": [
            "resting tremor",
            "bradykinesia",
            "rigidity",
            "postural instability",
            "shuffling gait",
            "reduced facial expression",
            "soft speech",
            "difficulty with fine motor tasks"
        ],
        "rare_symptoms": [
            "early-onset parkinsonism",
            "rapid eye movement sleep behavior disorder"
        ],
        "red_flag_symptoms": ["falls", "severe autonomic dysfunction"],
        "temporal_pattern": "Progressive, gradual onset over years",
        "diagnostic_criteria": [
            "Bradykinesia",
            "Plus at least one of: resting tremor, rigidity",
            "Response to levodopa",
            "Absence of atypical features"
        ],
        "differential_diagnoses": [
            "Essential tremor",
            "Multiple system atrophy",
            "Progressive supranuclear palsy",
            "Drug-induced parkinsonism"
        ],
        "urgency_level": UrgencyLevel.ROUTINE,
        "recommended_tests": [
            "Clinical diagnosis",
            "DaTscan (if uncertain)",
            "MRI brain",
            "Levodopa trial"
        ],
        "specialist_referral": "Movement disorder specialist",
        "evidence_sources": [
            "MDS Diagnostic Criteria 2015",
            "AAN Practice Guidelines"
        ]
    },
    {
        "condition_id": "cond_celiac_disease",
        "condition_name": "Celiac Disease",
        "icd_codes": ["K90.0"],
        "snomed_codes": ["396331005"],
        "prevalence": 0.01,  # 1%
        "is_rare_disease": False,
        "typical_symptoms": [
            "chronic diarrhea",
            "abdominal bloating",
            "weight loss",
            "fatigue",
            "anemia",
            "dermatitis herpetiformis",
            "osteoporosis"
        ],
        "rare_symptoms": [
            "neurological symptoms",
            "ataxia",
            "peripheral neuropathy"
        ],
        "red_flag_symptoms": ["severe malnutrition", "refractory celiac disease"],
        "temporal_pattern": "Can present at any age, chronic symptoms",
        "diagnostic_criteria": [
            "Positive tissue transglutaminase (tTG-IgA)",
            "Villous atrophy on duodenal biopsy",
            "Response to gluten-free diet",
            "HLA-DQ2 or DQ8 positive"
        ],
        "differential_diagnoses": [
            "Irritable bowel syndrome",
            "Inflammatory bowel disease",
            "Non-celiac gluten sensitivity",
            "Lactose intolerance"
        ],
        "urgency_level": UrgencyLevel.ROUTINE,
        "recommended_tests": [
            "tTG-IgA",
            "Total IgA",
            "EMA",
            "Duodenal biopsy",
            "HLA-DQ typing"
        ],
        "specialist_referral": "Gastroenterologist",
        "evidence_sources": [
            "ACG Clinical Guidelines 2023",
            "ESPGHAN Guidelines"
        ]
    },
]


def seed_database():
    """Seed the vector database with sample conditions"""
    logger.info("Starting database seeding process")

    # Initialize services
    logger.info("Initializing embedding service...")
    embedding_service = EmbeddingService()
    embedding_service.initialize()

    logger.info("Initializing vector store...")
    vector_store = VectorStoreService()
    vector_store.initialize()

    # Create collection (recreate if exists)
    logger.info("Creating Qdrant collection...")
    vector_store.create_collection(recreate=True)

    # Process each condition
    logger.info(f"Processing {len(SAMPLE_CONDITIONS)} medical conditions...")

    conditions = []
    embeddings = []

    for cond_data in SAMPLE_CONDITIONS:
        # Create MedicalCondition object
        condition = MedicalCondition(**cond_data)
        conditions.append(condition)

        # Generate embedding
        logger.info(f"Generating embedding for: {condition.condition_name}")
        embedding = embedding_service.encode_medical_condition(
            condition_name=condition.condition_name,
            typical_symptoms=condition.typical_symptoms,
            rare_symptoms=condition.rare_symptoms,
            temporal_pattern=condition.temporal_pattern
        )
        embeddings.append(embedding)

    # Batch insert
    logger.info("Inserting conditions into vector database...")
    vector_store.add_conditions_batch(conditions, embeddings)

    # Verify
    stats = vector_store.get_collection_stats()
    logger.info(f"Database seeding complete!")
    logger.info(f"Total conditions in database: {stats.get('total_conditions', 0)}")

    # Cleanup
    embedding_service.shutdown()
    vector_store.shutdown()


if __name__ == "__main__":
    seed_database()

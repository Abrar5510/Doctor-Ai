# Medical Datasets

This directory contains medical datasets used by Doctor-AI.

## Directory Structure

```
datasets/
├── ontologies/          # Medical ontologies
│   ├── hpo/            # Human Phenotype Ontology
│   ├── icd10/          # ICD-10-CM disease codes
│   ├── snomed_ct/      # SNOMED CT (external)
│   └── umls/           # UMLS (external)
├── samples/            # Sample datasets for testing
└── temp/               # Temporary processing files
```

## Datasets

### Human Phenotype Ontology (HPO)
- **Size**: ~50MB
- **Description**: Standardized vocabulary of phenotypic abnormalities
- **Use**: Rare disease detection

### ICD-10-CM Codes
- **Size**: ~50MB
- **Description**: International Classification of Diseases
- **Use**: Disease classification and coding

### Disease-Symptom Mappings
- **Size**: ~5MB
- **Description**: Curated symptom-disease relationships
- **Use**: ML model training

## Downloading Datasets

```bash
# Download all priority datasets
python scripts/download_datasets/download_all_priority.py

# Individual downloads
python scripts/download_datasets/download_hpo.py
python scripts/download_datasets/download_icd10.py
```

## Processing Datasets

```bash
# Index datasets in Qdrant
python scripts/process_datasets/index_hpo.py
python scripts/process_datasets/index_icd10.py

# Seed database
python scripts/seed_data.py
```

## Notes

- Large datasets (>50MB) are excluded from Git
- External datasets require credentials (MIMIC, UMLS, SNOMED CT)
- See individual scripts in `scripts/download_datasets/` for details

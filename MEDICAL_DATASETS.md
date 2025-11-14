# Medical Datasets for Doctor-Ai

This document provides a comprehensive overview of large medical datasets relevant to the Doctor-Ai project. These datasets contain disease information, symptoms, clinical notes, and medical ontologies that can enhance the diagnostic support system.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Disease-Symptom Datasets](#disease-symptom-datasets)
- [Medical Ontologies](#medical-ontologies)
- [Clinical Databases](#clinical-databases)
- [Genomic & Phenotype Datasets](#genomic--phenotype-datasets)
- [Imaging Datasets](#imaging-datasets)
- [Download Instructions](#download-instructions)
- [GitHub Size Considerations](#github-size-considerations)

---

## Quick Reference

| Dataset | Size | Records/Entities | Best For | Access |
|---------|------|------------------|----------|--------|
| NIH Clinical Tables | ~10MB | 2,400+ conditions | ICD codes, symptoms | Free API |
| EndlessMedical | ~50MB | 830+ features, 180+ diseases | JSON symptom data | Free API |
| Kaggle Disease-Symptom | ~2MB | 3,490 records, 100+ conditions | ML training | Free download |
| MIMIC-III | ~60GB | 40,000+ patients | Clinical notes, ICU data | Registration required |
| MIMIC-IV | ~100GB | 73,000+ patients | EHR data, diagnoses | Registration required |
| HPO | ~50MB | 15,247 phenotype terms | Rare diseases, phenotypes | Free download |
| SNOMED CT | ~500MB-2GB | 350,000+ concepts | Medical terminology | NLM license |
| ICD-10-CM | ~50MB | 70,000+ codes | Disease classification | Free download |
| UMLS | ~10GB | 4M+ concepts | Unified medical terms | Free registration |

---

## Disease-Symptom Datasets

### 1. Kaggle Disease Symptoms and Patient Profile Dataset

**Description**: A comprehensive dataset examining relationships between patients and diseases.

**Statistics**:
- **Records**: 3,490 patient records
- **Diseases**: 100+ distinct medical conditions
- **Symptoms**: Fever, cough, fatigue, breathing difficulty, and more
- **Demographics**: Age, gender, blood pressure, cholesterol levels

**Format**: CSV

**Size**: ~2MB

**Use Cases**:
- Training symptom-to-disease ML models
- Differential diagnosis validation
- Patient profile analysis

**Download**:
```bash
# Using Kaggle API
kaggle datasets download -d uom190346a/disease-symptoms-and-patient-profile-dataset
```

**Link**: https://www.kaggle.com/datasets/uom190346a/disease-symptoms-and-patient-profile-dataset

---

### 2. EndlessMedical API & Dictionaries

**Description**: Free database of symptoms, signs, physical examination findings, tests, and diseases in JSON format.

**Statistics**:
- **Clinical Data Points**: 2,000+
- **Features**: 830+ grouped features
- **Diseases**: 180+ diseases
- **Format**: JSON

**Size**: ~50MB (estimated for full database)

**Use Cases**:
- Symptom checker integration
- Medical feature extraction
- Disease probability calculations

**API Access**:
```python
# API endpoint
base_url = "https://api.endlessmedical.com/v1/dx"
```

**Download**:
```bash
# JSON dictionaries available at
wget https://www.endlessmedical.com/dictionaries-json/
```

**Link**: https://www.endlessmedical.com/dictionaries-json/

---

### 3. NIH Clinical Table Search Service - Medical Conditions

**Description**: Comprehensive medical conditions list from NIH with ICD codes and synonyms.

**Statistics**:
- **Conditions**: 2,400+ medical conditions
- **ICD-10-CM Codes**: Complete mapping
- **ICD-9-CM Codes**: Legacy mapping
- **Synonyms**: Extensive term variations

**Format**: JSON API

**Size**: ~10MB

**Use Cases**:
- Medical condition lookup
- ICD code mapping
- Terminology standardization

**API Access**:
```bash
# Example API call
curl "https://clinicaltables.nlm.nih.gov/api/conditions/v3/search?terms=diabetes"
```

**Link**: https://clinicaltables.nlm.nih.gov/apidoc/conditions/v3/doc.html

---

### 4. Disease Database (data.world)

**Description**: Collection of 245 disease datasets from various sources.

**Statistics**:
- **Datasets**: 245 disease-related datasets
- **Variety**: Multiple data formats and sources

**Format**: Various (CSV, JSON, Excel)

**Size**: Varies by dataset (1MB - 1GB each)

**Link**: https://data.world/datasets/disease

---

## Medical Ontologies

### 1. Human Phenotype Ontology (HPO)

**Description**: Standardized vocabulary of phenotypic abnormalities in human disease, essential for rare disease detection.

**Statistics**:
- **Phenotype Terms**: 15,247 terms
- **Diseases Annotated**: ~8,000 rare diseases
- **Updates**: Bi-monthly releases

**Format**:
- OBO (Ontology)
- OWL (Web Ontology Language)
- JSON
- TSV (phenotype.hpoa)

**Size**: ~50MB

**Use Cases**:
- Rare disease detection
- Phenotype-based diagnosis
- Gene-to-phenotype mapping

**Key Files**:
- `hp.obo` - Main ontology file
- `phenotype.hpoa` - Disease-to-phenotype annotations
- `genes_to_phenotype.txt` - Gene associations
- `phenotype_to_genes.txt` - Reverse mapping

**Download**:
```bash
# Latest release
wget https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download/hp.obo
wget https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download/phenotype.hpoa
```

**GitHub**: https://github.com/obophenotype/human-phenotype-ontology

**Official Site**: https://hpo.jax.org/

---

### 2. SNOMED CT (Systematized Nomenclature of Medicine - Clinical Terms)

**Description**: The most comprehensive, multilingual clinical healthcare terminology in the world.

**Statistics**:
- **Concepts**: 350,000+ active concepts
- **Descriptions**: 1,000,000+ descriptions
- **Relationships**: Extensive hierarchical relationships
- **Languages**: Multiple language support

**Format**: RF2 (Release Format 2), OWL

**Size**: ~500MB - 2GB (depending on edition)

**Use Cases**:
- Clinical documentation standardization
- Cross-terminology mapping (ICD-9/10, LOINC)
- Semantic search and reasoning

**Key Features**:
- Maps to ICD-9-CM, ICD-10-CM, ICD-10-AM
- Includes 126,000+ SNOMED CT to ICD-10-CM mappings
- LOINC laboratory term mappings

**Download**:
1. Register at NLM UMLS: https://www.nlm.nih.gov/research/umls/
2. Access SNOMED CT US Edition: https://www.nlm.nih.gov/healthit/snomedct/us_edition.html
3. Download from MLDS (for International Edition)

**Note**: Requires free NLM license registration

---

### 3. ICD-10-CM (International Classification of Diseases, 10th Revision)

**Description**: Standard diagnostic classification for clinical and research purposes.

**Statistics**:
- **Codes**: 70,000+ diagnostic codes
- **Categories**: 21 chapters
- **Updates**: Annual releases

**Format**: XML, TXT, CSV

**Size**: ~50MB

**Use Cases**:
- Disease classification
- Diagnosis coding
- Insurance and billing
- Epidemiological research

**Download**:
```bash
# From CDC
wget https://www.cdc.gov/nchs/icd/icd-10-cm.htm
```

**Link**: https://www.cdc.gov/nchs/icd/icd-10-cm.htm

---

### 4. UMLS (Unified Medical Language System)

**Description**: Comprehensive repository integrating biomedical terminology from multiple sources.

**Statistics**:
- **Concepts**: 4,000,000+ concepts
- **Source Vocabularies**: 200+ sources
- **Terms**: 15,000,000+ terms

**Format**: RRF (Rich Release Format), SQL

**Size**: ~10GB (full installation)

**Use Cases**:
- Cross-terminology mapping
- Natural language processing
- Semantic interoperability

**Download**:
1. Register at NLM: https://uts.nlm.nih.gov/uts/signup-login
2. Download from: https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html

**Note**: Free registration required

---

## Clinical Databases

### 1. MIMIC-III (Medical Information Mart for Intensive Care)

**Description**: Deidentified health data from ICU patients at Beth Israel Deaconess Medical Center (2001-2012).

**Statistics**:
- **Patients**: 40,000+ critical care patients
- **Admissions**: 53,000+ hospital admissions
- **Notes**: Physician and nursing notes, discharge summaries
- **Time Period**: 2001-2012

**Format**: CSV, SQL

**Size**: ~60GB

**Data Includes**:
- Demographics
- Vital signs (~1 data point/hour)
- Laboratory test results
- Procedures and medications
- ICD-9-CM diagnoses
- Clinical notes (deidentified)
- Imaging reports
- Mortality data

**Use Cases**:
- Clinical decision support training
- Predictive modeling
- Natural language processing on clinical notes
- ICU outcome prediction

**Download**:
1. Complete CITI training: https://about.citiprogram.org/
2. Register at PhysioNet: https://physionet.org/
3. Download: https://physionet.org/content/mimiciii/1.4/

**Link**: https://physionet.org/content/mimiciii/1.4/

---

### 2. MIMIC-IV

**Description**: Updated version with EHR data from 2008-2019.

**Statistics**:
- **Patients**: 73,000+ patients
- **Admissions**: 315,000+ admissions
- **Time Period**: 2008-2019

**Format**: CSV, SQL

**Size**: ~100GB

**Improvements over MIMIC-III**:
- ICD-10-CM diagnoses (in addition to ICD-9-CM)
- More recent data
- Enhanced data quality
- Additional clinical measurements

**Download**:
Same process as MIMIC-III via PhysioNet

**Link**: https://physionet.org/content/mimiciv/2.0/

---

### 3. Data.gov Health Datasets

**Description**: US government health data portal with disease surveillance and statistics.

**Statistics**:
- **Datasets**: 1,000+ health-related datasets
- **Sources**: CDC, NIH, CMS, FDA

**Format**: Various (CSV, JSON, XML)

**Size**: Varies

**Link**: https://catalog.data.gov/dataset?tags=disease

---

### 4. WHO Global Health Observatory (GHO)

**Description**: WHO's collection of health statistics for 194 member states.

**Statistics**:
- **Countries**: 194 member states
- **Indicators**: 1,000+ health indicators

**Topics**:
- Child health
- HIV/AIDS, Tuberculosis
- Immunization coverage
- Mental health
- Nutrition and food safety
- Disease outbreaks

**Format**: CSV, JSON, XML

**Link**: https://www.who.int/data/gho

---

## Genomic & Phenotype Datasets

### 1. 1000 Genomes Project

**Description**: One of the largest public genome repositories.

**Statistics**:
- **Individuals**: 2,500+ individuals
- **Populations**: 26 populations
- **Variants**: 84.7 million variants

**Format**: VCF, BAM

**Size**: ~200TB (full dataset)

**Access**: AWS Public Dataset

**Link**: https://www.internationalgenome.org/

---

### 2. OpenNeuro

**Description**: Free platform for neuroimaging data.

**Statistics**:
- **Datasets**: 563 medical datasets
- **Participants**: 19,187 participants

**Data Types**:
- MRI, MEG, EEG
- iEEG, ECoG
- ASL, PET

**Format**: BIDS (Brain Imaging Data Structure)

**Link**: https://openneuro.org/

---

### 3. OASIS (Open Access Series of Imaging Studies)

**Description**: Neuroimaging datasets for research.

**Statistics**:
- **Subjects**: 1,098 subjects
- **MR Sessions**: 2,168 sessions
- **PET Sessions**: 1,608 sessions

**Format**: DICOM, NIfTI

**Link**: https://www.oasis-brains.org/

---

## Imaging Datasets

### 1. The Cancer Imaging Archive (TCIA)

**Description**: Large archive of medical images of cancer.

**Statistics**:
- **Collections**: 200+ imaging collections
- **Images**: Millions of images

**Modalities**: CT, MRI, PET, X-ray

**Link**: https://www.cancerimagingarchive.net/

---

### 2. NIH Chest X-ray Dataset

**Description**: 100,000+ chest X-rays with disease labels.

**Statistics**:
- **Images**: 112,120 X-ray images
- **Patients**: 30,805 patients
- **Diseases**: 14 disease labels

**Format**: PNG images with CSV labels

**Size**: ~45GB

**Link**: https://nihcc.app.box.com/v/ChestXray-NIHCC

---

## Download Instructions

### Automated Download Scripts

We provide automated download scripts in `scripts/download_datasets/`:

```bash
# Download all ontologies (HPO, ICD-10)
python scripts/download_datasets/download_ontologies.py

# Download disease-symptom datasets
python scripts/download_datasets/download_disease_data.py

# Download and setup NIH Clinical Tables API
python scripts/download_datasets/setup_api_access.py
```

### Manual Downloads

For datasets requiring registration (MIMIC, SNOMED CT, UMLS):

1. **MIMIC-III/IV**:
   - Complete CITI training
   - Register at PhysioNet
   - Sign data use agreement
   - Download via wget or AWS

2. **SNOMED CT**:
   - Register at NLM UMLS
   - Agree to license terms
   - Download US Edition or International Edition

3. **UMLS**:
   - Create UTS account
   - Accept license agreement
   - Download Metathesaurus files

---

## GitHub Size Considerations

### GitHub Limits

- **File size warning**: 50MB
- **File size hard limit**: 100MB
- **Repository size soft limit**: 1GB
- **Repository size warning**: 5GB

### Our Strategy

Given GitHub's size limitations, we implement the following approach:

#### 1. Reference, Don't Store

**DON'T COMMIT**:
- Large raw datasets (MIMIC, UMLS, genomic data)
- Binary image files (X-rays, MRI scans)
- Full SNOMED CT distributions

**DO COMMIT**:
- Download scripts
- Data processing utilities
- Sample/subset data for testing
- Documentation and schemas

#### 2. Dataset Organization

```
datasets/
├── ontologies/          # Small ontology files (<50MB)
│   ├── hpo/
│   │   ├── hp.obo
│   │   └── phenotype.hpoa
│   ├── icd10/
│   │   └── icd10cm_codes_2024.txt
│   └── README.md
├── samples/             # Small sample datasets
│   ├── disease_symptoms_sample.csv
│   └── README.md
└── .gitignore          # Exclude large files
```

#### 3. .gitignore Configuration

Add to `.gitignore`:
```
# Large datasets
datasets/mimic/
datasets/umls/
datasets/snomed/
datasets/genomic/
datasets/imaging/

# Downloaded archives
*.tar.gz
*.zip
*.7z

# Large ontology downloads
datasets/ontologies/snomed_ct/
datasets/ontologies/umls/

# Temporary processing files
datasets/temp/
datasets/processed/large_*
```

#### 4. External Storage Options

For large datasets:

**Option 1: Cloud Storage**
- AWS S3
- Google Cloud Storage
- Azure Blob Storage

**Option 2: Git LFS (Large File Storage)**
```bash
# Track large files with Git LFS
git lfs track "datasets/ontologies/*.owl"
git lfs track "datasets/samples/*.csv"
```

**Option 3: External Data Repositories**
- Zenodo
- Figshare
- Dataverse

#### 5. Download Scripts

All large datasets have corresponding download scripts:

```bash
# Example: Download HPO (safe for GitHub, ~50MB)
python scripts/download_datasets/download_hpo.py

# Example: Download MIMIC-III (external, ~60GB)
python scripts/download_datasets/download_mimic.py --output /external/storage
```

#### 6. Size Estimates

**Safe to commit** (<50MB):
- HPO ontology files: ~50MB
- ICD-10-CM codes: ~10MB
- Sample disease-symptom datasets: ~5MB
- NIH Clinical Tables cache: ~10MB
- Processing scripts and utilities: ~1MB

**Commit with caution** (50-100MB):
- Medium-sized ontology subsets
- Compressed data samples
- Pre-processed embeddings (small collections)

**Never commit** (>100MB):
- MIMIC-III/IV full datasets
- UMLS Metathesaurus
- SNOMED CT full distribution
- Genomic sequence data
- Medical imaging datasets

---

## Integration with Doctor-Ai

### Recommended Datasets for Immediate Integration

1. **HPO** (High Priority)
   - Already mentioned in README
   - Perfect for rare disease detection
   - Manageable size (~50MB)
   - Download script: `scripts/download_datasets/download_hpo.py`

2. **NIH Clinical Tables API** (High Priority)
   - Excellent for ICD code mapping
   - API-based (no storage needed)
   - Integration script: `scripts/integrations/nih_clinical_tables.py`

3. **EndlessMedical JSON** (Medium Priority)
   - Good symptom-disease mappings
   - Moderate size (~50MB)
   - Download script: `scripts/download_datasets/download_endlessmedical.py`

4. **ICD-10-CM** (High Priority)
   - Standard disease classification
   - Small size (~10MB)
   - Already partially integrated via SNOMED mapping

5. **Kaggle Disease-Symptom** (Medium Priority)
   - Training and validation data
   - Very small (~2MB)
   - Good for ML model training

### Datasets Requiring External Storage

1. **MIMIC-III/IV**
   - Too large for GitHub
   - Requires PhysioNet credentials
   - Store in external database or cloud storage
   - Process and extract only necessary features

2. **UMLS**
   - ~10GB full installation
   - Extract relevant subsets
   - Cache API queries instead

3. **SNOMED CT**
   - Large full distribution
   - Use NLM API when possible
   - Store only necessary mappings

---

## Next Steps

1. **Execute Download Scripts**
   ```bash
   # Download priority datasets
   python scripts/download_datasets/download_all_priority.py
   ```

2. **Verify Dataset Integrity**
   ```bash
   python scripts/download_datasets/verify_datasets.py
   ```

3. **Process and Index**
   ```bash
   # Index datasets in Qdrant
   python scripts/process_datasets/index_hpo.py
   python scripts/process_datasets/index_disease_symptoms.py
   ```

4. **Update Vector Store**
   ```bash
   # Refresh medical conditions collection
   python scripts/seed_data.py --use-new-datasets
   ```

---

## Contributing

When adding new datasets:

1. Check size before committing
2. Add to appropriate category in this document
3. Create download script if >10MB
4. Update `.gitignore` if necessary
5. Document integration steps
6. Add to `scripts/download_datasets/download_all_priority.py`

---

## References

- MIMIC-III: Johnson et al. (2016) Scientific Data
- MIMIC-IV: Johnson et al. (2022) Scientific Data
- HPO: Köhler et al. (2021) Nucleic Acids Research
- SNOMED CT: SNOMED International
- ICD-10: WHO Classification
- UMLS: NLM/NIH

---

## License Information

Each dataset has its own license:

- **HPO**: Free for use
- **ICD-10-CM**: Public domain (US)
- **MIMIC**: PhysioNet Credentialed Health Data License
- **SNOMED CT**: SNOMED CT Affiliate License (free for NLM license holders)
- **UMLS**: UMLS Metathesaurus License
- **Kaggle Datasets**: Vary by dataset (check individual licenses)

Always review and comply with dataset licenses before use.

---

**Last Updated**: 2025-11-14
**Maintainer**: Doctor-Ai Project Team

# Medical Dataset Processing Scripts

This directory contains scripts to filter, process, and index medical datasets for the Doctor-Ai diagnostic system.

## Overview

The processing pipeline filters large medical datasets to extract only data relevant to symptom-based diagnosis, reducing dataset sizes by 60-80% while maintaining diagnostic value.

## Quick Start

### Process All Datasets (Recommended)

Run the complete pipeline:

```bash
# Full pipeline (filter, merge, index)
python scripts/process_datasets/process_all.py

# Skip Qdrant indexing
python scripts/process_datasets/process_all.py --skip-index
```

### Individual Steps

```bash
# 1. Filter HPO dataset
python scripts/process_datasets/filter_hpo.py

# 2. Filter ICD-10 dataset
python scripts/process_datasets/filter_icd10.py

# 3. Merge all datasets
python scripts/process_datasets/merge_all_datasets.py

# 4. Index in Qdrant
python scripts/process_datasets/index_in_qdrant.py
```

## Prerequisites

1. **Download datasets first**:
   ```bash
   python scripts/download_datasets/download_all_priority.py
   ```

2. **For Qdrant indexing**:
   - Qdrant must be running: `docker-compose up -d`
   - Doctor-Ai services must be available

## Scripts

### 1. `filter_hpo.py` - Filter HPO Dataset

Filters the Human Phenotype Ontology dataset for diagnostic relevance.

**What it does**:
- Extracts diseases with clear symptom presentations
- Focuses on observable phenotypes (pain, fever, fatigue, etc.)
- Filters out ultra-rare genetic conditions
- Creates disease-symptom mappings
- Reduces dataset by ~70% while keeping diagnostic value

**Input**: `datasets/ontologies/hpo/phenotype.hpoa`

**Output** (`datasets/processed/hpo/`):
- `hpo_disease_symptoms_filtered.csv` - Disease-symptom mappings
- `hpo_embeddings_data.json` - Ready for vector embeddings
- `hpo_filter_stats.json` - Statistics

**Usage**:
```bash
# Default processing
python filter_hpo.py

# Custom minimum phenotypes per disease
python filter_hpo.py --min-phenotypes 5

# Custom output directory
python filter_hpo.py --output /custom/path
```

**Options**:
- `--input, -i`: Input directory (default: `datasets/ontologies/hpo`)
- `--output, -o`: Output directory (default: `datasets/processed/hpo`)
- `--min-phenotypes, -m`: Minimum phenotypes per disease (default: 3)

**Example Output**:
```
Total diseases: 8,000+
Filtered diseases: 2,500
Reduction: 68.8%
```

---

### 2. `filter_icd10.py` - Filter ICD-10 Dataset

Filters ICD-10-CM codes for common diseases relevant to primary care.

**What it does**:
- Focuses on disease chapters (A-N, excluding injury/admin codes)
- Prioritizes symptom-relevant conditions
- Excludes administrative, injury, and cause codes
- Creates hierarchical disease categories
- Reduces dataset by ~75%

**Input**: `datasets/ontologies/icd10/icd10cm_codes_2024.csv`

**Output** (`datasets/processed/icd10/`):
- `icd10_codes_filtered.csv` - Filtered disease codes
- `icd10_categories.csv` - Disease categories
- `icd10_embeddings_data.json` - Ready for vector embeddings
- `icd10_filter_stats.json` - Statistics

**Usage**:
```bash
# Default processing
python filter_icd10.py

# Custom directories
python filter_icd10.py --input /path/to/icd10 --output /path/to/output
```

**Options**:
- `--input, -i`: Input directory (default: `datasets/ontologies/icd10`)
- `--output, -o`: Output directory (default: `datasets/processed/icd10`)

**Filtering Logic**:
- **Include**: Chapters A-N (infectious diseases through genitourinary)
- **Exclude**: O-Z (pregnancy, injuries, causes, administrative)
- **Keywords**: pain, syndrome, infection, inflammation, disease, etc.

**Example Output**:
```
Total codes: 70,000+
Filtered codes: 18,000
Disease categories: 1,200
Reduction: 74.3%
```

---

### 3. `merge_all_datasets.py` - Merge All Datasets

Merges filtered datasets into a unified, deduplicated collection.

**What it does**:
- Combines HPO, ICD-10, and sample datasets
- Deduplicates diseases by name
- Merges symptoms from multiple sources
- Creates unified schema for embeddings
- Prioritizes data quality (HPO > ICD-10 > Sample)

**Input**:
- `datasets/processed/hpo/hpo_embeddings_data.json`
- `datasets/processed/icd10/icd10_embeddings_data.json`
- `datasets/samples/disease_symptom_sample.csv`

**Output** (`datasets/processed/unified/`):
- `unified_diseases.json` - Unified dataset for embeddings
- `unified_diseases.csv` - Human-readable format
- `merge_stats.json` - Statistics

**Usage**:
```bash
# Default merging
python merge_all_datasets.py

# Custom directories
python merge_all_datasets.py --input /path/to/processed --output /path/to/output
```

**Options**:
- `--input, -i`: Processed datasets directory (default: `datasets/processed`)
- `--output, -o`: Output directory (default: `datasets/processed/unified`)

**Deduplication Logic**:
1. Match diseases by name (case-insensitive)
2. Merge symptoms from all sources
3. Combine ICD-10 codes
4. Keep highest-quality source data

**Example Output**:
```
HPO diseases: 2,500
ICD-10 diseases: 1,200
Sample diseases: 10
---
Total unique diseases: 3,100
Merged: 600
New diseases added: 2,500
```

---

### 4. `index_in_qdrant.py` - Index in Qdrant

Generates vector embeddings and indexes diseases in Qdrant.

**What it does**:
- Loads unified disease dataset
- Generates BioBERT/PubMedBERT embeddings
- Indexes in Qdrant vector database
- Batch processing for efficiency

**Input**: `datasets/processed/unified/unified_diseases.json`

**Output**: Qdrant vector database (no files)

**Usage**:
```bash
# Default indexing
python index_in_qdrant.py

# Custom collection name
python index_in_qdrant.py --collection my_diseases

# Custom input file
python index_in_qdrant.py --input /path/to/unified_diseases.json
```

**Options**:
- `--input, -i`: Input JSON file (default: `datasets/processed/unified/unified_diseases.json`)
- `--collection, -c`: Qdrant collection name (default: `medical_conditions`)

**Requirements**:
- Qdrant running: `docker-compose up -d`
- Doctor-Ai services available
- PubMedBERT model downloaded

**Processing Time**:
- ~3-5 seconds per 100 diseases
- 3,000 diseases: ~2-3 minutes

---

### 5. `process_all.py` - Master Pipeline Script

Runs the complete processing pipeline in correct order.

**What it does**:
- Executes all filtering scripts sequentially
- Merges filtered datasets
- Indexes in Qdrant (optional)
- Provides progress updates and error handling

**Usage**:
```bash
# Full pipeline
python process_all.py

# Skip Qdrant indexing
python process_all.py --skip-index

# Skip confirmation prompt
python process_all.py --yes
```

**Options**:
- `--skip-index`: Skip Qdrant indexing step
- `--yes, -y`: Skip confirmation prompt

**Pipeline Steps**:
1. Filter HPO dataset (~1-2 minutes)
2. Filter ICD-10 dataset (~30 seconds)
3. Merge all datasets (~10 seconds)
4. Index in Qdrant (~2-3 minutes for 3K diseases)

**Total Time**: ~5-10 minutes

---

## Output Directory Structure

```
datasets/processed/
├── hpo/
│   ├── hpo_disease_symptoms_filtered.csv
│   ├── hpo_embeddings_data.json
│   └── hpo_filter_stats.json
├── icd10/
│   ├── icd10_codes_filtered.csv
│   ├── icd10_categories.csv
│   ├── icd10_embeddings_data.json
│   └── icd10_filter_stats.json
└── unified/
    ├── unified_diseases.json        # Main file for Qdrant
    ├── unified_diseases.csv
    └── merge_stats.json
```

## Data Filtering Strategy

### What We Keep

✅ **Diseases**:
- Common conditions (diabetes, hypertension, pneumonia)
- Diseases with clear symptom presentations
- Conditions relevant to primary care
- Rare diseases with distinctive phenotypes

✅ **Symptoms**:
- Observable symptoms (pain, fever, rash)
- Reportable symptoms (fatigue, nausea, dizziness)
- Physical signs (edema, jaundice, tremor)

### What We Filter Out

❌ **Excluded**:
- Ultra-rare genetic conditions (<1/100,000)
- Administrative codes (Z codes)
- Injury/trauma codes (S/T codes)
- Cause codes (V/W/X/Y codes)
- Procedural codes
- Anatomical variations without symptoms

### Filtering Criteria

**HPO Dataset**:
- Minimum 3 phenotypes per disease
- Focus on symptom-related phenotypes
- Exclude purely genetic/molecular phenotypes

**ICD-10 Dataset**:
- Chapters A-N only (disease chapters)
- Keyword-based relevance filtering
- Category-level aggregation

## Dataset Statistics

### Before Filtering

| Dataset | Records | Size |
|---------|---------|------|
| HPO | 8,000 diseases | ~50MB |
| ICD-10 | 70,000 codes | ~50MB |
| **Total** | **78,000** | **~100MB** |

### After Filtering

| Dataset | Records | Size | Reduction |
|---------|---------|------|-----------|
| HPO | ~2,500 diseases | ~15MB | 68.8% |
| ICD-10 | ~1,200 categories | ~12MB | 74.3% |
| Unified | ~3,100 unique | ~25MB | 75% |
| **Total** | **~3,100** | **~25MB** | **75%** |

## Performance

### Processing Speed

| Step | Records | Time | Speed |
|------|---------|------|-------|
| Filter HPO | 8,000 → 2,500 | ~1-2 min | 70/sec |
| Filter ICD-10 | 70,000 → 18,000 | ~30 sec | 2,300/sec |
| Merge | 3,100 | ~10 sec | 310/sec |
| Index (Qdrant) | 3,100 | ~2-3 min | 20/sec |

### Resource Usage

- **Memory**: ~500MB peak
- **Disk I/O**: Minimal (sequential reads/writes)
- **CPU**: Mostly single-threaded (embeddings are CPU-bound)

## Troubleshooting

### Missing Input Files

**Error**: `File not found: datasets/ontologies/hpo/phenotype.hpoa`

**Solution**:
```bash
python scripts/download_datasets/download_all_priority.py
```

### Qdrant Connection Error

**Error**: `Could not connect to Qdrant`

**Solution**:
```bash
# Start Qdrant
docker-compose up -d

# Verify Qdrant is running
curl http://localhost:6333/health
```

### Import Errors

**Error**: `Could not import project modules`

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from src.services.embedding import EmbeddingService"
```

### Memory Issues

**Error**: Out of memory during embedding generation

**Solution**:
- Process in smaller batches
- Reduce embedding batch size in code
- Use a machine with more RAM

## Customization

### Adjusting Filters

**HPO Filter** (`filter_hpo.py`):
```python
# Add custom symptom keywords
SYMPTOM_KEYWORDS = [
    "pain", "fever", "fatigue",
    # Add your keywords here
]

# Adjust minimum phenotypes
python filter_hpo.py --min-phenotypes 5
```

**ICD-10 Filter** (`filter_icd10.py`):
```python
# Include additional chapters
PRIORITY_CHAPTERS = {
    'A': 'Infectious diseases',
    # Add your chapters here
}

# Adjust keyword filtering
SYMPTOM_KEYWORDS = ["pain", "syndrome", ...]
```

### Custom Merging Logic

Edit `merge_all_datasets.py`:
```python
# Change source priority
source_priority = {'HPO': 1, 'ICD10': 2, 'CUSTOM': 3}

# Add custom deduplication logic
def deduplicate_custom(disease1, disease2):
    # Your logic here
    pass
```

## Integration with Doctor-Ai

After processing, the unified dataset is ready for use:

1. **Vector Search**: Indexed in Qdrant for similarity search
2. **API**: Available via `/api/v1/analyze` endpoint
3. **Diagnostic Engine**: Powers symptom-to-disease matching

### Testing Integration

```bash
# Test API with processed data
python scripts/test_api.py

# Query specific disease
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"symptoms": [{"description": "fever and cough"}]}'
```

## Best Practices

1. **Always run download scripts first**:
   ```bash
   python scripts/download_datasets/download_all_priority.py
   ```

2. **Use the master script for consistency**:
   ```bash
   python scripts/process_datasets/process_all.py
   ```

3. **Review statistics after filtering**:
   - Check `*_filter_stats.json` files
   - Ensure reduction isn't too aggressive

4. **Backup processed data**:
   ```bash
   cp -r datasets/processed datasets/processed_backup
   ```

5. **Reprocess when datasets update**:
   - HPO releases bi-monthly
   - ICD-10 releases annually

## Contributing

When adding new filters or processors:

1. Follow existing script structure
2. Add comprehensive documentation
3. Include error handling
4. Generate statistics JSON
5. Update this README
6. Add to `process_all.py` pipeline

## References

- HPO Ontology: https://hpo.jax.org/
- ICD-10-CM: https://www.cdc.gov/nchs/icd/icd-10-cm.htm
- Doctor-Ai Architecture: ../README.md

---

**Last Updated**: 2025-11-14
**Maintainer**: Doctor-Ai Project Team

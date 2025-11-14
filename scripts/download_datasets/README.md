# Medical Dataset Download Scripts

This directory contains scripts to download medical datasets for the Doctor-Ai project.

## Quick Start

Download all priority datasets:

```bash
cd scripts/download_datasets
python download_all_priority.py
```

## Available Scripts

### 1. `download_all_priority.py` - Master Download Script

Downloads all priority datasets in one go.

**Usage:**
```bash
# Download all datasets
python download_all_priority.py

# Download to custom directory
python download_all_priority.py --output /path/to/datasets

# Download specific datasets only
python download_all_priority.py --datasets hpo icd10

# Include optional files
python download_all_priority.py --include-optional-hpo
```

**Options:**
- `--output, -o`: Custom output directory
- `--datasets, -d`: Specific datasets to download (hpo, icd10, disease_symptoms)
- `--include-optional-hpo`: Download optional HPO gene mapping files
- `--use-kaggle, -k`: Use Kaggle API for disease datasets
- `--quiet, -q`: Suppress verbose output

---

### 2. `download_hpo.py` - Human Phenotype Ontology

Downloads HPO ontology files for rare disease detection.

**Dataset Info:**
- **Size**: ~50MB
- **Files**: hp.obo, phenotype.hpoa, gene mappings
- **Use**: Rare disease phenotype matching

**Usage:**
```bash
# Download required files only
python download_hpo.py

# Include optional gene mapping files
python download_hpo.py --include-optional

# Custom output directory
python download_hpo.py --output /custom/path
```

**Downloaded Files:**
- `hp.obo` - Main ontology file (Required)
- `phenotype.hpoa` - Disease-phenotype annotations (Required)
- `genes_to_phenotype.txt` - Gene mappings (Optional)
- `phenotype_to_genes.txt` - Reverse mappings (Optional)

---

### 3. `download_icd10.py` - ICD-10-CM Codes

Downloads ICD-10-CM disease classification codes.

**Dataset Info:**
- **Size**: ~50MB
- **Codes**: 70,000+ diagnostic codes
- **Use**: Disease classification, billing codes

**Usage:**
```bash
# Download and create CSV
python download_icd10.py

# Download without CSV export
python download_icd10.py --no-csv

# Custom output directory
python download_icd10.py --output /custom/path
```

**Downloaded Files:**
- `icd10cm-codes-2024.zip` - Raw codes archive
- `icd10cm-tabular-2024.xml` - Tabular list
- `icd10cm_codes_2024.csv` - Processed CSV (auto-generated)

---

### 4. `download_disease_symptoms.py` - Disease-Symptom Datasets

Downloads disease-symptom mapping datasets.

**Dataset Info:**
- **Size**: ~5MB
- **Use**: Training data, symptom-disease mappings

**Usage:**
```bash
# Create sample dataset
python download_disease_symptoms.py

# Use Kaggle API (requires setup)
python download_disease_symptoms.py --use-kaggle

# Skip sample creation
python download_disease_symptoms.py --no-sample
```

**Kaggle Setup:**
1. Install Kaggle API: `pip install kaggle`
2. Get API credentials: https://github.com/Kaggle/kaggle-api#api-credentials
3. Place credentials in `~/.kaggle/kaggle.json`

---

## Output Structure

Downloaded datasets are organized as follows:

```
datasets/
├── ontologies/
│   ├── hpo/
│   │   ├── hp.obo
│   │   ├── phenotype.hpoa
│   │   └── ...
│   └── icd10/
│       ├── icd10cm_codes_2024.csv
│       └── ...
└── samples/
    ├── disease_symptom_sample.csv
    └── ...
```

## GitHub Size Considerations

All priority datasets are selected to be within GitHub limits:

- **HPO**: ~50MB ✅
- **ICD-10-CM**: ~50MB ✅
- **Sample datasets**: ~5MB ✅

**Total**: ~105MB (safe for GitHub)

### Large Datasets (Not Committed)

The following datasets are **too large** for GitHub and should be stored externally:

- **MIMIC-III**: ~60GB ❌
- **MIMIC-IV**: ~100GB ❌
- **UMLS**: ~10GB ❌
- **SNOMED CT**: ~2GB ❌

These are referenced in `MEDICAL_DATASETS.md` with download instructions but are not automatically downloaded.

## Verification

After downloading, verify the datasets:

```bash
# Verify all datasets
python scripts/download_datasets/verify_datasets.py

# Verify specific dataset
python scripts/download_datasets/verify_datasets.py --dataset hpo
```

## Next Steps

After downloading datasets:

1. **Verify downloads:**
   ```bash
   ls -lh datasets/ontologies/hpo/
   ls -lh datasets/ontologies/icd10/
   ls -lh datasets/samples/
   ```

2. **Process and index:**
   ```bash
   python scripts/process_datasets/index_hpo.py
   python scripts/process_datasets/index_icd10.py
   ```

3. **Update vector store:**
   ```bash
   python scripts/seed_data.py --use-new-datasets
   ```

4. **Test integration:**
   ```bash
   python scripts/test_api.py
   ```

## Troubleshooting

### Download Fails

**Issue**: Network errors or timeouts

**Solution**:
- Check internet connection
- Retry the download
- Use a VPN if geo-restricted

### Kaggle API Not Working

**Issue**: `kaggle` module not found or authentication error

**Solution**:
1. Install Kaggle: `pip install kaggle`
2. Get API token from https://www.kaggle.com/account
3. Place `kaggle.json` in `~/.kaggle/`
4. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`

### File Corruption

**Issue**: Downloaded file appears corrupted

**Solution**:
- Delete the file
- Re-download
- Check disk space

### Permission Errors

**Issue**: Cannot write to output directory

**Solution**:
```bash
# Create directory with proper permissions
mkdir -p datasets
chmod 755 datasets

# Or use custom output directory
python download_all_priority.py --output ~/my_datasets
```

## API Rate Limits

Some datasets use APIs that may have rate limits:

- **NIH Clinical Tables**: No known limits
- **Kaggle API**: Rate limited per user
- **HPO GitHub**: No limits (direct file download)

If you encounter rate limits, wait a few minutes and retry.

## Contributing

When adding new dataset downloaders:

1. Follow the existing script structure
2. Include progress indicators
3. Verify downloads after completion
4. Update this README
5. Check file sizes (<50MB preferred)
6. Add to `download_all_priority.py` if priority dataset

## License

Each dataset has its own license. See `MEDICAL_DATASETS.md` for details.

---

**Last Updated**: 2025-11-14
**Maintainer**: Doctor-Ai Project Team

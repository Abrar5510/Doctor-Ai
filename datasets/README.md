# Medical Datasets Directory

This directory contains medical datasets used by the Doctor-Ai diagnostic support system.

## Directory Structure

```
datasets/
├── ontologies/          # Medical ontologies and taxonomies
│   ├── hpo/            # Human Phenotype Ontology (~50MB)
│   │   ├── hp.obo
│   │   ├── phenotype.hpoa
│   │   └── ...
│   ├── icd10/          # ICD-10-CM disease codes (~50MB)
│   │   ├── icd10cm_codes_2024.csv
│   │   └── ...
│   ├── snomed_ct/      # SNOMED CT (NOT in Git - too large)
│   └── umls/           # UMLS (NOT in Git - too large)
├── samples/            # Sample datasets for testing
│   ├── disease_symptom_sample.csv
│   └── ...
├── mimic/              # MIMIC-III/IV data (NOT in Git - too large)
├── imaging/            # Medical images (NOT in Git - too large)
└── temp/               # Temporary processing files (NOT in Git)
```

## What's Included in Git

✅ **Small datasets** (<50MB):
- HPO ontology files (~50MB)
- ICD-10-CM codes (~50MB)
- Sample disease-symptom datasets (~5MB)
- Metadata and schema files
- Processing scripts

Total committed data: ~105MB

## What's NOT in Git

❌ **Large datasets** (>50MB):
- MIMIC-III/IV clinical databases (~60-100GB)
- UMLS Metathesaurus (~10GB)
- SNOMED CT full distribution (~2GB)
- Medical imaging datasets (varies, GB-TB)
- Genomic sequence data (~200TB)
- Downloaded ZIP archives
- Processed binary files (.bin, .pkl, .h5)

These are excluded via `.gitignore` to respect GitHub's size limits.

## Downloading Datasets

### Quick Start

Download all priority datasets (safe for GitHub):

```bash
python scripts/download_datasets/download_all_priority.py
```

### Individual Downloads

```bash
# Human Phenotype Ontology
python scripts/download_datasets/download_hpo.py

# ICD-10-CM codes
python scripts/download_datasets/download_icd10.py

# Disease-symptom datasets
python scripts/download_datasets/download_disease_symptoms.py
```

See `scripts/download_datasets/README.md` for detailed instructions.

## Dataset Information

### 1. Human Phenotype Ontology (HPO)

**Location**: `datasets/ontologies/hpo/`

**Size**: ~50MB

**Description**: Standardized vocabulary of phenotypic abnormalities in human disease. Essential for rare disease detection.

**Files**:
- `hp.obo` - Main ontology
- `phenotype.hpoa` - Disease annotations
- `genes_to_phenotype.txt` - Gene mappings (optional)

**Use Cases**:
- Rare disease phenotype matching
- Symptom-to-disease mapping
- Clinical decision support

**License**: Free for use

**Update Frequency**: Bi-monthly

---

### 2. ICD-10-CM Codes

**Location**: `datasets/ontologies/icd10/`

**Size**: ~50MB

**Description**: International Classification of Diseases, 10th Revision, Clinical Modification. Standard for disease classification.

**Files**:
- `icd10cm_codes_2024.csv` - All diagnostic codes
- `icd10cm-tabular-2024.xml` - Structured format

**Statistics**:
- 70,000+ diagnostic codes
- 21 chapters
- Annual updates

**Use Cases**:
- Disease classification
- Diagnosis coding
- EHR integration
- Insurance/billing

**License**: Public domain (US)

**Update Frequency**: Annual

---

### 3. Disease-Symptom Datasets

**Location**: `datasets/samples/`

**Size**: ~5MB

**Description**: Curated datasets mapping diseases to their common symptoms.

**Files**:
- `disease_symptom_sample.csv` - Sample dataset

**Use Cases**:
- ML model training
- Validation testing
- Symptom checker development

**License**: Varies by source

---

## Large Datasets (External Storage)

The following datasets are documented in `MEDICAL_DATASETS.md` but must be stored externally:

### MIMIC-III/IV

**Size**: 60-100GB

**Download**: Requires PhysioNet credentials

**Storage**: External database or cloud storage

**Documentation**: See `MEDICAL_DATASETS.md`

### UMLS Metathesaurus

**Size**: ~10GB

**Download**: Requires NLM registration

**Storage**: External directory

**Documentation**: See `MEDICAL_DATASETS.md`

### SNOMED CT

**Size**: ~2GB

**Download**: Requires NLM license

**Storage**: External directory

**Documentation**: See `MEDICAL_DATASETS.md`

## Processing Datasets

After downloading, process datasets for use with Doctor-Ai:

```bash
# Index HPO in Qdrant
python scripts/process_datasets/index_hpo.py

# Index ICD-10 codes
python scripts/process_datasets/index_icd10.py

# Update vector store
python scripts/seed_data.py --use-new-datasets
```

## Data Format Standards

### CSV Files

- **Encoding**: UTF-8
- **Delimiter**: Comma (,)
- **Headers**: First row
- **Quotes**: Double quotes for fields with commas

### JSON Files

- **Encoding**: UTF-8
- **Format**: Pretty-printed (2-space indent)
- **Structure**: Documented in schema files

### Ontology Files

- **OBO Format**: Human-readable ontology format
- **OWL Format**: Web Ontology Language (XML/RDF)
- **TSV Format**: Tab-separated values for annotations

## Updating Datasets

### Manual Updates

```bash
# Re-download latest versions
python scripts/download_datasets/download_all_priority.py

# Verify integrity
python scripts/download_datasets/verify_datasets.py

# Re-index if needed
python scripts/process_datasets/index_all.py
```

### Automated Updates

Consider setting up a cron job for regular updates:

```bash
# Update HPO monthly (releases bi-monthly)
0 0 1 */2 * cd /path/to/Doctor-Ai && python scripts/download_datasets/download_hpo.py

# Update ICD-10 annually (October releases)
0 0 1 10 * cd /path/to/Doctor-Ai && python scripts/download_datasets/download_icd10.py
```

## Data Privacy & Security

### HIPAA Compliance

- ✅ All datasets are de-identified
- ✅ No patient-specific information in repository
- ✅ MIMIC data requires credentialing
- ✅ Audit trail for all data access

### Best Practices

1. **Never commit**:
   - Patient data
   - PHI (Protected Health Information)
   - Credentials or API keys

2. **Always**:
   - Use de-identified datasets
   - Follow data use agreements
   - Respect dataset licenses
   - Implement access controls

3. **Before committing**:
   - Check file sizes (<50MB)
   - Verify no PHI included
   - Confirm license allows sharing

## Troubleshooting

### Dataset Not Downloading

**Issue**: Download script fails

**Solution**:
1. Check internet connection
2. Verify disk space
3. Check source URL is still valid
4. Review error messages for specifics

### File Corrupted

**Issue**: Downloaded file appears corrupted

**Solution**:
```bash
# Delete and re-download
rm datasets/ontologies/hpo/hp.obo
python scripts/download_datasets/download_hpo.py
```

### Out of Disk Space

**Issue**: Not enough space for large datasets

**Solution**:
- Move large datasets to external storage
- Use symbolic links:
  ```bash
  ln -s /external/storage/mimic datasets/mimic
  ```
- Clean up temporary files:
  ```bash
  rm -rf datasets/temp/*
  ```

### Git Won't Commit

**Issue**: File too large for GitHub

**Solution**:
```bash
# Check file size
ls -lh datasets/ontologies/icd10/*

# If >50MB, add to .gitignore
echo "datasets/ontologies/icd10/large_file.csv" >> .gitignore
```

## Contributing New Datasets

When adding new datasets:

1. **Check size**: Must be <50MB for Git
2. **Document**: Add to `MEDICAL_DATASETS.md`
3. **Create downloader**: Add script to `scripts/download_datasets/`
4. **Update README**: Document structure and usage
5. **Add to .gitignore**: If large dataset
6. **Test**: Verify download and processing

## References

- Full dataset catalog: `../MEDICAL_DATASETS.md`
- Download scripts: `../scripts/download_datasets/`
- Processing scripts: `../scripts/process_datasets/`
- Project README: `../README.md`

## License

Each dataset has its own license. See `../MEDICAL_DATASETS.md` for specific license information.

## Support

- Issues: https://github.com/Abrar5510/Doctor-Ai/issues
- Documentation: `../MEDICAL_DATASETS.md`
- Download help: `../scripts/download_datasets/README.md`

---

**Last Updated**: 2025-11-14
**Maintainer**: Doctor-Ai Project Team

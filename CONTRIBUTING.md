# Contributing to Doctor-AI

Thank you for your interest in contributing to Doctor-AI! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Submitting Changes](#submitting-changes)
- [Review Process](#review-process)
- [Medical Data Guidelines](#medical-data-guidelines)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community and patients
- Show empathy towards other contributors
- Maintain patient privacy and data security

### Unacceptable Behavior

- Harassment or discriminatory language
- Publishing others' private information
- Trolling or insulting comments
- Professional misconduct

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Python 3.9+** installed
2. **Git** configured with your GitHub account
3. **Docker and Docker Compose** (for local testing)
4. Basic understanding of:
   - Medical terminology (helpful but not required)
   - Machine learning and NLP
   - Vector databases
   - FastAPI

### Setting Up Your Development Environment

1. **Fork the repository**

   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/Doctor-Ai.git
   cd Doctor-Ai
   ```

2. **Add upstream remote**

   ```bash
   git remote add upstream https://github.com/Abrar5510/Doctor-Ai.git
   ```

3. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If exists
   ```

5. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

6. **Start services**

   ```bash
   docker-compose up -d
   ```

7. **Seed the database**

   ```bash
   python scripts/seed_data.py
   ```

8. **Run tests**

   ```bash
   pytest tests/ -v
   ```

## Development Workflow

### Branching Strategy

We use a feature branch workflow:

1. **Main branch (`main`)**: Production-ready code
2. **Feature branches**: `feature/description` or `feat/description`
3. **Bug fix branches**: `fix/description` or `bugfix/description`
4. **Documentation branches**: `docs/description`
5. **Hotfix branches**: `hotfix/description`

### Creating a Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a new branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Write clear, focused commits**

   ```bash
   git add file1.py file2.py
   git commit -m "Add symptom clustering algorithm"
   ```

2. **Commit message format**

   ```
   <type>: <subject>

   <body>

   <footer>
   ```

   **Types:**
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation changes
   - `style`: Code formatting (no logic changes)
   - `refactor`: Code restructuring
   - `test`: Adding or updating tests
   - `chore`: Maintenance tasks

   **Example:**
   ```
   feat: Add rare disease detection algorithm

   Implements HPO-based rare disease pattern matching using
   phenotype similarity scores and inheritance patterns.

   Closes #123
   ```

3. **Keep commits atomic**
   - One logical change per commit
   - Commits should be self-contained
   - Easy to review and revert if needed

### Syncing with Upstream

```bash
# Fetch upstream changes
git fetch upstream

# Rebase your branch
git rebase upstream/main

# Push to your fork (force push if rebased)
git push origin feature/your-feature-name --force-with-lease
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Imports**: Group and sort (stdlib, third-party, local)
- **Docstrings**: Google style

### Code Formatting

**Use Black for formatting:**

```bash
black src/ tests/ scripts/
```

**Use isort for imports:**

```bash
isort src/ tests/ scripts/
```

**Use flake8 for linting:**

```bash
flake8 src/ tests/ scripts/
```

**Use mypy for type checking:**

```bash
mypy src/
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case()`
- **Constants**: `UPPER_CASE`
- **Private**: `_leading_underscore`

### Docstring Format

Use Google-style docstrings:

```python
def analyze_symptoms(symptoms: List[Symptom], patient_age: int) -> DiagnosisResult:
    """Analyze patient symptoms to generate differential diagnosis.

    Args:
        symptoms: List of patient symptoms with metadata
        patient_age: Patient age in years

    Returns:
        DiagnosisResult containing differential diagnoses, confidence scores,
        and recommended next steps

    Raises:
        ValueError: If symptoms list is empty
        VectorStoreError: If vector database is unavailable

    Example:
        >>> symptoms = [Symptom(description="fever", severity="high")]
        >>> result = analyze_symptoms(symptoms, patient_age=35)
        >>> print(result.primary_diagnosis.condition_name)
        'Influenza'
    """
    if not symptoms:
        raise ValueError("Symptoms list cannot be empty")

    # Implementation...
```

### Type Hints

Always use type hints:

```python
from typing import List, Optional, Dict, Any

def process_data(
    input_data: List[Dict[str, Any]],
    max_results: int = 10,
    filter_func: Optional[Callable] = None
) -> List[Result]:
    """Process input data and return results."""
    pass
```

## Testing Guidelines

### Test Structure

```
tests/
├── __init__.py
├── test_api/
│   ├── test_routes.py
│   └── test_middleware.py
├── test_services/
│   ├── test_embedding.py
│   ├── test_diagnostic.py
│   └── test_vector_store.py
└── test_models/
    └── test_schemas.py
```

### Writing Tests

**Use pytest:**

```python
import pytest
from src.services.diagnostic import DiagnosticService

class TestDiagnosticService:
    """Test diagnostic service functionality."""

    @pytest.fixture
    def diagnostic_service(self):
        """Create diagnostic service instance."""
        return DiagnosticService()

    def test_analyze_common_symptoms(self, diagnostic_service):
        """Test analysis of common symptom presentation."""
        symptoms = [
            {"description": "fever", "severity": "high"},
            {"description": "cough", "severity": "moderate"}
        ]

        result = diagnostic_service.analyze(symptoms)

        assert result is not None
        assert len(result.differential_diagnoses) > 0
        assert result.overall_confidence > 0

    def test_empty_symptoms_raises_error(self, diagnostic_service):
        """Test that empty symptoms list raises ValueError."""
        with pytest.raises(ValueError, match="Symptoms list cannot be empty"):
            diagnostic_service.analyze([])
```

### Test Coverage

- Aim for **80%+ code coverage**
- Focus on critical paths and edge cases
- Test both success and failure scenarios

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### Medical Data Testing

When testing with medical data:

1. **Use synthetic data** - Never use real patient data
2. **Create fixtures** - Reusable test data
3. **Test edge cases** - Rare diseases, unusual presentations
4. **Validate outputs** - Ensure medical accuracy

## Documentation Guidelines

### Code Documentation

1. **Docstrings**: All public modules, classes, and functions
2. **Comments**: Explain "why", not "what"
3. **Type hints**: Always include for function signatures
4. **Examples**: Provide usage examples in docstrings

### Project Documentation

When updating documentation:

1. **Keep it current** - Update docs with code changes
2. **Be clear and concise** - Use simple language
3. **Add examples** - Show, don't just tell
4. **Test instructions** - Verify setup steps work

### Documentation Files

- `README.md`: Project overview and quick start
- `CONTRIBUTING.md`: This file
- `ARCHITECTURE.md`: System architecture
- `API.md`: API documentation
- Inline comments and docstrings

## Submitting Changes

### Before Submitting

**Checklist:**

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No sensitive data in commits
- [ ] Commits are atomic and well-described
- [ ] Branch is up-to-date with main

### Pull Request Process

1. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**

   - Go to GitHub and create a PR from your fork
   - Use the PR template
   - Link related issues

3. **PR Title Format**

   ```
   feat: Add rare disease detection
   fix: Correct confidence score calculation
   docs: Update API documentation
   ```

4. **PR Description**

   Include:
   - What changes were made
   - Why these changes are needed
   - How to test the changes
   - Screenshots/examples (if applicable)
   - Related issue numbers

5. **Request Review**

   - Tag relevant reviewers
   - Respond to feedback promptly
   - Make requested changes

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement

## Testing

How to test these changes:

1. Step 1
2. Step 2
3. Expected result

## Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Related Issues

Closes #123
```

## Review Process

### Code Review

All submissions require review before merging:

1. **Automated checks** must pass
   - Tests
   - Linting
   - Type checking
   - Coverage

2. **Manual review** by maintainers
   - Code quality
   - Medical accuracy
   - Security considerations
   - Performance impact

3. **Changes requested**
   - Address feedback
   - Push updates
   - Request re-review

4. **Approval and merge**
   - Squash and merge (preferred)
   - Rebase and merge (for clean history)

### Review Guidelines

When reviewing code:

- **Be respectful and constructive**
- **Explain reasoning** for requested changes
- **Suggest alternatives** when appropriate
- **Approve quickly** when code is good
- **Focus on substance** over style (if formatted correctly)

## Medical Data Guidelines

### HIPAA Compliance

When working with medical data:

1. **Never commit PHI** (Protected Health Information)
2. **Use synthetic data** for testing
3. **Anonymize all examples** in documentation
4. **Follow data use agreements** for datasets
5. **Implement audit logging** for data access

### Medical Accuracy

1. **Cite sources** for medical information
2. **Verify accuracy** with medical literature
3. **Consult experts** when uncertain
4. **Document limitations** clearly
5. **Add warnings** for unvalidated features

### Data Sources

Acceptable data sources:

- ✅ Public medical ontologies (SNOMED CT, ICD-10)
- ✅ De-identified research datasets (MIMIC-III/IV)
- ✅ Synthetic patient data
- ✅ Published medical literature

Not acceptable:

- ❌ Real patient records
- ❌ Proprietary medical databases (without license)
- ❌ Unverified crowdsourced data

## Questions or Issues?

- **Technical questions**: Open a GitHub issue
- **Security concerns**: See SECURITY.md
- **Feature requests**: Open a GitHub discussion
- **Bug reports**: Use issue template

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

**Thank you for contributing to better healthcare through technology!**

# Fix Qdrant installation and setup issues

## Summary

This PR resolves issues with Qdrant not working via Docker or pip install by providing comprehensive setup documentation, automated installation scripts, and troubleshooting guides.

## Changes Made

### 1. New Documentation
- **QDRANT_SETUP.md**: Comprehensive guide covering 5 different installation methods
  - Docker with Docker Compose (recommended)
  - Docker standalone
  - Binary installation (no Docker required)
  - Qdrant Cloud (production-ready, free tier available)
  - Embedded mode (testing/development only)
- Detailed troubleshooting section for common errors

### 2. Automated Setup Script
- **scripts/setup_qdrant.sh**: One-command installation script
  - Automatically installs qdrant-client Python package
  - Detects Docker availability
  - Offers to start Qdrant container
  - Provides alternative installation options if Docker is unavailable
  - Tests connection after setup

### 3. Connection Test Script
- **scripts/test_qdrant_connection.py**: Verification utility
  - Tests connection to Qdrant server
  - Verifies collection creation permissions
  - Checks for medical_conditions collection
  - Provides actionable error messages and troubleshooting steps

### 4. Updated README
- Added Qdrant setup instructions with multiple options
- Linked to comprehensive QDRANT_SETUP.md guide
- Added connection test step to Quick Start section
- Improved user experience for new developers

## Problem Solved

Users were experiencing issues with:
- Missing qdrant-client Python package
- Docker not available/installed
- Connection errors to Qdrant
- Unclear setup instructions

## Solution Approach

This PR provides multiple pathways to success:
1. **Quick automated setup** for users with Docker
2. **Binary installation guide** for users without Docker
3. **Cloud option** for production deployments
4. **Comprehensive troubleshooting** for common issues

## Testing

- ✅ qdrant-client package installs successfully
- ✅ Setup script executes without errors
- ✅ Test script correctly detects connection issues
- ✅ Documentation is clear and comprehensive
- ✅ All scripts are executable

## Files Changed

- `QDRANT_SETUP.md` (new) - 312 lines
- `scripts/setup_qdrant.sh` (new) - 139 lines
- `scripts/test_qdrant_connection.py` (new) - 192 lines
- `README.md` (modified) - Updated setup instructions

## How to Test

1. Clone the branch
2. Run the setup script:
   ```bash
   chmod +x scripts/setup_qdrant.sh
   ./scripts/setup_qdrant.sh
   ```
3. Test the connection:
   ```bash
   python scripts/test_qdrant_connection.py
   ```

## Impact

- ✅ Improves developer onboarding experience
- ✅ Reduces setup friction for new contributors
- ✅ Provides clear troubleshooting guidance
- ✅ Supports multiple deployment scenarios
- ✅ No breaking changes to existing code

## Related Issues

Resolves the issue where Qdrant wasn't working via Docker or pip install.

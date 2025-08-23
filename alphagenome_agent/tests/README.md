# AlphaGenome Agent Tests

## Running Tests

### Option 1: Direct Execution
Run tests directly from the project root:

```bash
# Run all tests
python run_tests.py

# Run specific test suite
python run_tests.py alphagenome  # AlphaGenome client tests
python run_tests.py cbioportal   # CBioPortal client tests
```

### Option 2: Using Python Module
Run tests as Python modules:

```bash
# From the alphagenome_agent directory
python -m src.clients.tests.test_alphagenome_client
python -m src.clients.tests.test_cbioportal_client
```

### Option 3: Using pytest (if installed)
```bash
# Install pytest first
pip install pytest

# Run all tests
pytest

# Run specific test file
pytest src/clients/tests/test_alphagenome_client.py -v
```

## Environment Variables

### Required for AlphaGenome tests:
- `ALPHAGENOME_API_KEY`: Your AlphaGenome API key

Example:
```bash
export ALPHAGENOME_API_KEY="your-api-key-here"
python run_tests.py alphagenome
```

## Import Structure

The tests use absolute imports from the `src` package root. The import structure is:

```python
from src.clients.alphagenome_client import AlphaGenomeClient
from src.clients.cbioportal_client import CBioPortalClient
from src.core.schemas import Variant, GenomicInterval, Assembly
```

## Troubleshooting

### Import Errors
If you encounter import errors, ensure you're running tests from the correct directory:
- Always run from the `alphagenome_agent` directory
- The tests automatically add the correct path to `sys.path`

### API Key Issues
If AlphaGenome tests fail with API key errors:
1. Ensure the `ALPHAGENOME_API_KEY` environment variable is set
2. Verify the API key is valid
3. Check network connectivity to the AlphaGenome API
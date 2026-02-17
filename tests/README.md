# Tests for biokb_wfo

## Running Tests

### Prerequisites

1. Install the package with test dependencies:
```bash
# Using pip
pip install -e ".[tests]"

# Or using uv (if available)
uv pip install -e ".[tests]"
```

2. Alternatively, install dependencies directly:
```bash
pip install pytest pytest-cov pytest-sugar
```

### Run All Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=biokb_wfo --cov-report=html

# Run with verbose output
pytest tests/ -v

# Run with pretty output (requires pytest-sugar)
pytest tests/
```

### Run Specific Test Files

```bash
# Test database manager only
pytest tests/test_db_manager.py -v

# Test CLI commands only
pytest tests/test_cli.py -v

# Test API endpoints only
pytest tests/test_api.py -v
```

### Run Specific Test Classes or Methods

```bash
# Run a specific test class
pytest tests/test_db_manager.py::TestDbManager -v

# Run a specific test method
pytest tests/test_db_manager.py::TestDbManager::test_import_data_from_test_file -v
```

## Test Features

### Using Simplified Test Data

The tests use the simplified test data file instead of downloading the full dataset:

```python
@pytest.fixture
def db_manager(test_engine, test_data_folder):
    """Create DbManager with test data folder."""
    manager = DbManager(engine=test_engine)
    manager._set_data_folder(test_data_folder)  # Point to test data
    return manager
```

### Temporary Databases

All tests use temporary SQLite databases that are automatically created and cleaned up:

```python
@pytest.fixture
def test_engine():
    """Create a temporary SQLite database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        engine = create_engine(f"sqlite:///{db_path}")
        yield engine
```

### Mock External Dependencies

Tests mock external dependencies like Neo4j connections to avoid requiring actual infrastructure:

```python
with patch("biokb_wfo.cli.Neo4jImporter") as mock_importer:
    mock_instance = MagicMock()
    mock_importer.return_value = mock_instance
    # Test logic here
```

## Test Coverage

The test suite covers:

- Database import functionality
- Data validation and relationships
- CLI command execution
- API endpoint functionality
- Authentication and authorization
- Error handling
- Pagination and filtering
- CORS configuration
- Session management

## Continuous Integration

To run tests in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -e ".[tests]"
    pytest tests/ --cov=biokb_wfo --cov-report=xml
```

## Troubleshooting

### Import Errors
If you get import errors, make sure the package is installed in editable mode:
```bash
pip install -e .
```

### Missing Dependencies
Install test dependencies:
```bash
pip install pytest pytest-cov
```

### Test Data Issues
The test data file must be present at `tests/data/plant_list_2025-12.json.zip`. This file contains the simplified JSON with 10 entries representing a full taxonomic hierarchy.

### Resource Warnings
If you see ResourceWarning messages about unclosed database connections, these are automatically filtered in pytest configuration. The test fixtures properly dispose of database engines to prevent resource leaks. To see all warnings, run:
```bash
pytest tests/ -W default
```

## Adding New Tests

When adding new tests:

1. Use the existing fixtures for test data and databases
2. Follow the existing test structure and naming conventions
3. Mock external dependencies (Neo4j, file downloads, etc.)
4. Ensure tests are isolated and don't depend on external state
5. Add docstrings explaining what each test validates

## Notes

- Tests do not download real WFO data
- Tests do not require Neo4j installation
- Tests use simplified data for speed and clarity
- All tests are isolated and can run in parallel
- Test data is preserved and not deleted during test runs

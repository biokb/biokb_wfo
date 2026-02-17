# biokb_wfo


## Howro tox

```bash
Run tests on Python 3.13 with coverage
tox -e py313

# Run tests on all Python versions
tox

# Run linting (black, isort, flake8)
tox -e lint

# Run type checking
tox -e mypy

# Build docs
tox -e docs

# Generate coverage report from all test runs
tox -e coverage
```
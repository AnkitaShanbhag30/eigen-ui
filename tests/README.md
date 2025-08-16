# Test Structure for eigen-ui

This directory contains organized tests for the eigen-ui project, categorized by scope and complexity.

## Test Categories

### 🧪 Unit Tests (`tests/unit/`)
- **Purpose**: Test individual functions and classes in isolation
- **Speed**: Fast (seconds)
- **Scope**: Single module/function
- **When to run**: During development, before commits, CI/CD

**Files:**
- `test_brand.py` - BrandIdentity model tests
- `test_html_tokens.py` - Design token generation tests
- `test_util.py` - Utility function tests

### 🔗 Integration Tests (`tests/integration/`)
- **Purpose**: Test module interactions and data flow
- **Speed**: Medium (seconds to minutes)
- **Scope**: Multiple modules working together
- **When to run**: Before major changes, integration testing

**Files:**
- `test_templates.py` - Template rendering and design token integration

### 🚀 Comprehensive Tests (`tests/comprehensive/`)
- **Purpose**: Test complete workflows end-to-end
- **Speed**: Slow (minutes)
- **Scope**: Full application workflows
- **When to run**: Before releases, major refactoring, deployment

**Files:**
- `test_end_to_end.py` - Complete content generation to export workflows

## Running Tests

### Quick Test Runner
```bash
# Run unit tests (fastest)
python run_tests.py unit

# Run integration tests (medium)
python run_tests.py integration

# Run comprehensive tests (slowest)
python run_tests.py comprehensive

# Run all tests
python run_tests.py all

# Run with verbose output
python run_tests.py unit --verbose

# Run a specific test file
python run_tests.py all --file tests/unit/test_brand.py
```

### Direct pytest
```bash
# Run all tests
pytest

# Run specific category
pytest tests/unit/
pytest tests/integration/
pytest tests/comprehensive/

# Run with markers
pytest -m unit
pytest -m integration
pytest -m comprehensive

# Run specific test
pytest tests/unit/test_brand.py::test_brand_identity_model
```

## Test Guidelines

### When to Run Which Tests

#### 🚀 **Small Changes** (run unit tests)
- Bug fixes
- Simple refactoring
- Adding new functions
- Documentation updates

```bash
python run_tests.py unit
```

#### 🔗 **Medium Changes** (run unit + integration tests)
- New features
- API changes
- Database schema changes
- Template modifications

```bash
python run_tests.py integration
```

#### 🎯 **Big Changes** (run all tests)
- Major refactoring
- Architecture changes
- New modules
- Before releases

```bash
python run_tests.py all
```

### Test Development

#### Adding New Tests
1. **Unit tests**: Add to appropriate `tests/unit/test_*.py` file
2. **Integration tests**: Add to appropriate `tests/integration/test_*.py` file
3. **Comprehensive tests**: Add to appropriate `tests/comprehensive/test_*.py` file

#### Test Naming Convention
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

#### Test Structure
```python
def test_function_name():
    """Test description"""
    # Arrange
    # Act
    # Assert
```

### Mocking and Dependencies
- **Unit tests**: Mock external dependencies
- **Integration tests**: Mock only external APIs
- **Comprehensive tests**: Use real dependencies when possible

### Performance Considerations
- **Unit tests**: Should run in < 1 second
- **Integration tests**: Should run in < 10 seconds
- **Comprehensive tests**: May take several minutes

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: python run_tests.py unit
      - name: Run integration tests
        run: python run_tests.py integration
      - name: Run comprehensive tests
        run: python run_tests.py comprehensive
```

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure `sys.path` includes the `app` directory
2. **Missing dependencies**: Install required packages with `pip install -r requirements.txt`
3. **Test failures**: Check that the app code hasn't changed significantly

### Debug Mode
```bash
# Run with detailed output
python run_tests.py unit --verbose

# Run specific failing test
pytest tests/unit/test_brand.py::test_brand_identity_model -v -s
```

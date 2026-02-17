# Contributing to django-role-based-masking

Thank you for your interest in contributing to django-role-based-masking! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/gaikwadakshay79/django-role-based-masking.git
   cd django-role-based-masking
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Running Tests

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=django_role_based_masking --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_strategies.py
```

Run specific test:

```bash
pytest tests/test_strategies.py::TestFullStrategy::test_full_masks_entire_string
```

### Code Quality

Check code with ruff:

```bash
ruff check .
```

Format code:

```bash
ruff format .
```

Auto-fix issues:

```bash
ruff check --fix .
```

### Using Make Commands

We provide a Makefile for common tasks:

```bash
make help          # Show available commands
make install-dev   # Install with dev dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linter
make format        # Format code
make clean         # Remove build artifacts
make build         # Build distribution packages
```

## Contribution Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write descriptive docstrings for all public functions and classes
- Keep line length to 100 characters
- Use double quotes for strings

### Testing

- Write tests for all new features
- Maintain or improve code coverage (target: 95%+)
- Ensure all tests pass before submitting PR
- Include both positive and negative test cases
- Test edge cases and error conditions

### Commit Messages

Use clear and descriptive commit messages:

```
Add support for custom masking strategies

- Implement strategy registration system
- Add documentation for custom strategies
- Include tests for custom strategy usage
```

### Pull Request Process

1. **Fork the repository** and create a new branch

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Write or update tests** for your changes

4. **Run tests and linting**

   ```bash
   make test
   make lint
   ```

5. **Update documentation** if needed
   - Update README.md for user-facing changes
   - Update docstrings for API changes
   - Add examples if introducing new features

6. **Commit your changes**

   ```bash
   git add .
   git commit -m "Description of changes"
   ```

7. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure CI checks pass

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

- Python version
- Django version
- DRF version
- Package version
- Minimal code to reproduce the issue
- Expected vs actual behavior
- Full error traceback if applicable

### Feature Requests

When requesting features:

- Describe the use case
- Explain why it would be useful
- Provide examples of how it would work
- Consider backward compatibility

### Documentation

Documentation improvements are always welcome:

- Fix typos or clarify existing docs
- Add examples for common use cases
- Improve API documentation
- Translate documentation

### Code Contributions

Areas where contributions are especially welcome:

- Additional masking strategies
- Performance improvements
- Better error messages
- Extended test coverage
- Bug fixes

## Project Structure

```
django-role-based-masking/
├── django_role_based_masking/  # Main package
│   ├── __init__.py
│   ├── exceptions.py           # Custom exceptions
│   ├── settings.py             # Configuration
│   ├── strategies.py           # Masking strategies
│   ├── utils.py                # Utility functions
│   ├── masking.py              # Core masking engine
│   └── serializers.py          # DRF integration
├── tests/                      # Test suite
│   ├── conftest.py             # Pytest fixtures
│   ├── settings.py             # Django test settings
│   ├── testapp/                # Test Django app
│   ├── test_strategies.py
│   ├── test_utils.py
│   ├── test_masking.py
│   └── test_serializers.py
├── docs/                       # Documentation
│   └── examples/               # Usage examples
├── .github/                    # GitHub configuration
│   └── workflows/              # CI/CD workflows
├── pyproject.toml              # Package configuration
├── README.md                   # Main documentation
└── CHANGELOG.md                # Version history
```

## Adding New Masking Strategies

To add a new built-in masking strategy:

1. **Add the strategy function** in `django_role_based_masking/strategies.py`:

   ```python
   def my_strategy(value, param=default, mask_char=None):
       """
       Description of what the strategy does.

       Args:
           value: The value to mask
           param: Strategy parameter
           mask_char: Masking character

       Returns:
           Masked value
       """
       # Implementation
       pass
   ```

2. **Register the strategy** in the `STRATEGIES` dict:

   ```python
   STRATEGIES = {
       # ... existing strategies
       "my_strategy": my_strategy,
   }
   ```

3. **Add tests** in `tests/test_strategies.py`:

   ```python
   class TestMyStrategy:
       def test_basic_functionality(self):
           result = my_strategy("test")
           assert result == "expected"
   ```

4. **Update documentation** in README.md

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `__init__.py`
2. Update `CHANGELOG.md` with changes
3. Run full test suite: `make test`
4. Build package: `make build`
5. Create git tag: `git tag v0.x.x`
6. Push tag: `git push origin v0.x.x`
7. Publish to PyPI: `make publish`

## Questions?

If you have questions about contributing:

- Open an issue on GitHub
- Check existing issues and discussions
- Review the documentation

## Code of Conduct

Be respectful and inclusive. We welcome contributions from everyone.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

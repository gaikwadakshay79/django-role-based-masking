# Publishing to PyPI Guide

This guide walks you through publishing `django-role-based-masking` to PyPI.

## Prerequisites

1. **PyPI Account**
   - Create account at https://pypi.org/account/register/
   - Verify your email address

2. **PyPI API Token** (Recommended)
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token with scope for this project
   - Save the token securely (you'll only see it once)

3. **Install Required Tools**
   ```bash
   pip install build twine
   ```

## Step-by-Step Publishing Process

### Step 1: Verify Everything is Ready

```bash
# Run all tests
pytest

# Check code quality
ruff check .

# Format code
ruff format .

# Verify package metadata
python -m build --help
```

### Step 2: Update Version (if needed)

Update version in two places:

1. **pyproject.toml**

   ```toml
   [project]
   version = "0.1.0"  # Update this
   ```

2. **django_role_based_masking/**init**.py**
   ```python
   __version__ = "0.1.0"  # Update this
   ```

### Step 3: Update CHANGELOG.md

Add release notes:

```markdown
## [0.1.0] - 2026-XX-XX

### Added

- Initial release
- Role-based field masking
- Built-in strategies
- etc.
```

### Step 4: Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info

# Or use make
make clean
```

### Step 5: Build the Package

```bash
# Build source distribution and wheel
python -m build

# Or use make
make build
```

This creates:

- `dist/django_role_based_masking-0.1.0.tar.gz` (source distribution)
- `dist/django_role_based_masking-0.1.0-py3-none-any.whl` (wheel)

### Step 6: Check the Build

```bash
# Verify the package
twine check dist/*
```

Expected output:

```
Checking dist/django_role_based_masking-0.1.0.tar.gz: PASSED
Checking dist/django_role_based_masking-0.1.0-py3-none-any.whl: PASSED
```

### Step 7: Test on TestPyPI (Recommended)

TestPyPI is a separate instance for testing:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

You'll be prompted for credentials:

- Username: `__token__`
- Password: Your TestPyPI API token (starts with `pypi-`)

Or configure `.pypirc`:

```ini
[testpypi]
username = __token__
password = pypi-your-testpypi-token-here
```

Test installation:

```bash
pip install --index-url https://test.pypi.org/simple/ django-role-based-masking
```

### Step 8: Publish to PyPI

**⚠️ Warning: This cannot be undone! Once published, you cannot delete or re-upload the same version.**

```bash
# Upload to PyPI
twine upload dist/*
```

You'll be prompted for credentials:

- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

### Step 9: Verify Publication

1. Check PyPI page: https://pypi.org/project/django-role-based-masking/
2. Test installation:
   ```bash
   pip install django-role-based-masking
   ```

### Step 10: Create Git Tag

```bash
# Create and push tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

## Using Make Commands

We provide convenient make commands:

```bash
# Clean, build, and publish in one command
make publish

# Or step by step
make clean
make build
twine upload dist/*
```

## Configuration Files

### Option 1: Using .pypirc (Recommended)

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-production-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-token-here
```

Set permissions:

```bash
chmod 600 ~/.pypirc
```

### Option 2: Using Environment Variables

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here
twine upload dist/*
```

### Option 3: Using Keyring

```bash
pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__
```

## Automated Publishing with GitHub Actions

The repository includes a GitHub Actions workflow. To enable:

1. Add PyPI API token to GitHub Secrets:
   - Go to repository Settings → Secrets → Actions
   - Add secret: `PYPI_API_TOKEN`

2. Create a release on GitHub:
   - The workflow will automatically publish to PyPI

## Troubleshooting

### Error: "File already exists"

- You cannot re-upload the same version
- Increment version number and rebuild

### Error: "Invalid credentials"

- Verify your API token is correct
- Ensure username is `__token__` (not your PyPI username)
- Check token hasn't expired

### Error: "Package name already taken"

- Choose a different package name
- Update `name` in `pyproject.toml`

### Error: "README rendering failed"

- Check README.md syntax
- Verify all links work
- Test with: `python -m readme_renderer README.md`

## Quick Reference Commands

```bash
# Complete publishing workflow
make clean          # Clean old builds
make test           # Run tests
make lint           # Check code quality
make build          # Build package
twine check dist/*  # Verify build
twine upload --repository testpypi dist/*  # Test on TestPyPI
twine upload dist/* # Publish to PyPI

# Or all at once
make clean && make test && make build && twine upload dist/*
```

## Post-Publication Checklist

- [ ] Verify package appears on PyPI
- [ ] Test installation: `pip install django-role-based-masking`
- [ ] Test import: `python -c "import django_role_based_masking"`
- [ ] Create GitHub release with changelog
- [ ] Update documentation if needed
- [ ] Announce release (Twitter, Reddit, etc.)

## Version Numbering

Follow Semantic Versioning (semver.org):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.1.1): Bug fixes, backward compatible

## Support

- PyPI Help: https://pypi.org/help/
- Twine Docs: https://twine.readthedocs.io/
- Packaging Guide: https://packaging.python.org/

---

**Ready to publish?** Follow the steps above and your package will be live on PyPI! 🚀

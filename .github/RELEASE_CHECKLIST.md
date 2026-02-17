# Release Checklist

Use this checklist when preparing a new release.

## Pre-Release

- [ ] All tests passing locally (`pytest`)
- [ ] Code formatted (`ruff format .`)
- [ ] Linting passes (`ruff check .`)
- [ ] Documentation updated
- [ ] Examples tested

## Version Update

- [ ] Update version in `pyproject.toml`
- [ ] Update version in `django_role_based_masking/__init__.py`
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Commit changes: `git commit -m "Bump version to X.Y.Z"`

## Testing on TestPyPI (Recommended)

Before publishing to production PyPI, test on TestPyPI:

- [ ] Push to main: `git push origin main`
- [ ] Create test tag: `git tag -a vX.Y.Z-test -m "Test release X.Y.Z"`
- [ ] Push test tag: `git push origin vX.Y.Z-test`
- [ ] Wait for GitHub Actions to publish to TestPyPI
- [ ] Verify on TestPyPI: https://test.pypi.org/project/django-role-based-masking/
- [ ] Test installation: `pip install --index-url https://test.pypi.org/simple/ django-role-based-masking==X.Y.Z`
- [ ] Delete test tag if successful: `git tag -d vX.Y.Z-test && git push origin :refs/tags/vX.Y.Z-test`

## Production Release

- [ ] Create production tag: `git tag -a vX.Y.Z -m "Release version X.Y.Z"`
- [ ] Push production tag: `git push origin vX.Y.Z`
- [ ] Wait for GitHub Actions to complete
- [ ] Verify package on PyPI: https://pypi.org/project/django-role-based-masking/

## Post-Release

- [ ] Test installation: `pip install django-role-based-masking==X.Y.Z`
- [ ] Create GitHub Release with changelog
- [ ] Announce on social media (optional)
- [ ] Update documentation site (if applicable)

## Version Numbering Guide

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.1.1): Bug fixes, backward compatible

## Tag Naming Convention

The workflow automatically detects where to publish based on tag name:

- **Production tags**: `v0.1.0`, `v1.2.3` → Publishes to **PyPI**
- **Test tags**: `v0.1.0-test`, `v1.2.3-test` → Publishes to **TestPyPI**

Any tag containing the word "test" will be published to TestPyPI.

## Quick Commands

### Testing on TestPyPI

```bash
# Update version and commit
git add pyproject.toml django_role_based_masking/__init__.py CHANGELOG.md
git commit -m "Bump version to X.Y.Z"
git push origin main

# Create and push TEST tag
git tag -a vX.Y.Z-test -m "Test release X.Y.Z"
git push origin vX.Y.Z-test

# Monitor workflow
# Visit: https://github.com/YOUR_USERNAME/django-role-based-masking/actions

# After verification, delete test tag
git tag -d vX.Y.Z-test
git push origin :refs/tags/vX.Y.Z-test
```

### Production Release

```bash
# Create and push PRODUCTION tag
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin vX.Y.Z

# Monitor workflow
# Visit: https://github.com/YOUR_USERNAME/django-role-based-masking/actions
```

## GitHub Secrets Required

Make sure these secrets are configured in your repository:

- `PYPI_API_TOKEN` - For production / test PyPI releases

## Rollback (if needed)

If something goes wrong:

```bash
# Delete local tag
git tag -d vX.Y.Z

# Delete remote tag
git push origin :refs/tags/vX.Y.Z

# Note: You cannot delete a PyPI release, only yank it
# To yank: Go to PyPI project page → Manage → Yank release
```

# Release Guide

This guide explains how to create releases for this project.

## Creating a Release

### Option 1: Create Release via GitHub UI (Recommended)

1. **Go to Releases page**:
   - Navigate to: **Releases** → **Draft a new release**

2. **Choose a tag**:
   - Click **Choose a tag** → **Create new tag**
   - Tag version: `v0.1.0` (follow semantic versioning)
   - Target: `main` branch

3. **Release title**:
   - Use format: `Release 0.1.0` or just `0.1.0`

4. **Release notes**:
   - Copy relevant section from `CHANGELOG.md`
   - Or use the template in `.github/RELEASE_TEMPLATE.md`
   - Format using Markdown

5. **Attach files** (optional):
   - Source code (zip)
   - Source code (tar.gz)

6. **Publish**:
   - Click **Publish release**

### Option 2: Create Release via Git Tags

1. **Update CHANGELOG.md**:
   - Move items from `[Unreleased]` to new version section
   - Update version number and date

2. **Commit changes**:
   ```bash
   git add CHANGELOG.md
   git commit -m "Prepare release 0.1.0"
   git push
   ```

3. **Create and push tag**:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

4. **GitHub Actions will automatically create the release**

### Option 3: Create Release via GitHub Actions

1. **Go to Actions** → **Release** workflow
2. Click **Run workflow**
3. Enter version number (e.g., `0.1.0`)
4. Click **Run workflow**

## Semantic Versioning

Follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Examples:
- `0.1.0` - Initial release
- `0.1.1` - Bug fix
- `0.2.0` - New features
- `1.0.0` - First stable release

## Release Checklist

Before creating a release:

- [ ] Update `CHANGELOG.md` with new version
- [ ] Update version in code (if applicable)
- [ ] Run tests: `pytest`
- [ ] Check CI status: All checks passing
- [ ] Review security scans: No critical issues
- [ ] Update documentation if needed
- [ ] Create release notes from CHANGELOG
- [ ] Tag the release
- [ ] Publish release

## Release Notes Template

```markdown
## 🎉 Release Notes

### What's New
- Feature 1
- Feature 2

### 🐛 Bug Fixes
- Fixed issue X
- Fixed issue Y

### 🔧 Changes
- Improvement 1
- Improvement 2

### 📚 Documentation
- Updated README
- Added examples

### ⚠️ Breaking Changes
- None (or list breaking changes)

### 📦 Installation

```bash
# Update dependencies
pip install -r requirements.txt --upgrade
```

### 🔗 Links
- [Full Changelog](CHANGELOG.md)
- [Documentation](README.md)
```

## First Release (v0.1.0)

For the first release, you can use:

**Tag**: `v0.1.0`
**Title**: `Release 0.1.0 - Initial Release`
**Notes**: Copy from `CHANGELOG.md` section `[0.1.0]`

## Automated Releases

The `.github/workflows/release.yml` workflow automatically:
- Creates releases when you push a tag (e.g., `v0.1.0`)
- Generates release notes from `CHANGELOG.md`
- Can be triggered manually via workflow_dispatch

## Best Practices

1. **Always update CHANGELOG.md** before releasing
2. **Use semantic versioning** consistently
3. **Write clear release notes** describing changes
4. **Test before releasing** (run full test suite)
5. **Tag releases** for easy reference
6. **Keep releases focused** (one major change per release)


# Release Process

This project uses automated releases via GitHub Actions with PyPI Trusted Publishing.

## Prerequisites

### First-time Setup: Configure PyPI Trusted Publishing

Trusted Publishing allows GitHub Actions to publish packages to PyPI without using API tokens. This is more secure and easier to manage.

#### Step 1: Ensure PyPI Project Exists

If this is the first release:
1. Create the project on PyPI first (upload an initial version manually)
2. OR request that a PyPI admin create the project name for you

For existing projects, skip to Step 2.

#### Step 2: Configure Trusted Publishing on PyPI

1. **Log in to PyPI** with an account that has "Owner" or "Maintainer" role for `plone.versioncheck`

2. **Navigate to Publishing Settings:**
   - Go to: https://pypi.org/manage/project/plone.versioncheck/settings/publishing/
   - OR: https://pypi.org/manage/account/publishing/ → Select "plone.versioncheck"

3. **Add a new publisher** (scroll to "Add a new publisher"):
   - **PyPI Project Name:** `plone.versioncheck`
   - **Owner:** `plone`
   - **Repository name:** `plone.versioncheck`
   - **Workflow name:** `release.yaml`
   - **Environment name:** `release-pypi`

4. Click "Add"

#### Step 3: (Optional) Configure Test PyPI

For testing the release process:

1. **Log in to Test PyPI:** https://test.pypi.org/
2. **Navigate to:** https://test.pypi.org/manage/account/publishing/
3. **Add a new pending publisher:**
   - **PyPI Project Name:** `plone.versioncheck`
   - **Owner:** `plone`
   - **Repository name:** `plone.versioncheck`
   - **Workflow name:** `release.yaml`
   - **Environment name:** `release-test-pypi`

**Note:** Test PyPI uses "pending publishers" - the project will be created automatically on first publish.

#### Step 4: Configure GitHub Environments (Optional but Recommended)

For additional security, configure deployment environments in GitHub:

1. Go to: https://github.com/plone/plone.versioncheck/settings/environments
2. Create environment: `release-pypi`
   - Add protection rules (e.g., require review from maintainers)
   - Restrict to `master` branch only
3. Create environment: `release-test-pypi`

#### Verification

To verify the setup:
1. Check that the publisher appears in PyPI's Publishing settings
2. The workflow will fail with a clear error if trusted publishing isn't configured
3. Test with a push to master (will publish to Test PyPI if configured)

#### Troubleshooting Setup

**Error: "Trusted publishing exchange failure"**
- Verify the repository owner, name, and workflow name match exactly
- Check that the environment name matches the workflow

**Error: "Not authorized to publish"**
- Ensure your PyPI account is an owner/maintainer of the project
- For new projects, create the project manually first

**Need Help?**
- PyPI Trusted Publishing docs: https://docs.pypi.org/trusted-publishers/
- GitHub OIDC docs: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect

## Release Steps

### 1. Prepare the Release

```bash
# Ensure you're on master and up to date
git checkout master
git pull

# Update CHANGES.md with release notes
# - Summarize new features, bug fixes, and breaking changes
# - Set the release date

# Update version in pyproject.toml (remove .dev0)
# Change: version = "1.8.3.dev0"
# To:     version = "1.8.3"

# Commit the changes
git add CHANGES.md pyproject.toml
git commit -m "Preparing release 1.8.3"
```

### 2. Create and Push the Tag

```bash
# Create an annotated tag
git tag -a 1.8.3 -m "Release 1.8.3"

# Push commits and tags
git push
git push --tags
```

### 3. Create GitHub Release

1. Go to https://github.com/plone/plone.versioncheck/releases/new
2. Select the tag you just created (e.g., `1.8.3`)
3. Title: `Release 1.8.3`
4. Description: Copy the relevant section from CHANGES.md
5. Click "Publish release"

**This triggers the automated release workflow:**
- Tests run automatically
- Package is built with provenance attestation
- Package is published to PyPI using Trusted Publishing

### 4. Bump Version for Next Development Cycle

```bash
# Update version in pyproject.toml (add .dev0)
# Change: version = "1.8.3"
# To:     version = "1.8.4.dev0"

# Update CHANGES.md with new unreleased section
# Add:
# ## 1.8.4 (unreleased)
#
# ### Breaking changes
#
# - *add item here*
#
# ### New features
#
# - *add item here*
#
# ### Bug fixes
#
# - *add item here*

# Commit the changes
git add CHANGES.md pyproject.toml
git commit -m "Back to development: 1.8.4"
git push
```

## Development Releases

Development releases are automatically published to Test PyPI on every push to master:

- Triggered by: Push to `master` branch
- Published to: https://test.pypi.org/project/plone.versioncheck/
- Install from Test PyPI: `pip install --index-url https://test.pypi.org/simple/ plone.versioncheck`

## Workflow Details

The release workflow (`.github/workflows/release.yaml`) performs these steps:

1. **Run Tests** - Ensures all tests pass before building
2. **Build Package** - Creates wheel and sdist with hatchling
3. **Verify Package** - Uses `build-and-inspect-python-package`
4. **Attest Build** - Generates SLSA provenance attestation
5. **Publish to PyPI** - Uses Trusted Publishing (no API tokens needed)

## Troubleshooting

### Release workflow fails

- Check the GitHub Actions logs for specific errors
- Ensure tests pass locally: `tox`
- Verify the version in `pyproject.toml` is correct

### Package not appearing on PyPI

- Verify PyPI Trusted Publishing is configured correctly
- Check that the GitHub Release was created (not just a tag)
- Review the workflow logs in GitHub Actions

### "Environment protection rules" error

- The `release-pypi` environment may have protection rules
- Contact a repository admin to approve the deployment

## Manual Release (Fallback)

If automated release fails, you can release manually:

```bash
# Build the package
python -m build

# Check the built package
twine check dist/*

# Upload to Test PyPI (optional)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

**Note:** Manual releases won't have build provenance attestation.

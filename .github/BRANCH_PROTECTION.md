# Branch Protection Rules

This document describes the recommended branch protection rules for maximum security and owner-only control.

**⚠️ IMPORTANT**: This configuration ensures only the repository owner can control the repository. See `.github/RULESET_CONFIG.md` for detailed setup instructions.

## Main Branch Protection

### Required Settings

1. **Require a pull request before merging**
   - ✅ Required approvals: **2**
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require review from Code Owners (if CODEOWNERS file exists)

2. **Require status checks to pass before merging**
   - ✅ Require branches to be up to date before merging
   - ✅ Required status checks:
     - `CI / test (3.10)`
     - `CI / test (3.11)`
     - `CI / test (3.12)`
     - `Security Scan / security-scan`
     - `Security Scan / codeql-analysis`
     - `Security Scan / dependency-review` (for PRs)

3. **Require conversation resolution before merging**
   - ✅ All conversations on the pull request must be resolved

4. **Require signed commits**
   - ✅ Require signed commits (optional but recommended)

5. **Require linear history**
   - ✅ Require linear history (prevents merge commits)

6. **Include administrators**
   - ❌ **DO NOT CHECK THIS** - This ensures even administrators must follow rules
   - ✅ **Instead**: Add yourself to bypass list if you need emergency access

7. **Restrict who can push to matching branches**
   - ✅ Only allow specific teams/users to push directly
   - ✅ **Add only**: Your GitHub username (e.g., `riedemannai`)
   - ❌ **Do not add**: Any other users or teams

8. **Allow force pushes**
   - ❌ Do not allow force pushes
   - ❌ Do not allow deletions

9. **Lock branch**
   - ❌ Do not lock branch (unless needed for critical releases)

## Security Rules

### Code Scanning
- Enable CodeQL analysis
- Enable Dependabot alerts
- Enable secret scanning
- Enable dependency review

### Workflow Permissions
- Set workflow permissions to "Read and write permissions" only for pull requests
- Use least privilege principle

### Actions Permissions
- Require approval for all third-party actions
- Pin actions to specific commit SHAs

## How to Configure

1. Go to **Settings** → **Branches**
2. Click **Add rule** or edit existing rule for `main`
3. Configure according to the settings above
4. Save the rule

## Alternative: Using GitHub Rulesets (Recommended)

GitHub Rulesets provide more granular control:

```yaml
# Configure via GitHub API or UI
# Settings → Rules → Rulesets → New ruleset
```

### Ruleset Configuration:
- **Target branches**: `main`, `master`
- **Bypass list**: Only repository administrators
- **Enforcement**: Active
- **Bypass mode**: No bypass allowed

### Rules:
1. **Pull Request**: Required, 2 approvals
2. **Status Check**: All required checks must pass
3. **Conversation Resolution**: Required
4. **Signed Commits**: Required (optional)
5. **Linear History**: Required
6. **Deletion Protection**: Enabled

## Security Best Practices

1. **Never disable branch protection** for the main branch
2. **Use CODEOWNERS file** to require reviews from specific maintainers
3. **Enable branch protection** for all release branches
4. **Regularly review** and update protection rules
5. **Monitor security alerts** and act on them promptly
6. **Use security policies** for vulnerability disclosure


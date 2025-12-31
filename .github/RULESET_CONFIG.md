# Repository Ruleset Configuration

This document provides the configuration for maximum repository control, ensuring only the repository owner can make changes to the main branch.

## GitHub Rulesets (Recommended)

GitHub Rulesets provide the most granular control. Configure via GitHub UI or API.

### Configuration Steps

1. Go to **Settings** → **Rules** → **Rulesets** → **New ruleset**
2. Select **Branch ruleset**
3. Configure as follows:

### Ruleset Settings

**Name**: `Main Branch Protection - Owner Only`
**Target branches**: `main`, `master`
**Enforcement**: `Active`
**Bypass list**: Only add your GitHub username (e.g., `riedemannai`)

### Rules Configuration

#### 1. Pull Request Rules
- ✅ **Required**: Yes
- ✅ **Required approvals**: 2
- ✅ **Dismiss stale reviews**: Yes
- ✅ **Require review from Code Owners**: Yes
- ✅ **Require last push approval**: Yes
- ✅ **Restrict who can dismiss reviews**: Only repository administrators

#### 2. Status Check Rules
- ✅ **Require status checks to pass**: Yes
- ✅ **Require branches to be up to date**: Yes
- ✅ **Required status checks**:
  - `CI / test (3.10)`
  - `CI / test (3.11)`
  - `CI / test (3.12)`
  - `Security Scan / security-scan`
  - `Security Scan / codeql-analysis`
  - `Security Scan / dependency-review`

#### 3. Conversation Resolution Rules
- ✅ **Require conversation resolution**: Yes
- ✅ **Require all comments to be resolved**: Yes

#### 4. Commit Rules
- ✅ **Require signed commits**: Recommended (optional)
- ✅ **Require linear history**: Yes
- ✅ **Require merge queue**: Optional

#### 5. Update Rules
- ✅ **Allow deletions**: No
- ✅ **Allow force pushes**: No
- ✅ **Allow force pushes to matching branches**: No
- ✅ **Block force pushes**: Yes
- ✅ **Block deletions**: Yes

#### 6. Bypass List
- **Only add**: Your GitHub username (e.g., `riedemannai`)
- **Do not add**: Any other users, teams, or apps

### API Configuration

You can also configure via GitHub API:

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/riedemannai/parakeet-mlx-server/rulesets \
  -d @.github/ruleset.json
```

## Branch Protection Rules (Alternative)

If Rulesets are not available, use Branch Protection Rules:

### Settings → Branches → Add rule for `main`

1. **Protect matching branches**
   - Branch name pattern: `main`

2. **Require a pull request before merging**
   - ✅ Required number of approvals: **2**
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require review from Code Owners
   - ✅ Restrict who can dismiss pull request reviews: Only repository administrators

3. **Require status checks to pass before merging**
   - ✅ Require branches to be up to date before merging
   - ✅ Required status checks:
     - `CI / test (3.10)`
     - `CI / test (3.11)`
     - `CI / test (3.12)`
     - `Security Scan / security-scan`
     - `Security Scan / codeql-analysis`

4. **Require conversation resolution before merging**
   - ✅ All conversations on the pull request must be resolved

5. **Require signed commits**
   - ✅ Require signed commits (optional but recommended)

6. **Require linear history**
   - ✅ Require linear history

7. **Include administrators**
   - ✅ **DO NOT CHECK THIS** - This ensures even you must follow the rules
   - ⚠️ **Exception**: If you want to bypass, add yourself to bypass list instead

8. **Restrict who can push to matching branches**
   - ✅ Only allow specific people to push
   - Add only: Your GitHub username

9. **Allow force pushes**
   - ❌ Do not allow force pushes
   - ❌ Do not allow deletions

10. **Lock branch**
    - ❌ Do not lock branch (unless needed temporarily)

## Repository Settings

### General Settings

1. **Settings** → **General**
   - ✅ **Features**: Enable only what you need
   - ✅ **Pull Requests**: Require pull request reviews
   - ✅ **Merge button**: Require status checks

2. **Settings** → **Actions** → **General**
   - **Workflow permissions**: Read and write permissions
   - ✅ **Allow GitHub Actions to create and approve pull requests**
   - ✅ **Require approval for all outside collaborators**

3. **Settings** → **Collaborators and teams**
   - Review all collaborators
   - Remove unnecessary access
   - Set appropriate permission levels

### Access Control

1. **Settings** → **Collaborators**
   - Only add collaborators if absolutely necessary
   - Use minimum required permissions
   - Regular access reviews

2. **Settings** → **Teams**
   - Review team access
   - Remove unnecessary teams

3. **Settings** → **Deploy keys**
   - Review and remove unused keys

4. **Settings** → **Secrets and variables** → **Actions**
   - Review all secrets
   - Rotate regularly
   - Use least privilege

## CODEOWNERS Configuration

The `.github/CODEOWNERS` file ensures you are required for all reviews:

```
* @riedemannai
```

This means:
- All files require your approval
- GitHub automatically requests your review
- PRs cannot be merged without your approval

## Verification

After configuration, verify:

1. ✅ Try to push directly to `main` (should fail)
2. ✅ Try to force push (should fail)
3. ✅ Try to delete branch (should fail)
4. ✅ Create a PR and verify approvals are required
5. ✅ Verify status checks are required
6. ✅ Verify you can bypass (if configured)

## Emergency Access

If you need to bypass rules in an emergency:

1. **Temporary bypass** (if configured):
   - Use the bypass list
   - Or temporarily disable branch protection

2. **Via GitHub UI**:
   - Settings → Branches → Temporarily disable protection
   - Make changes
   - Re-enable protection

3. **Via GitHub API**:
   ```bash
   # Temporarily disable protection
   curl -X DELETE \
     -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.github.com/repos/riedemannai/parakeet-mlx-server/branches/main/protection
   ```

## Important Notes

⚠️ **Warning**: 
- Do not check "Include administrators" if you want strict control
- Instead, add yourself to the bypass list
- This ensures even administrators follow the rules by default

✅ **Best Practice**:
- Use Rulesets if available (more granular control)
- Fall back to Branch Protection Rules if needed
- Regularly review and update rules
- Document any exceptions

## Troubleshooting

**Issue**: Cannot push to main branch
- **Solution**: This is expected. Use pull requests instead.

**Issue**: Cannot merge PR
- **Solution**: Ensure all required checks pass and you have approved the PR.

**Issue**: Need emergency access
- **Solution**: Use bypass list or temporarily disable protection.


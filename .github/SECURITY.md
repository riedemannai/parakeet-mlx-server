# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not** open a public issue. Instead, please report it via one of the following methods:

1. **Email**: Send details to the repository maintainers
2. **Private Security Advisory**: Use GitHub's [Private Vulnerability Reporting](https://github.com/riedemannai/parakeet-mlx-server/security/advisories/new)

### What to Include

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity and complexity

## Security Best Practices

When using this server:

1. **Never expose the server to the public internet without proper authentication**
2. **Use HTTPS in production** (via reverse proxy like nginx)
3. **Keep dependencies up to date**: Run `pip install -r requirements.txt --upgrade` regularly
4. **Limit file upload sizes** (default: 100MB)
5. **Monitor server logs** for suspicious activity
6. **Use firewall rules** to restrict access
7. **Run in isolated environments** (containers, VMs) when possible
8. **Enable branch protection** on the main branch
9. **Require code reviews** before merging (minimum 2 approvals)
10. **Use signed commits** for important changes
11. **Regularly review security alerts** from GitHub
12. **Never commit secrets** or API keys to the repository

## Known Security Considerations

- The server accepts file uploads - validate all inputs
- CORS is enabled by default - configure appropriately for production
- No authentication is built-in - add authentication for production use
- Model files are downloaded from HuggingFace - verify model integrity

## Security Updates

Security updates will be announced via:
- GitHub Releases
- Security Advisories
- CHANGELOG.md


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

1. **Enable API key authentication for production**: Set `API_KEY` environment variable
2. **Restrict CORS origins**: Set `CORS_ORIGINS` to specific domains (not `*`)
3. **Use HTTPS in production** (via reverse proxy like nginx)
4. **Never expose the server to the public internet without proper authentication**
5. **Keep dependencies up to date**: Run `pip install -r requirements.txt --upgrade` regularly
6. **Verify model integrity**: Set `MODEL_SHA256` for model verification (optional)
7. **Monitor server logs** for suspicious activity
8. **Use firewall rules** to restrict access
9. **Run in isolated environments** (containers, VMs) when possible
10. **Enable branch protection** on the main branch
11. **Require code reviews** before merging (minimum 2 approvals)
12. **Use signed commits** for important changes
13. **Regularly review security alerts** from GitHub
14. **Never commit secrets** or API keys to the repository

## Production Deployment Checklist

- [ ] Set `API_KEY` environment variable
- [ ] Configure `CORS_ORIGINS` with specific allowed domains
- [ ] Use HTTPS (reverse proxy with SSL/TLS)
- [ ] Set `MODEL_SHA256` for model integrity verification (optional)
- [ ] Configure firewall to restrict access
- [ ] Monitor logs for suspicious activity
- [ ] Keep dependencies updated
- [ ] Run in isolated environment (container/VM)

## Security Features Implemented

### ✅ File Upload Validation
- **Filename sanitization**: Path traversal attacks prevented
- **File type validation**: Only allowed audio MIME types and extensions accepted
- **File size limits**: Maximum 100MB per file
- **Empty file detection**: Rejects empty uploads
- **MIME type checking**: Validates Content-Type headers

**Allowed file types**: `.wav`, `.mp3`, `.flac`, `.m4a`, `.aac`, `.ogg`, `.opus`, `.webm`

### ✅ CORS Configuration
- **Configurable origins**: Set via `CORS_ORIGINS` environment variable
- **Default restriction**: Limited to `localhost` by default (not open to all)
- **Production ready**: Configure specific allowed origins for production

**Configuration**: Set `CORS_ORIGINS` environment variable (comma-separated list)
```bash
export CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
```

### ✅ API Key Authentication (Optional)
- **Bearer token support**: Use `Authorization: Bearer <key>` header
- **X-API-Key header**: Alternative header format supported
- **Constant-time comparison**: Prevents timing attacks
- **Health check exemption**: `/health` endpoint remains public

**Configuration**: Set `API_KEY` environment variable to enable
```bash
export API_KEY="your-secret-api-key-here"
```

### ✅ Model Integrity Verification
- **SHA256 checksum support**: Optional verification via `MODEL_SHA256` environment variable
- **HuggingFace verification**: Models downloaded from HuggingFace Hub
- **Logging**: Integrity checks logged for audit

**Configuration**: Set `MODEL_SHA256` environment variable (optional)
```bash
export MODEL_SHA256="expected-sha256-checksum"
```

### ✅ Security Headers
- `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - XSS protection
- `Referrer-Policy: strict-origin-when-cross-origin` - Referrer information control

## Security Updates

Security updates will be announced via:
- GitHub Releases
- Security Advisories
- CHANGELOG.md


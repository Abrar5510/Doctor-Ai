# Security Policy

## Overview

Doctor-AI is a medical diagnostic support system that handles sensitive health information. We take security seriously and are committed to protecting patient data and maintaining the integrity of our system.

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

### Where to Report

**DO NOT** create public GitHub issues for security vulnerabilities.

Instead, please report security issues privately:

1. **Email**: Send details to the project maintainer at the email listed in the GitHub profile
2. **GitHub Security Advisory**: Use GitHub's private vulnerability reporting feature
3. **Encrypted Communication**: PGP key available upon request

### What to Include

Please include the following in your report:

- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact and severity
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Affected Versions**: Which versions are affected
- **Proof of Concept**: Code or screenshots demonstrating the issue (if applicable)
- **Suggested Fix**: Your recommendation for fixing the issue (if any)

### Response Timeline

We are committed to the following response times:

- **Initial Response**: Within 48 hours of report
- **Severity Assessment**: Within 5 business days
- **Fix Timeline**:
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium: Within 90 days
  - Low: Next regular release

### Disclosure Policy

- We will acknowledge your report within 48 hours
- We will provide regular updates on our progress
- We will credit you in the security advisory (unless you prefer to remain anonymous)
- We request that you do not publicly disclose the issue until we have released a fix
- We will publicly disclose the vulnerability after a fix is available

## Security Measures

### Data Protection

#### HIPAA Compliance

Doctor-AI implements HIPAA-compliant security measures:

- ✅ **Audit Logging**: All data access is logged
- ✅ **Data Anonymization**: PII removal capabilities
- ✅ **Access Control**: Role-based access (when configured)
- ✅ **Encryption**: Data encryption in transit (HTTPS)
- ✅ **Session Management**: Secure session handling

#### Data Handling

- **No PHI Storage**: System does not store Protected Health Information by default
- **Temporary Processing**: Patient data processed in memory, not persisted
- **De-identified Datasets**: All training data is de-identified
- **API Security**: API key authentication for sensitive endpoints
- **Rate Limiting**: Protection against abuse

### Infrastructure Security

#### Application Security

- **Environment Variables**: Sensitive configuration stored in environment variables
- **Secret Management**: No hardcoded credentials
- **Input Validation**: All API inputs are validated and sanitized
- **Output Encoding**: Protection against injection attacks
- **CORS Configuration**: Proper cross-origin resource sharing policies
- **SQL Injection Protection**: Parameterized queries and ORM usage
- **XSS Protection**: Input sanitization and output encoding
- **CSRF Protection**: Token-based CSRF prevention

#### Database Security

- **Qdrant**: API key authentication, TLS support
- **PostgreSQL**: Password authentication, connection encryption
- **Redis**: Password protection, bind to localhost by default

#### Container Security

- **Minimal Images**: Use official, minimal base images
- **Non-root User**: Containers run as non-root users
- **Resource Limits**: Memory and CPU limits configured
- **Network Isolation**: Internal network for service communication
- **Image Scanning**: Regular vulnerability scanning (recommended)

### AI Model Security

#### Model Integrity

- **Model Verification**: Verify model checksums after download
- **Official Sources**: Only use models from trusted sources (HuggingFace)
- **Version Pinning**: Specific model versions in requirements

#### Prompt Injection Protection

- **Input Sanitization**: Clean user inputs before LLM processing
- **Output Validation**: Validate LLM outputs before returning to users
- **Context Limits**: Limit context window size
- **Rate Limiting**: Prevent API abuse

## Security Best Practices

### For Deployment

1. **Use HTTPS**: Always use TLS/SSL in production
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
   }
   ```

2. **Set Strong Secrets**: Use cryptographically secure random values
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Limit Network Exposure**: Only expose necessary ports
   ```yaml
   # docker-compose.yml
   ports:
     - "127.0.0.1:6333:6333"  # Bind to localhost only
   ```

4. **Enable Authentication**: Require authentication for all endpoints
   ```env
   REQUIRE_API_KEY=true
   API_KEY=your-secure-api-key
   ```

5. **Regular Updates**: Keep all dependencies up to date
   ```bash
   pip install --upgrade -r requirements.txt
   ```

6. **Monitoring**: Implement security monitoring and alerting
   - Log analysis
   - Intrusion detection
   - Anomaly detection

### For Development

1. **Never Commit Secrets**: Use .gitignore for sensitive files
   ```gitignore
   .env
   *.key
   *.pem
   credentials.json
   ```

2. **Use Environment Variables**: Store configuration in .env
   ```python
   import os
   API_KEY = os.getenv("API_KEY")
   ```

3. **Code Review**: All changes should be reviewed for security issues

4. **Dependency Scanning**: Regularly scan for vulnerable dependencies
   ```bash
   pip install safety
   safety check
   ```

5. **Static Analysis**: Use security linters
   ```bash
   pip install bandit
   bandit -r src/
   ```

### For Researchers

1. **Data Anonymization**: Always anonymize patient data
2. **Secure Storage**: Encrypt sensitive data at rest
3. **Access Logs**: Maintain audit trails
4. **Data Retention**: Follow institutional policies
5. **IRB Approval**: Obtain necessary approvals for human subjects research

## Known Security Limitations

### Current Limitations

1. **AI Hallucinations**: LLM may generate incorrect medical information
   - **Mitigation**: Always require human medical professional review

2. **Model Poisoning**: Risk of adversarial inputs affecting model outputs
   - **Mitigation**: Input validation, output verification

3. **API Key Storage**: API keys stored in environment variables
   - **Mitigation**: Use proper secrets management in production (Vault, AWS Secrets Manager)

4. **Local File Access**: Application can read local files
   - **Mitigation**: Run in containerized environment with limited file system access

### Not Suitable For

Doctor-AI is **NOT** designed for:

- ❌ Direct patient-facing diagnosis without physician oversight
- ❌ Emergency medical situations
- ❌ Prescription decisions
- ❌ Definitive diagnosis without clinical validation
- ❌ Replacement for professional medical judgment

## Compliance

### HIPAA Compliance

Doctor-AI includes features to support HIPAA compliance but requires proper deployment:

- **Technical Safeguards**: Encryption, access controls, audit logs
- **Administrative Safeguards**: Policies, procedures, training (your responsibility)
- **Physical Safeguards**: Secure facilities (your responsibility)

**Important**: Full HIPAA compliance requires organizational policies and procedures beyond this software.

### Data Protection Regulations

- **GDPR**: Data minimization, right to erasure, data portability support
- **CCPA**: Data access and deletion capabilities
- **PIPEDA**: Privacy by design principles

**Note**: Compliance with regulations requires proper configuration and operational procedures.

## Security Checklist

### Before Production Deployment

- [ ] All secrets moved to secure secret management system
- [ ] HTTPS/TLS enabled with valid certificates
- [ ] API authentication enabled
- [ ] Rate limiting configured
- [ ] CORS policy restricted to known domains
- [ ] Database access restricted to application only
- [ ] Firewall rules configured
- [ ] Backup and disaster recovery plan in place
- [ ] Monitoring and alerting configured
- [ ] Security scanning tools integrated
- [ ] Penetration testing completed
- [ ] Incident response plan documented
- [ ] HIPAA Business Associate Agreement in place (if applicable)
- [ ] Security training completed for all team members

### Regular Maintenance

- [ ] Weekly: Review security logs
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Security audit
- [ ] Annually: Penetration testing
- [ ] As needed: Apply security patches

## Security Tools

### Recommended Tools

1. **Dependency Scanning**
   ```bash
   pip install safety
   safety check --json
   ```

2. **Static Analysis**
   ```bash
   pip install bandit
   bandit -r src/ -f json -o security-report.json
   ```

3. **Secret Scanning**
   ```bash
   pip install detect-secrets
   detect-secrets scan --baseline .secrets.baseline
   ```

4. **Container Scanning**
   ```bash
   docker scan doctor-ai:latest
   ```

## Incident Response

### In Case of Security Incident

1. **Assess**: Determine scope and impact
2. **Contain**: Isolate affected systems
3. **Notify**: Inform stakeholders and users if required
4. **Remediate**: Apply fixes and patches
5. **Document**: Record incident details and response
6. **Review**: Conduct post-incident review

### Contact Information

- **Security Issues**: Report privately to maintainers
- **General Security Questions**: Open a GitHub discussion
- **Compliance Questions**: Consult with your organization's compliance team

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)

## Updates

This security policy is reviewed and updated regularly. Last updated: 2025-11-14

---

**Thank you for helping keep Doctor-AI and its users safe!**

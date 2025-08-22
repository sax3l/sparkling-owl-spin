# Security Policy

## Supported Versions

Vi tillhandahåller säkerhetsuppdateringar för följande versioner:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**RAPPORTERA ALDRIG säkerhetsproblem via offentliga GitHub Issues.**

### Säker rapportering

Säkerhetsproblem ska rapporteras via:

**Email**: security@ecadp.se
- Använd PGP-nyckel: [Hämta här](https://keys.openpgp.org/search?q=security%40ecadp.se)
- Inkludera "SECURITY" i subject line

### Vad ska inkluderas

1. **Problembeskrivning**: Detaljerad beskrivning av sårbarheten
2. **Påverkan**: Vad kan en angripare uppnå?
3. **Reproduktion**: Steg-för-steg guide
4. **Miljö**: Systemdetaljer där problemet upptäcktes
5. **Proof of Concept**: Kod eller exempel (om säkert)

### Response Timeline

- **24 timmar**: Bekräftelse av rapport
- **72 timmar**: Initial bedömning och prioritering  
- **7 dagar**: Detaljerad analys och åtgärdsplan
- **30 dagar**: Fix och security release (om möjligt)

### Disclosure Policy

Vi följer **koordinerad disclosure**:

1. **Privat rapportering** → vi undersöker
2. **Fix utvecklas** i privat branch
3. **Security release** publiceras
4. **Public disclosure** efter 90 dagar eller när fix är tillgänglig

### Bug Bounty

Vi har för närvarande inget formellt bug bounty-program, men vi:

- Erkänner säkerhetsforskare i våra release notes
- Överväger belöningar för kritiska sårbarheter
- Tillhandahåller snabb response och feedback

## Security Measures

### Kod-säkerhet

- **Static Analysis**: Bandit, Safety, CodeQL
- **Dependency Scanning**: Automated vulnerability detection
- **Secret Scanning**: Förhindra läckage av API-nycklar
- **SAST/DAST**: Security testing i CI/CD

### Runtime-säkerhet

- **Input Validation**: Alla inputs valideras och saneras
- **Rate Limiting**: API rate limits och DDoS-skydd
- **Authentication**: OAuth2 + JWT med proper expiration
- **Authorization**: RBAC med minsta privilegium
- **Encryption**: TLS 1.3, AES-256, proper key management

### Infrastructure

- **Container Security**: Minimal base images, non-root users
- **Secrets Management**: HashiCorp Vault eller AWS Secrets Manager
- **Network Security**: VPC, security groups, WAF
- **Monitoring**: Real-time security event detection
- **Backup**: Encrypted backups med offline copies

### Data Protection

- **PII Handling**: Pseudonymisering och kryptering
- **GDPR Compliance**: Right to erasure, data portability
- **Access Logging**: Fullständig audit trail
- **Data Retention**: Automatisk radering enligt policy

## Threat Model

### Identifierade hot

1. **Web Scraping Abuse**: Missbruk för att kringgå säkerhet
2. **Data Exfiltration**: Stöld av känslig data  
3. **Credential Stuffing**: Brute force-attacker
4. **Injection Attacks**: SQL, XSS, command injection
5. **Supply Chain**: Komprometterade dependencies

### Mitigeringar

- Etiska riktlinjer med teknisk enforcement
- Kryptering av känslig data i vila och transport
- Multi-factor authentication för admin-åtkomst
- Input sanitization och parameterized queries
- Dependency vulnerability scanning

## Incident Response

### Severity Levels

**Critical (P0)**
- Remote code execution
- Data breach med PII
- Complete service compromise
- Response: Inom 1 timme

**High (P1)**
- Privilege escalation
- Authentication bypass
- Significant data exposure
- Response: Inom 4 timmar

**Medium (P2)**
- Information disclosure
- Limited DoS
- Minor privilege issues
- Response: Inom 24 timmar

**Low (P3)**
- Security misconfigurations
- Non-exploitable information leaks
- Response: Inom 7 dagar

### Response Process

1. **Detection** → Automated alerts + manual reporting
2. **Assessment** → Confirm and classify severity
3. **Containment** → Isolate affected systems
4. **Eradication** → Remove threat and vulnerabilities
5. **Recovery** → Restore services safely
6. **Lessons Learned** → Post-mortem och improvements

## Security Contacts

- **Security Team**: security@ecadp.se
- **Lead Developer**: alex@ecadp.se
- **PGP Keys**: https://keys.openpgp.org/

---

**Tack för att du hjälper oss hålla ECaDP säkert! 🔐**
# Security & Input Validation

## Purpose

The Security & Input Validation skill is responsible for protecting the GDI (Genome Document Intelligence) Platform against malicious inputs, unauthorized access, data corruption, and common application security vulnerabilities.

Its objective is to ensure that every external interaction—including file uploads, API requests, user input, and database operations—is validated, sanitized, authenticated, authorized, and processed securely.

Security must be integrated into every stage of the application lifecycle rather than treated as an afterthought.

---

# Mission Statement

Build secure-by-design systems that protect data, maintain integrity, and minimize attack surfaces while preserving usability and performance.

Every security mechanism should be:

* Preventive
* Layered
* Auditable
* Deterministic
* Configurable
* Production-ready

---

# Primary Responsibilities

* Input validation
* File validation
* API security
* Authentication integration
* Authorization enforcement
* Secret management
* Secure configuration
* Data integrity verification
* Secure file handling
* Secure database interaction
* Threat mitigation
* Security auditing
* Vulnerability prevention
* Error sanitization
* Security logging
* Compliance with secure coding practices

---

# Core Principles

## Never Trust External Input

Treat every request, uploaded file, header, parameter, and payload as untrusted until validated.

---

## Defense in Depth

Implement multiple independent security layers.

No single mechanism should be relied upon exclusively.

---

## Least Privilege

Users, services, and processes should only receive the minimum permissions required.

---

## Fail Securely

Failures should deny unsafe operations while preserving system integrity.

---

## Secure by Default

Default configurations should prioritize security over convenience.

---

# Input Validation

Validate:

* Request bodies
* Query parameters
* Path parameters
* Headers
* Cookies
* UUIDs
* Numeric values
* Strings
* Dates
* JSON payloads

Reject malformed or unexpected input immediately.

---

# File Validation

Before processing uploaded documents:

Validate:

* MIME type
* Magic bytes
* File extension
* File size
* Page count
* Image dimensions
* File integrity
* Encryption status
* Password protection

Reject unsupported or suspicious files before they reach processing pipelines.

---

# Secure File Handling

Requirements:

* Store uploads outside public directories
* Generate unique filenames
* Preserve original evidence
* Process in isolated temporary locations
* Remove temporary files securely
* Prevent directory traversal

Never trust client-provided filenames.

---

# Authentication

Support:

* JWT authentication
* OAuth2 integration (future)
* Secure password hashing
* Token expiration
* Refresh tokens
* Session validation

Authentication should remain independent of business logic.

---

# Authorization

Implement role-based access control (RBAC).

Typical roles:

* Administrator
* Organization
* Analyst
* Auditor
* Read-only User

Every protected resource should verify permissions before access.

---

# API Security

Protect APIs using:

* HTTPS
* Authentication
* Authorization
* Request validation
* Rate limiting
* CORS configuration
* Secure headers
* Request size limits

Public endpoints should expose only necessary information.

---

# Database Security

Ensure:

* Parameterized queries
* ORM usage where appropriate
* Principle of least privilege
* Secure credentials
* TLS database connections
* Controlled migrations

Never build SQL queries using string concatenation.

---

# Secret Management

Store secrets securely:

* Environment variables
* Secret managers
* Encrypted configuration

Never commit secrets to version control.

---

# Error Handling

Security-related errors should:

* Avoid revealing internal implementation details
* Return standardized responses
* Be logged internally
* Include correlation IDs for investigation

Stack traces must never be exposed to clients.

---

# Logging & Auditing

Log:

* Authentication attempts
* Authorization failures
* File validation failures
* Suspicious requests
* Rate limit violations
* Administrative actions
* Security configuration changes

Security logs should be immutable where practical.

---

# Threat Mitigation

Protect against:

* SQL Injection
* Cross-Site Scripting (XSS)
* Cross-Site Request Forgery (CSRF) where applicable
* Path Traversal
* Command Injection
* File Upload Attacks
* Denial of Service (DoS)
* Brute Force Attacks
* Replay Attacks
* Malformed Input Attacks

Mitigation strategies should be regularly reviewed and updated.

---

# Rate Limiting

Apply configurable limits to:

* Login attempts
* API requests
* File uploads
* Resource-intensive operations

Limits should protect availability without unnecessarily impacting legitimate users.

---

# Data Integrity

Verify:

* File hashes
* Processing integrity
* Database consistency
* Configuration integrity

Integrity checks should be performed before critical operations.

---

# Security Testing

Regularly perform:

* Input validation testing
* Authentication testing
* Authorization testing
* File upload testing
* Dependency vulnerability scanning
* Penetration testing
* Regression security testing

Security defects should be treated with high priority.

---

# Performance Considerations

Security mechanisms should:

* Minimize unnecessary overhead
* Scale efficiently
* Avoid blocking legitimate workloads
* Be measurable and configurable

Security should not compromise system stability.

---

# Coding Standards

* Follow secure coding best practices.
* Validate all external input.
* Sanitize output where required.
* Use parameterized database access.
* Prefer allowlists over blocklists.
* Document security-sensitive code.
* Keep dependencies updated.

---

# Deliverables

This skill is responsible for producing:

* Input validation rules
* File validation pipelines
* Authentication integration
* Authorization policies
* Secure API implementations
* Security audit logs
* Threat mitigation strategies
* Secure configuration guidelines
* Vulnerability remediation recommendations
* Production-ready security controls

These deliverables establish the security foundation of the GDI platform, protecting its APIs, processing pipelines, databases, and forensic evidence while ensuring reliable and secure operation in production.

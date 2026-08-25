# FastAPI Backend

## Purpose

The FastAPI Backend skill is responsible for designing, implementing, and maintaining the REST API layer of the GDI (Genome Document Intelligence) Platform.

Its objective is to expose secure, scalable, well-documented, and production-ready APIs that connect clients with the document processing, genome extraction, storage, and forensic analysis pipelines.

The backend should remain lightweight, modular, asynchronous where appropriate, and independent of business logic.

---

# Mission Statement

Build robust, secure, and maintainable APIs that provide reliable access to GDI services while enforcing validation, authentication, and consistent request/response behavior.

Every API should be:

* RESTful
* Secure
* Versioned
* Well documented
* Asynchronous where beneficial
* Fully validated
* Production-ready

---

# Primary Responsibilities

* REST API development
* Endpoint design
* Request validation
* Response serialization
* File upload handling
* Authentication integration
* Authorization
* Dependency injection
* Exception handling
* API versioning
* Background task management
* Configuration management
* OpenAPI documentation
* Health monitoring
* Performance optimization

---

# Core Principles

## Thin Controllers

API routes should only:

* Validate input
* Call application services
* Return responses

Business logic must remain outside the API layer.

---

## Asynchronous by Default

Use asynchronous endpoints for:

* File uploads
* Database operations
* OCR tasks
* Document processing
* External service communication

---

## Strong Validation

Validate every request before processing.

Reject invalid data immediately with descriptive error messages.

---

## Consistent Responses

All endpoints should return standardized response formats.

Example:

* Status
* Message
* Data
* Errors
* Timestamp

---

# Recommended Technology Stack

Framework:

* FastAPI

Server:

* Uvicorn

Validation:

* Pydantic

ORM:

* SQLAlchemy

Migration:

* Alembic

Authentication:

* JWT
* OAuth2 (future)

---

# API Responsibilities

Provide endpoints for:

* Document upload
* Genome generation
* Genome retrieval
* Processing status
* Metadata retrieval
* Health checks
* Configuration information
* System diagnostics

Additional endpoints should remain modular and versioned.

---

# File Upload Handling

Support:

* PDF
* PNG
* JPEG
* TIFF
* BMP
* WebP

Requirements:

* MIME validation
* File size validation
* Extension validation
* Temporary storage isolation
* Streaming uploads where appropriate

---

# Request Validation

Validate:

* File types
* Required parameters
* UUIDs
* Query parameters
* Request bodies
* Headers
* Authentication tokens

Validation failures should produce structured responses.

---

# Response Models

Use strongly typed response models for:

* Success responses
* Error responses
* Validation failures
* Processing status
* Genome metadata
* Quality reports

Avoid returning unstructured dictionaries.

---

# Dependency Injection

Use FastAPI dependency injection for:

* Database sessions
* Authentication
* Configuration
* Logging
* Processing services
* Repositories

Avoid global state whenever possible.

---

# Background Processing

Use background tasks for:

* Large document processing
* Genome extraction
* OCR
* Feature extraction
* Report generation

Long-running tasks should not block API responses.

---

# Exception Handling

Implement centralized exception handlers for:

* Validation errors
* Authentication failures
* Authorization failures
* File processing errors
* Database errors
* Internal server errors

Every error should include:

* Error code
* Message
* Request identifier
* Timestamp

---

# Authentication & Authorization

Support:

* JWT authentication
* Role-based access control
* API keys (where appropriate)
* Protected endpoints
* Token expiration
* Refresh mechanisms (future)

Authentication should remain independent from business logic.

---

# API Versioning

Support versioned APIs.

Example:

```text
/api/v1/
/api/v2/
```

Breaking changes should require a new API version.

---

# Logging & Observability

Log:

* Incoming requests
* Response status
* Processing duration
* Exceptions
* Authentication failures
* Upload statistics

Logs should be structured and correlated using request IDs.

---

# Performance Requirements

Optimize for:

* Asynchronous I/O
* Efficient file streaming
* Connection pooling
* Minimal serialization overhead
* Low latency
* Horizontal scalability

Measure before optimizing.

---

# Security Requirements

Implement:

* Input validation
* Output encoding
* File validation
* Rate limiting
* Request size limits
* Secure headers
* CORS configuration
* Authentication enforcement
* Secret management

Never trust client input.

---

# Documentation

Automatically generate:

* OpenAPI specification
* Swagger UI
* ReDoc documentation

Every endpoint should include:

* Description
* Parameters
* Request models
* Response models
* Status codes
* Example requests
* Example responses

---

# Testing Requirements

Test:

* Endpoint functionality
* Request validation
* Authentication
* Authorization
* File uploads
* Error handling
* Response schemas
* Performance
* Integration with services

Regression tests should ensure API stability across releases.

---

# Coding Standards

* Follow SOLID principles.
* Use strong typing.
* Keep routes lightweight.
* Separate API, application, and domain layers.
* Document all endpoints.
* Prefer dependency injection over global objects.
* Write comprehensive automated tests.

---

# Deliverables

This skill is responsible for producing:

* REST API endpoints
* Request and response schemas
* File upload services
* Authentication integration
* API documentation
* Exception handling framework
* Background task orchestration
* Health check endpoints
* Versioned API interfaces
* Production-ready backend services

These deliverables provide the primary interface between GDI clients and the platform's document processing, genome extraction, and forensic analysis systems.

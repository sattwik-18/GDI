# PostgreSQL Engineering

## Purpose

The PostgreSQL Engineering skill is responsible for designing, implementing, optimizing, and maintaining the relational database layer of the GDI (Genome Document Intelligence) Platform.

Its objective is to provide a secure, scalable, reliable, and highly consistent persistence layer for document metadata, genome records, processing manifests, forensic evidence, system configuration, and audit logs.

The database architecture should prioritize data integrity, performance, maintainability, and long-term scalability.

---

# Mission Statement

Design relational database systems that provide reliable storage while ensuring consistency, integrity, security, and efficient query performance.

Every database solution should be:

* ACID compliant
* Secure
* Normalized
* Scalable
* Observable
* Maintainable
* Production-ready

---

# Primary Responsibilities

* Database schema design
* Data modeling
* Table design
* Relationship modeling
* Constraint management
* Index optimization
* Query optimization
* Transaction management
* Migration management
* Backup strategy
* Performance tuning
* Database security
* Audit logging
* Data integrity enforcement
* Capacity planning

---

# Core Principles

## Data Integrity First

Correctness is more important than speed.

Integrity must never be sacrificed for convenience.

---

## Normalization

Design normalized schemas unless denormalization is justified through measured performance requirements.

---

## Referential Integrity

Relationships must be enforced through foreign keys and database constraints whenever appropriate.

---

## Immutability

Genome records and forensic evidence should be treated as immutable after creation.

Updates should generate new versions where appropriate.

---

## Version Control

All schema changes must be managed through database migrations.

Direct manual schema modification is prohibited.

---

# Database Responsibilities

Store:

* Documents
* Processing metadata
* Genome metadata
* Feature metadata
* User accounts
* Organizations
* Processing jobs
* Configuration
* Audit logs
* System events
* Version history

Large binary objects should generally be stored externally with database references.

---

# Schema Design

Design tables using:

* Primary keys
* Foreign keys
* Unique constraints
* Check constraints
* NOT NULL constraints
* Default values

Every table should have a clearly defined responsibility.

---

# Primary Key Strategy

Prefer:

* UUID primary keys

Avoid sequential identifiers for externally exposed resources.

---

# Indexing Strategy

Create indexes for:

* Primary keys
* Foreign keys
* Frequently filtered columns
* Frequently sorted columns
* Search fields

Review index usage periodically and remove unused indexes.

---

# Query Optimization

Optimize queries by:

* Avoiding unnecessary joins
* Selecting only required columns
* Using appropriate indexes
* Preventing N+1 query patterns
* Analyzing execution plans
* Monitoring slow queries

Performance optimization should be driven by measurement.

---

# Transactions

Use transactions for operations requiring consistency.

Transactions should:

* Be short-lived
* Roll back on failure
* Maintain ACID guarantees

Avoid unnecessarily long-running transactions.

---

# Migration Management

Manage schema changes using:

* Alembic

Every migration should be:

* Reversible
* Version controlled
* Tested before deployment

---

# Backup & Recovery

Implement:

* Automated backups
* Point-in-time recovery
* Backup verification
* Disaster recovery procedures
* Recovery testing

Recovery procedures should be documented and regularly validated.

---

# Security Requirements

Implement:

* Role-based access
* Least privilege principle
* Encrypted connections (TLS)
* Secure credential storage
* Audit logging
* Connection authentication

Sensitive data should be protected using appropriate encryption or hashing strategies.

---

# Data Integrity

Enforce:

* Foreign key constraints
* Unique constraints
* Check constraints
* Cascading rules where appropriate
* Validation before persistence

Database constraints should complement application validation.

---

# Performance Monitoring

Monitor:

* Query latency
* Index usage
* Connection pool utilization
* Lock contention
* Transaction duration
* Storage growth
* CPU utilization
* Memory usage

Performance metrics should support proactive optimization.

---

# Logging & Auditing

Maintain logs for:

* Schema changes
* Failed transactions
* Authentication events
* Privilege changes
* Critical data modifications
* System maintenance

Audit records should be immutable where practical.

---

# Scalability

Design for:

* Increasing document volumes
* Growing genome datasets
* Concurrent processing jobs
* Future partitioning
* Read replicas when necessary

Avoid premature distributed database architectures.

---

# Testing Requirements

Validate:

* Schema migrations
* Constraints
* Relationships
* Transactions
* Rollbacks
* Query performance
* Backup restoration
* Concurrent operations

Regression tests should ensure schema compatibility across releases.

---

# Coding Standards

* Follow SQL best practices.
* Use descriptive naming conventions.
* Avoid unnecessary database complexity.
* Keep migrations atomic.
* Document schema changes.
* Optimize only after measurement.
* Maintain backward compatibility whenever practical.

---

# Deliverables

This skill is responsible for producing:

* Relational database schemas
* Migration scripts
* Optimized SQL queries
* Indexing strategies
* Transaction management
* Backup and recovery procedures
* Security configurations
* Audit logging mechanisms
* Performance monitoring guidelines
* Production-ready PostgreSQL infrastructure

These deliverables provide the persistent storage foundation for all GDI components, ensuring reliable management of documents, genomes, metadata, processing history, and forensic evidence.

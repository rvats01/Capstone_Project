# Insurance Claim Assessment System
## Technical Design Document

**Document Version:** 1.0  
**Date:** June 2026  
**Classification:** Technical - Confidential  
**Audience:** Developers, Architects, Technical Reviewers

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Design Principles](#design-principles)
3. [System Requirements](#system-requirements)
4. [API Specification](#api-specification)
5. [Agent Design](#agent-design)
6. [Hooks Implementation](#hooks-implementation)
7. [Database Schema](#database-schema)
8. [MCP Server Integration](#mcp-server-integration)
9. [Error Handling](#error-handling)
10. [Performance Specifications](#performance-specifications)

---

## Executive Summary

This document details the technical architecture and design patterns of the Insurance Claim Assessment System. The system is built on a multi-agent agentic AI framework using Claude Sonnet 4 for decision-making, with comprehensive hooks for security, compliance, and auditability.

**Key Technical Decisions:**
- Async-first architecture (FastAPI + asyncio) for scalability
- Multi-agent pattern for separation of concerns
- Hook pipeline for cross-cutting concerns
- MCP (Model Context Protocol) for external knowledge access
- SQLite with async support for data persistence
- Immutable audit logging for compliance

---

## Design Principles

### 1. Separation of Concerns
Each agent has a single responsibility:
- **CustomerAgent**: Customer identity & data validation
- **KnowledgeAgent**: Domain knowledge retrieval
- **ComplianceAgent**: Regulatory checks
- **RiskAgent**: Fraud & anomaly detection
- **DecisionAgent**: Final recommendation synthesis
- **AuditAgent**: Record-keeping

### 2. Async-First Architecture
- All I/O operations are non-blocking
- Concurrent claim processing without blocking
- Efficient resource utilization
- Database: SQLAlchemy async ORM (aiosqlite backend)

### 3. Pipeline with Hooks
- Pluggable hooks for cross-cutting concerns
- Consistent error handling across pipeline
- Auditability at each stage
- Security validation layered throughout

### 4. Explainability & Traceability
- Every decision includes reasoning and confidence score
- Full audit trail of all operations
- Chain-of-thought reasoning from Claude
- Tool call history and intermediate results

### 5. Production-Ready
- Comprehensive error handling and recovery
- Graceful degradation
- Logging at every stage
- Configuration via environment variables

---

## System Requirements

### Functional Requirements

| Requirement | Description | Priority |
|-------------|-------------|----------|
| FR-1 | Accept insurance claims via API and web form | MUST |
| FR-2 | Validate customer identity and policy details | MUST |
| FR-3 | Perform regulatory compliance checks | MUST |
| FR-4 | Detect fraud using ML-based scoring | MUST |
| FR-5 | Generate assessment recommendation | MUST |
| FR-6 | Create immutable audit trail | MUST |
| FR-7 | Provide claim status dashboard | SHOULD |
| FR-8 | Export audit reports | SHOULD |
| FR-9 | Handle document attachments | COULD |
| FR-10 | Multi-currency support | COULD |

### Non-Functional Requirements

| Requirement | Target | Priority |
|-------------|--------|----------|
| NFR-1 | Assessment latency | < 5 minutes (99th percentile) | MUST |
| NFR-2 | System availability | 99.5% uptime | MUST |
| NFR-3 | Concurrent claims | 100+ simultaneous assessments | MUST |
| NFR-4 | Data consistency | ACID compliance | MUST |
| NFR-5 | Compliance audit trail | 100% coverage | MUST |
| NFR-6 | PII encryption | AES-256 | MUST |
| NFR-7 | Response time (API) | < 500ms (p95) | SHOULD |
| NFR-8 | System scalability | Horizontal scaling via load balancer | SHOULD |

---

## API Specification

### Base URL
```
https://api.insurance-assessment.local/api
```

### Authentication
All endpoints require Bearer token authentication (JWT).
```
Authorization: Bearer <JWT_TOKEN>
```

### Core Endpoints

#### 1. Submit Claim
```http
POST /claims/submit
Content-Type: application/json

Request Body:
{
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_id": "CUST123456",
  "policy_number": "POL-2024-001",
  "claim_type": "health",
  "incident_date": "2026-06-10",
  "claim_amount": 25000.00,
  "description": "Emergency hospitalization for appendicitis"
}

Success Response (201):
{
  "claim_id": "CLM-2026-001234",
  "status": "submitted",
  "created_at": "2026-06-14T10:30:00Z",
  "assessment_start": null,
  "message": "Claim submitted successfully"
}

Error Response (400/422):
{
  "error": "Validation error",
  "details": [
    {
      "field": "claim_amount",
      "message": "Must be greater than 0"
    }
  ]
}
```

#### 2. Get Claim Status
```http
GET /claims/{claim_id}

Success Response (200):
{
  "claim_id": "CLM-2026-001234",
  "status": "assessing",
  "customer_name": "John Doe",
  "policy_number": "POL-2024-001",
  "claim_type": "health",
  "claim_amount": 25000.00,
  "created_at": "2026-06-14T10:30:00Z",
  "assessment_start": "2026-06-14T10:35:00Z",
  "assessment_status": "in_progress",
  "current_phase": "compliance_check"
}
```

#### 3. Trigger Assessment
```http
POST /claims/{claim_id}/assess
Content-Type: application/json

Request Body:
{
  "priority": "normal"  # "low", "normal", "high", "urgent"
}

Success Response (202):
{
  "claim_id": "CLM-2026-001234",
  "assessment_job_id": "ASSESS-2026-005678",
  "status": "queued",
  "message": "Assessment queued for processing"
}
```

#### 4. Get Assessment Result
```http
GET /claims/{claim_id}/assessment

Success Response (200):
{
  "claim_id": "CLM-2026-001234",
  "assessment_id": "ASSESS-2026-005678",
  "status": "completed",
  "decision": "approved",
  "confidence": 0.95,
  "recommendation": "Approve claim for full amount",
  "reasoning": "Claim passes all compliance checks...",
  "agent_outputs": {
    "customer_validation": {...},
    "compliance_check": {...},
    "risk_score": {...},
    "decision": {...}
  },
  "assessment_duration_ms": 245000,
  "completed_at": "2026-06-14T10:40:00Z"
}
```

#### 5. Get Audit Trail
```http
GET /claims/{claim_id}/audit

Success Response (200):
{
  "claim_id": "CLM-2026-001234",
  "audit_trail": [
    {
      "timestamp": "2026-06-14T10:30:00Z",
      "event": "claim_submitted",
      "actor": "customer_portal",
      "details": {...}
    },
    {
      "timestamp": "2026-06-14T10:35:00Z",
      "event": "assessment_started",
      "actor": "orchestrator",
      "details": {...}
    },
    {...}
  ],
  "total_events": 42,
  "integrity_hash": "sha256:abc123..."
}
```

#### 6. Dashboard
```http
GET /dashboard

Success Response (200):
{
  "claims_summary": {
    "total_submitted": 1250,
    "total_approved": 875,
    "total_rejected": 225,
    "under_review": 150
  },
  "daily_statistics": {
    "date": "2026-06-14",
    "submitted": 48,
    "approved": 32,
    "avg_duration_ms": 240000
  },
  "risk_distribution": {
    "low": 750,
    "medium": 350,
    "high": 125,
    "critical": 25
  }
}
```

---

## Agent Design

### BaseAgent Architecture

All agents inherit from `BaseAgent` which provides:
- Claude API integration via Anthropic client
- Token management and rate limiting
- Error handling and retry logic
- Execution timing and logging

```python
class BaseAgent:
    def __init__(self, name: str, model: str = "claude-sonnet-4-6"):
        self.name = name
        self.model = model
        self.client = anthropic.Anthropic()
        self.max_tokens = 2048
    
    def _call_claude(self, system_prompt, user_message, tools=None):
        # Calls Claude API with optional tool use
        # Returns: AgentResult (success, data, reasoning, confidence)
```

### Agent Result Structure

```python
@dataclass
class AgentResult:
    agent_name: str              # Name of agent
    success: bool                # Whether agent succeeded
    data: dict                   # Output data
    reasoning: str               # Explanation of reasoning
    confidence: float            # Confidence score [0.0, 1.0]
    duration_ms: int             # Execution time
    error: Optional[str]         # Error message if failed
```

### Individual Agent Specifications

#### CustomerAgent
**Responsibility**: Customer identity validation and claim data extraction

**Input**:
```python
{
    "customer_name": str,
    "customer_email": str,
    "customer_id": str (optional),
    "policy_number": str,
    "incident_date": str,
    "claim_amount": float,
    "description": str
}
```

**Output**:
```python
AgentResult(
    data={
        "customer_valid": bool,
        "policy_exists": bool,
        "policy_active": bool,
        "customer_history": {...},
        "previous_claims": int,
        "avg_claim_amount": float
    },
    confidence=0.92,
    reasoning="Customer and policy validated successfully..."
)
```

**Process**:
1. Validate customer identity against KYC database
2. Verify policy is active and covers claim type
3. Check customer claims history
4. Identify any red flags in customer profile

#### KnowledgeAgent
**Responsibility**: Domain knowledge retrieval via MCP server

**Input**:
```python
{
    "query_type": str,  # "policy_terms" | "regulations" | "precedents"
    "claim_type": str,  # "health", "auto", "life", etc.
    "query": str
}
```

**Output**:
```python
AgentResult(
    data={
        "policy_terms": [...],
        "applicable_regulations": [...],
        "similar_precedents": [...],
        "coverage_limits": {...},
        "exclusions": [...]
    },
    confidence=0.98,
    reasoning="Retrieved from MCP regulatory knowledge base..."
)
```

#### ComplianceAgent
**Responsibility**: Regulatory compliance validation

**Validations**:
- IRDAI (Insurance Regulatory & Development Authority) guidelines
- SOX (Sarbanes-Oxley) compliance
- AML (Anti-Money Laundering) screening
- KYC (Know Your Customer) requirements
- Data privacy (GDPR, local laws)

**Output**:
```python
AgentResult(
    data={
        "irdai_compliant": bool,
        "sox_compliant": bool,
        "aml_status": str,  # "clear" | "review" | "blocked"
        "kyc_verified": bool,
        "violations": [...]
    },
    confidence=0.97,
    reasoning="All regulatory checks passed..."
)
```

#### RiskAgent
**Responsibility**: Fraud detection and risk scoring

**Analysis**:
- Claim amount vs. historical average
- Incident-to-claim submission time lag
- Claimant history (frequency, patterns)
- Claim description text analysis (anomalies)
- Geographic/temporal patterns
- ML-based fraud probability scoring

**Output**:
```python
AgentResult(
    data={
        "risk_level": str,  # "low" | "medium" | "high" | "critical"
        "fraud_probability": float,  # [0.0, 1.0]
        "anomaly_flags": [...],
        "flagged_patterns": [...],
        "risk_factors": {
            "historical_frequency": 0.2,
            "amount_deviation": 1.8,
            "temporal_pattern": 0.3
        }
    },
    confidence=0.88,
    reasoning="Risk score elevated due to..."
)
```

#### DecisionAgent
**Responsibility**: Synthesize all assessments into final recommendation

**Decision Logic**:
```
IF compliance_failed:
    decision = REJECTED
    confidence = 0.99
ELIF fraud_probability > 0.7:
    decision = REJECTED
    confidence = 0.92
ELIF risk_level == "critical":
    decision = UNDER_REVIEW
    confidence = 0.85
ELIF compliance_passed AND fraud_probability < 0.3 AND risk_level != "high":
    decision = APPROVED
    confidence = min(compliance.confidence, risk.confidence)
ELSE:
    decision = UNDER_REVIEW
    confidence = average([compliance, risk, customer].confidence)
```

**Output**:
```python
AgentResult(
    data={
        "decision": str,  # "approved" | "rejected" | "under_review"
        "payment_amount": float,
        "conditions": [...],
        "next_steps": [...]
    },
    confidence=0.93,
    reasoning="Based on complete assessment: policy covers claim..."
)
```

#### AuditAgent
**Responsibility**: Immutable audit trail creation

**Captures**:
- Claim submission metadata
- Customer identity verification
- Policy terms retrieved
- Compliance checks performed
- Risk analysis results
- Agent decisions and reasoning
- Final decision and payout
- All tool invocations
- Execution timings

**Output**:
```python
AgentResult(
    data={
        "audit_trail_id": str,
        "claim_id": str,
        "events": [...],  # Chronological list of all events
        "integrity_hash": str,  # SHA-256 of audit trail
        "seal_timestamp": str  # When audit trail was sealed
    },
    confidence=1.0,
    reasoning="Audit trail sealed and immutable"
)
```

---

## Hooks Implementation

### Hook Pipeline Pattern

Each hook implements the following interface:

```python
class Hook(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs) -> Tuple[bool, Any, List[str]]:
        """
        Returns: (success: bool, data: Any, messages: List[str])
        """
        pass
```

### InputValidationHook

**Purpose**: Sanitize and validate all input data

**Validations**:
```python
{
    "customer_name": {
        "type": "string",
        "min_length": 2,
        "max_length": 200,
        "pattern": "^[A-Za-z\\s'-]+$"  # No injection chars
    },
    "email": {
        "type": "email",
        "max_length": 200
    },
    "claim_amount": {
        "type": "float",
        "min": 0.01,
        "max": 10_000_000
    },
    "claim_type": {
        "type": "enum",
        "values": ["health", "auto", "life", "property", "liability"]
    },
    "description": {
        "type": "string",
        "min_length": 10,
        "max_length": 5000
    }
}
```

### SecurityHook

**Purpose**: Enforce security and authorization checks

**Checks**:
1. JWT token validation and expiration
2. Role-based access control (RBAC)
3. IP whitelist/blacklist
4. Rate limiting (claims per user, per IP)
5. PII detection and protection
6. Session validation

### GovernanceHook

**Purpose**: Enforce business rules and constraints

**Rules**:
1. Business hours restrictions (optional)
2. Claim amount caps by policy type
3. Maximum claims per customer (time window)
4. Policy exclusion checks
5. Geographic restrictions
6. Fraud pattern triggers
7. Regulatory freeze periods

### AuditHook

**Purpose**: Record all operations for compliance

**Records**:
- Agent invocations (input, output, duration)
- Hook executions (status, decisions)
- Tool calls (type, parameters, results)
- Decision points and reasoning
- Errors and exceptions
- State transitions

**Implementation**:
```python
def record(self, claim_id, agent_name, phase, input_data=None, 
           output_data=None, duration_ms=0, error=None):
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "claim_id": claim_id,
        "agent": agent_name,
        "phase": phase,
        "input": input_data,
        "output": output_data,
        "duration_ms": duration_ms,
        "error": error,
        "actor": get_current_user()
    }
    # Write to immutable audit log
    self.db.audit_logs.insert(event)
```

### OutputValidationHook

**Purpose**: Ensure final decision integrity

**Validations**:
1. Decision enum validation
2. Confidence score range [0.0, 1.0]
3. Payment amount sanity checks
4. Required fields presence
5. Reasoning non-empty
6. Audit trail completeness

---

## Database Schema

### Core Tables

#### insurance_claims
```sql
CREATE TABLE insurance_claims (
    id VARCHAR PRIMARY KEY,
    claim_number VARCHAR UNIQUE NOT NULL,
    
    -- Customer Information
    customer_id VARCHAR NOT NULL,
    customer_name VARCHAR NOT NULL,
    customer_email VARCHAR NOT NULL,
    policy_number VARCHAR NOT NULL,
    
    -- Claim Details
    claim_type VARCHAR NOT NULL,  -- Enum: health, auto, life, property, liability
    incident_date DATE NOT NULL,
    claim_amount FLOAT NOT NULL,
    description TEXT NOT NULL,
    
    -- Assessment Results
    status VARCHAR NOT NULL,  -- Enum: submitted, validating, assessing, approved, rejected, under_review
    assessment_id VARCHAR,
    decision VARCHAR,  -- approved, rejected, under_review
    confidence FLOAT,
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    assessed_at DATETIME,
    assessment_duration_ms INTEGER
);
```

#### assessments
```sql
CREATE TABLE assessments (
    id VARCHAR PRIMARY KEY,
    claim_id VARCHAR NOT NULL,
    
    -- Agent Results
    customer_validation JSON,
    knowledge_retrieval JSON,
    compliance_assessment JSON,
    risk_assessment JSON,
    final_decision JSON,
    
    -- Metadata
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    total_duration_ms INTEGER,
    priority VARCHAR,  -- low, normal, high, urgent
    
    FOREIGN KEY (claim_id) REFERENCES insurance_claims(id)
);
```

#### audit_logs
```sql
CREATE TABLE audit_logs (
    id VARCHAR PRIMARY KEY,
    claim_id VARCHAR NOT NULL,
    timestamp DATETIME NOT NULL,
    
    -- Event Details
    event_type VARCHAR NOT NULL,
    actor VARCHAR NOT NULL,
    phase VARCHAR,
    agent_name VARCHAR,
    
    -- Data
    input_data JSON,
    output_data JSON,
    duration_ms INTEGER,
    error TEXT,
    
    -- Integrity
    previous_hash VARCHAR,
    hash VARCHAR UNIQUE NOT NULL,  -- SHA-256 chain
    
    FOREIGN KEY (claim_id) REFERENCES insurance_claims(id),
    INDEX idx_claim_timestamp (claim_id, timestamp)
);
```

#### regulatory_knowledge
```sql
CREATE TABLE regulatory_knowledge (
    id VARCHAR PRIMARY KEY,
    category VARCHAR NOT NULL,  -- IRDAI, SOX, AML, KYC
    subcategory VARCHAR,
    content TEXT NOT NULL,
    effective_date DATE,
    sunset_date DATE,
    priority INTEGER,
    
    created_at DATETIME,
    updated_at DATETIME
);
```

---

## MCP Server Integration

### RegulatoryKnowledgeMCP

The MCP server provides standardized access to regulatory knowledge:

**Resources**:
```
regulatory://policies/{policy_id}
regulatory://regulations/{regulation_code}
regulatory://precedents/{case_id}
regulatory://fraud_patterns
```

**Tools**:
```
search_policy_terms(claim_type, query) -> List[PolicyTerm]
get_regulations(jurisdiction, category) -> List[Regulation]
check_fraud_patterns(claim_type, attributes) -> List[Pattern]
retrieve_precedent(similarity_threshold) -> List[Precedent]
```

---

## Error Handling

### Error Classification

| Category | HTTP Status | Recovery |
|----------|------------|----------|
| **Validation Error** | 400 | Retry with corrected data |
| **Authentication Error** | 401 | Re-authenticate |
| **Authorization Error** | 403 | Use different credentials |
| **Not Found** | 404 | Verify resource ID |
| **Rate Limit** | 429 | Exponential backoff |
| **Server Error** | 500 | Retry with backoff |
| **Service Unavailable** | 503 | Retry after delay |

### Retry Strategy

```python
async def call_with_retry(func, max_attempts=3, backoff_factor=2):
    for attempt in range(max_attempts):
        try:
            return await func()
        except RetryableError as e:
            if attempt < max_attempts - 1:
                wait_time = backoff_factor ** attempt
                await asyncio.sleep(wait_time)
            else:
                raise
```

---

## Performance Specifications

### Latency Targets

| Operation | Target (p95) | Target (p99) |
|-----------|------------|------------|
| API request validation | 50ms | 100ms |
| Customer validation | 200ms | 500ms |
| Compliance check | 1000ms | 2000ms |
| Risk assessment | 500ms | 1500ms |
| Decision synthesis | 100ms | 200ms |
| **Total Assessment** | **3000ms** | **5000ms** |

### Throughput

- **Concurrent Claims**: 100+
- **Daily Capacity**: 50,000 claims
- **Request Rate**: 10 req/sec per instance

### Resource Usage

- **Memory per Instance**: ~500MB baseline + 50MB per concurrent claim
- **CPU**: 2 cores recommended
- **Database**: SQLite with async connection pool (10 connections)
- **API Tokens**: ~2000-3000 tokens per claim assessment

---

## Monitoring & Observability

### Key Metrics

```
# Latency
assessment_duration_ms
api_response_time_ms
agent_execution_time_ms[agent_name]

# Throughput
claims_submitted_per_minute
assessments_completed_per_minute
api_requests_per_second

# Quality
decision_confidence_score
compliance_violation_rate
fraud_detection_rate

# System Health
database_connection_pool_usage
api_error_rate
authentication_failures
```

### Logging

All operations logged with:
- Timestamp (UTC ISO 8601)
- Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Component (agent name, hook name)
- Message and context
- Execution time
- Error stack traces (if applicable)

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Jun 2026 | Architecture Team | Initial release |

---

## Related Documents

- Architecture Diagram & Overview
- Governance Report
- Testing & Evaluation Report
- Deployment Guide

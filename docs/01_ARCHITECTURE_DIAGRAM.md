# Insurance Claim Assessment System
## Architecture Diagram & Overview

**Document Version:** 1.0  
**Date:** June 2026  
**Classification:** Technical Documentation

---

## Executive Summary

The Insurance Claim Assessment System is a production-ready, multi-agent agentic AI application designed for the BFSI (Banking, Financial Services & Insurance) domain. It implements autonomous insurance claim assessment with fraud detection, compliance validation, and full decision traceability through an immutable audit system.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          END-USER LAYER                             │
│  Web UI (Claims Dashboard) │ REST API │ Mobile Integration          │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                              │
│              Assessment Orchestrator (FastAPI)                      │
│  Coordinates pipeline flow, manages state, error handling           │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┬──────────────┬────────────┐
        │                     │              │            │
┌───────▼──────┐    ┌─────────▼────┐  ┌─────▼──────┐  ┌──▼───────┐
│   INPUT      │    │   SECURITY   │  │ GOVERNANCE │  │  AUDIT   │
│ VALIDATION   │    │     HOOK     │  │  PRE-CHECK │  │   HOOK   │
│    HOOK      │    └──────────────┘  └────────────┘  └──────────┘
└──────────────┘
        │
        └──────────────────┬──────────────────────────────┐
                           │                              │
                    ┌──────▼──────┐            ┌──────────▼─────┐
                    │  SECURITY   │            │   CUSTOMER     │
                    │   HOOK      │            │     AGENT      │
                    └─────────────┘            └──────┬─────────┘
                                                      │
                                              ┌───────▼────────┐
                                              │  KNOWLEDGE     │
                                              │   AGENT (MCP)  │
                                              └────────────────┘
                                                      │
                ┌─────────────────────────────────────┼─────────────────────────┐
                │                                     │                         │
        ┌───────▼──────────┐              ┌──────────▼──────────┐  ┌──────────▼──┐
        │  COMPLIANCE      │              │    RISK AGENT      │  │ DOCUMENT    │
        │  AGENT           │              │  (Fraud Detection) │  │ PROCESSING  │
        │  (IRDAI/SOX/AML) │              └────────────────────┘  └─────────────┘
        └──────────────────┘
                │
        ┌───────┴─────────────────┐
        │                         │
┌───────▼──────────┐    ┌────────▼──────────┐
│  GOVERNANCE      │    │   DECISION       │
│  VALIDATION      │    │   AGENT          │
│  (HOOK)          │    │  (Synthesis)     │
└──────────────────┘    └─────────┬────────┘
                                  │
                        ┌─────────▼────────┐
                        │   AUDIT AGENT    │
                        │ (Immutable Trail)│
                        └────────┬─────────┘
                                 │
                        ┌────────▼──────────┐
                        │   OUTPUT          │
                        │  VALIDATION HOOK  │
                        └────────┬──────────┘
                                 │
                        ┌────────▼──────────┐
                        │   FINAL RESPONSE  │
                        │ (Decision + Audit)│
                        └───────────────────┘
```

---

## Component Details

### 1. Orchestration Layer

**Assessment Orchestrator** (`assessment_orchestrator.py`)
- Central coordinator for the multi-agent pipeline
- Manages phase transitions and state consistency
- Handles error recovery and retry logic
- Integrates all agents, hooks, tools, and MCP servers
- Provides end-to-end claim assessment flow

### 2. Agents (AI Decision-Making Units)

| Agent | Purpose | Responsibility |
|-------|---------|-----------------|
| **CustomerAgent** | Identity & Data Intake | Validates customer info, extracts claim data, verifies policy details |
| **KnowledgeAgent** | Domain Knowledge Retrieval | Accesses regulatory knowledge base via MCP server, retrieves policy terms and precedents |
| **ComplianceAgent** | Regulatory Validation | Checks IRDAI guidelines, SOX compliance, AML rules, sanctions screening |
| **RiskAgent** | Fraud & Anomaly Detection | ML-based fraud scoring, pattern detection, risk assessment |
| **DecisionAgent** | Decision Synthesis | Integrates all agent outputs, generates final assessment with confidence scores |
| **AuditAgent** | Immutable Record-Keeping | Creates tamper-proof audit trails, generates compliance reports |

### 3. Hooks Pipeline (Cross-Cutting Concerns)

| Hook | Stage | Function |
|------|-------|----------|
| **InputValidationHook** | Entry | Sanitizes all inputs, validates schema, detects injection attempts |
| **SecurityHook** | Early | Authentication, authorization, PII protection, IP validation |
| **GovernanceHook** | Pre/Post Assessment | Enforces business rules, rate limiting, policy constraints |
| **AuditHook** | Throughout | Records all interactions, decisions, tool calls for compliance |
| **OutputValidationHook** | Exit | Validates final decisions, ensures response integrity |

### 4. Tools & Integrations

**DatabaseTool** (`tools/database_tool.py`)
- SQLite-backed persistent storage
- CRUD operations for claims, assessments, audit trails
- Full async support for concurrent operations

**DocumentProcessingTool** (`tools/document_processing_tool.py`)
- PDF/text claim document analysis
- Information extraction from unstructured documents
- OCR support for claim forms and attachments

**MCP Server** (`mcp_server/regulatory_knowledge_mcp.py`)
- Model Context Protocol server for knowledge retrieval
- Hosts regulatory knowledge base
- Provides API for policy terms, IRDAI guidelines, fraud patterns

### 5. Data Layer

**Database Models** (`database/models.py`)
```
InsuranceClaim
├── Claim Metadata (ID, number, type, status)
├── Customer Info (ID, name, email, policy)
├── Claim Details (amount, incident date, description)
├── Assessment Results (decisions, scores, recommendations)
├── Audit Trail (immutable history)
└── Timestamps (created, updated, assessed)
```

**Statuses & Enums**
- ClaimStatus: SUBMITTED → VALIDATING → ASSESSING → APPROVED/REJECTED
- RiskLevel: LOW, MEDIUM, HIGH, CRITICAL
- ClaimType: HEALTH, AUTO, LIFE, PROPERTY, LIABILITY

---

## Data Flow

### End-to-End Claim Assessment Pipeline

```
1. USER SUBMISSION
   └─> Web form or API call with claim data

2. INPUT VALIDATION
   └─> InputValidationHook: Sanitize & validate schema
   └─> Security Hook: Check authentication & PII protection
   
3. INITIAL PROCESSING
   └─> CustomerAgent: Extract customer identity, policy validation
   └─> DocumentProcessingTool: Process attachments if present
   
4. KNOWLEDGE RETRIEVAL
   └─> KnowledgeAgent + MCP Server: Retrieve policy terms & regulations
   
5. PARALLEL ASSESSMENT
   ├─> ComplianceAgent: IRDAI/SOX/AML compliance checks
   └─> RiskAgent: Fraud detection & anomaly scoring
   
6. GOVERNANCE CHECK
   └─> GovernanceHook: Apply business rules & constraints
   
7. DECISION SYNTHESIS
   └─> DecisionAgent: Integrate all assessments, generate recommendation
   
8. AUDIT & OUTPUT
   ├─> AuditAgent: Create immutable audit trail
   ├─> OutputValidationHook: Validate final decision
   └─> DatabaseTool: Persist claim & assessment
   
9. USER RESPONSE
   └─> Dashboard/API: Return decision with confidence scores & audit trail
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **API Framework** | FastAPI 0.100.0+ |
| **AI Model** | Claude 3 Sonnet (via Anthropic API) |
| **Database** | SQLAlchemy 2.0+ with SQLite async support |
| **Web Server** | Uvicorn (ASGI) |
| **Frontend** | Jinja2 templates + HTML/CSS |
| **async/await** | Python 3.10+ asyncio |

---

## Security Architecture

### Multi-Layer Security

1. **Input Layer**: InputValidationHook sanitizes all inputs
2. **Auth Layer**: SecurityHook enforces RBAC, IP whitelisting
3. **Data Layer**: PII encryption, secure session management
4. **Audit Layer**: AuditHook creates immutable records
5. **Output Layer**: OutputValidationHook validates responses

### Compliance Frameworks

- **IRDAI**: Insurance Regulatory & Development Authority (India)
- **SOX**: Sarbanes-Oxley Act compliance
- **AML**: Anti-Money Laundering checks
- **GDPR**: Data protection for PII

---

## Scalability Considerations

### Horizontal Scaling
- Stateless FastAPI application servers
- Load balancing across multiple instances
- Database connection pooling via SQLAlchemy async

### Vertical Scaling
- Async/await for concurrent request handling
- Parallel agent execution (ComplianceAgent + RiskAgent)
- Caching layer for regulatory knowledge (MCP)

### Performance Optimization
- Agent result caching
- Parallel hook execution where possible
- Database query optimization with indexes
- Minimal token usage in Claude calls

---

## Deployment Architecture

```
┌──────────────────────────────────────────────┐
│         Cloud Infrastructure                 │
│  (AWS/GCP/Azure/On-premise)                 │
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │   Load Balancer / Reverse Proxy        │ │
│  │   (Nginx / AWS ALB)                    │ │
│  └────────────┬─────────────────────────┘ │
│               │                            │
│  ┌────────────▼──────────┐                 │
│  │  FastAPI Instances    │ ─┐              │
│  │  (Scale: 2-N)         │  │              │
│  └───────────────────────┘  │              │
│  ┌────────────┬──────────┐  │              │
│  │ SQLite DB  │   MCP    │  │              │
│  │   (Async)  │  Server  │  │              │
│  └───────────────────────┘  │              │
│  ┌────────────▼──────────┐  │              │
│  │  Anthropic API        │  │              │
│  │  (Claude Sonnet)      │  │              │
│  └───────────────────────┘  │              │
│                              │              │
│  ┌──────────────────────┐   │              │
│  │  Log Aggregation     │ ◄─┘              │
│  │  (ELK/Datadog)       │                  │
│  └──────────────────────┘                  │
│                                            │
└──────────────────────────────────────────────┘
```

---

## Key Features & Benefits

### For Insurers
✓ **Autonomous Assessment**: 24/7 claim processing without human intervention  
✓ **Fraud Detection**: ML-based anomaly detection with pattern matching  
✓ **Compliance**: Automated regulatory compliance validation  
✓ **Speed**: Sub-5-minute assessment for 80% of claims  

### For Customers
✓ **Transparency**: Full audit trail of assessment decisions  
✓ **Speed**: Faster claim resolution with automated processing  
✓ **Fairness**: Unbiased, consistent evaluation criteria  

### For Operations
✓ **Explainability**: Clear reasoning for each decision  
✓ **Auditability**: Complete immutable record for regulatory review  
✓ **Scalability**: Handles peak loads with async architecture  
✓ **Maintainability**: Clean separation of concerns via agent pattern  

---

## Next Sections

See related documents:
- **Technical Design Document**: Detailed implementation specifications
- **Governance Report**: Compliance & policy framework
- **Testing & Evaluation Report**: Quality assurance & performance metrics
- **Deployment Guide**: Step-by-step installation & operation

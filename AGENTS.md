# Insurance Claim Assessment System — Agent Guide

Production-ready multi-agent AI system for autonomous BFSI insurance claim processing. Six specialized agents collaborate through hooks pipeline to assess claims with fraud detection, compliance validation, and full decision traceability.

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env          # Add ANTHROPIC_API_KEY
python main.py                # Starts FastAPI on http://localhost:8000
```

## System Architecture

**6 Agents + 5 Hooks + MCP Server + 2 Tools**

```
User/API → InputValidationHook → SecurityHook
         → CustomerAgent → KnowledgeAgent (MCP)
         → ComplianceAgent + RiskAgent (parallel)
         → DecisionAgent → AuditAgent
         → GovernanceHook → OutputValidationHook
         → Response
```

See [Architecture Diagram](docs/01_ARCHITECTURE_DIAGRAM.md) for detailed flow.

## Key Components

### Agents (agents/ directory)

| Agent | File | Responsibility |
|-------|------|-----------------|
| **CustomerAgent** | `customer_agent.py` | Validates identity, extracts claim data, interfaces with claimants |
| **KnowledgeAgent** | `knowledge_agent.py` | Retrieves regulatory knowledge, policy terms, precedents via MCP |
| **ComplianceAgent** | `compliance_agent.py` | Validates claims against IRDAI, SOX, AML regulations |
| **RiskAgent** | `risk_agent.py` | Fraud detection, risk scoring, anomaly analysis |
| **DecisionAgent** | `decision_agent.py` | Synthesizes agent outputs, generates final assessment with confidence |
| **AuditAgent** | `audit_agent.py` | Creates immutable audit trails, generates compliance reports |

**Key Pattern**: All agents extend `BaseAgent` and use `AgentResult` dataclass for consistent response format.

### Hooks (hooks/ directory)

Enforce validation, security, governance, and auditability. Execute in sequence:

1. **InputValidationHook** — Sanitize/validate incoming claim data
2. **SecurityHook** — Auth, authorization, PII protection
3. **GovernanceHook** — Business rules, regulatory constraints (mid-assessment)
4. **AuditHook** — Capture all agent interactions (implicit in orchestrator)
5. **OutputValidationHook** — Validate final decisions before delivery

**Pattern**: Hooks raise `ValidationError` on failure; orchestrator handles gracefully.

### MCP Server (mcp_server/ directory)

**RegulatoryKnowledgeMCP** — Provides policy terms, IRDAI guidelines, fraud patterns, compliance rules to KnowledgeAgent.

### Tools (tools/ directory)

- **DatabaseTool** — SQLite + SQLAlchemy for claims CRUD, audit log storage
- **DocumentProcessingTool** — Extract structured data from PDF/text claim documents

## API Endpoints

```
POST   /api/claims/submit           - Submit new claim
GET    /api/claims/{id}             - Get claim status & assessment
POST   /api/claims/{id}/assess      - Trigger assessment pipeline
GET    /api/claims/{id}/audit       - Get immutable audit trail
GET    /api/dashboard               - System dashboard
```

## Critical Conventions

### Environment & Configuration

Set in `.env`:
- `ANTHROPIC_API_KEY` — Required for Claude API calls
- `APP_PORT` — Default 8000
- `LOG_LEVEL` — INFO/DEBUG

### Agent Interaction Pattern

```python
# All agents follow this pattern:
from agents.base_agent import BaseAgent, AgentResult

result = agent.assess(claim_data, context)
# Returns: AgentResult(agent_name, success, data, reasoning, confidence, duration_ms, error)
```

### Database & State

- SQLite-backed claims storage: `insurance_claims.db`
- All claim updates immutable once audited
- PII fields encrypted in storage
- Async SQLAlchemy for concurrent operations

### Pydantic Validation

Request/response models in `main.py`:
- `ClaimSubmission` — Input schema with field validators
- `AssessmentResponse` — Output schema with confidence scores
- All inputs validated before reaching hooks

## Common Tasks

### Adding a New Agent

1. Create `agents/new_agent.py` extending `BaseAgent`
2. Implement `assess(claim_data, context) → AgentResult`
3. Add to `assessment_orchestrator.py` assessment pipeline
4. Update hooks if new validation needed

### Adding a Hook

1. Create `hooks/new_hook.py` with `execute(claim_data, context)` method
2. Add to pipeline in correct sequence (see Hooks section above)
3. Raise `ValidationError` on failure

### Database Changes

Modify `database/setup.py` for schema; uses SQLAlchemy async sessions in `get_db()` dependency.

## Key Files Reference

- [README.md](README.md) — Feature overview
- [CLAUDE.md](CLAUDE.md) — Detailed architecture & security notes
- [Governance Report](docs/03_GOVERNANCE_REPORT.md) — Regulatory compliance framework
- [Testing Report](docs/04_TESTING_EVALUATION_REPORT.md) — Test coverage & validation
- [Deployment Guide](docs/05_DEPLOYMENT_GUIDE.md) — Production deployment
- [Technical Design](docs/02_TECHNICAL_DESIGN_DOCUMENT.md) — Deep design details

## Potential Pitfalls

- **API Key Missing**: Ensure `ANTHROPIC_API_KEY` set in `.env` or environment
- **Database Init**: Database auto-initializes on app startup; check logs for errors
- **Async Context**: All database operations must use async sessions from `get_db()`
- **PII Handling**: Sensitive fields marked in models; encryption applied in DatabaseTool
- **Audit Trail Immutability**: Once audit written, cannot be modified; log decisions carefully

## Testing & Validation

Run comprehensive tests: See [Testing Report](docs/04_TESTING_EVALUATION_REPORT.md).

For quick validation: `python main.py` starts the system; test via `/api/dashboard` or Swagger UI at `/docs`.

---

For detailed API specifications, regulatory compliance mappings, and deployment procedures, see the [docs](docs/) directory.

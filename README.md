# Insurance Claim Assessment System

An autonomous, production-ready multi-agent AI system for BFSI insurance claim processing.

## Features

- **Autonomous Claim Assessment**: End-to-end AI-driven claim evaluation
- **Fraud Detection**: ML-pattern-based anomaly and fraud scoring
- **Compliance Validation**: IRDAI, SOX, AML regulatory checks
- **Decision Traceability**: Full audit trail with explainable AI decisions
- **Real-time Dashboard**: Web UI for claim submission and monitoring

## Quick Start

```bash
git clone <repo>
cd insurance-claim-assessment
pip install -r requirements.txt
cp .env.example .env  # Add ANTHROPIC_API_KEY
python main.py
```

Visit http://localhost:8000

## System Components

| Component | Purpose |
|-----------|---------|
| CustomerAgent | Claim intake and identity validation |
| KnowledgeAgent | Regulatory knowledge retrieval via MCP |
| ComplianceAgent | Regulatory compliance checking |
| RiskAgent | Fraud detection and risk scoring |
| DecisionAgent | Final decision synthesis |
| AuditAgent | Immutable audit trail generation |

## API Endpoints

- `POST /api/claims/submit` — Submit new claim
- `GET /api/claims/{id}` — Get claim status
- `POST /api/claims/{id}/assess` — Trigger assessment
- `GET /api/claims/{id}/audit` — Get audit trail
- `GET /api/dashboard` — System dashboard

## Architecture

```
User/API → InputValidationHook → SecurityHook
         → CustomerAgent → KnowledgeAgent (MCP)
         → ComplianceAgent + RiskAgent (parallel)
         → DecisionAgent → AuditAgent
         → GovernanceHook → OutputValidationHook
         → Response
```

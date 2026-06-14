# Insurance Claim Assessment System — CLAUDE.md

## Project Overview

Production-ready Agentic AI application for BFSI (Banking, Financial Services & Insurance) domain.
Focuses on autonomous insurance claim assessment with fraud detection, compliance validation, and decision traceability.

## Architecture

### Multi-Agent System
- **CustomerAgent**: Validates customer identity, extracts claim data, interfaces with claimants
- **KnowledgeAgent**: Retrieves regulatory knowledge, policy terms, precedents via MCP server
- **ComplianceAgent**: Validates claims against regulatory requirements (IRDAI, SOX, AML)
- **RiskAgent**: Performs risk scoring, fraud detection, anomaly analysis
- **DecisionAgent**: Synthesizes agent outputs, generates final assessment with confidence scores
- **AuditAgent**: Creates immutable audit trails, generates compliance reports

### Hooks Pipeline
1. **InputValidationHook**: Sanitizes and validates all incoming claim data
2. **SecurityHook**: Checks authentication, authorization, PII protection
3. **GovernanceHook**: Enforces business rules and regulatory constraints
4. **AuditHook**: Captures all agent interactions for traceability
5. **OutputValidationHook**: Validates final decisions before delivery

### MCP Server
- **RegulatoryKnowledgeBase**: Insurance policies, IRDAI guidelines, fraud patterns, compliance rules

### Tools/Plugins
- **DatabaseTool**: SQLite-backed claims storage with full CRUD
- **DocumentProcessingTool**: PDF/text claim document analysis

## Running the System

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python main.py

# Access UI at http://localhost:8000
```

## Configuration

Set environment variables in `.env`:
```
ANTHROPIC_API_KEY=your_key_here
APP_PORT=8000
LOG_LEVEL=INFO
```

## Security Notes
- All inputs sanitized via InputValidationHook
- PII fields encrypted in storage
- Audit trails immutable once written
- RBAC enforced on all endpoints

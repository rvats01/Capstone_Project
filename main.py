"""
Insurance Claim Assessment System — Main FastAPI Application
Production-ready BFSI Agentic AI system with multi-agent assessment pipeline.
"""

import os
import logging
import uvicorn
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from database.setup import init_db, get_db
from tools.database_tool import DatabaseTool
from assessment_orchestrator import orchestrator

# Load env
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    logger.info("Starting Insurance Claim Assessment System...")
    await init_db()
    logger.info("Database initialized with regulatory seed data.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Insurance Claim Assessment System",
    description="Production-ready multi-agent AI system for BFSI insurance claim processing",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
jinja_env = Environment(loader=FileSystemLoader("templates"))

def render(template_name: str, **kwargs) -> HTMLResponse:
    tmpl = jinja_env.get_template(template_name)
    return HTMLResponse(content=tmpl.render(**kwargs))


# ─── Request/Response Models ──────────────────────────────────────────────────

class ClaimSubmission(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=200)
    customer_email: str = Field(..., max_length=200)
    customer_id: Optional[str] = Field(default=None)
    policy_number: str = Field(..., min_length=5, max_length=30)
    claim_type: str = Field(..., description="health/auto/life/property/liability")
    incident_date: str = Field(..., description="ISO format date")
    claim_amount: float = Field(..., gt=0, le=10_000_000)
    description: str = Field(..., min_length=10, max_length=5000)

    @field_validator("claim_type")
    @classmethod
    def validate_claim_type(cls, v):
        valid = {"health", "auto", "life", "property", "liability"}
        if v.lower() not in valid:
            raise ValueError(f"claim_type must be one of {valid}")
        return v.lower()


class AssessmentRequest(BaseModel):
    priority: Optional[str] = "normal"


# ─── UI Routes ────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return render("index.html")


@app.get("/submit", response_class=HTMLResponse)
async def submit_form(request: Request):
    return render("submit_claim.html")


@app.get("/claims", response_class=HTMLResponse)
async def claims_list(request: Request):
    return render("claims_list.html")


@app.get("/claims/{claim_id}/detail", response_class=HTMLResponse)
async def claim_detail(request: Request, claim_id: str):
    return render("claim_detail.html", claim_id=claim_id)


# ─── API Routes ───────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "Insurance Claim Assessment System",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": ["CustomerAgent", "KnowledgeAgent", "ComplianceAgent", "RiskAgent", "DecisionAgent", "AuditAgent"],
        "hooks": ["InputValidationHook", "SecurityHook", "GovernanceHook", "AuditHook", "OutputValidationHook"],
        "mcp_server": "RegulatoryKnowledgeMCP",
        "tools": ["DatabaseTool", "DocumentProcessingTool"]
    }


@app.post("/api/claims/submit")
async def submit_claim(
    claim: ClaimSubmission,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Submit a new insurance claim."""
    client_ip = request.client.host if request.client else "unknown"
    db_tool = DatabaseTool(db)

    try:
        claim_data = claim.model_dump()
        # Create claim record
        new_claim = await db_tool.create_claim(claim_data)

        await db_tool.update_claim_status(new_claim.id, "submitted")

        return {
            "success": True,
            "claim_id": new_claim.id,
            "claim_number": new_claim.claim_number,
            "status": "submitted",
            "message": "Claim submitted successfully. Trigger assessment to begin processing.",
            "submitted_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Submit claim error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/claims/{claim_id}/assess")
async def assess_claim(
    claim_id: str,
    request: Request,
    assessment_req: Optional[AssessmentRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    """Trigger multi-agent claim assessment."""
    client_ip = request.client.host if request.client else "unknown"
    db_tool = DatabaseTool(db)

    # Get claim from DB
    claim = await db_tool.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")

    if claim.status in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail=f"Claim already assessed: {claim.status}")

    # Update status to assessing
    await db_tool.update_claim_status(claim_id, "assessing")

    # Build claim data dict
    claim_data = {
        "customer_id": claim.customer_id,
        "customer_name": claim.customer_name,
        "customer_email": claim.customer_email,
        "policy_number": claim.policy_number,
        "claim_type": claim.claim_type,
        "incident_date": claim.incident_date.isoformat(),
        "claim_amount": claim.claim_amount,
        "description": claim.description
    }

    try:
        # Run full assessment pipeline
        result = await orchestrator.assess_claim(claim_id, claim_data, client_ip)

        # Save results to DB
        if result.get("status") == "assessed":
            await db_tool.save_assessment_results(
                claim_id,
                result.get("customer_assessment", {}),
                result.get("compliance_assessment", {}),
                result.get("risk_assessment", {}),
                {
                    "decision": result.get("decision", "under_review"),
                    "decision_reason": result.get("decision_reason", ""),
                    "approved_amount": result.get("approved_amount", 0),
                    "final_score": result.get("final_score", 0),
                    "score_breakdown": result.get("score_breakdown", {}),
                    "key_factors": result.get("agent_reasoning", {})
                }
            )

            # Persist audit logs
            for audit_entry in orchestrator.get_audit_trail(claim_id):
                try:
                    await db_tool.save_audit_log(audit_entry)
                except Exception:
                    pass  # Don't fail assessment if audit log save fails

        return result

    except Exception as e:
        logger.error(f"Assessment error for {claim_id}: {e}", exc_info=True)
        await db_tool.update_claim_status(claim_id, "under_review")
        raise HTTPException(status_code=500, detail=f"Assessment error: {str(e)}")


@app.get("/api/claims")
async def list_claims(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List all claims."""
    db_tool = DatabaseTool(db)
    claims = await db_tool.get_all_claims(limit=limit, offset=offset)

    return {
        "claims": [
            {
                "id": c.id,
                "claim_number": c.claim_number,
                "customer_name": c.customer_name,
                "claim_type": c.claim_type,
                "claim_amount": c.claim_amount,
                "approved_amount": c.approved_amount,
                "status": c.status,
                "risk_level": c.risk_level,
                "fraud_score": round(c.fraud_score or 0, 3),
                "final_score": round(c.final_score or 0, 3),
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "assessed_at": c.assessed_at.isoformat() if c.assessed_at else None
            }
            for c in claims
        ],
        "count": len(claims),
        "limit": limit,
        "offset": offset
    }


@app.get("/api/claims/{claim_id}")
async def get_claim(claim_id: str, db: AsyncSession = Depends(get_db)):
    """Get claim details including assessment results."""
    db_tool = DatabaseTool(db)
    claim = await db_tool.get_claim(claim_id)

    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    return {
        "id": claim.id,
        "claim_number": claim.claim_number,
        "customer_id": claim.customer_id,
        "customer_name": claim.customer_name,
        "customer_email": claim.customer_email,
        "policy_number": claim.policy_number,
        "claim_type": claim.claim_type,
        "incident_date": claim.incident_date.isoformat() if claim.incident_date else None,
        "claim_amount": claim.claim_amount,
        "approved_amount": claim.approved_amount,
        "status": claim.status,
        "risk_level": claim.risk_level,
        "fraud_score": round(claim.fraud_score or 0, 3),
        "compliance_score": round(claim.compliance_score or 0, 3),
        "risk_score": round(claim.risk_score or 0, 3),
        "final_score": round(claim.final_score or 0, 3),
        "decision": claim.decision,
        "decision_reason": claim.decision_reason,
        "agent_reasoning": claim.agent_reasoning or {},
        "compliance_flags": claim.compliance_flags or [],
        "fraud_indicators": claim.fraud_indicators or [],
        "created_at": claim.created_at.isoformat() if claim.created_at else None,
        "assessed_at": claim.assessed_at.isoformat() if claim.assessed_at else None,
        "description": claim.description
    }


@app.get("/api/claims/{claim_id}/audit")
async def get_audit_trail(claim_id: str, db: AsyncSession = Depends(get_db)):
    """Get complete audit trail for a claim."""
    db_tool = DatabaseTool(db)

    # Try DB first, fall back to in-memory
    db_logs = await db_tool.get_audit_trail(claim_id)
    memory_logs = orchestrator.get_audit_trail(claim_id)

    db_entries = [
        {
            "id": str(log.id),
            "agent_name": log.agent_name,
            "action": log.action,
            "hook_applied": log.hook_applied,
            "compliance_check": log.compliance_check,
            "passed": log.passed,
            "audit_hash": log.audit_hash,
            "duration_ms": log.duration_ms,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "source": "database"
        }
        for log in db_logs
    ]

    # Merge with in-memory (avoid duplicates by timestamp)
    db_timestamps = {e["timestamp"] for e in db_entries}
    memory_entries = [
        {**e, "source": "memory"}
        for e in memory_logs
        if e.get("timestamp") not in db_timestamps
    ]

    all_entries = db_entries + memory_entries
    all_entries.sort(key=lambda x: x.get("timestamp", ""))

    return {
        "claim_id": claim_id,
        "total_entries": len(all_entries),
        "audit_trail": all_entries
    }


@app.get("/api/dashboard/stats")
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics."""
    db_tool = DatabaseTool(db)
    stats = await db_tool.get_stats()

    stats["approval_rate"] = (
        round(stats["approved"] / stats["total_claims"] * 100, 1)
        if stats["total_claims"] > 0 else 0
    )
    stats["fraud_rate"] = (
        round(stats["fraud_suspected"] / stats["total_claims"] * 100, 1)
        if stats["total_claims"] > 0 else 0
    )
    stats["system_health"] = "operational"
    stats["agents_active"] = 6
    stats["mcp_status"] = "connected"

    return stats


@app.get("/api/mcp/regulations")
async def get_regulations(claim_type: Optional[str] = None, regulation_type: str = "ALL"):
    """Query the MCP regulatory knowledge base directly."""
    from mcp_server.regulatory_knowledge_mcp import mcp_server
    results = mcp_server.query_regulations(regulation_type, claim_type=claim_type)
    return {"regulations": results, "count": len(results)}


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )

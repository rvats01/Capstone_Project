"""DatabaseTool: SQLite-backed claims storage with full CRUD operations."""

import logging
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from database.models import InsuranceClaim, AuditLog, ClaimStatus

logger = logging.getLogger(__name__)


class DatabaseTool:
    """Manages all database operations for the claims system."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_claim(self, claim_data: dict) -> InsuranceClaim:
        """Create a new claim record."""
        claim_number = f"CLM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        claim = InsuranceClaim(
            id=str(uuid.uuid4()),
            claim_number=claim_number,
            customer_id=claim_data.get("customer_id", str(uuid.uuid4())[:8]),
            customer_name=claim_data["customer_name"],
            customer_email=claim_data["customer_email"],
            policy_number=claim_data["policy_number"],
            claim_type=claim_data["claim_type"],
            incident_date=datetime.fromisoformat(str(claim_data["incident_date"]).replace("Z", "")),
            claim_amount=float(claim_data["claim_amount"]),
            description=claim_data["description"],
            status=ClaimStatus.SUBMITTED
        )

        self.db.add(claim)
        await self.db.commit()
        await self.db.refresh(claim)
        logger.info(f"[DatabaseTool] Created claim {claim.claim_number}")
        return claim

    async def get_claim(self, claim_id: str) -> InsuranceClaim:
        """Get claim by ID."""
        result = await self.db.execute(
            select(InsuranceClaim).where(InsuranceClaim.id == claim_id)
        )
        return result.scalar_one_or_none()

    async def get_all_claims(self, limit: int = 50, offset: int = 0) -> list:
        """Get all claims paginated."""
        result = await self.db.execute(
            select(InsuranceClaim)
            .order_by(InsuranceClaim.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def update_claim_status(self, claim_id: str, status: str) -> bool:
        """Update claim status."""
        await self.db.execute(
            update(InsuranceClaim)
            .where(InsuranceClaim.id == claim_id)
            .values(status=status, updated_at=datetime.utcnow())
        )
        await self.db.commit()
        return True

    async def save_assessment_results(
        self,
        claim_id: str,
        customer_result: dict,
        compliance_result: dict,
        risk_result: dict,
        decision_result: dict
    ) -> bool:
        """Save full assessment results to claim."""
        fraud_score = float(risk_result.get("fraud_score", 0))
        compliance_score = float(compliance_result.get("compliance_score", 0))
        risk_score = float(risk_result.get("risk_score", 0))

        # Weighted final score
        final_score = (
            compliance_score * 0.35 +
            (1 - fraud_score) * 0.35 +
            float(customer_result.get("identity_confidence", 0.5)) * 0.15 +
            (1 - risk_score) * 0.15
        )

        decision = decision_result.get("decision", "under_review")
        status_map = {
            "approved": ClaimStatus.APPROVED,
            "rejected": ClaimStatus.REJECTED,
            "referred": ClaimStatus.UNDER_REVIEW,
            "partial_approval": ClaimStatus.APPROVED,
            "fraud_suspected": ClaimStatus.FRAUD_SUSPECTED,
            "under_review": ClaimStatus.UNDER_REVIEW
        }

        await self.db.execute(
            update(InsuranceClaim)
            .where(InsuranceClaim.id == claim_id)
            .values(
                status=status_map.get(decision, ClaimStatus.UNDER_REVIEW),
                fraud_score=fraud_score,
                compliance_score=compliance_score,
                risk_score=risk_score,
                final_score=final_score,
                decision=decision,
                decision_reason=decision_result.get("decision_reason", ""),
                approved_amount=float(decision_result.get("approved_amount", 0)),
                agent_reasoning={
                    "customer": customer_result.get("reasoning", ""),
                    "compliance": compliance_result.get("reasoning", ""),
                    "risk": risk_result.get("reasoning", ""),
                    "decision": decision_result.get("decision_reason", ""),
                    "score_breakdown": decision_result.get("score_breakdown", {}),
                    "key_factors": decision_result.get("key_factors", {})
                },
                compliance_flags=compliance_result.get("blocking_violations", []),
                fraud_indicators=[
                    f.get("indicator", "") for f in risk_result.get("fraud_indicators", [])
                ],
                assessed_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        return True

    async def save_audit_log(self, audit_entry: dict) -> AuditLog:
        """Save an audit log entry."""
        log = AuditLog(
            claim_id=audit_entry.get("claim_id", ""),
            agent_name=audit_entry.get("agent_name", "SYSTEM"),
            action=audit_entry.get("action", ""),
            input_data=audit_entry.get("input_summary"),
            output_data=audit_entry.get("output_summary"),
            hook_applied=audit_entry.get("hook_applied"),
            compliance_check=audit_entry.get("compliance_check"),
            passed=audit_entry.get("passed", True),
            audit_hash=audit_entry.get("audit_hash", ""),
            duration_ms=audit_entry.get("duration_ms", 0)
        )
        self.db.add(log)
        await self.db.commit()
        return log

    async def get_audit_trail(self, claim_id: str) -> list:
        """Get full audit trail for a claim."""
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.claim_id == claim_id)
            .order_by(AuditLog.timestamp)
        )
        return result.scalars().all()

    async def get_stats(self) -> dict:
        """Get dashboard statistics."""
        total = await self.db.scalar(select(func.count(InsuranceClaim.id)))
        approved = await self.db.scalar(select(func.count(InsuranceClaim.id)).where(InsuranceClaim.status == "approved"))
        rejected = await self.db.scalar(select(func.count(InsuranceClaim.id)).where(InsuranceClaim.status == "rejected"))
        fraud = await self.db.scalar(select(func.count(InsuranceClaim.id)).where(InsuranceClaim.status == "fraud_suspected"))
        pending = await self.db.scalar(select(func.count(InsuranceClaim.id)).where(InsuranceClaim.status.in_(["submitted", "validating", "assessing"])))
        avg_amount = await self.db.scalar(select(func.avg(InsuranceClaim.claim_amount)))
        avg_fraud = await self.db.scalar(select(func.avg(InsuranceClaim.fraud_score)))

        return {
            "total_claims": total or 0,
            "approved": approved or 0,
            "rejected": rejected or 0,
            "fraud_suspected": fraud or 0,
            "pending": pending or 0,
            "under_review": max(0, (total or 0) - (approved or 0) - (rejected or 0) - (fraud or 0) - (pending or 0)),
            "avg_claim_amount": round(float(avg_amount or 0), 2),
            "avg_fraud_score": round(float(avg_fraud or 0), 3)
        }

"""Database models for Insurance Claim Assessment System."""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum
import uuid

Base = declarative_base()


class ClaimStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    VALIDATING = "validating"
    ASSESSING = "assessing"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"
    FRAUD_SUSPECTED = "fraud_suspected"


class ClaimType(str, enum.Enum):
    HEALTH = "health"
    AUTO = "auto"
    LIFE = "life"
    PROPERTY = "property"
    LIABILITY = "liability"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_number = Column(String, unique=True, nullable=False)

    # Customer info
    customer_id = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    policy_number = Column(String, nullable=False)

    # Claim details
    claim_type = Column(String, nullable=False)
    incident_date = Column(DateTime, nullable=False)
    claim_amount = Column(Float, nullable=False)
    description = Column(Text, nullable=False)

    # Status tracking
    status = Column(String, default=ClaimStatus.SUBMITTED)
    risk_level = Column(String, default=RiskLevel.MEDIUM)

    # Assessment results
    fraud_score = Column(Float, default=0.0)
    compliance_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)

    # Decision
    decision = Column(String, nullable=True)
    decision_reason = Column(Text, nullable=True)
    approved_amount = Column(Float, nullable=True)

    # Metadata
    agent_reasoning = Column(JSON, nullable=True)
    compliance_flags = Column(JSON, nullable=True)
    fraud_indicators = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    assessed_at = Column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id = Column(String, nullable=False)

    # Audit details
    agent_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)

    # Governance
    hook_applied = Column(String, nullable=True)
    compliance_check = Column(String, nullable=True)
    passed = Column(Boolean, default=True)

    # Integrity
    audit_hash = Column(String, nullable=True)
    timestamp = Column(DateTime, default=func.now())
    duration_ms = Column(Integer, default=0)


class RegulationCache(Base):
    __tablename__ = "regulation_cache"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    regulation_type = Column(String, nullable=False)
    rule_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    severity = Column(String, default="medium")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

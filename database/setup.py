"""Database setup and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import insert
from database.models import Base, RegulationCache
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./insurance_claims.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_regulations()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def seed_regulations():
    """Seed regulatory knowledge base with IRDAI/SOX/AML rules."""
    regulations = [
        {
            "rule_id": "IRDAI-001",
            "regulation_type": "IRDAI",
            "title": "Claim Settlement Time Limit",
            "content": "All insurance claims must be settled within 30 days of receiving all required documents. Rejection must be communicated within 30 days with valid reasons.",
            "category": "settlement",
            "severity": "high"
        },
        {
            "rule_id": "IRDAI-002",
            "regulation_type": "IRDAI",
            "title": "Anti-Fraud Requirements",
            "content": "Insurers must implement fraud detection systems. Claims with fraud indicators above 0.7 must be referred to investigation unit. Fraudulent claims must be reported to IB.",
            "category": "fraud",
            "severity": "critical"
        },
        {
            "rule_id": "IRDAI-003",
            "regulation_type": "IRDAI",
            "title": "Policy Document Verification",
            "content": "Valid policy must be active at time of incident. Premium must be paid up to date. Waiting period must have elapsed for health claims.",
            "category": "verification",
            "severity": "high"
        },
        {
            "rule_id": "IRDAI-004",
            "regulation_type": "IRDAI",
            "title": "Claim Amount Limits",
            "content": "Claim amount cannot exceed policy sum insured. Sub-limits apply per category. Deductibles must be applied before settlement.",
            "category": "financial",
            "severity": "high"
        },
        {
            "rule_id": "SOX-001",
            "regulation_type": "SOX",
            "title": "Financial Reporting Integrity",
            "content": "All claim payments above $10,000 must have dual approval. Large settlements require CFO sign-off. All financial decisions must be auditable.",
            "category": "financial",
            "severity": "high"
        },
        {
            "rule_id": "SOX-002",
            "regulation_type": "SOX",
            "title": "Internal Controls",
            "content": "Segregation of duties required for claim approval. No single agent can both assess and approve claims. Audit trails must be immutable.",
            "category": "controls",
            "severity": "critical"
        },
        {
            "rule_id": "AML-001",
            "regulation_type": "AML",
            "title": "Suspicious Transaction Monitoring",
            "content": "Claims that may be used to launder money must be flagged. Multiple small claims from same customer within 30 days is suspicious. Large cash payouts require KYC verification.",
            "category": "aml",
            "severity": "critical"
        },
        {
            "rule_id": "AML-002",
            "regulation_type": "AML",
            "title": "KYC Requirements",
            "content": "Customer identity must be verified for all claims above $5,000. Politically Exposed Persons (PEPs) require enhanced due diligence. Beneficial ownership must be established.",
            "category": "kyc",
            "severity": "high"
        },
        {
            "rule_id": "FRAUD-001",
            "regulation_type": "FRAUD_PATTERN",
            "title": "Application Fraud Indicators",
            "content": "Inflated claim amounts 20% above market value. Multiple claims within 6 months. Claim filed immediately after policy purchase. Inconsistent statement details.",
            "category": "fraud_pattern",
            "severity": "high"
        },
        {
            "rule_id": "FRAUD-002",
            "regulation_type": "FRAUD_PATTERN",
            "title": "Medical Claim Fraud Patterns",
            "content": "Bills from non-empaneled hospitals. Duplicate bills for same treatment. Treatment dates inconsistent with hospital records. Procedure codes not matching diagnosis.",
            "category": "fraud_pattern",
            "severity": "critical"
        },
        {
            "rule_id": "COMPLIANCE-001",
            "regulation_type": "COMPLIANCE",
            "title": "Data Privacy Requirements",
            "content": "Customer PII must be encrypted at rest and in transit. Access to claim data must be role-based. Data retention policy: 7 years for settled claims. Right to explanation for AI decisions.",
            "category": "privacy",
            "severity": "high"
        }
    ]

    async with AsyncSessionLocal() as session:
        from database.models import RegulationCache as RC
        for reg in regulations:
            try:
                existing = await session.get(RC, reg["rule_id"])
                if not existing:
                    obj = RC(**reg)
                    session.add(obj)
                    await session.flush()
            except Exception:
                await session.rollback()
        try:
            await session.commit()
        except Exception:
            await session.rollback()

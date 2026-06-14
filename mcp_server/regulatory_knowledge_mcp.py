"""
MCP Server: Regulatory Knowledge Base for Insurance
Provides structured access to IRDAI, SOX, AML regulations and fraud patterns.
"""

import json
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

# Tool definitions for Claude's tool_use API (MCP-style)
REGULATORY_MCP_TOOLS = [
    {
        "name": "query_regulations",
        "description": "Query the regulatory knowledge base for applicable insurance regulations, IRDAI guidelines, SOX requirements, and AML rules",
        "input_schema": {
            "type": "object",
            "properties": {
                "regulation_type": {
                    "type": "string",
                    "enum": ["IRDAI", "SOX", "AML", "FRAUD_PATTERN", "COMPLIANCE", "ALL"],
                    "description": "Type of regulation to query"
                },
                "category": {
                    "type": "string",
                    "description": "Specific category (e.g., 'fraud', 'settlement', 'kyc', 'financial')"
                },
                "claim_type": {
                    "type": "string",
                    "enum": ["health", "auto", "life", "property", "liability"],
                    "description": "Insurance claim type for contextual filtering"
                }
            },
            "required": ["regulation_type"]
        }
    },
    {
        "name": "get_fraud_patterns",
        "description": "Retrieve known fraud patterns and indicators for a specific claim type",
        "input_schema": {
            "type": "object",
            "properties": {
                "claim_type": {
                    "type": "string",
                    "description": "Type of insurance claim"
                },
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Minimum severity level to return"
                }
            },
            "required": ["claim_type"]
        }
    },
    {
        "name": "get_policy_limits",
        "description": "Get standard policy limits, deductibles, and coverage rules for claim type",
        "input_schema": {
            "type": "object",
            "properties": {
                "claim_type": {
                    "type": "string",
                    "description": "Insurance claim type"
                },
                "claim_amount": {
                    "type": "number",
                    "description": "Claimed amount for limit checking"
                }
            },
            "required": ["claim_type", "claim_amount"]
        }
    }
]


class RegulatoryKnowledgeMCP:
    """
    MCP Server that provides regulatory knowledge to agents.
    Acts as an authoritative source for insurance regulations.
    """

    def __init__(self):
        self.name = "RegulatoryKnowledgeMCP"
        self._knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> dict:
        """Load in-memory regulatory knowledge base."""
        return {
            "IRDAI": [
                {
                    "rule_id": "IRDAI-001",
                    "title": "Claim Settlement Timeline",
                    "content": "Claims must be settled within 30 days. Rejection must be communicated within 30 days with valid reasons per IRDAI Circular 2015/Insurance/Claim Settlement.",
                    "category": "settlement",
                    "severity": "high",
                    "applies_to": ["health", "auto", "life", "property", "liability"]
                },
                {
                    "rule_id": "IRDAI-002",
                    "title": "Anti-Fraud System Requirement",
                    "content": "Insurers must maintain fraud detection systems. Claims with fraud score >0.7 must be investigated. Fraudulent claims reported to Insurance Bureau.",
                    "category": "fraud",
                    "severity": "critical",
                    "applies_to": ["health", "auto", "life", "property", "liability"]
                },
                {
                    "rule_id": "IRDAI-003",
                    "title": "Policy Document Verification",
                    "content": "Valid policy must be active at incident time. Premium paid up-to-date. Waiting periods elapsed (90 days for health, 30 days for property).",
                    "category": "verification",
                    "severity": "high",
                    "applies_to": ["health", "property"]
                },
                {
                    "rule_id": "IRDAI-004",
                    "title": "Claim Amount Limits",
                    "content": "Claim amount cannot exceed policy sum insured. Sub-limits apply per category. Deductibles applied before settlement. Co-payment rules for health.",
                    "category": "financial",
                    "severity": "high",
                    "applies_to": ["health", "auto", "life", "property", "liability"]
                },
                {
                    "rule_id": "IRDAI-005",
                    "title": "Health Claim Pre-Authorization",
                    "content": "Planned hospitalizations require pre-authorization within 48 hours. Emergency admissions must be intimated within 24 hours of admission.",
                    "category": "health",
                    "severity": "medium",
                    "applies_to": ["health"]
                }
            ],
            "SOX": [
                {
                    "rule_id": "SOX-001",
                    "title": "Large Payment Approval",
                    "content": "Claim payments above $10,000 require dual approval. Above $100,000 requires CFO sign-off. All large settlements must be auditable.",
                    "category": "financial",
                    "severity": "high",
                    "applies_to": ["health", "auto", "life", "property", "liability"]
                },
                {
                    "rule_id": "SOX-002",
                    "title": "Segregation of Duties",
                    "content": "Assessment and approval roles must be separated. No single person/agent can both assess and approve. Audit trails must be immutable and tamper-evident.",
                    "category": "controls",
                    "severity": "critical",
                    "applies_to": ["health", "auto", "life", "property", "liability"]
                }
            ],
            "AML": [
                {
                    "rule_id": "AML-001",
                    "title": "Suspicious Transaction Monitoring",
                    "content": "Claims potentially used for money laundering must be flagged. Multiple small claims from same customer within 30 days is suspicious. Large cash payouts require KYC.",
                    "category": "aml",
                    "severity": "critical",
                    "applies_to": ["health", "auto", "life", "property", "liability"]
                },
                {
                    "rule_id": "AML-002",
                    "title": "KYC Requirements",
                    "content": "Identity verified for claims above $5,000. PEPs require enhanced due diligence. Beneficial ownership must be established for corporate claimants.",
                    "category": "kyc",
                    "severity": "high",
                    "applies_to": ["health", "auto", "life", "property", "liability"]
                }
            ],
            "FRAUD_PATTERN": [
                {
                    "rule_id": "FRAUD-001",
                    "title": "Application Fraud",
                    "content": "Inflated amounts 20%+ above market. Multiple claims within 6 months. Claim filed immediately after policy purchase. Inconsistent statements.",
                    "category": "fraud_pattern",
                    "severity": "high",
                    "applies_to": ["health", "auto", "life", "property", "liability"]
                },
                {
                    "rule_id": "FRAUD-002",
                    "title": "Medical Claim Fraud",
                    "content": "Bills from non-empaneled hospitals. Duplicate bills for same treatment. Treatment dates inconsistent with records. Procedure codes not matching diagnosis.",
                    "category": "fraud_pattern",
                    "severity": "critical",
                    "applies_to": ["health"]
                },
                {
                    "rule_id": "FRAUD-003",
                    "title": "Auto Insurance Fraud",
                    "content": "Staged accidents in high-fraud zones. Phantom injuries. Vehicle damage inconsistent with accident description. Multiple claims on same vehicle.",
                    "category": "fraud_pattern",
                    "severity": "high",
                    "applies_to": ["auto"]
                },
                {
                    "rule_id": "FRAUD-004",
                    "title": "Property Insurance Fraud",
                    "content": "Claim filed shortly after increased coverage. Contents claimed exceed reasonable value. Fire/damage suspiciously total. No police report for theft claims.",
                    "category": "fraud_pattern",
                    "severity": "critical",
                    "applies_to": ["property"]
                }
            ],
            "COMPLIANCE": [
                {
                    "rule_id": "COMP-001",
                    "title": "Data Privacy",
                    "content": "Customer PII encrypted at rest and in transit. RBAC access to claim data. 7-year retention for settled claims. Right to explanation for AI decisions.",
                    "category": "privacy",
                    "severity": "high",
                    "applies_to": ["health", "auto", "life", "property", "liability"]
                }
            ]
        }

    def query_regulations(self, regulation_type: str, category: str = None, claim_type: str = None) -> list:
        """Query regulations by type, category, and claim type."""
        if regulation_type == "ALL":
            all_regs = []
            for regs in self._knowledge_base.values():
                all_regs.extend(regs)
            results = all_regs
        else:
            results = self._knowledge_base.get(regulation_type, [])

        # Filter by claim type
        if claim_type:
            results = [r for r in results if claim_type in r.get("applies_to", [])]

        # Filter by category
        if category:
            results = [r for r in results if r.get("category", "").lower() == category.lower()]

        return results

    def get_fraud_patterns(self, claim_type: str, severity: str = "medium") -> list:
        """Get fraud patterns applicable to claim type."""
        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        min_severity = severity_order.get(severity, 1)

        patterns = self._knowledge_base.get("FRAUD_PATTERN", [])
        return [
            p for p in patterns
            if claim_type in p.get("applies_to", [])
            and severity_order.get(p.get("severity", "low"), 0) >= min_severity
        ]

    def get_policy_limits(self, claim_type: str, claim_amount: float) -> dict:
        """Get policy limits and flags for claim type/amount."""
        limits = {
            "health": {"max_claim": 500_000, "deductible": 500, "co_payment": 0.1, "waiting_period_days": 90},
            "auto": {"max_claim": 100_000, "deductible": 1_000, "co_payment": 0, "waiting_period_days": 0},
            "life": {"max_claim": 1_000_000, "deductible": 0, "co_payment": 0, "waiting_period_days": 365},
            "property": {"max_claim": 500_000, "deductible": 2_500, "co_payment": 0, "waiting_period_days": 30},
            "liability": {"max_claim": 300_000, "deductible": 1_000, "co_payment": 0, "waiting_period_days": 0}
        }

        policy = limits.get(claim_type, limits["property"])
        exceeds_limit = claim_amount > policy["max_claim"]

        return {
            "claim_type": claim_type,
            "requested_amount": claim_amount,
            "max_allowed": policy["max_claim"],
            "deductible": policy["deductible"],
            "co_payment_pct": policy["co_payment"],
            "waiting_period_days": policy["waiting_period_days"],
            "exceeds_limit": exceeds_limit,
            "payable_amount": min(claim_amount, policy["max_claim"]) * (1 - policy["co_payment"]) - policy["deductible"],
            "flags": ["EXCEEDS_POLICY_LIMIT"] if exceeds_limit else []
        }

    def process_tool_call(self, tool_name: str, tool_input: dict) -> dict:
        """Process an MCP tool call and return result."""
        if tool_name == "query_regulations":
            return {
                "result": self.query_regulations(
                    regulation_type=tool_input.get("regulation_type", "ALL"),
                    category=tool_input.get("category"),
                    claim_type=tool_input.get("claim_type")
                )
            }
        elif tool_name == "get_fraud_patterns":
            return {
                "result": self.get_fraud_patterns(
                    claim_type=tool_input.get("claim_type", "auto"),
                    severity=tool_input.get("severity", "medium")
                )
            }
        elif tool_name == "get_policy_limits":
            return {
                "result": self.get_policy_limits(
                    claim_type=tool_input.get("claim_type", "auto"),
                    claim_amount=float(tool_input.get("claim_amount", 0))
                )
            }
        else:
            return {"error": f"Unknown tool: {tool_name}"}


# Global MCP instance
mcp_server = RegulatoryKnowledgeMCP()

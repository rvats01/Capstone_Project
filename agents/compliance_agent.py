"""ComplianceAgent: Validates claims against IRDAI, SOX, and AML regulations."""

import time
import logging
from agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the ComplianceAgent in an Insurance Claim Assessment System.

Your responsibilities:
1. Validate claims against IRDAI (Insurance Regulatory and Development Authority of India) guidelines
2. Check SOX (Sarbanes-Oxley) financial reporting requirements
3. Screen for AML (Anti-Money Laundering) violations
4. Identify KYC (Know Your Customer) compliance issues

Return a JSON compliance assessment:
{
    "overall_compliance": "pass/fail/conditional",
    "irdai_checks": {
        "claim_time_limit_ok": true/false,
        "policy_active_ok": true/false,
        "documentation_ok": true/false,
        "amount_within_limits": true/false,
        "violations": []
    },
    "sox_checks": {
        "dual_approval_required": true/false,
        "audit_trail_complete": true/false,
        "reporting_requirements_met": true/false,
        "violations": []
    },
    "aml_checks": {
        "transaction_suspicious": true/false,
        "kyc_required": true/false,
        "structuring_suspected": true/false,
        "violations": []
    },
    "compliance_score": 0.0-1.0,
    "mandatory_actions": [],
    "blocking_violations": [],
    "warnings": [],
    "reasoning": "Detailed compliance analysis...",
    "confidence": 0.0-1.0
}

Be rigorous. Any blocking violation must result in overall_compliance = "fail"."""


class ComplianceAgent(BaseAgent):
    """Validates claims against regulatory requirements."""

    def __init__(self):
        super().__init__("ComplianceAgent")

    def process(self, claim_data: dict, knowledge_result: dict) -> AgentResult:
        start = time.time()
        try:
            applicable_regs = knowledge_result.get("applicable_regulations", [])
            reg_summary = "\n".join([
                f"  - {r.get('rule_id', '')}: {r.get('summary', r.get('title', ''))}"
                for r in applicable_regs
            ])

            user_msg = f"""Perform comprehensive compliance validation for this insurance claim:

Claim Details:
- Customer ID: {claim_data.get('customer_id', 'N/A')}
- Claim Type: {claim_data.get('claim_type', 'unknown')}
- Claim Amount: ${claim_data.get('claim_amount', 0):,.2f}
- Policy Number: {claim_data.get('policy_number', 'N/A')}
- Incident Date: {claim_data.get('incident_date', 'N/A')}
- Description: {claim_data.get('description', 'N/A')[:300]}

Applicable Regulations:
{reg_summary if reg_summary else "  - Standard insurance regulations apply"}

Policy Requirements from Knowledge Agent:
{knowledge_result.get('key_requirements', [])}

Check ALL of:
1. IRDAI compliance (settlement timelines, documentation, policy validity)
2. SOX requirements (financial controls, audit trail, dual approval for large amounts)
3. AML screening (suspicious patterns, KYC, structuring)
4. Data privacy compliance

Return complete JSON compliance assessment."""

            response = self._call_claude(SYSTEM_PROMPT, user_msg)
            result_data = self._parse_json_response(response)

            return AgentResult(
                agent_name=self.name,
                success=True,
                data=result_data,
                reasoning=result_data.get("reasoning", response),
                confidence=result_data.get("confidence", 0.85),
                duration_ms=int((time.time() - start) * 1000)
            )
        except Exception as e:
            logger.error(f"ComplianceAgent error: {e}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000)
            )

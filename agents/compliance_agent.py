"""ComplianceAgent: Validates claims against IRDAI, SOX, and AML regulations."""

import time
import logging
from agents.base_agent import BaseAgent, AgentResult
from skills.compliance_validation import ComplianceValidator

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
        self.compliance_validator = ComplianceValidator()

    def process(self, claim_data: dict, knowledge_result: dict) -> AgentResult:
        start = time.time()
        try:
            # Use ComplianceValidator skill for structured compliance checks
            customer_data = {
                "customer_id": claim_data.get("customer_id", ""),
                "kyc_completed": claim_data.get("kyc_completed", False),
                "aml_screening_passed": claim_data.get("aml_screening_passed", True),
                "pep_status": False,
                "recent_claims_count": 0
            }

            applicable_regs = knowledge_result.get("applicable_regulations", [])

            compliance_result = self.compliance_validator.validate_compliance(
                claim_data,
                applicable_regs,
                customer_data
            )

            reg_summary = "\n".join([
                f"  - {r.get('rule_id', '')}: {r.get('summary', r.get('title', ''))}"
                for r in applicable_regs
            ])

            user_msg = f"""Review our structured compliance validation for this insurance claim:

Compliance Assessment Summary:
- Overall Compliance: {compliance_result.get('overall_compliance', 'unknown').upper()}
- Compliance Score: {compliance_result.get('compliance_score', 0):.1%}
- Blocking Violations: {len(compliance_result.get('blocking_violations', []))}

IRDAI Checks:
- Policy Active: {compliance_result.get('irdai_checks', {}).get('policy_active_ok', False)}
- Documentation Complete: {compliance_result.get('irdai_checks', {}).get('documentation_ok', False)}
- Claim Timeline Met: {compliance_result.get('irdai_checks', {}).get('claim_time_limit_ok', False)}

SOX Checks:
- Dual Approval Required: {compliance_result.get('sox_checks', {}).get('dual_approval_required', False)}
- Audit Trail Complete: {compliance_result.get('sox_checks', {}).get('audit_trail_complete', False)}

AML Checks:
- KYC Completed: {compliance_result.get('aml_checks', {}).get('kyc_completed', False)}
- AML Screening Passed: {compliance_result.get('aml_checks', {}).get('aml_screening_passed', True)}

Applicable Regulations:
{reg_summary if reg_summary else "  - Standard insurance regulations apply"}

Mandatory Actions: {compliance_result.get('mandatory_actions', [])}

Provide final compliance recommendation and any additional considerations."""

            response = self._call_claude(SYSTEM_PROMPT, user_msg)
            result_data = self._parse_json_response(response)

            # Merge validator results with Claude analysis
            result_data.update({
                "overall_compliance": compliance_result.get("overall_compliance", result_data.get("overall_compliance", "fail")),
                "compliance_score": compliance_result.get("compliance_score", result_data.get("compliance_score", 0)),
                "irdai_checks": compliance_result.get("irdai_checks"),
                "sox_checks": compliance_result.get("sox_checks"),
                "aml_checks": compliance_result.get("aml_checks"),
                "blocking_violations": compliance_result.get("blocking_violations"),
                "mandatory_actions": compliance_result.get("mandatory_actions")
            })

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

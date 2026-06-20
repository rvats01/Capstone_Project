"""DecisionAgent: Synthesizes all agent outputs into final claim assessment."""

import time
import logging
from agents.base_agent import BaseAgent, AgentResult
from skills.financial_assessment import FinancialAssessor

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the DecisionAgent — the final arbiter in an Insurance Claim Assessment System.

Your responsibilities:
1. Synthesize outputs from CustomerAgent, KnowledgeAgent, ComplianceAgent, and RiskAgent
2. Calculate weighted final score
3. Make a final claim decision with full justification
4. Determine approved amount (if applicable)
5. Provide explainable AI reasoning for traceability

Return a comprehensive JSON decision:
{
    "decision": "approved/rejected/referred/partial_approval",
    "decision_reason": "Clear, detailed explanation",
    "approved_amount": 0.0,
    "deductible_applied": 0.0,
    "final_score": 0.0-1.0,
    "score_breakdown": {
        "customer_score": 0.0-1.0,
        "compliance_score": 0.0-1.0,
        "risk_score": 0.0-1.0,
        "knowledge_score": 0.0-1.0
    },
    "key_factors": {
        "supporting": ["factors that support approval"],
        "against": ["factors against approval"]
    },
    "conditions": ["Any conditions attached to approval"],
    "next_steps": ["Required actions"],
    "sla_days": 0,
    "escalation_required": true/false,
    "explainability": {
        "decision_path": ["Step 1...", "Step 2...", "Step 3..."],
        "regulatory_basis": "..."
    },
    "confidence": 0.0-1.0
}

Decision criteria:
- fraud_score > 0.7: REJECT or REFER for investigation
- compliance_score < 0.5: REJECT
- overall_compliance = "fail": REJECT
- All checks pass with risk < 0.5: APPROVE
- Mixed signals: REFER to human review"""


class DecisionAgent(BaseAgent):
    """Synthesizes all agent outputs into final decision."""

    def __init__(self):
        super().__init__("DecisionAgent")
        self.financial_assessor = FinancialAssessor()

    def process(
        self,
        claim_data: dict,
        customer_result: dict,
        knowledge_result: dict,
        compliance_result: dict,
        risk_result: dict
    ) -> AgentResult:
        start = time.time()
        try:
            # Use FinancialAssessor skill for claim valuation
            policy_data = knowledge_result.get("policy_data", {})
            market_data = claim_data.get("market_data", {})

            financial_assessment = self.financial_assessor.assess_claim_value(
                claim_data,
                policy_data,
                market_data
            )

            fraud_score = risk_result.get("fraud_score", 0)
            compliance_status = compliance_result.get("overall_compliance", "unknown")

            user_msg = f"""Make the final insurance claim decision based on all agent assessments:

Original Claim:
- Type: {claim_data.get('claim_type', 'unknown')}
- Amount Requested: ${claim_data.get('claim_amount', 0):,.2f}
- Customer: {claim_data.get('customer_name', 'N/A')}
- Policy: {claim_data.get('policy_number', 'N/A')}

CustomerAgent Assessment:
- Identity Validated: {customer_result.get('customer_validated', False)}
- Identity Confidence: {customer_result.get('identity_confidence', 0.5):.0%}
- Policy Active: {customer_result.get('policy_active', False)}
- Inconsistencies: {len(customer_result.get('inconsistencies', []))} found

ComplianceAgent Assessment:
- Overall Status: {compliance_status.upper()}
- Compliance Score: {compliance_result.get('compliance_score', 0):.0%}
- Blocking Violations: {len(compliance_result.get('blocking_violations', []))}

RiskAgent Assessment:
- Fraud Score: {fraud_score:.3f}
- Risk Level: {risk_result.get('risk_level', 'medium').upper()}
- Investigation Required: {risk_result.get('investigation_required', False)}
- Fraud Indicators: {len(risk_result.get('fraud_indicators', []))} detected

Financial Assessment:
- Claimed Amount: ${claim_data.get('claim_amount', 0):,.2f}
- Valuation: ${financial_assessment.get('valuation', {}).get('estimated_value', 0):,.2f}
- Approved Amount (Before Deductible): ${financial_assessment.get('adjusted_approved_amount', 0):,.2f}
- Coverage Applies: {financial_assessment.get('coverage_details', {}).get('policy_coverage_applies', False)}
- Approval Rate: {financial_assessment.get('approval_percentage', 0):.1f}%

Make final decision with complete justification using all assessments and financial analysis."""

            response = self._call_claude(SYSTEM_PROMPT, user_msg)
            result_data = self._parse_json_response(response)

            # Merge financial assessment results
            result_data.update({
                "approved_amount": financial_assessment.get("adjusted_approved_amount", result_data.get("approved_amount", 0)),
                "financial_assessment": financial_assessment,
                "deductible_applied": financial_assessment.get("coverage_details", {}).get("deductible", 0)
            })

            return AgentResult(
                agent_name=self.name,
                success=True,
                data=result_data,
                reasoning=result_data.get("decision_reason", response),
                confidence=result_data.get("confidence", 0.85),
                duration_ms=int((time.time() - start) * 1000)
            )
        except Exception as e:
            logger.error(f"DecisionAgent error: {e}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000)
            )

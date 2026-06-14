"""DecisionAgent: Synthesizes all agent outputs into final claim assessment."""

import time
import logging
from agents.base_agent import BaseAgent, AgentResult

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
            user_msg = f"""Make the final insurance claim decision based on all agent assessments:

Original Claim:
- Type: {claim_data.get('claim_type', 'unknown')}
- Amount Requested: ${claim_data.get('claim_amount', 0):,.2f}
- Customer: {claim_data.get('customer_name', 'N/A')}
- Policy: {claim_data.get('policy_number', 'N/A')}
- Description: {claim_data.get('description', 'N/A')[:300]}

CustomerAgent Assessment:
- Identity Validated: {customer_result.get('customer_validated', False)}
- Policy Active: {customer_result.get('policy_active', False)}
- Identity Confidence: {customer_result.get('identity_confidence', 0.5)}
- Inconsistencies: {customer_result.get('inconsistencies', [])}
- Behavioral Flags: {customer_result.get('behavioral_flags', [])}

KnowledgeAgent Assessment:
- Applicable Regulations: {len(knowledge_result.get('applicable_regulations', []))} found
- Key Requirements: {knowledge_result.get('key_requirements', [])}
- Regulatory Flags: {knowledge_result.get('regulatory_flags', [])}

ComplianceAgent Assessment:
- Overall Compliance: {compliance_result.get('overall_compliance', 'unknown')}
- Compliance Score: {compliance_result.get('compliance_score', 0)}
- Blocking Violations: {compliance_result.get('blocking_violations', [])}
- IRDAI Issues: {compliance_result.get('irdai_checks', {}).get('violations', [])}
- AML Issues: {compliance_result.get('aml_checks', {}).get('violations', [])}

RiskAgent Assessment:
- Fraud Score: {risk_result.get('fraud_score', 0)}
- Risk Level: {risk_result.get('risk_level', 'medium')}
- Investigation Required: {risk_result.get('investigation_required', False)}
- Fraud Indicators: {[f.get('indicator', '') for f in risk_result.get('fraud_indicators', [])[:3]]}

Make final decision with complete justification and explain the reasoning chain step by step."""

            response = self._call_claude(SYSTEM_PROMPT, user_msg)
            result_data = self._parse_json_response(response)

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

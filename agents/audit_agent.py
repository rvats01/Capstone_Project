"""AuditAgent: Creates immutable audit trails and compliance reports."""

import time
import hashlib
import json
import logging
from datetime import datetime
from agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the AuditAgent in an Insurance Claim Assessment System.

Your responsibilities:
1. Generate comprehensive audit reports for claim assessments
2. Create cryptographic audit hashes for immutability
3. Produce compliance summaries for regulators
4. Document the complete decision chain

Return a JSON audit record:
{
    "audit_summary": "Executive summary of claim assessment",
    "timeline": [
        {"step": "...", "agent": "...", "timestamp": "...", "outcome": "..."}
    ],
    "compliance_attestation": {
        "irdai_compliant": true/false,
        "sox_compliant": true/false,
        "aml_cleared": true/false,
        "overall": "compliant/non-compliant/conditional"
    },
    "decision_chain": ["Step 1...", "Step 2...", "Final decision..."],
    "data_quality_score": 0.0-1.0,
    "process_integrity": {
        "all_agents_ran": true/false,
        "no_bypass_detected": true/false,
        "hooks_applied": []
    },
    "recommendations": [],
    "audit_notes": "...",
    "confidence": 0.0-1.0
}"""


class AuditAgent(BaseAgent):
    """Creates audit trails and compliance reports."""

    def __init__(self):
        super().__init__("AuditAgent")

    def _compute_audit_hash(self, claim_id: str, all_results: dict) -> str:
        """Compute SHA-256 hash of the complete assessment for immutability."""
        payload = json.dumps({
            "claim_id": claim_id,
            "timestamp": datetime.utcnow().isoformat(),
            "results": all_results
        }, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()

    def process(
        self,
        claim_id: str,
        claim_data: dict,
        customer_result: dict,
        knowledge_result: dict,
        compliance_result: dict,
        risk_result: dict,
        decision_result: dict
    ) -> AgentResult:
        start = time.time()
        try:
            all_results = {
                "customer": customer_result,
                "knowledge": knowledge_result,
                "compliance": compliance_result,
                "risk": risk_result,
                "decision": decision_result
            }
            audit_hash = self._compute_audit_hash(claim_id, all_results)

            user_msg = f"""Generate a comprehensive audit report for this insurance claim assessment:

Claim ID: {claim_id}
Claim Type: {claim_data.get('claim_type', 'unknown')}
Amount: ${claim_data.get('claim_amount', 0):,.2f}
Customer: {claim_data.get('customer_name', 'N/A')}

Assessment Results:
1. CustomerAgent: validated={customer_result.get('customer_validated', False)}, confidence={customer_result.get('confidence', 0)}
2. KnowledgeAgent: {len(knowledge_result.get('applicable_regulations', []))} regulations assessed
3. ComplianceAgent: {compliance_result.get('overall_compliance', 'unknown')}, score={compliance_result.get('compliance_score', 0)}
4. RiskAgent: fraud={risk_result.get('fraud_score', 0):.2f}, risk_level={risk_result.get('risk_level', 'unknown')}
5. DecisionAgent: {decision_result.get('decision', 'unknown')}, amount=${decision_result.get('approved_amount', 0):,.2f}

Audit Hash: {audit_hash}
Assessment Timestamp: {datetime.utcnow().isoformat()}

Generate a complete audit record including timeline, compliance attestation, and decision chain.
This audit record will be stored immutably for regulatory review."""

            response = self._call_claude(SYSTEM_PROMPT, user_msg)
            result_data = self._parse_json_response(response)

            # Add computed hash to audit data
            result_data["audit_hash"] = audit_hash
            result_data["claim_id"] = claim_id
            result_data["generated_at"] = datetime.utcnow().isoformat()

            return AgentResult(
                agent_name=self.name,
                success=True,
                data=result_data,
                reasoning=result_data.get("audit_summary", response),
                confidence=result_data.get("confidence", 0.95),
                duration_ms=int((time.time() - start) * 1000)
            )
        except Exception as e:
            logger.error(f"AuditAgent error: {e}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000)
            )

"""RiskAgent: Performs fraud detection, risk scoring, and anomaly analysis."""

import time
import logging
from agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the RiskAgent in an Insurance Claim Assessment System specializing in fraud detection.

Your responsibilities:
1. Calculate multi-dimensional fraud scores
2. Detect anomalies and suspicious patterns
3. Perform velocity checks (multiple claims, rapid filing)
4. Assess financial risk exposure
5. Identify behavioral indicators of fraud

Return a comprehensive JSON risk assessment:
{
    "fraud_score": 0.0-1.0,
    "risk_level": "low/medium/high/critical",
    "fraud_indicators": [
        {"indicator": "...", "severity": "low/medium/high", "weight": 0.0-1.0}
    ],
    "anomalies": [],
    "velocity_checks": {
        "multiple_claims_flag": true/false,
        "rapid_filing_flag": true/false,
        "amount_inflation_flag": true/false
    },
    "financial_risk": {
        "exposure_level": "low/medium/high",
        "potential_loss": 0.0,
        "recommended_reserve": 0.0
    },
    "behavioral_analysis": {
        "suspicious_patterns": [],
        "consistency_score": 0.0-1.0
    },
    "investigation_required": true/false,
    "risk_score": 0.0-1.0,
    "reasoning": "Detailed risk analysis...",
    "confidence": 0.0-1.0
}

Fraud score > 0.7 = HIGH RISK, flag for investigation.
Fraud score > 0.9 = CRITICAL, auto-reject pending investigation."""


class RiskAgent(BaseAgent):
    """Detects fraud and assesses claim risk."""

    def __init__(self):
        super().__init__("RiskAgent")

    def process(self, claim_data: dict, customer_result: dict, fraud_patterns: list) -> AgentResult:
        start = time.time()
        try:
            patterns_text = "\n".join([
                f"  - [{p.get('rule_id', '')}] {p.get('title', '')}: {p.get('content', '')[:200]}"
                for p in fraud_patterns[:5]
            ])

            behavioral_flags = customer_result.get("behavioral_flags", [])
            inconsistencies = customer_result.get("inconsistencies", [])

            user_msg = f"""Perform comprehensive fraud detection and risk assessment:

Claim Details:
- Claim Type: {claim_data.get('claim_type', 'unknown')}
- Claim Amount: ${claim_data.get('claim_amount', 0):,.2f}
- Incident Date: {claim_data.get('incident_date', 'N/A')}
- Filing Date: Today
- Customer History: New customer (simulated)
- Description: {claim_data.get('description', 'N/A')[:400]}

Customer Validation Flags from CustomerAgent:
- Behavioral Flags: {behavioral_flags}
- Data Inconsistencies: {inconsistencies}
- Identity Confidence: {customer_result.get('identity_confidence', 0.5)}

Known Fraud Patterns:
{patterns_text if patterns_text else "  - Standard fraud patterns apply"}

Analyze for:
1. Application fraud (inflated amounts, false statements)
2. Staged incidents (suspicious timing, circumstances)
3. Medical billing fraud (if health claim)
4. Velocity fraud (multiple rapid claims)
5. Identity fraud indicators
6. Financial exposure to insurer

Provide risk score, fraud score, and detailed reasoning."""

            response = self._call_claude(SYSTEM_PROMPT, user_msg)
            result_data = self._parse_json_response(response)

            return AgentResult(
                agent_name=self.name,
                success=True,
                data=result_data,
                reasoning=result_data.get("reasoning", response),
                confidence=result_data.get("confidence", 0.8),
                duration_ms=int((time.time() - start) * 1000)
            )
        except Exception as e:
            logger.error(f"RiskAgent error: {e}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000)
            )

"""RiskAgent: Performs fraud detection, risk scoring, and anomaly analysis."""

import time
import logging
from agents.base_agent import BaseAgent, AgentResult
from skills.risk_analysis import RiskAnalyzer

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
        self.risk_analyzer = RiskAnalyzer()

    def process(self, claim_data: dict, customer_result: dict, fraud_patterns: list) -> AgentResult:
        start = time.time()
        try:
            # Use RiskAnalyzer skill for core risk analysis
            customer_history = {
                "total_claims": customer_result.get("total_claims", 0),
                "recent_claims_count": customer_result.get("recent_claims_count", 0),
                "days_since_policy_issue": customer_result.get("days_since_policy_issue", 365),
                "avg_claim_amount": customer_result.get("avg_claim_amount", claim_data.get("claim_amount", 0)),
                "claim_types_filed": customer_result.get("claim_types_filed", [])
            }

            fraud_score_analysis = self.risk_analyzer.calculate_fraud_score(
                claim_data,
                customer_history,
                fraud_patterns
            )

            financial_exposure = self.risk_analyzer.calculate_financial_exposure(
                claim_data,
                fraud_score_analysis.get("fraud_score", 0)
            )

            velocity_analysis = self.risk_analyzer.perform_velocity_analysis(customer_history)

            patterns_text = "\n".join([
                f"  - [{p.get('rule_id', '')}] {p.get('title', '')}: {p.get('content', '')[:200]}"
                for p in fraud_patterns[:5]
            ])

            behavioral_flags = customer_result.get("behavioral_flags", [])
            inconsistencies = customer_result.get("inconsistencies", [])

            user_msg = f"""Review and validate risk assessment from our fraud analysis system:

Fraud Analysis Results:
- Fraud Score: {fraud_score_analysis.get('fraud_score', 0):.3f}
- Risk Level: {fraud_score_analysis.get('risk_level', 'unknown')}
- Key Indicators: {', '.join([i.get('indicator', '') for i in fraud_score_analysis.get('fraud_indicators', [])[:3]])}
- Investigation Required: {fraud_score_analysis.get('investigation_required', False)}

Financial Exposure:
- Exposure Level: {financial_exposure.get('exposure_level', 'unknown')}
- Potential Loss: ${financial_exposure.get('potential_loss', 0):,.2f}
- Recommended Reserve: ${financial_exposure.get('recommended_reserve', 0):,.2f}

Velocity Patterns:
- Recent Claims: {velocity_analysis.get('recent_claims_count', 0)}
- Velocity Alert: {velocity_analysis.get('velocity_alert', False)}
- Days Since Last Claim: {velocity_analysis.get('days_since_last_claim', 0)}

Customer Validation:
- Behavioral Flags: {behavioral_flags}
- Identity Confidence: {customer_result.get('identity_confidence', 0.5):.1%}

Provide validation and enhance assessment with additional insights."""

            response = self._call_claude(SYSTEM_PROMPT, user_msg)
            result_data = self._parse_json_response(response)

            # Merge analyzer results with Claude analysis
            result_data.update({
                "fraud_score": fraud_score_analysis.get("fraud_score", result_data.get("fraud_score", 0)),
                "risk_level": fraud_score_analysis.get("risk_level", result_data.get("risk_level", "low")),
                "financial_risk": financial_exposure,
                "velocity_checks": velocity_analysis
            })

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

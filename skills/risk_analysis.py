"""Risk Analysis Skill - Multi-dimensional risk scoring and assessment for insurance claims."""

import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """Performs comprehensive risk analysis on insurance claims."""

    RISK_FACTORS = {
        "high_amount": {"threshold": 100000, "weight": 0.15, "description": "Claim amount exceeds high threshold"},
        "new_customer": {"weight": 0.10, "description": "Customer has minimal claim history"},
        "rapid_filing": {"weight": 0.12, "description": "Multiple claims filed in short period"},
        "incomplete_info": {"weight": 0.08, "description": "Missing or vague claim documentation"},
        "unusual_claim_type": {"weight": 0.10, "description": "Claim type is uncommon"},
        "timing_suspicious": {"weight": 0.15, "description": "Claim filed short time after policy issuance"},
        "inconsistent_data": {"weight": 0.12, "description": "Data inconsistencies in claim"},
        "behavioral_red_flag": {"weight": 0.18, "description": "Behavioral patterns indicate risk"},
    }

    def __init__(self):
        self.name = "RiskAnalyzer"
        logger.info(f"Initialized {self.name}")

    def calculate_fraud_score(
        self,
        claim_data: Dict[str, Any],
        customer_history: Dict[str, Any],
        fraud_patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate multi-dimensional fraud risk score.

        Args:
            claim_data: Current claim information
            customer_history: Customer's claim history
            fraud_patterns: Known fraud patterns to check against

        Returns:
            Dictionary with fraud score, risk level, and indicators
        """
        fraud_score = 0.0
        indicators = []
        weighted_factors = {}

        claim_amount = claim_data.get("claim_amount", 0)
        claim_type = claim_data.get("claim_type", "").lower()
        incident_date = claim_data.get("incident_date", "")
        filing_date = claim_data.get("filing_date", datetime.now().isoformat())

        # Factor 1: High claim amount
        if claim_amount > self.RISK_FACTORS["high_amount"]["threshold"]:
            weight = self.RISK_FACTORS["high_amount"]["weight"]
            factor_score = min(claim_amount / 500000, 1.0)
            weighted_factors["high_amount"] = factor_score * weight
            indicators.append({
                "indicator": "High Claim Amount",
                "value": f"${claim_amount:,.2f}",
                "severity": "high" if claim_amount > 200000 else "medium",
                "weight": weight
            })

        # Factor 2: New customer (simulated check)
        if customer_history.get("total_claims", 0) == 0:
            weight = self.RISK_FACTORS["new_customer"]["weight"]
            weighted_factors["new_customer"] = 0.5 * weight
            indicators.append({
                "indicator": "New Customer",
                "value": "No prior claim history",
                "severity": "low",
                "weight": weight
            })

        # Factor 3: Velocity - Multiple claims in short period
        recent_claims_count = customer_history.get("recent_claims_count", 0)
        if recent_claims_count > 2:
            weight = self.RISK_FACTORS["rapid_filing"]["weight"]
            velocity_score = min(recent_claims_count / 5, 1.0)
            weighted_factors["rapid_filing"] = velocity_score * weight
            indicators.append({
                "indicator": "Rapid Filing Pattern",
                "value": f"{recent_claims_count} claims in 90 days",
                "severity": "high",
                "weight": weight
            })

        # Factor 4: Claim timing - filed soon after policy issuance
        days_since_policy = customer_history.get("days_since_policy_issue", 365)
        if days_since_policy < 30:
            weight = self.RISK_FACTORS["timing_suspicious"]["weight"]
            timing_score = max(1.0 - (days_since_policy / 30), 0.0)
            weighted_factors["timing_suspicious"] = timing_score * weight
            indicators.append({
                "indicator": "Suspicious Timing",
                "value": f"Claim filed {days_since_policy} days after policy issuance",
                "severity": "critical",
                "weight": weight
            })

        # Factor 5: Pattern matching against known fraud signatures
        matched_patterns = self._match_fraud_patterns(claim_data, fraud_patterns)
        if matched_patterns:
            weight_per_pattern = 0.08
            for pattern in matched_patterns[:3]:
                weighted_factors[f"pattern_{pattern['rule_id']}"] = 0.4 * weight_per_pattern
                indicators.append({
                    "indicator": f"Pattern Match: {pattern.get('title', 'Unknown')}",
                    "value": pattern.get("content", "")[:100],
                    "severity": pattern.get("severity", "medium"),
                    "weight": weight_per_pattern
                })

        # Calculate total weighted fraud score
        fraud_score = sum(weighted_factors.values())
        fraud_score = min(fraud_score, 1.0)

        # Determine risk level
        risk_level = self._determine_risk_level(fraud_score)

        # Velocity checks
        velocity_checks = {
            "multiple_claims_flag": recent_claims_count > 2,
            "rapid_filing_flag": recent_claims_count > 1 and days_since_policy < 60,
            "amount_inflation_flag": claim_amount > claim_data.get("estimated_value", claim_amount * 2)
        }

        return {
            "fraud_score": round(fraud_score, 4),
            "risk_level": risk_level,
            "fraud_indicators": indicators,
            "anomalies": self._detect_anomalies(claim_data, customer_history),
            "velocity_checks": velocity_checks,
            "investigation_required": fraud_score > 0.6,
            "confidence": min(0.85 + (len(indicators) * 0.02), 1.0),
            "reasoning": self._generate_reasoning(fraud_score, indicators, risk_level)
        }

    def _match_fraud_patterns(self, claim_data: Dict[str, Any], patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match claim data against known fraud patterns."""
        matched = []
        description = claim_data.get("description", "").lower()
        claim_type = claim_data.get("claim_type", "").lower()

        for pattern in patterns:
            keywords = pattern.get("keywords", [])
            rule_id = pattern.get("rule_id", "")

            if any(keyword.lower() in description or keyword.lower() in claim_type for keyword in keywords if keywords):
                matched.append({
                    "rule_id": rule_id,
                    "title": pattern.get("title", ""),
                    "content": pattern.get("content", ""),
                    "severity": "medium"
                })

        return matched

    def _detect_anomalies(self, claim_data: Dict[str, Any], customer_history: Dict[str, Any]) -> List[Dict[str, str]]:
        """Detect anomalous patterns in claim."""
        anomalies = []

        # Anomaly 1: Amount significantly higher than average
        avg_claim = customer_history.get("avg_claim_amount", 0)
        current_claim = claim_data.get("claim_amount", 0)
        if avg_claim > 0 and current_claim > (avg_claim * 2.5):
            anomalies.append({
                "type": "Amount Inflation",
                "description": f"Claim is {round(current_claim / avg_claim, 1)}x customer's average claim amount"
            })

        # Anomaly 2: Unusual claim type for customer
        claim_type = claim_data.get("claim_type", "")
        customer_types = customer_history.get("claim_types_filed", [])
        if claim_type not in customer_types and customer_types:
            anomalies.append({
                "type": "Unusual Claim Type",
                "description": f"Customer has never filed {claim_type} claims before"
            })

        # Anomaly 3: Geographic mismatch
        policy_region = claim_data.get("policy_region", "")
        incident_region = claim_data.get("incident_region", "")
        if policy_region and incident_region and policy_region != incident_region:
            anomalies.append({
                "type": "Geographic Mismatch",
                "description": f"Policy registered in {policy_region}, incident occurred in {incident_region}"
            })

        return anomalies

    def _determine_risk_level(self, fraud_score: float) -> str:
        """Determine risk level from fraud score."""
        if fraud_score >= 0.8:
            return "critical"
        elif fraud_score >= 0.6:
            return "high"
        elif fraud_score >= 0.4:
            return "medium"
        else:
            return "low"

    def _generate_reasoning(self, fraud_score: float, indicators: List[Dict], risk_level: str) -> str:
        """Generate human-readable reasoning for risk assessment."""
        top_indicators = sorted(indicators, key=lambda x: x.get("weight", 0), reverse=True)[:3]
        indicator_text = ", ".join([ind.get("indicator", "") for ind in top_indicators])

        if risk_level == "critical":
            reasoning = f"CRITICAL RISK: Fraud score of {fraud_score:.1%} based on multiple high-severity factors including {indicator_text}. Immediate investigation and manual review required."
        elif risk_level == "high":
            reasoning = f"HIGH RISK: Fraud score of {fraud_score:.1%} due to concerning patterns: {indicator_text}. Enhanced verification recommended."
        elif risk_level == "medium":
            reasoning = f"MODERATE RISK: Fraud score of {fraud_score:.1%} with some risk factors present: {indicator_text}. Standard verification should be sufficient."
        else:
            reasoning = f"LOW RISK: Fraud score of {fraud_score:.1%} with minimal risk indicators. Routine processing recommended."

        return reasoning

    def calculate_financial_exposure(self, claim_data: Dict[str, Any], fraud_score: float) -> Dict[str, Any]:
        """Calculate potential financial exposure for the insurer."""
        claim_amount = claim_data.get("claim_amount", 0)

        # Calculate reserve as percentage of claim based on fraud risk
        if fraud_score > 0.8:
            reserve_multiplier = 0.5
            exposure_level = "high"
        elif fraud_score > 0.6:
            reserve_multiplier = 0.35
            exposure_level = "medium"
        elif fraud_score > 0.4:
            reserve_multiplier = 0.15
            exposure_level = "low"
        else:
            reserve_multiplier = 0.05
            exposure_level = "minimal"

        recommended_reserve = claim_amount * reserve_multiplier
        potential_loss = claim_amount if fraud_score > 0.9 else 0

        return {
            "exposure_level": exposure_level,
            "potential_loss": round(potential_loss, 2),
            "recommended_reserve": round(recommended_reserve, 2),
            "reserve_percentage": round(reserve_multiplier * 100, 1),
            "investigation_depth": "comprehensive" if fraud_score > 0.7 else "standard"
        }

    def perform_velocity_analysis(self, customer_history: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze claim velocity patterns."""
        recent_claims = customer_history.get("recent_claims_count", 0)
        historical_avg = customer_history.get("avg_claims_per_year", 0)
        days_since_last_claim = customer_history.get("days_since_last_claim", 999)

        velocity_risk = 0.0
        if recent_claims > 3:
            velocity_risk = 0.3
        if recent_claims > 5:
            velocity_risk = 0.6
        if days_since_last_claim < 30 and recent_claims > 1:
            velocity_risk = min(velocity_risk + 0.2, 1.0)

        return {
            "recent_claims_count": recent_claims,
            "historical_average_per_year": historical_avg,
            "days_since_last_claim": days_since_last_claim,
            "velocity_risk_score": round(velocity_risk, 3),
            "velocity_alert": velocity_risk > 0.4
        }

"""Fraud Detection Skill - Advanced fraud pattern recognition and detection."""

import logging
from typing import Dict, List, Any, Tuple
import re

logger = logging.getLogger(__name__)


class FraudDetector:
    """Advanced fraud detection with pattern matching and behavioral analysis."""

    FRAUD_INDICATORS = {
        "staged_incident": {
            "severity": "critical",
            "keywords": ["staged", "setup", "arranged", "planned"],
            "weight": 0.25
        },
        "inflated_amount": {
            "severity": "high",
            "keywords": ["maximum", "total loss", "full value"],
            "weight": 0.20
        },
        "identity_fraud": {
            "severity": "critical",
            "keywords": ["identity", "impersonation", "fraudulent"],
            "weight": 0.30
        },
        "collusion": {
            "severity": "high",
            "keywords": ["partner", "associate", "friend", "relative"],
            "weight": 0.22
        },
        "documentation_fraud": {
            "severity": "high",
            "keywords": ["forged", "falsified", "counterfeit", "fake"],
            "weight": 0.25
        },
        "medical_billing_fraud": {
            "severity": "high",
            "keywords": ["upcoding", "unbundling", "duplicate", "unnecessary"],
            "weight": 0.20
        },
    }

    def __init__(self):
        self.name = "FraudDetector"
        logger.info(f"Initialized {self.name}")

    def detect_fraud_indicators(
        self,
        claim_data: Dict[str, Any],
        customer_behavioral_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect fraud indicators in claim data.

        Args:
            claim_data: Current claim information
            customer_behavioral_data: Customer's behavioral patterns

        Returns:
            Dictionary with detected fraud indicators and analysis
        """
        indicators_found = []
        fraud_patterns = []
        confidence_scores = []

        # Pattern 1: Staged incident detection
        staged_score, staged_indicators = self._detect_staged_incident(claim_data)
        if staged_score > 0.5:
            fraud_patterns.append({
                "pattern": "Staged Incident",
                "score": staged_score,
                "severity": "critical",
                "indicators": staged_indicators
            })
            confidence_scores.append(staged_score)

        # Pattern 2: Amount inflation detection
        inflation_score, inflation_indicators = self._detect_amount_inflation(claim_data, customer_behavioral_data)
        if inflation_score > 0.4:
            fraud_patterns.append({
                "pattern": "Amount Inflation",
                "score": inflation_score,
                "severity": "high",
                "indicators": inflation_indicators
            })
            confidence_scores.append(inflation_score)

        # Pattern 3: Identity fraud detection
        identity_score, identity_indicators = self._detect_identity_fraud(claim_data, customer_behavioral_data)
        if identity_score > 0.5:
            fraud_patterns.append({
                "pattern": "Identity Fraud",
                "score": identity_score,
                "severity": "critical",
                "indicators": identity_indicators
            })
            confidence_scores.append(identity_score)

        # Pattern 4: Documentation fraud detection
        doc_score, doc_indicators = self._detect_documentation_fraud(claim_data)
        if doc_score > 0.4:
            fraud_patterns.append({
                "pattern": "Documentation Fraud",
                "score": doc_score,
                "severity": "high",
                "indicators": doc_indicators
            })
            confidence_scores.append(doc_score)

        # Pattern 5: Behavioral anomalies
        behavior_score, behavior_indicators = self._detect_behavioral_anomalies(customer_behavioral_data)
        if behavior_score > 0.4:
            fraud_patterns.append({
                "pattern": "Behavioral Anomaly",
                "score": behavior_score,
                "severity": "medium",
                "indicators": behavior_indicators
            })
            confidence_scores.append(behavior_score)

        # Calculate overall fraud confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return {
            "fraud_patterns_detected": fraud_patterns,
            "overall_fraud_confidence": round(overall_confidence, 3),
            "high_risk_indicators": [p for p in fraud_patterns if p["score"] > 0.7],
            "medium_risk_indicators": [p for p in fraud_patterns if 0.4 <= p["score"] <= 0.7],
            "patterns_count": len(fraud_patterns),
            "requires_investigation": len(fraud_patterns) > 1 or overall_confidence > 0.65,
            "investigation_priority": self._determine_investigation_priority(fraud_patterns)
        }

    def _detect_staged_incident(self, claim_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Detect indicators of staged/arranged incidents."""
        score = 0.0
        indicators = []

        description = claim_data.get("description", "").lower()
        claim_type = claim_data.get("claim_type", "").lower()
        incident_date = claim_data.get("incident_date", "")

        # Check for suspicious timing
        if "just happened" not in description and "suddenly" not in description:
            tokens = re.findall(r'\b(conveniently|fortunately|luckily|happened to)\b', description)
            if tokens:
                score += 0.15
                indicators.append("Suspicious timing language in incident description")

        # Check for too-perfect circumstances
        if "total loss" in description or "complete destruction" in description:
            score += 0.12
            indicators.append("Claim describes unusually severe/complete damage")

        # Check for financial motive patterns
        claim_amount = claim_data.get("claim_amount", 0)
        if claim_amount > 50000 and "just after" in description:
            score += 0.10
            indicators.append("High-value claim shortly after policy issuance")

        # Check for documentation issues typical of staged incidents
        documentation = claim_data.get("documentation", [])
        if len(documentation) < 2:
            score += 0.08
            indicators.append("Insufficient documentation for claimed incident severity")

        # Check for witness information
        has_witnesses = "witness" in description or "saw" in description
        if not has_witnesses and claim_type in ["auto", "property"]:
            score += 0.05
            indicators.append("No independent witnesses mentioned for incident")

        return min(score, 1.0), indicators

    def _detect_amount_inflation(
        self,
        claim_data: Dict[str, Any],
        customer_behavioral_data: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """Detect indicators of inflated claim amounts."""
        score = 0.0
        indicators = []

        claim_amount = claim_data.get("claim_amount", 0)
        estimated_value = claim_data.get("estimated_value", 0)
        avg_claim = customer_behavioral_data.get("avg_claim_amount", claim_amount)

        # Check 1: Claim significantly exceeds estimate
        if estimated_value > 0 and claim_amount > (estimated_value * 1.5):
            overage_pct = ((claim_amount - estimated_value) / estimated_value) * 100
            score += 0.25
            indicators.append(f"Claim amount {overage_pct:.0f}% higher than estimate")

        # Check 2: Claim exceeds customer's historical average
        if avg_claim > 0 and claim_amount > (avg_claim * 2.5):
            multiple = claim_amount / avg_claim
            score += 0.20
            indicators.append(f"Claim is {multiple:.1f}x customer's historical average")

        # Check 3: Rounding suspicion
        if claim_amount % 1000 == 0 and claim_amount > 10000:
            score += 0.08
            indicators.append("Claim amount suspiciously round (multiple of 1000)")

        # Check 4: Description doesn't match amount
        description = claim_data.get("description", "").lower()
        description_length = len(description)
        if description_length < 50 and claim_amount > 100000:
            score += 0.12
            indicators.append("Minimal description for high-value claim")

        # Check 5: Multiple items with exact same value
        items = re.findall(r'\$[\d,]+\.?\d*', claim_data.get("description", ""))
        if items and len(set(items)) < len(items) * 0.5:
            score += 0.10
            indicators.append("Multiple claim items with identical values (suspicious)")

        return min(score, 1.0), indicators

    def _detect_identity_fraud(
        self,
        claim_data: Dict[str, Any],
        customer_behavioral_data: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """Detect indicators of identity fraud."""
        score = 0.0
        indicators = []

        # Check 1: Changed contact information
        phones_on_file = customer_behavioral_data.get("phones_on_file", 0)
        current_phone = claim_data.get("phone", "")
        if phones_on_file > 2:
            score += 0.15
            indicators.append("Multiple phone numbers on file (possible account takeover)")

        # Check 2: New address associated with claim
        address_matches_historical = customer_behavioral_data.get("current_address_matches_historical", True)
        if not address_matches_historical:
            score += 0.18
            indicators.append("Claim filed from address different from policy address")

        # Check 3: Unusual access pattern
        filing_device_match = customer_behavioral_data.get("filing_device_matches_historical", True)
        if not filing_device_match:
            score += 0.12
            indicators.append("Claim filed from unusual device/location")

        # Check 4: Claim filed soon after account changes
        days_since_account_change = customer_behavioral_data.get("days_since_account_change", 999)
        if days_since_account_change < 7:
            score += 0.20
            indicators.append("Claim filed shortly after account information changed")

        # Check 5: Account reactivation fraud
        account_previously_inactive = customer_behavioral_data.get("account_reactivated", False)
        if account_previously_inactive:
            score += 0.15
            indicators.append("Account was reactivated recently before claiming")

        return min(score, 1.0), indicators

    def _detect_documentation_fraud(self, claim_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Detect indicators of forged/fraudulent documentation."""
        score = 0.0
        indicators = []

        documentation = claim_data.get("documentation", [])
        doc_quality = claim_data.get("documentation_quality_score", 0.8)

        # Check 1: Poor documentation quality
        if doc_quality < 0.6:
            score += 0.20
            indicators.append("Documentation quality significantly below standard")

        # Check 2: Missing standard documentation
        required_docs = {"policy_proof", "incident_proof", "identity_proof"}
        provided_docs = set(documentation)
        missing = required_docs - provided_docs
        if missing:
            score += len(missing) * 0.12
            indicators.append(f"Missing standard documentation: {', '.join(missing)}")

        # Check 3: Inconsistent dates in documentation
        date_inconsistencies = claim_data.get("date_inconsistencies", [])
        if date_inconsistencies:
            score += 0.15
            indicators.append(f"Date inconsistencies found in documentation: {', '.join(date_inconsistencies[:2])}")

        # Check 4: Redacted/altered areas in documents
        altered_docs = claim_data.get("altered_documents_detected", [])
        if altered_docs:
            score += 0.25
            indicators.append(f"Document alterations detected in: {', '.join(altered_docs)}")

        # Check 5: Signature/handwriting issues
        signature_match = claim_data.get("signature_verification_passed", True)
        if not signature_match:
            score += 0.22
            indicators.append("Signature verification failed")

        return min(score, 1.0), indicators

    def _detect_behavioral_anomalies(self, customer_behavioral_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Detect behavioral anomalies in customer activity."""
        score = 0.0
        indicators = []

        recent_behavior = customer_behavioral_data.get("recent_behavior_changes", [])
        for behavior_change in recent_behavior:
            score += 0.10
            indicators.append(f"Behavioral change detected: {behavior_change}")

        # Check for claim frequency changes
        usual_claims_per_year = customer_behavioral_data.get("avg_claims_per_year", 0.5)
        recent_claims_count = customer_behavioral_data.get("recent_claims_count", 0)
        if usual_claims_per_year > 0 and recent_claims_count > (usual_claims_per_year * 3):
            score += 0.15
            indicators.append("Unusually high claim frequency compared to historical pattern")

        # Check for amount pattern changes
        amount_variance = customer_behavioral_data.get("claim_amount_variance", 0)
        if amount_variance > 0.7:
            score += 0.12
            indicators.append("Significant variance in claim amounts (inconsistent pattern)")

        return min(score, 1.0), indicators

    def _determine_investigation_priority(self, fraud_patterns: List[Dict[str, Any]]) -> str:
        """Determine priority level for fraud investigation."""
        if not fraud_patterns:
            return "low"

        critical_count = len([p for p in fraud_patterns if p["score"] > 0.8])
        high_count = len([p for p in fraud_patterns if 0.6 < p["score"] <= 0.8])
        avg_score = sum(p["score"] for p in fraud_patterns) / len(fraud_patterns)

        if critical_count > 0:
            return "critical"
        elif critical_count == 0 and high_count > 1:
            return "high"
        elif avg_score > 0.65:
            return "high"
        elif avg_score > 0.50:
            return "medium"
        else:
            return "low"

    def generate_investigation_brief(self, fraud_analysis: Dict[str, Any]) -> str:
        """Generate a brief for investigation team."""
        patterns = fraud_analysis.get("fraud_patterns_detected", [])
        confidence = fraud_analysis.get("overall_fraud_confidence", 0)
        priority = fraud_analysis.get("investigation_priority", "low")

        if not patterns:
            return "No fraud indicators detected. Standard processing recommended."

        brief = f"FRAUD INVESTIGATION BRIEF (Priority: {priority.upper()})\n"
        brief += f"Overall Fraud Confidence: {confidence:.0%}\n\n"
        brief += "Detected Patterns:\n"

        for i, pattern in enumerate(patterns, 1):
            brief += f"{i}. {pattern['pattern']} (Score: {pattern['score']:.0%})\n"
            for indicator in pattern.get("indicators", [])[:2]:
                brief += f"   - {indicator}\n"

        return brief

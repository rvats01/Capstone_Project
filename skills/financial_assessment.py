"""Financial Assessment Skill - Claim valuation, reserve calculation, and financial analysis."""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FinancialAssessor:
    """Performs financial assessment and valuation of insurance claims."""

    # Policy and coverage constants
    STANDARD_DEDUCTIBLES = {
        "auto": 500,
        "property": 1000,
        "health": 250,
        "life": 0,
        "travel": 100
    }

    COVERAGE_LIMITS = {
        "auto": 500000,
        "property": 2000000,
        "health": 1000000,
        "life": 5000000,
        "travel": 100000
    }

    DEPRECIATION_RATES = {
        "vehicle": 0.15,  # 15% per year
        "property": 0.02,  # 2% per year
        "equipment": 0.20,  # 20% per year
        "medical": 0.0,    # No depreciation
    }

    def __init__(self):
        self.name = "FinancialAssessor"
        logger.info(f"Initialized {self.name}")

    def assess_claim_value(
        self,
        claim_data: Dict[str, Any],
        policy_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive financial assessment of claim.

        Args:
            claim_data: Current claim information
            policy_data: Policy coverage and terms
            market_data: Market value and comparable data

        Returns:
            Dictionary with claim valuation and financial recommendations
        """
        claim_type = claim_data.get("claim_type", "auto")
        claimed_amount = claim_data.get("claim_amount", 0)

        # Get applicable policy limits and deductibles
        deductible = self.STANDARD_DEDUCTIBLES.get(claim_type, 500)
        coverage_limit = self.COVERAGE_LIMITS.get(claim_type, claimed_amount)

        # Perform valuations
        valuation = self._perform_valuation(claim_data, policy_data, market_data, claim_type)
        adjusted_value = self._calculate_adjusted_value(valuation, deductible, coverage_limit)
        reserves = self._calculate_reserves(claim_data, adjusted_value, valuation)
        financial_risk = self._assess_financial_risk(claim_data, valuation, adjusted_value)

        return {
            "claim_type": claim_type,
            "claimed_amount": round(claimed_amount, 2),
            "valuation": valuation,
            "coverage_details": {
                "deductible": round(deductible, 2),
                "coverage_limit": round(coverage_limit, 2),
                "policy_coverage_applies": claimed_amount <= coverage_limit
            },
            "adjusted_approved_amount": round(adjusted_value, 2),
            "approval_percentage": round((adjusted_value / claimed_amount * 100) if claimed_amount > 0 else 0, 1),
            "reserve_recommendations": reserves,
            "financial_risk_assessment": financial_risk,
            "payment_recommendations": self._generate_payment_recommendations(adjusted_value, claim_type),
            "financial_reasoning": self._generate_financial_reasoning(claimed_amount, adjusted_value, valuation)
        }

    def _perform_valuation(
        self,
        claim_data: Dict[str, Any],
        policy_data: Dict[str, Any],
        market_data: Dict[str, Any],
        claim_type: str
    ) -> Dict[str, Any]:
        """Perform claim valuation based on type and supporting evidence."""
        valuation_method = self._determine_valuation_method(claim_type, claim_data)

        if claim_type == "auto":
            return self._value_auto_claim(claim_data, market_data)
        elif claim_type == "property":
            return self._value_property_claim(claim_data, market_data)
        elif claim_type == "health":
            return self._value_health_claim(claim_data, policy_data)
        elif claim_type == "life":
            return self._value_life_claim(claim_data, policy_data)
        elif claim_type == "travel":
            return self._value_travel_claim(claim_data)
        else:
            return {
                "method": "standard",
                "estimated_value": claim_data.get("claim_amount", 0),
                "confidence": 0.5
            }

    def _value_auto_claim(self, claim_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Value auto insurance claim."""
        damage_type = claim_data.get("damage_type", "")
        vehicle_year = claim_data.get("vehicle_year", 2020)
        vehicle_mileage = claim_data.get("vehicle_mileage", 100000)
        claimed_amount = claim_data.get("claim_amount", 0)

        # Calculate vehicle depreciation
        years_old = datetime.now().year - vehicle_year
        depreciation_factor = (1 - self.DEPRECIATION_RATES.get("vehicle", 0.15)) ** years_old

        # Get comparable market value
        market_value = market_data.get("comparable_value", claimed_amount)
        depreciated_value = market_value * depreciation_factor

        if damage_type == "total_loss":
            estimated_value = depreciated_value * 0.85  # Account for salvage value
            confidence = 0.88
        elif damage_type == "collision":
            repair_estimate = market_data.get("repair_estimate", claimed_amount)
            estimated_value = min(repair_estimate, depreciated_value * 0.95)
            confidence = 0.85
        elif damage_type == "comprehensive":
            estimated_value = min(claimed_amount * 0.9, depreciated_value * 0.80)
            confidence = 0.82
        else:
            estimated_value = claimed_amount * 0.75
            confidence = 0.70

        return {
            "method": "auto_valuation",
            "vehicle_depreciation_factor": round(depreciation_factor, 3),
            "market_value_comparable": round(depreciated_value, 2),
            "repair_estimate": round(market_data.get("repair_estimate", 0), 2),
            "estimated_value": round(max(estimated_value, 0), 2),
            "confidence": confidence,
            "notes": f"Total loss valuation based on {years_old}-year-old vehicle with {vehicle_mileage:,} miles"
        }

    def _value_property_claim(self, claim_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Value property insurance claim."""
        property_type = claim_data.get("property_type", "residential")
        damage_percentage = claim_data.get("damage_percentage", 100)
        replacement_cost = market_data.get("replacement_cost", 0)
        original_value = market_data.get("original_value", claim_data.get("claim_amount", 0))

        # Calculate actual cash value
        property_age_years = claim_data.get("property_age_years", 10)
        depreciation_factor = (1 - self.DEPRECIATION_RATES.get("property", 0.02)) ** property_age_years
        acv = original_value * depreciation_factor

        # Calculate claim value
        if damage_percentage >= 80:
            # Total loss scenario
            estimated_value = acv
            valuation_method = "actual_cash_value"
        else:
            # Partial damage - use replacement cost with depreciation
            damage_value = (replacement_cost * (damage_percentage / 100)) * depreciation_factor
            estimated_value = min(damage_value, acv * 0.95)
            valuation_method = "repair_cost"

        return {
            "method": "property_valuation",
            "property_type": property_type,
            "damage_percentage": damage_percentage,
            "original_value": round(original_value, 2),
            "depreciation_factor": round(depreciation_factor, 3),
            "actual_cash_value": round(acv, 2),
            "replacement_cost": round(replacement_cost, 2),
            "estimated_value": round(estimated_value, 2),
            "valuation_method": valuation_method,
            "confidence": 0.87
        }

    def _value_health_claim(self, claim_data: Dict[str, Any], policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Value health insurance claim."""
        service_type = claim_data.get("service_type", "outpatient")
        billed_amount = claim_data.get("claim_amount", 0)
        network_status = claim_data.get("network_status", "in-network")

        # Get network negotiated rates
        negotiated_rate = policy_data.get("negotiated_rate", billed_amount * 0.8)

        # Apply network discounts
        if network_status == "in-network":
            allowed_amount = negotiated_rate
            discount_percentage = ((billed_amount - allowed_amount) / billed_amount * 100) if billed_amount > 0 else 0
        else:
            allowed_amount = billed_amount * 0.75
            discount_percentage = 25

        # Check against policy maximums
        annual_max = policy_data.get("annual_max", 500000)
        remaining_benefit = policy_data.get("remaining_annual_benefit", annual_max)
        approved_amount = min(allowed_amount, remaining_benefit)

        return {
            "method": "health_valuation",
            "service_type": service_type,
            "billed_amount": round(billed_amount, 2),
            "network_status": network_status,
            "negotiated_rate": round(negotiated_rate, 2),
            "discount_applied": round(discount_percentage, 1),
            "allowed_amount": round(allowed_amount, 2),
            "annual_benefit_remaining": round(remaining_benefit, 2),
            "estimated_value": round(approved_amount, 2),
            "confidence": 0.92
        }

    def _value_life_claim(self, claim_data: Dict[str, Any], policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Value life insurance claim."""
        policy_type = policy_data.get("policy_type", "term")
        death_benefit = policy_data.get("death_benefit", 0)
        exclusion_applies = claim_data.get("exclusion_applies", False)

        if exclusion_applies:
            # Policy exclusion applies (e.g., suicide clause)
            estimated_value = 0
            confidence = 0.98
            notes = "Policy exclusion applies - requires legal review"
        else:
            estimated_value = death_benefit
            confidence = 0.99
            notes = f"{policy_type} life insurance claim for full death benefit"

        return {
            "method": "life_valuation",
            "policy_type": policy_type,
            "death_benefit": round(death_benefit, 2),
            "exclusion_applies": exclusion_applies,
            "estimated_value": round(estimated_value, 2),
            "confidence": confidence,
            "notes": notes
        }

    def _value_travel_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Value travel insurance claim."""
        claim_reason = claim_data.get("claim_reason", "")
        claimed_amount = claim_data.get("claim_amount", 0)

        # Validate against receipts and documentation
        supporting_docs_provided = claim_data.get("supporting_docs_provided", [])
        doc_score = len(supporting_docs_provided) / 3  # Typical 3 doc types

        estimated_value = claimed_amount * doc_score
        confidence = 0.75 + (doc_score * 0.20)

        return {
            "method": "travel_valuation",
            "claim_reason": claim_reason,
            "claimed_amount": round(claimed_amount, 2),
            "supporting_documentation_score": round(doc_score, 2),
            "estimated_value": round(estimated_value, 2),
            "confidence": round(confidence, 2)
        }

    def _determine_valuation_method(self, claim_type: str, claim_data: Dict[str, Any]) -> str:
        """Determine which valuation method to use."""
        if claim_type in ["auto", "property"]:
            if claim_data.get("damage_percentage", 0) >= 80:
                return "total_loss"
            else:
                return "partial_damage"
        elif claim_type == "health":
            return "network_negotiated"
        elif claim_type == "life":
            return "death_benefit"
        else:
            return "standard"

    def _calculate_adjusted_value(self, valuation: Dict[str, Any], deductible: float, coverage_limit: float) -> float:
        """Calculate adjusted claim value after deductible and coverage limits."""
        estimated_value = valuation.get("estimated_value", 0)
        adjusted = max(estimated_value - deductible, 0)
        adjusted = min(adjusted, coverage_limit)
        return adjusted

    def _calculate_reserves(
        self,
        claim_data: Dict[str, Any],
        adjusted_value: float,
        valuation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate reserve recommendations for claim."""
        claimed_amount = claim_data.get("claim_amount", 0)
        estimated_value = valuation.get("estimated_value", 0)
        confidence = valuation.get("confidence", 0.8)

        # Case reserves
        case_reserve = adjusted_value

        # IBNR (Incurred But Not Reported) - for potential hidden damages
        ibnr_reserve = adjusted_value * (1 - confidence) * 0.5

        # Litigation reserve - if claim disputed
        is_disputed = claim_data.get("is_disputed", False)
        litigation_reserve = (adjusted_value * 0.25) if is_disputed else 0

        # Investigation reserve - if fraud suspected
        fraud_risk = claim_data.get("fraud_risk_score", 0)
        investigation_reserve = adjusted_value * fraud_risk * 0.3

        total_reserve = case_reserve + ibnr_reserve + litigation_reserve + investigation_reserve

        return {
            "case_reserve": round(case_reserve, 2),
            "ibnr_reserve": round(ibnr_reserve, 2),
            "litigation_reserve": round(litigation_reserve, 2),
            "investigation_reserve": round(investigation_reserve, 2),
            "total_reserve": round(total_reserve, 2),
            "reserve_confidence": round(confidence, 2)
        }

    def _assess_financial_risk(
        self,
        claim_data: Dict[str, Any],
        valuation: Dict[str, Any],
        adjusted_value: float
    ) -> Dict[str, Any]:
        """Assess financial risk exposure."""
        claimed_amount = claim_data.get("claim_amount", 0)
        estimated_value = valuation.get("estimated_value", 0)
        claim_type = claim_data.get("claim_type", "auto")

        # Calculate potential variance
        variance = abs(estimated_value - claimed_amount)
        variance_pct = (variance / claimed_amount * 100) if claimed_amount > 0 else 0

        # Determine risk factors
        high_value = adjusted_value > self.COVERAGE_LIMITS.get(claim_type, 500000) * 0.7
        significant_variance = variance_pct > 30
        fraud_risk = claim_data.get("fraud_risk_score", 0) > 0.6
        is_disputed = claim_data.get("is_disputed", False)

        risk_level = "low"
        if is_disputed or fraud_risk:
            risk_level = "high"
        elif high_value and significant_variance:
            risk_level = "high"
        elif significant_variance:
            risk_level = "medium"

        return {
            "risk_level": risk_level,
            "claim_variance_percentage": round(variance_pct, 1),
            "high_value_claim": high_value,
            "is_disputed": is_disputed,
            "fraud_risk": fraud_risk > 0.6,
            "total_exposure": round(adjusted_value, 2),
            "risk_factors": [
                f"High-value claim (${adjusted_value:,.0f})" if high_value else None,
                f"Significant variance ({variance_pct:.0f}%)" if significant_variance else None,
                "Fraud risk detected" if fraud_risk else None,
                "Disputed claim" if is_disputed else None,
            ]
        }

    def _generate_payment_recommendations(self, approved_amount: float, claim_type: str) -> Dict[str, Any]:
        """Generate payment recommendations."""
        if approved_amount == 0:
            return {
                "recommendation": "deny",
                "reason": "Claim does not meet policy requirements",
                "payment_status": "not_approved"
            }
        elif approved_amount > 100000:
            return {
                "recommendation": "hold_for_review",
                "reason": "Large claim amount requires additional review",
                "payment_status": "pending_management_review",
                "suggested_review_level": "supervisor"
            }
        else:
            return {
                "recommendation": "approve",
                "reason": "Claim meets policy requirements and valuation",
                "payment_status": "ready_for_payment",
                "payment_method": "direct_deposit"
            }

    def _generate_financial_reasoning(
        self,
        claimed_amount: float,
        approved_amount: float,
        valuation: Dict[str, Any]
    ) -> str:
        """Generate human-readable financial reasoning."""
        estimated = valuation.get("estimated_value", 0)
        approval_pct = (approved_amount / claimed_amount * 100) if claimed_amount > 0 else 0

        if approved_amount == 0:
            return "Claim does not meet policy coverage requirements or valuation does not support payment."
        elif approval_pct >= 95:
            return f"Claim approved for ~{approval_pct:.0f}% of requested amount. Fair market valuation supports approved amount."
        elif approval_pct >= 75:
            return f"Claim approved for {approval_pct:.0f}% of requested amount. Partial approval due to deductible and policy limits."
        else:
            return f"Claim approved for {approval_pct:.0f}% of requested amount. Significant difference between claim and valuation requires further review."

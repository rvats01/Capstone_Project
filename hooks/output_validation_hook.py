"""OutputValidationHook: Validates final decisions before delivery."""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

VALID_DECISIONS = {"approved", "rejected", "referred", "partial_approval", "fraud_suspected", "under_review"}
REQUIRED_OUTPUT_FIELDS = ["decision", "decision_reason", "final_score"]


class OutputValidationHook:
    """Validates and normalizes final claim decision output."""

    def __init__(self):
        self.name = "OutputValidationHook"

    def execute(
        self,
        decision_result: dict,
        fraud_score: float,
        compliance_result: dict
    ) -> Tuple[bool, dict, list]:
        """
        Validate the final output before sending to client.
        Returns: (is_valid, validated_output, validation_errors)
        """
        errors = []
        validated = dict(decision_result)

        # Check required fields
        for field in REQUIRED_OUTPUT_FIELDS:
            if field not in decision_result or decision_result[field] is None:
                errors.append(f"Missing required output field: {field}")

        # Validate decision value
        decision = decision_result.get("decision", "")
        if decision not in VALID_DECISIONS:
            errors.append(f"Invalid decision value '{decision}'. Must be one of {VALID_DECISIONS}")
            # Default to safe fallback
            validated["decision"] = "under_review"

        # Validate score range
        final_score = float(decision_result.get("final_score", 0))
        if not 0.0 <= final_score <= 1.0:
            errors.append(f"final_score {final_score} out of range [0,1]")
            validated["final_score"] = max(0.0, min(1.0, final_score))

        # Validate approved amount makes sense
        if decision == "rejected" and float(decision_result.get("approved_amount", 0)) > 0:
            errors.append("Rejected claim should not have approved_amount > 0")
            validated["approved_amount"] = 0.0

        # Safety check: High fraud score should NOT be approved
        if fraud_score > 0.85 and decision == "approved":
            errors.append(f"Safety block: fraud_score {fraud_score:.2f} too high for approval")
            validated["decision"] = "fraud_suspected"
            validated["decision_reason"] = f"Blocked by OutputValidationHook: fraud score {fraud_score:.2f}"
            validated["approved_amount"] = 0.0

        # Ensure decision reason is not empty for rejections
        if decision in {"rejected", "fraud_suspected"} and not decision_result.get("decision_reason"):
            errors.append("Rejection/fraud decision must include decision_reason")
            validated["decision_reason"] = "Rejected due to assessment findings"

        # Add output metadata
        validated["_validated"] = True
        validated["_validation_errors"] = errors

        is_valid = len([e for e in errors if "Safety block" in e or "Missing required" in e]) == 0
        logger.info(f"[OutputValidationHook] valid={is_valid}, decision={validated.get('decision')}, errors={errors}")
        return is_valid, validated, errors

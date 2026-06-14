"""GovernanceHook: Enforces business rules and regulatory governance constraints."""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Business rules thresholds
LARGE_CLAIM_THRESHOLD = 100_000   # Requires escalation
FRAUD_AUTO_REJECT = 0.90          # Fraud score above this = auto-reject
FRAUD_REFER_THRESHOLD = 0.65      # Fraud score above this = refer to investigation
COMPLIANCE_BLOCK_THRESHOLD = 0.5  # Compliance score below this = block
MAX_CLAIM_PER_YEAR = 5            # Max claims per customer per year (simulated check)


class GovernanceHook:
    """Enforces governance rules during claim assessment."""

    def __init__(self):
        self.name = "GovernanceHook"

    def pre_assessment(self, claim_data: dict) -> Tuple[bool, list]:
        """
        Apply governance rules before assessment starts.
        Returns: (can_proceed, governance_notes)
        """
        notes = []
        can_proceed = True

        # Check claim amount governance
        amount = float(claim_data.get("claim_amount", 0))
        if amount >= LARGE_CLAIM_THRESHOLD:
            notes.append(f"Large claim (${amount:,.2f}) — dual approval required per SOX-001")
            notes.append("CFO notification required for claims above $100,000")

        # Escalation flag for life insurance claims
        if claim_data.get("claim_type") == "life":
            notes.append("Life insurance claim — enhanced validation required")
            notes.append("Medical examiner report mandatory")

        logger.info(f"[GovernanceHook] pre_assessment: notes={notes}")
        return can_proceed, notes

    def post_risk_assessment(self, risk_result: dict) -> Tuple[bool, str, list]:
        """
        Apply governance rules after risk assessment.
        Returns: (can_continue, override_decision, actions)
        """
        actions = []
        fraud_score = float(risk_result.get("fraud_score", 0))
        investigation_required = risk_result.get("investigation_required", False)

        # Auto-reject for critical fraud
        if fraud_score >= FRAUD_AUTO_REJECT:
            actions.append(f"AUTO-REJECT: Fraud score {fraud_score:.2f} exceeds threshold {FRAUD_AUTO_REJECT}")
            actions.append("Case referred to Special Investigations Unit (SIU)")
            actions.append("Regulatory notification required under IRDAI-002")
            return True, "fraud_suspected", actions

        # Refer for investigation
        if fraud_score >= FRAUD_REFER_THRESHOLD or investigation_required:
            actions.append(f"REFER: Fraud score {fraud_score:.2f} requires investigation")
            actions.append("Claim placed on hold pending investigation")
            return True, "referred", actions

        return True, None, actions

    def post_compliance_check(self, compliance_result: dict) -> Tuple[bool, list]:
        """
        Apply governance rules after compliance check.
        Returns: (compliant, blocking_actions)
        """
        blocking = []
        blocking_violations = compliance_result.get("blocking_violations", [])
        overall = compliance_result.get("overall_compliance", "pass")
        compliance_score = float(compliance_result.get("compliance_score", 1.0))

        if overall == "fail" or blocking_violations:
            blocking.append(f"BLOCK: Compliance violations found: {blocking_violations}")
            blocking.append("Claim cannot proceed without resolving compliance issues")
            return False, blocking

        if compliance_score < COMPLIANCE_BLOCK_THRESHOLD:
            blocking.append(f"BLOCK: Compliance score {compliance_score:.2f} below minimum {COMPLIANCE_BLOCK_THRESHOLD}")
            return False, blocking

        return True, []

    def validate_final_decision(self, decision_result: dict, claim_data: dict) -> Tuple[bool, list]:
        """
        Final governance validation of decision.
        Returns: (approved, governance_checks)
        """
        checks = []
        decision = decision_result.get("decision", "")
        approved_amount = float(decision_result.get("approved_amount", 0))
        claim_amount = float(claim_data.get("claim_amount", 0))

        # Can't approve more than claimed
        if approved_amount > claim_amount * 1.01:  # Allow 1% tolerance
            checks.append(f"ERROR: Approved amount ${approved_amount:,.2f} exceeds claimed ${claim_amount:,.2f}")
            decision_result["approved_amount"] = min(approved_amount, claim_amount)

        # Large approvals need escalation flag
        if approved_amount >= LARGE_CLAIM_THRESHOLD and decision == "approved":
            checks.append(f"ESCALATION: Large approval ${approved_amount:,.2f} requires senior approval")

        # Ensure rejected claims have reason
        if decision == "rejected" and not decision_result.get("decision_reason"):
            checks.append("GOVERNANCE: Rejection must include documented reason")

        logger.info(f"[GovernanceHook] final_decision: decision={decision}, checks={len(checks)}")
        return True, checks

"""Compliance Validation Skill - IRDAI, SOX, AML, and regulatory compliance checking."""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ComplianceValidator:
    """Validates insurance claims against regulatory requirements."""

    # IRDAI Regulations
    IRDAI_CLAIM_SETTLEMENT_DAYS = 30
    IRDAI_MIN_DOCUMENTATION = ["policy_proof", "incident_proof", "identity_proof"]
    IRDAI_CLAIM_LIMIT_VERIFICATION_REQUIRED = 500000

    # SOX Requirements
    SOX_DUAL_APPROVAL_THRESHOLD = 1000000
    SOX_AUTO_AUDIT_TRAIL = True
    SOX_RETENTION_YEARS = 7

    # AML Thresholds
    AML_HIGH_ALERT_AMOUNT = 10000
    AML_EXTREMELY_SUSPICIOUS_AMOUNT = 100000

    def __init__(self):
        self.name = "ComplianceValidator"
        logger.info(f"Initialized {self.name}")

    def validate_compliance(
        self,
        claim_data: Dict[str, Any],
        regulations: List[Dict[str, Any]],
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive compliance validation.

        Args:
            claim_data: Current claim information
            regulations: Applicable regulatory rules
            customer_data: Customer information for KYC/AML checks

        Returns:
            Dictionary with complete compliance assessment
        """
        irdai_result = self._check_irdai_compliance(claim_data)
        sox_result = self._check_sox_compliance(claim_data, regulations)
        aml_result = self._check_aml_compliance(claim_data, customer_data)

        # Compile overall assessment
        blocking_violations = []
        blocking_violations.extend(irdai_result.get("blocking_violations", []))
        blocking_violations.extend(sox_result.get("blocking_violations", []))
        blocking_violations.extend(aml_result.get("blocking_violations", []))

        overall_compliance = "fail" if blocking_violations else "pass"
        compliance_score = self._calculate_compliance_score(irdai_result, sox_result, aml_result)

        return {
            "overall_compliance": overall_compliance,
            "irdai_checks": irdai_result,
            "sox_checks": sox_result,
            "aml_checks": aml_result,
            "compliance_score": round(compliance_score, 3),
            "blocking_violations": blocking_violations,
            "warnings": self._compile_warnings(irdai_result, sox_result, aml_result),
            "mandatory_actions": self._compile_mandatory_actions(irdai_result, sox_result, aml_result),
            "reasoning": self._generate_compliance_reasoning(overall_compliance, blocking_violations),
            "confidence": 0.95
        }

    def _check_irdai_compliance(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check IRDAI (Insurance Regulatory and Development Authority of India) compliance."""
        violations = []
        blocking_violations = []

        claim_type = claim_data.get("claim_type", "").lower()
        claim_amount = claim_data.get("claim_amount", 0)
        incident_date = claim_data.get("incident_date", "")
        policy_active = claim_data.get("policy_active", True)
        documentation = claim_data.get("documentation", [])

        # Check 1: Policy must be active
        if not policy_active:
            violations.append("Policy is not active for this claim period")
            blocking_violations.append("IRDAI-001: Inactive policy cannot process claims")

        # Check 2: Claim filed within IRDAI time limits
        if incident_date:
            try:
                incident_dt = datetime.fromisoformat(incident_date)
                days_since_incident = (datetime.now() - incident_dt).days
                if days_since_incident > 365:
                    violations.append(f"Claim filed {days_since_incident} days after incident (limit: 365 days)")
                    blocking_violations.append("IRDAI-002: Claim filing deadline exceeded")
            except:
                pass

        # Check 3: Required documentation present
        missing_docs = [doc for doc in self.IRDAI_MIN_DOCUMENTATION if doc not in documentation]
        if missing_docs:
            violations.append(f"Missing required documentation: {', '.join(missing_docs)}")

        # Check 4: Claim within policy limits (simulated)
        if claim_amount > 10000000:
            violations.append(f"Claim amount ${claim_amount:,.0f} exceeds typical policy limits")

        # Check 5: Claim type validity
        valid_claim_types = ["health", "auto", "property", "life", "travel"]
        if claim_type not in valid_claim_types:
            violations.append(f"Unknown claim type: {claim_type}")

        return {
            "claim_time_limit_ok": (datetime.now() - datetime.fromisoformat(incident_date)).days <= 365 if incident_date else False,
            "policy_active_ok": policy_active,
            "documentation_ok": len(missing_docs) == 0,
            "amount_within_limits": claim_amount <= 10000000,
            "claim_type_valid": claim_type in valid_claim_types,
            "violations": violations,
            "blocking_violations": blocking_violations
        }

    def _check_sox_compliance(self, claim_data: Dict[str, Any], regulations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check SOX (Sarbanes-Oxley Act) compliance for large claims."""
        violations = []
        blocking_violations = []
        claim_amount = claim_data.get("claim_amount", 0)

        # Check 1: Dual approval requirement
        dual_approval_required = claim_amount > self.SOX_DUAL_APPROVAL_THRESHOLD
        approval_count = claim_data.get("approval_count", 0)
        if dual_approval_required and approval_count < 2:
            violations.append(f"Large claim (${claim_amount:,.0f}) requires dual approval (current: {approval_count})")

        # Check 2: Audit trail completeness
        has_audit_trail = claim_data.get("audit_trail_created", False)
        if self.SOX_AUTO_AUDIT_TRAIL and not has_audit_trail:
            violations.append("SOX audit trail not created for claim processing")

        # Check 3: Reporting requirements
        reporting_completed = claim_data.get("financial_reporting_completed", True)
        if not reporting_completed and claim_amount > 500000:
            violations.append("Financial reporting not completed for material claim amount")

        # Check 4: Data retention compliance
        retention_years = claim_data.get("retention_policy_years", 7)
        if retention_years < self.SOX_RETENTION_YEARS:
            violations.append(f"Retention policy insufficient: {retention_years} years (required: {self.SOX_RETENTION_YEARS})")

        return {
            "dual_approval_required": dual_approval_required,
            "dual_approval_met": approval_count >= 2 if dual_approval_required else True,
            "audit_trail_complete": has_audit_trail,
            "reporting_requirements_met": reporting_completed,
            "retention_policy_compliant": retention_years >= self.SOX_RETENTION_YEARS,
            "violations": violations,
            "blocking_violations": blocking_violations
        }

    def _check_aml_compliance(self, claim_data: Dict[str, Any], customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check AML (Anti-Money Laundering) and KYC (Know Your Customer) compliance."""
        violations = []
        blocking_violations = []

        claim_amount = claim_data.get("claim_amount", 0)
        customer_id = customer_data.get("customer_id", "")
        kyc_completed = customer_data.get("kyc_completed", False)
        aml_screening_passed = customer_data.get("aml_screening_passed", True)

        # Check 1: KYC completion
        if not kyc_completed:
            violations.append("KYC not completed for customer")
            blocking_violations.append("AML-001: KYC verification required before claim processing")

        # Check 2: AML screening
        if not aml_screening_passed:
            violations.append("Customer failed AML screening")
            blocking_violations.append("AML-002: Customer on AML watchlist - immediate escalation required")

        # Check 3: Suspicious transaction detection
        transaction_suspicious = False
        pep_status = customer_data.get("pep_status", False)
        if pep_status:
            transaction_suspicious = True
            violations.append("Politically Exposed Person (PEP) detected - enhanced due diligence required")

        # Check 4: Structuring detection
        recent_claims = customer_data.get("recent_claims_count", 0)
        structuring_detected = False
        if recent_claims > 3 and claim_amount > self.AML_HIGH_ALERT_AMOUNT:
            structuring_detected = True
            violations.append(f"Possible structuring detected: {recent_claims} claims in recent period")

        # Check 5: High-value transaction alert
        high_value_transaction = claim_amount > self.AML_EXTREMELY_SUSPICIOUS_AMOUNT

        return {
            "transaction_suspicious": transaction_suspicious,
            "kyc_required": not kyc_completed,
            "kyc_completed": kyc_completed,
            "aml_screening_passed": aml_screening_passed,
            "pep_status": pep_status,
            "structuring_suspected": structuring_detected,
            "high_value_transaction": high_value_transaction,
            "violations": violations,
            "blocking_violations": blocking_violations
        }

    def _calculate_compliance_score(
        self,
        irdai: Dict[str, Any],
        sox: Dict[str, Any],
        aml: Dict[str, Any]
    ) -> float:
        """Calculate overall compliance score."""
        score = 1.0

        # Deduct for IRDAI violations
        irdai_violations = len(irdai.get("violations", []))
        score -= irdai_violations * 0.1

        # Deduct for SOX violations
        sox_violations = len(sox.get("violations", []))
        score -= sox_violations * 0.15

        # Deduct for AML violations (most critical)
        aml_violations = len(aml.get("violations", []))
        score -= aml_violations * 0.25

        # Deduct for blocking violations
        all_blocking = len(irdai.get("blocking_violations", []) +
                          sox.get("blocking_violations", []) +
                          aml.get("blocking_violations", []))
        score -= all_blocking * 0.2

        return max(score, 0.0)

    def _compile_warnings(
        self,
        irdai: Dict[str, Any],
        sox: Dict[str, Any],
        aml: Dict[str, Any]
    ) -> List[str]:
        """Compile all warnings from compliance checks."""
        warnings = []

        for violation in irdai.get("violations", []):
            if violation not in irdai.get("blocking_violations", []):
                warnings.append(f"IRDAI: {violation}")

        for violation in sox.get("violations", []):
            if violation not in sox.get("blocking_violations", []):
                warnings.append(f"SOX: {violation}")

        for violation in aml.get("violations", []):
            if violation not in aml.get("blocking_violations", []):
                warnings.append(f"AML: {violation}")

        return warnings

    def _compile_mandatory_actions(
        self,
        irdai: Dict[str, Any],
        sox: Dict[str, Any],
        aml: Dict[str, Any]
    ) -> List[str]:
        """Compile mandatory actions required for compliance."""
        actions = []

        if not irdai.get("policy_active_ok", False):
            actions.append("Verify policy is active before processing")

        if not irdai.get("documentation_ok", False):
            actions.append("Collect missing required documentation")

        if sox.get("dual_approval_required", False) and not sox.get("dual_approval_met", False):
            actions.append("Obtain second-level approval for large claim amount")

        if not aml.get("kyc_completed", False):
            actions.append("Complete KYC verification for customer")

        if aml.get("pep_status", False):
            actions.append("Escalate to Compliance Officer for PEP enhanced due diligence")

        if not sox.get("audit_trail_complete", False):
            actions.append("Create complete audit trail for claim processing")

        return actions

    def _generate_compliance_reasoning(self, overall_compliance: str, blocking_violations: List[str]) -> str:
        """Generate human-readable compliance reasoning."""
        if overall_compliance == "fail":
            violation_list = "\n".join([f"  • {v}" for v in blocking_violations[:3]])
            return f"COMPLIANCE FAILED: The following blocking violations must be resolved:\n{violation_list}" + \
                   (f"\n  ... and {len(blocking_violations) - 3} more" if len(blocking_violations) > 3 else "")
        else:
            return "COMPLIANCE PASSED: Claim meets all regulatory requirements for IRDAI, SOX, and AML standards. Processing can proceed."

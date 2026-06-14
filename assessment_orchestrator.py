"""
Assessment Orchestrator: Coordinates all agents, hooks, MCP, and tools
for the full insurance claim assessment pipeline.
"""

import logging
import asyncio
from datetime import datetime

from agents.customer_agent import CustomerAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.compliance_agent import ComplianceAgent
from agents.risk_agent import RiskAgent
from agents.decision_agent import DecisionAgent
from agents.audit_agent import AuditAgent

from hooks.input_validation_hook import InputValidationHook
from hooks.security_hook import SecurityHook
from hooks.governance_hook import GovernanceHook
from hooks.audit_hook import AuditHook
from hooks.output_validation_hook import OutputValidationHook

from mcp_server.regulatory_knowledge_mcp import mcp_server
from tools.document_processing_tool import DocumentProcessingTool

logger = logging.getLogger(__name__)


class AssessmentOrchestrator:
    """
    Orchestrates the full multi-agent insurance claim assessment pipeline.

    Pipeline:
    InputValidation → Security → CustomerAgent → KnowledgeAgent (MCP)
    → ComplianceAgent || RiskAgent (parallel) → GovernanceCheck
    → DecisionAgent → AuditAgent → OutputValidation → Result
    """

    def __init__(self):
        # Agents
        self.customer_agent = CustomerAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.compliance_agent = ComplianceAgent()
        self.risk_agent = RiskAgent()
        self.decision_agent = DecisionAgent()
        self.audit_agent = AuditAgent()

        # Hooks
        self.input_validation_hook = InputValidationHook()
        self.security_hook = SecurityHook()
        self.governance_hook = GovernanceHook()
        self.audit_hook = AuditHook()
        self.output_validation_hook = OutputValidationHook()

        # Tools
        self.doc_tool = DocumentProcessingTool()

    async def assess_claim(
        self,
        claim_id: str,
        claim_data: dict,
        client_ip: str = "unknown"
    ) -> dict:
        """
        Run the complete multi-agent assessment pipeline.
        Returns full assessment result with traceability.
        """
        pipeline_start = datetime.utcnow()
        assessment_log = []

        try:
            # ─── PHASE 1: Input Validation Hook ───────────────────────────
            logger.info(f"[Orchestrator] Phase 1: Input Validation for {claim_id}")
            is_valid, sanitized_data, val_errors = self.input_validation_hook.execute(claim_data)
            self.audit_hook.record_hook_execution(claim_id, "InputValidationHook", is_valid, val_errors)

            if not is_valid:
                return self._error_response(claim_id, "Input validation failed", val_errors, pipeline_start)

            assessment_log.append({"phase": "input_validation", "status": "passed", "errors": val_errors})

            # ─── PHASE 2: Security Hook ────────────────────────────────────
            logger.info(f"[Orchestrator] Phase 2: Security Check for {claim_id}")
            is_secure, secured_data, sec_issues = self.security_hook.execute(sanitized_data, client_ip)
            self.audit_hook.record_hook_execution(claim_id, "SecurityHook", is_secure, sec_issues)

            if not is_secure:
                return self._error_response(claim_id, "Security check failed", sec_issues, pipeline_start)

            assessment_log.append({"phase": "security_check", "status": "passed", "issues": sec_issues})

            # ─── PHASE 3: Governance Pre-Check ────────────────────────────
            logger.info(f"[Orchestrator] Phase 3: Governance Pre-Check for {claim_id}")
            can_proceed, gov_notes = self.governance_hook.pre_assessment(secured_data)
            self.audit_hook.record(claim_id, "GovernanceHook", "pre_assessment", output_data={"notes": gov_notes})

            assessment_log.append({"phase": "governance_precheck", "status": "passed", "notes": gov_notes})

            # ─── PHASE 4: Document Processing ─────────────────────────────
            logger.info(f"[Orchestrator] Phase 4: Document Processing for {claim_id}")
            doc_analysis = self.doc_tool.extract_from_structured_form(secured_data)
            self.audit_hook.record(claim_id, "DocumentProcessingTool", "process_document",
                                   output_data={"quality": doc_analysis.get("document_analysis", {}).get("quality_score")})

            # ─── PHASE 5: MCP - Regulatory Knowledge Retrieval ─────────────
            logger.info(f"[Orchestrator] Phase 5: MCP Regulatory Knowledge for {claim_id}")
            claim_type = secured_data.get("claim_type", "auto")

            regulations = mcp_server.query_regulations("ALL", claim_type=claim_type)
            fraud_patterns = mcp_server.get_fraud_patterns(claim_type, severity="medium")
            policy_limits = mcp_server.get_policy_limits(claim_type, float(secured_data.get("claim_amount", 0)))

            self.audit_hook.record(claim_id, "RegulatoryKnowledgeMCP", "query_regulations",
                                   output_data={"regulations_found": len(regulations), "fraud_patterns": len(fraud_patterns)})

            assessment_log.append({"phase": "mcp_knowledge", "regulations": len(regulations), "fraud_patterns": len(fraud_patterns)})

            # ─── PHASE 6: CustomerAgent ────────────────────────────────────
            logger.info(f"[Orchestrator] Phase 6: CustomerAgent for {claim_id}")
            customer_result = await asyncio.get_event_loop().run_in_executor(
                None, self.customer_agent.process, secured_data
            )
            self.audit_hook.record(claim_id, "CustomerAgent", "validate_customer",
                                   output_data={"confidence": customer_result.confidence, "success": customer_result.success},
                                   duration_ms=customer_result.duration_ms)

            customer_data = customer_result.data if customer_result.success else {}
            assessment_log.append({"phase": "customer_agent", "confidence": customer_result.confidence})

            # ─── PHASE 7: KnowledgeAgent (MCP-enhanced) ───────────────────
            logger.info(f"[Orchestrator] Phase 7: KnowledgeAgent for {claim_id}")
            knowledge_result = await asyncio.get_event_loop().run_in_executor(
                None, self.knowledge_agent.process, secured_data, regulations
            )
            self.audit_hook.record(claim_id, "KnowledgeAgent", "retrieve_knowledge",
                                   output_data={"confidence": knowledge_result.confidence},
                                   duration_ms=knowledge_result.duration_ms)

            knowledge_data = knowledge_result.data if knowledge_result.success else {}
            assessment_log.append({"phase": "knowledge_agent", "confidence": knowledge_result.confidence})

            # ─── PHASE 8: ComplianceAgent + RiskAgent (parallel-simulated) ─
            logger.info(f"[Orchestrator] Phase 8: Compliance + Risk Agents (parallel) for {claim_id}")

            compliance_result, risk_result = await asyncio.gather(
                asyncio.get_event_loop().run_in_executor(
                    None, self.compliance_agent.process, secured_data, knowledge_data
                ),
                asyncio.get_event_loop().run_in_executor(
                    None, self.risk_agent.process, secured_data, customer_data, fraud_patterns
                )
            )

            compliance_data = compliance_result.data if compliance_result.success else {}
            risk_data = risk_result.data if risk_result.success else {}

            self.audit_hook.record(claim_id, "ComplianceAgent", "validate_compliance",
                                   output_data={"compliance": compliance_data.get("overall_compliance"), "score": compliance_data.get("compliance_score")},
                                   duration_ms=compliance_result.duration_ms)
            self.audit_hook.record(claim_id, "RiskAgent", "assess_risk",
                                   output_data={"fraud_score": risk_data.get("fraud_score"), "risk_level": risk_data.get("risk_level")},
                                   duration_ms=risk_result.duration_ms)

            assessment_log.append({
                "phase": "parallel_assessment",
                "compliance": compliance_data.get("overall_compliance", "unknown"),
                "fraud_score": risk_data.get("fraud_score", 0)
            })

            # ─── PHASE 9: Governance Post-Risk Check ──────────────────────
            logger.info(f"[Orchestrator] Phase 9: Governance Post-Risk for {claim_id}")
            _, risk_override, risk_actions = self.governance_hook.post_risk_assessment(risk_data)
            compliance_ok, compliance_blocks = self.governance_hook.post_compliance_check(compliance_data)

            gov_audit_data = {"risk_override": risk_override, "compliance_blocks": compliance_blocks}
            self.audit_hook.record(claim_id, "GovernanceHook", "post_assessment", output_data=gov_audit_data)

            # ─── PHASE 10: DecisionAgent ───────────────────────────────────
            logger.info(f"[Orchestrator] Phase 10: DecisionAgent for {claim_id}")
            decision_result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.decision_agent.process,
                secured_data, customer_data, knowledge_data, compliance_data, risk_data
            )

            decision_data = decision_result.data if decision_result.success else {}

            # Apply governance override if needed
            if risk_override:
                decision_data["decision"] = risk_override
                decision_data["approved_amount"] = 0.0
                decision_data["decision_reason"] = f"Governance override: {'; '.join(risk_actions)}"

            if not compliance_ok:
                decision_data["decision"] = "rejected"
                decision_data["approved_amount"] = 0.0
                decision_data["decision_reason"] = f"Compliance block: {'; '.join(compliance_blocks)}"

            self.audit_hook.record(claim_id, "DecisionAgent", "final_decision",
                                   output_data={"decision": decision_data.get("decision"), "amount": decision_data.get("approved_amount")},
                                   duration_ms=decision_result.duration_ms)

            # ─── PHASE 11: Output Validation Hook ─────────────────────────
            logger.info(f"[Orchestrator] Phase 11: Output Validation for {claim_id}")
            out_valid, validated_decision, out_errors = self.output_validation_hook.execute(
                decision_data,
                float(risk_data.get("fraud_score", 0)),
                compliance_data
            )
            self.audit_hook.record_hook_execution(claim_id, "OutputValidationHook", out_valid, out_errors)

            # ─── PHASE 12: AuditAgent ──────────────────────────────────────
            logger.info(f"[Orchestrator] Phase 12: AuditAgent for {claim_id}")
            audit_result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.audit_agent.process,
                claim_id, secured_data, customer_data, knowledge_data,
                compliance_data, risk_data, validated_decision
            )

            audit_data = audit_result.data if audit_result.success else {}
            self.audit_hook.record(claim_id, "AuditAgent", "generate_audit_report",
                                   output_data={"audit_hash": audit_data.get("audit_hash"), "compliance_attestation": audit_data.get("compliance_attestation")},
                                   duration_ms=audit_result.duration_ms)

            # ─── FINAL: Compile Assessment Result ─────────────────────────
            duration_total = int((datetime.utcnow() - pipeline_start).total_seconds() * 1000)

            return {
                "claim_id": claim_id,
                "status": "assessed",
                "decision": validated_decision.get("decision", "under_review"),
                "decision_reason": validated_decision.get("decision_reason", ""),
                "approved_amount": float(validated_decision.get("approved_amount", 0)),
                "final_score": float(validated_decision.get("final_score", 0)),
                "score_breakdown": validated_decision.get("score_breakdown", {}),

                "risk_assessment": {
                    "fraud_score": float(risk_data.get("fraud_score", 0)),
                    "risk_level": risk_data.get("risk_level", "medium"),
                    "fraud_indicators": risk_data.get("fraud_indicators", []),
                    "investigation_required": risk_data.get("investigation_required", False)
                },

                "compliance_assessment": {
                    "overall_compliance": compliance_data.get("overall_compliance", "unknown"),
                    "compliance_score": float(compliance_data.get("compliance_score", 0)),
                    "blocking_violations": compliance_data.get("blocking_violations", []),
                    "irdai_compliant": compliance_data.get("irdai_checks", {}).get("violations", []) == [],
                    "aml_cleared": not compliance_data.get("aml_checks", {}).get("transaction_suspicious", False)
                },

                "customer_assessment": {
                    "identity_validated": customer_data.get("customer_validated", False),
                    "identity_confidence": float(customer_data.get("identity_confidence", 0)),
                    "behavioral_flags": customer_data.get("behavioral_flags", [])
                },

                "document_analysis": doc_analysis.get("document_analysis", {}),

                "policy_limits": policy_limits,

                "audit": {
                    "audit_hash": audit_data.get("audit_hash", ""),
                    "compliance_attestation": audit_data.get("compliance_attestation", {}),
                    "decision_chain": audit_data.get("decision_chain", []),
                    "timeline_steps": len(audit_data.get("timeline", [])),
                    "generated_at": audit_data.get("generated_at", "")
                },

                "agent_reasoning": {
                    "customer": customer_data.get("reasoning", ""),
                    "compliance": compliance_data.get("reasoning", ""),
                    "risk": risk_data.get("reasoning", ""),
                    "decision": validated_decision.get("decision_reason", ""),
                    "explainability": validated_decision.get("explainability", {})
                },

                "governance_notes": gov_notes + risk_actions + compliance_blocks,
                "pipeline_log": assessment_log,
                "total_duration_ms": duration_total,
                "assessed_at": datetime.utcnow().isoformat(),
                "pipeline_version": "1.0.0"
            }

        except Exception as e:
            logger.error(f"[Orchestrator] Pipeline error for {claim_id}: {e}", exc_info=True)
            return self._error_response(claim_id, f"Assessment pipeline error: {str(e)}", [], pipeline_start)

    def get_audit_trail(self, claim_id: str) -> list:
        """Get in-memory audit trail for a claim."""
        return self.audit_hook.get_claim_audit_trail(claim_id)

    def _error_response(self, claim_id: str, reason: str, details: list, start: datetime) -> dict:
        duration = int((datetime.utcnow() - start).total_seconds() * 1000)
        return {
            "claim_id": claim_id,
            "status": "error",
            "decision": "rejected",
            "decision_reason": reason,
            "approved_amount": 0.0,
            "final_score": 0.0,
            "error_details": details,
            "total_duration_ms": duration,
            "assessed_at": datetime.utcnow().isoformat()
        }


# Singleton orchestrator
orchestrator = AssessmentOrchestrator()

"""AuditHook: Captures all agent interactions for traceability."""

import json
import logging
import time
import hashlib
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

_audit_buffer = []  # In-memory buffer before DB flush


class AuditHook:
    """Records every agent interaction immutably."""

    def __init__(self):
        self.name = "AuditHook"

    def record(
        self,
        claim_id: str,
        agent_name: str,
        action: str,
        input_data: Optional[dict] = None,
        output_data: Optional[dict] = None,
        hook_applied: Optional[str] = None,
        compliance_check: Optional[str] = None,
        passed: bool = True,
        duration_ms: int = 0
    ) -> dict:
        """Record an audit event."""
        entry = {
            "claim_id": claim_id,
            "agent_name": agent_name,
            "action": action,
            "input_summary": self._summarize(input_data),
            "output_summary": self._summarize(output_data),
            "hook_applied": hook_applied,
            "compliance_check": compliance_check,
            "passed": passed,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Compute integrity hash
        entry["audit_hash"] = self._compute_hash(entry)

        # Buffer for batch DB write
        _audit_buffer.append(entry)
        logger.info(f"[AuditHook] recorded: claim={claim_id}, agent={agent_name}, action={action}")
        return entry

    def record_hook_execution(self, claim_id: str, hook_name: str, passed: bool, details: list):
        """Record hook execution in audit trail."""
        return self.record(
            claim_id=claim_id,
            agent_name="HOOK",
            action=f"hook_executed:{hook_name}",
            output_data={"details": details, "passed": passed},
            hook_applied=hook_name,
            passed=passed
        )

    def get_claim_audit_trail(self, claim_id: str) -> list:
        """Get all audit records for a claim."""
        return [e for e in _audit_buffer if e.get("claim_id") == claim_id]

    def flush_to_db_records(self, claim_id: str) -> list:
        """Get records ready for DB persistence."""
        records = [e for e in _audit_buffer if e.get("claim_id") == claim_id]
        return records

    def _summarize(self, data: Optional[dict]) -> Optional[dict]:
        """Create a compact summary for storage (avoid huge blob storage)."""
        if not data:
            return None
        summary = {}
        for k, v in data.items():
            if k.startswith("_"):  # Skip internal fields
                continue
            if isinstance(v, str) and len(v) > 200:
                summary[k] = v[:200] + "...[truncated]"
            elif isinstance(v, dict):
                summary[k] = f"{{dict with {len(v)} keys}}"
            elif isinstance(v, list):
                summary[k] = f"[list with {len(v)} items]"
            else:
                summary[k] = v
        return summary

    def _compute_hash(self, entry: dict) -> str:
        """Compute integrity hash (excluding the hash field itself)."""
        hashable = {k: v for k, v in entry.items() if k != "audit_hash"}
        payload = json.dumps(hashable, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

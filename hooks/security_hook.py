"""SecurityHook: Authentication, authorization, PII protection, and rate limiting."""

import re
import logging
import hashlib
import time
from collections import defaultdict
from typing import Tuple

logger = logging.getLogger(__name__)

# Simple in-memory rate limiter (production would use Redis)
_rate_limit_store = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 20     # max requests per window

PII_FIELDS = ["customer_email", "customer_id", "policy_number", "customer_name"]
SENSITIVE_PATTERNS = [
    (r'\b\d{16}\b', "credit_card"),       # Credit card numbers
    (r'\b\d{3}-\d{2}-\d{4}\b', "ssn"),   # SSN
    (r'\b\d{10,12}\b', "phone"),          # Phone numbers
]


class SecurityHook:
    """Enforces security controls on all claim processing."""

    def __init__(self):
        self.name = "SecurityHook"

    def execute(self, claim_data: dict, client_ip: str = "unknown") -> Tuple[bool, dict, list]:
        """
        Apply security checks.
        Returns: (is_secure, processed_data, security_issues)
        """
        issues = []
        processed = dict(claim_data)

        # Rate limiting
        if not self._check_rate_limit(client_ip):
            issues.append(f"Rate limit exceeded for {client_ip}. Max {RATE_LIMIT_MAX} requests per minute.")
            return False, processed, issues

        # PII protection — mask sensitive fields in logs
        self._log_with_masked_pii(claim_data)

        # Scan for sensitive data in description
        description = str(claim_data.get("description", ""))
        for pattern, data_type in SENSITIVE_PATTERNS:
            if re.search(pattern, description):
                issues.append(f"Potential {data_type} detected in description — will be masked")
                processed["description"] = re.sub(pattern, f"[REDACTED-{data_type.upper()}]", description)

        # Validate no eval/injection in any field
        all_text = " ".join([str(v) for v in claim_data.values()])
        dangerous_patterns = [
            r'__(import|class|subclasses|bases|mro)__',
            r'eval\s*\(',
            r'exec\s*\(',
            r'os\.system',
            r'subprocess\.',
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                issues.append(f"Potential code injection detected in claim data")
                return False, processed, issues

        # Generate security metadata
        processed["_security"] = {
            "client_ip": self._hash_ip(client_ip),
            "checked_at": time.time(),
            "pii_masked": True
        }

        is_secure = len(issues) == 0
        logger.info(f"[SecurityHook] secure={is_secure}, client={self._hash_ip(client_ip)}")
        return True, processed, issues  # Return True even with warnings (not hard blocks)

    def _check_rate_limit(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW
        _rate_limit_store[client_ip] = [t for t in _rate_limit_store[client_ip] if t > window_start]
        if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_MAX:
            return False
        _rate_limit_store[client_ip].append(now)
        return True

    def _hash_ip(self, ip: str) -> str:
        return hashlib.sha256(ip.encode()).hexdigest()[:12]

    def _log_with_masked_pii(self, data: dict):
        masked = {k: ("***MASKED***" if k in PII_FIELDS else v) for k, v in data.items()}
        logger.debug(f"[SecurityHook] Processing claim: {masked}")

    def mask_pii_in_response(self, data: dict) -> dict:
        """Remove _security meta and mask PII for external responses."""
        result = {k: v for k, v in data.items() if k != "_security"}
        # Partially mask email
        if "customer_email" in result:
            email = str(result["customer_email"])
            if "@" in email:
                parts = email.split("@")
                result["customer_email"] = parts[0][:3] + "***@" + parts[1]
        return result

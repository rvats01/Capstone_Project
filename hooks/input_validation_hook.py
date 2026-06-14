"""InputValidationHook: Sanitizes and validates all incoming claim data."""

import re
import logging
from datetime import datetime, date
from typing import Tuple

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    "customer_name", "customer_email", "customer_id",
    "policy_number", "claim_type", "incident_date",
    "claim_amount", "description"
]

VALID_CLAIM_TYPES = {"health", "auto", "life", "property", "liability"}
MAX_CLAIM_AMOUNT = 10_000_000  # $10M max
MIN_CLAIM_AMOUNT = 1.0
MAX_DESCRIPTION_LENGTH = 5000
MIN_DESCRIPTION_LENGTH = 10


class InputValidationHook:
    """Validates and sanitizes claim input data."""

    def __init__(self):
        self.name = "InputValidationHook"

    def execute(self, claim_data: dict) -> Tuple[bool, dict, list]:
        """
        Validate claim data.
        Returns: (is_valid, sanitized_data, errors)
        """
        errors = []
        sanitized = dict(claim_data)

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in claim_data or not str(claim_data[field]).strip():
                errors.append(f"Missing required field: {field}")

        if errors:
            return False, sanitized, errors

        # Sanitize strings (strip XSS, SQL injection attempts)
        sanitized["customer_name"] = self._sanitize_string(claim_data["customer_name"], 200)
        sanitized["description"] = self._sanitize_string(claim_data["description"], MAX_DESCRIPTION_LENGTH)

        # Validate email
        if not self._is_valid_email(claim_data["customer_email"]):
            errors.append("Invalid email format")

        # Validate claim type
        if claim_data.get("claim_type", "").lower() not in VALID_CLAIM_TYPES:
            errors.append(f"Invalid claim type. Must be one of: {VALID_CLAIM_TYPES}")
        else:
            sanitized["claim_type"] = claim_data["claim_type"].lower()

        # Validate claim amount
        try:
            amount = float(claim_data["claim_amount"])
            if amount < MIN_CLAIM_AMOUNT:
                errors.append(f"Claim amount must be at least ${MIN_CLAIM_AMOUNT}")
            elif amount > MAX_CLAIM_AMOUNT:
                errors.append(f"Claim amount exceeds maximum allowed ${MAX_CLAIM_AMOUNT:,}")
            sanitized["claim_amount"] = round(amount, 2)
        except (ValueError, TypeError):
            errors.append("Invalid claim amount: must be a number")

        # Validate incident date
        try:
            if isinstance(claim_data["incident_date"], str):
                incident_dt = datetime.fromisoformat(claim_data["incident_date"].replace("Z", "+00:00"))
            else:
                incident_dt = claim_data["incident_date"]

            now = datetime.now(incident_dt.tzinfo) if incident_dt.tzinfo else datetime.now()
            if incident_dt > now:
                errors.append("Incident date cannot be in the future")

            days_old = (now - incident_dt).days
            if days_old > 365:
                errors.append("Incident date is more than 1 year old — claim may be time-barred")

            sanitized["incident_date"] = incident_dt.isoformat()
        except (ValueError, AttributeError) as e:
            errors.append(f"Invalid incident date format: {e}")

        # Validate description length
        if len(str(claim_data.get("description", ""))) < MIN_DESCRIPTION_LENGTH:
            errors.append(f"Description too short (minimum {MIN_DESCRIPTION_LENGTH} characters)")

        # Validate policy number format
        policy = str(claim_data.get("policy_number", ""))
        if not re.match(r'^[A-Z0-9\-]{5,30}$', policy):
            errors.append("Policy number must be 5-30 alphanumeric characters")

        is_valid = len(errors) == 0
        logger.info(f"[InputValidationHook] valid={is_valid}, errors={errors}")
        return is_valid, sanitized, errors

    def _sanitize_string(self, value: str, max_len: int) -> str:
        """Remove potentially dangerous characters."""
        # Strip HTML tags
        clean = re.sub(r'<[^>]+>', '', str(value))
        # Remove SQL injection patterns
        clean = re.sub(r"(--|;|DROP|INSERT|DELETE|UPDATE|SELECT|UNION|EXEC)", "", clean, flags=re.IGNORECASE)
        return clean[:max_len].strip()

    def _is_valid_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email)))

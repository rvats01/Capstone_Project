"""CustomerAgent: Validates customer identity and extracts structured claim data."""

import time
import logging
from agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the CustomerAgent in an Insurance Claim Assessment System.

Your responsibilities:
1. Validate customer identity and policy details
2. Extract and structure claim information
3. Identify missing or inconsistent data
4. Flag suspicious customer behavior patterns

For each claim, return a JSON object with:
{
    "customer_validated": true/false,
    "policy_active": true/false,
    "identity_confidence": 0.0-1.0,
    "extracted_data": {
        "customer_id": "...",
        "customer_name": "...",
        "policy_number": "...",
        "claim_type": "...",
        "incident_date": "...",
        "claim_amount": 0.0,
        "description_quality": "poor/fair/good",
        "supporting_docs_count": 0
    },
    "missing_fields": [],
    "inconsistencies": [],
    "behavioral_flags": [],
    "reasoning": "Step-by-step validation reasoning...",
    "confidence": 0.0-1.0
}

Be thorough and precise. Flag any data quality issues."""


class CustomerAgent(BaseAgent):
    """Validates customer identity and extracts claim data."""

    def __init__(self):
        super().__init__("CustomerAgent")

    def process(self, claim_data: dict) -> AgentResult:
        start = time.time()
        try:
            user_msg = f"""Validate and process this insurance claim:

Claim Data:
{claim_data}

Validate:
1. Is the customer identity consistent and verifiable?
2. Is the policy number format valid?
3. Is the incident date reasonable (not future, not too old)?
4. Is the claim amount within policy limits?
5. Are there any behavioral red flags?

Return structured JSON assessment."""

            response = self._call_claude(SYSTEM_PROMPT, user_msg)
            result_data = self._parse_json_response(response)

            return AgentResult(
                agent_name=self.name,
                success=True,
                data=result_data,
                reasoning=result_data.get("reasoning", response),
                confidence=result_data.get("confidence", 0.7),
                duration_ms=int((time.time() - start) * 1000)
            )
        except Exception as e:
            logger.error(f"CustomerAgent error: {e}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000)
            )

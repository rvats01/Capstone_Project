"""KnowledgeAgent: Retrieves regulatory knowledge and policy terms via MCP server."""

import time
import logging
from agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the KnowledgeAgent in an Insurance Claim Assessment System.

Your responsibilities:
1. Retrieve relevant regulatory requirements for the claim type
2. Identify applicable policy terms and conditions
3. Look up precedents for similar claims
4. Provide regulatory context for compliance checks

Based on the claim type and regulations provided, return a JSON object:
{
    "applicable_regulations": [
        {"rule_id": "...", "title": "...", "relevance": "high/medium/low", "summary": "..."}
    ],
    "policy_terms": {
        "coverage_type": "...",
        "applicable_limits": {...},
        "exclusions": [],
        "waiting_periods": {}
    },
    "precedents": [
        {"case_type": "...", "typical_outcome": "...", "notes": "..."}
    ],
    "key_requirements": [],
    "regulatory_flags": [],
    "reasoning": "Knowledge retrieval reasoning...",
    "confidence": 0.0-1.0
}"""


class KnowledgeAgent(BaseAgent):
    """Retrieves regulatory knowledge and policy context."""

    def __init__(self):
        super().__init__("KnowledgeAgent")

    def process(self, claim_data: dict, regulations: list) -> AgentResult:
        start = time.time()
        try:
            reg_text = "\n".join([
                f"- [{r.get('rule_id', '')}] {r.get('title', '')}: {r.get('content', '')}"
                for r in regulations[:8]  # Top 8 most relevant
            ])

            user_msg = f"""Retrieve and analyze regulatory knowledge for this claim:

Claim Type: {claim_data.get('claim_type', 'unknown')}
Claim Amount: ${claim_data.get('claim_amount', 0):,.2f}
Policy Number: {claim_data.get('policy_number', 'N/A')}

Available Regulations:
{reg_text}

1. Which regulations apply most directly to this claim?
2. What are the key policy terms that govern this claim type?
3. What are typical precedents for this claim type?
4. What critical requirements must be met?

Return structured JSON analysis."""

            response = self._call_claude(SYSTEM_PROMPT, user_msg)
            result_data = self._parse_json_response(response)

            return AgentResult(
                agent_name=self.name,
                success=True,
                data=result_data,
                reasoning=result_data.get("reasoning", response),
                confidence=result_data.get("confidence", 0.8),
                duration_ms=int((time.time() - start) * 1000)
            )
        except Exception as e:
            logger.error(f"KnowledgeAgent error: {e}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000)
            )

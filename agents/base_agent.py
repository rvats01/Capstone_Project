"""Base agent class with shared Claude interaction logic."""

import anthropic
import json
import os
import time
import logging
from typing import Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    agent_name: str
    success: bool
    data: dict = field(default_factory=dict)
    reasoning: str = ""
    confidence: float = 0.0
    duration_ms: int = 0
    error: Optional[str] = None


class BaseAgent:
    """Base class for all insurance assessment agents."""

    def __init__(self, name: str, model: str = "claude-sonnet-4-6"):
        self.name = name
        self.model = model
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.max_tokens = 2048

    def _call_claude(self, system_prompt: str, user_message: str, tools: list = None) -> str:
        """Call Claude API with optional tool use."""
        start = time.time()
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}]
        }
        if tools:
            kwargs["tools"] = tools

        response = self.client.messages.create(**kwargs)
        duration = int((time.time() - start) * 1000)
        logger.info(f"[{self.name}] Claude call: {duration}ms")

        # Extract text from response content
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return ""

    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from Claude response, handling markdown code blocks."""
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON object from text
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
            return {"raw_response": text}

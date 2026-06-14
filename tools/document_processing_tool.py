"""DocumentProcessingTool: Extracts structured data from claim documents."""

import re
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

CLAIM_TYPE_KEYWORDS = {
    "health": ["hospital", "medical", "treatment", "surgery", "doctor", "diagnosis", "medicine", "prescription", "icu", "therapy"],
    "auto": ["accident", "vehicle", "car", "collision", "damage", "repair", "crash", "motor", "truck", "fender"],
    "life": ["death", "deceased", "passed away", "fatal", "mortality", "nominee", "beneficiary"],
    "property": ["fire", "flood", "theft", "burglary", "damage", "home", "house", "property", "building", "roof"],
    "liability": ["lawsuit", "third party", "injury", "negligence", "legal", "court", "damages awarded"]
}

SUSPICIOUS_PHRASES = [
    "immediately after purchasing",
    "just got the policy",
    "coincidence",
    "no witnesses",
    "cash only",
    "urgent payment",
    "bypass insurance",
    "before anyone finds out"
]

AMOUNT_PATTERNS = [
    r'\$[\d,]+(?:\.\d{2})?',
    r'USD\s*[\d,]+(?:\.\d{2})?',
    r'Rs\.?\s*[\d,]+(?:\.\d{2})?',
    r'₹\s*[\d,]+(?:\.\d{2})?'
]

DATE_PATTERNS = [
    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
    r'\d{4}-\d{2}-\d{2}',
    r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{4}'
]


class DocumentProcessingTool:
    """Extracts and analyzes structured data from claim documents."""

    def __init__(self):
        self.name = "DocumentProcessingTool"

    def process_claim_description(self, description: str, claim_type: str = None) -> dict:
        """
        Extract structured information from claim description text.
        Returns enriched claim analysis.
        """
        desc_lower = description.lower()

        # Detect claim type from content if not provided
        if not claim_type:
            claim_type = self._detect_claim_type(desc_lower)

        # Extract amounts mentioned
        amounts = self._extract_amounts(description)

        # Extract dates mentioned
        dates = self._extract_dates(description)

        # Check for suspicious phrases
        suspicious = self._check_suspicious_content(desc_lower)

        # Measure description quality
        quality = self._assess_description_quality(description)

        # Extract key entities
        entities = self._extract_entities(description)

        result = {
            "detected_claim_type": claim_type,
            "extracted_amounts": amounts,
            "mentioned_dates": dates,
            "suspicious_phrases_found": suspicious,
            "description_quality": quality["level"],
            "quality_score": quality["score"],
            "quality_issues": quality["issues"],
            "key_entities": entities,
            "word_count": len(description.split()),
            "completeness_indicators": {
                "has_date": len(dates) > 0,
                "has_amount": len(amounts) > 0,
                "has_location": any(w in desc_lower for w in ["at", "in", "location", "address", "street", "city"]),
                "has_description": len(description) > 50,
                "has_witnesses": "witness" in desc_lower or "witnesses" in desc_lower
            }
        }

        logger.info(f"[DocumentProcessingTool] Processed description: quality={quality['level']}, suspicious={len(suspicious)}")
        return result

    def _detect_claim_type(self, text: str) -> str:
        scores = {}
        for ctype, keywords in CLAIM_TYPE_KEYWORDS.items():
            scores[ctype] = sum(1 for kw in keywords if kw in text)

        if not any(scores.values()):
            return "unknown"
        return max(scores, key=scores.get)

    def _extract_amounts(self, text: str) -> list:
        amounts = []
        for pattern in AMOUNT_PATTERNS:
            matches = re.findall(pattern, text)
            amounts.extend(matches)
        return list(set(amounts))[:5]  # Deduplicate, limit to 5

    def _extract_dates(self, text: str) -> list:
        dates = []
        for pattern in DATE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        return list(set(dates))[:5]

    def _check_suspicious_content(self, text: str) -> list:
        found = []
        for phrase in SUSPICIOUS_PHRASES:
            if phrase in text:
                found.append(phrase)
        return found

    def _assess_description_quality(self, description: str) -> dict:
        issues = []
        score = 1.0
        word_count = len(description.split())

        if word_count < 20:
            issues.append("Description too brief (under 20 words)")
            score -= 0.4
        elif word_count < 50:
            issues.append("Description could be more detailed")
            score -= 0.2

        if not any(c in description for c in [".", "!", "?"]):
            issues.append("No sentence structure detected")
            score -= 0.1

        # Check for vague language
        vague_terms = ["something", "somehow", "some reason", "i don't know", "not sure"]
        vague_count = sum(1 for t in vague_terms if t in description.lower())
        if vague_count > 1:
            issues.append(f"Vague language detected ({vague_count} instances)")
            score -= 0.1 * vague_count

        score = max(0.0, min(1.0, score))
        level = "poor" if score < 0.4 else "fair" if score < 0.7 else "good"

        return {"level": level, "score": round(score, 2), "issues": issues}

    def _extract_entities(self, text: str) -> dict:
        """Simple entity extraction from description."""
        entities = {
            "has_hospital_name": bool(re.search(r'(hospital|clinic|medical center|health center)', text, re.I)),
            "has_vehicle_info": bool(re.search(r'(car|truck|vehicle|model|year|plate|registration)', text, re.I)),
            "has_police_report": bool(re.search(r'(police|FIR|report|filed|complaint)', text, re.I)),
            "has_doctor_name": bool(re.search(r'(dr\.|doctor|physician|surgeon)', text, re.I)),
            "has_location": bool(re.search(r'(street|road|avenue|city|state|zip|pincode)', text, re.I))
        }
        return entities

    def extract_from_structured_form(self, form_data: dict) -> dict:
        """Process structured form submission."""
        description = str(form_data.get("description", ""))
        claim_type = form_data.get("claim_type", "").lower()

        doc_analysis = self.process_claim_description(description, claim_type)

        # Cross-validate form fields vs description
        validations = []
        if doc_analysis["extracted_amounts"]:
            validations.append("Amount references found in description — cross-check with claimed amount")

        if doc_analysis["suspicious_phrases_found"]:
            validations.append(f"ALERT: Suspicious language detected: {doc_analysis['suspicious_phrases_found']}")

        if doc_analysis["quality_score"] < 0.4:
            validations.append("Low quality description — may need additional documentation")

        return {
            "document_analysis": doc_analysis,
            "cross_validations": validations,
            "processing_status": "complete",
            "risk_signals": doc_analysis["suspicious_phrases_found"]
        }

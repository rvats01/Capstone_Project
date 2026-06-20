# Skills Quick Reference Guide

## Skills Directory Structure

```
skills/
├── __init__.py                      # Exports: RiskAnalyzer, ComplianceValidator, FraudDetector, FinancialAssessor
├── risk_analysis.py                 # Multi-dimensional risk and fraud scoring
├── compliance_validation.py          # IRDAI, SOX, AML regulatory compliance
├── fraud_detection.py               # Fraud pattern detection and behavioral analysis
└── financial_assessment.py          # Claim valuation and reserve calculations
```

---

## Skill Summary Table

| Skill | Purpose | Agent | Key Output |
|-------|---------|-------|-----------|
| **RiskAnalyzer** | Fraud scoring & risk assessment | RiskAgent | Fraud score (0-1), risk level, indicators |
| **ComplianceValidator** | Regulatory compliance checking | ComplianceAgent | Compliance status, violations, score |
| **FraudDetector** | Pattern-based fraud detection | RiskAgent | Patterns detected, priority level, brief |
| **FinancialAssessor** | Claim valuation & reserves | DecisionAgent | Approved amount, reserves, risk level |

---

## Quick Usage Examples

### RiskAnalyzer

```python
from skills.risk_analysis import RiskAnalyzer

analyzer = RiskAnalyzer()

# Calculate fraud score
fraud_result = analyzer.calculate_fraud_score(
    claim_data={
        "claim_type": "auto",
        "claim_amount": 50000,
        "incident_date": "2026-06-15"
    },
    customer_history={
        "total_claims": 2,
        "recent_claims_count": 1,
        "days_since_policy_issue": 60
    },
    fraud_patterns=[...]
)

# Access results
print(f"Fraud Score: {fraud_result['fraud_score']}")
print(f"Risk Level: {fraud_result['risk_level']}")

# Calculate financial exposure
exposure = analyzer.calculate_financial_exposure(
    claim_data,
    fraud_score=fraud_result['fraud_score']
)

# Perform velocity analysis
velocity = analyzer.perform_velocity_analysis(customer_history)
```

### ComplianceValidator

```python
from skills.compliance_validation import ComplianceValidator

validator = ComplianceValidator()

# Validate compliance
result = validator.validate_compliance(
    claim_data=claim,
    regulations=[...],
    customer_data=customer
)

# Check results
if result['overall_compliance'] == 'pass':
    print("✓ Claim compliant with all regulations")
else:
    print("✗ Blocking violations:", result['blocking_violations'])
    print("Required actions:", result['mandatory_actions'])
```

### FraudDetector

```python
from skills.fraud_detection import FraudDetector

detector = FraudDetector()

# Detect fraud indicators
fraud_analysis = detector.detect_fraud_indicators(
    claim_data=claim,
    customer_behavioral_data=behavior
)

# Get investigation brief
brief = detector.generate_investigation_brief(fraud_analysis)

print(brief)
```

### FinancialAssessor

```python
from skills.financial_assessment import FinancialAssessor

assessor = FinancialAssessor()

# Assess claim value
assessment = assessor.assess_claim_value(
    claim_data=claim,
    policy_data=policy,
    market_data=market
)

# Get approved amount
print(f"Claimed: ${claim['claim_amount']:,.2f}")
print(f"Valued at: ${assessment['valuation']['estimated_value']:,.2f}")
print(f"Approved: ${assessment['adjusted_approved_amount']:,.2f}")
print(f"Reserves: ${assessment['reserve_recommendations']['total_reserve']:,.2f}")
```

---

## Key Metrics & Thresholds

### Risk Analysis
- **Fraud Score**: 0.0-1.0 (higher = more risky)
  - < 0.4: Low risk
  - 0.4-0.6: Medium risk
  - 0.6-0.8: High risk
  - > 0.8: Critical risk
- **Investigation Threshold**: Fraud score > 0.6
- **High Amount Threshold**: $100,000

### Compliance Validation
- **Compliance Score**: 0.0-1.0 (higher = more compliant)
- **Auto-Reject**: Any blocking violation
- **IRDAI Settlement**: 30 days standard
- **SOX Dual Approval**: Claims > $1,000,000
- **AML High Alert**: Transactions > $10,000

### Fraud Detection
- **Staged Incident**: Common indicators (50+ suspicious phrases tracked)
- **Amount Inflation**: >150% of estimate
- **Velocity Alert**: >2 claims in 90 days
- **Investigation Priority**: Critical/High/Medium/Low

### Financial Assessment
- **Depreciation Rates**:
  - Vehicles: 15% per year
  - Property: 2% per year
  - Equipment: 20% per year
- **Reserve Multipliers**:
  - Case: 100% of approved amount
  - IBNR: 0-50% (based on confidence)
  - Litigation: 25% for disputed
  - Investigation: 0-30% for fraud risk

---

## Agent Integration Points

### RiskAgent Integration
```python
class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("RiskAgent")
        self.risk_analyzer = RiskAnalyzer()  # ← Initialize skill
    
    def process(self, claim_data, customer_result, fraud_patterns):
        # Use skill
        fraud_analysis = self.risk_analyzer.calculate_fraud_score(
            claim_data, customer_history, fraud_patterns
        )
        # Merge with Claude analysis
        result_data.update({
            "fraud_score": fraud_analysis.get("fraud_score"),
            "risk_level": fraud_analysis.get("risk_level"),
            "financial_risk": fraud_analysis.get("financial_exposure")
        })
```

### ComplianceAgent Integration
```python
class ComplianceAgent(BaseAgent):
    def __init__(self):
        super().__init__("ComplianceAgent")
        self.compliance_validator = ComplianceValidator()  # ← Initialize skill
    
    def process(self, claim_data, knowledge_result):
        # Use skill
        compliance = self.compliance_validator.validate_compliance(
            claim_data, regulations, customer_data
        )
        # Merge with Claude analysis
        result_data.update({
            "overall_compliance": compliance.get("overall_compliance"),
            "irdai_checks": compliance.get("irdai_checks"),
            "aml_checks": compliance.get("aml_checks")
        })
```

### DecisionAgent Integration
```python
class DecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("DecisionAgent")
        self.financial_assessor = FinancialAssessor()  # ← Initialize skill
    
    def process(self, claim_data, customer_result, ...):
        # Use skill
        financial = self.financial_assessor.assess_claim_value(
            claim_data, policy_data, market_data
        )
        # Merge with decision
        result_data.update({
            "approved_amount": financial.get("adjusted_approved_amount"),
            "financial_assessment": financial,
            "deductible_applied": financial.get("coverage_details")
        })
```

---

## Output JSON Schemas

### RiskAnalyzer Output
```json
{
  "fraud_score": 0.4523,
  "risk_level": "medium",
  "fraud_indicators": [
    {
      "indicator": "High Claim Amount",
      "value": "$125,000",
      "severity": "high",
      "weight": 0.15
    }
  ],
  "anomalies": [],
  "velocity_checks": {
    "multiple_claims_flag": false,
    "rapid_filing_flag": false,
    "amount_inflation_flag": false
  },
  "investigation_required": false,
  "confidence": 0.87,
  "reasoning": "..."
}
```

### ComplianceValidator Output
```json
{
  "overall_compliance": "pass",
  "compliance_score": 0.92,
  "irdai_checks": { ... },
  "sox_checks": { ... },
  "aml_checks": { ... },
  "blocking_violations": [],
  "warnings": [],
  "mandatory_actions": [],
  "confidence": 0.95
}
```

### FraudDetector Output
```json
{
  "fraud_patterns_detected": [
    {
      "pattern": "Staged Incident",
      "score": 0.72,
      "severity": "critical",
      "indicators": ["Suspicious timing language", "Total loss claim"]
    }
  ],
  "overall_fraud_confidence": 0.65,
  "high_risk_indicators": [...],
  "medium_risk_indicators": [...],
  "patterns_count": 2,
  "requires_investigation": true,
  "investigation_priority": "high"
}
```

### FinancialAssessor Output
```json
{
  "claim_type": "auto",
  "claimed_amount": 50000.00,
  "valuation": {
    "method": "auto_valuation",
    "estimated_value": 42000.00,
    "confidence": 0.88
  },
  "coverage_details": {
    "deductible": 500.00,
    "coverage_limit": 500000.00
  },
  "adjusted_approved_amount": 41500.00,
  "approval_percentage": 83.0,
  "reserve_recommendations": {
    "case_reserve": 41500.00,
    "ibnr_reserve": 1248.00,
    "total_reserve": 42748.00
  },
  "financial_risk_assessment": {
    "risk_level": "low",
    "claim_variance_percentage": 8.0
  },
  "payment_recommendations": {
    "recommendation": "approve",
    "status": "ready_for_payment"
  }
}
```

---

## Testing Checklist

- [ ] All four skills import successfully
- [ ] RiskAnalyzer calculates fraud scores 0.0-1.0
- [ ] ComplianceValidator returns pass/fail status
- [ ] FraudDetector identifies patterns correctly
- [ ] FinancialAssessor values claims accurately
- [ ] All skills handle missing data gracefully
- [ ] Agent integration merges skill outputs with Claude analysis
- [ ] No circular dependencies between skills
- [ ] Performance acceptable (<300ms total for all 4 skills)
- [ ] Documented error handling and fallbacks

---

## Common Patterns

### Cascading Fraud Detection
```python
# High fraud score from RiskAnalyzer triggers FraudDetector
if fraud_score > 0.6:
    detailed_fraud = detector.detect_fraud_indicators(claim_data)
    investigation_required = True
```

### Compliance Gating
```python
# Blocking violations from ComplianceValidator immediately fails claim
if blocking_violations:
    decision = "rejected"
    return AgentResult(success=False, data={"decision": decision})
```

### Financial Cascades
```python
# Fraud score influences reserve multipliers
reserve = calculate_reserve(
    approved_amount,
    fraud_risk_score  # Higher score = higher reserves
)
```

---

## Debugging Tips

1. **Enable Skill Logging**:
   ```python
   import logging
   logging.getLogger("skills").setLevel(logging.DEBUG)
   ```

2. **Inspect Skill Outputs**:
   ```python
   import json
   print(json.dumps(analyzer.calculate_fraud_score(...), indent=2))
   ```

3. **Validate Input Data**:
   ```python
   required_fields = ["claim_type", "claim_amount", "incident_date"]
   for field in required_fields:
       assert field in claim_data, f"Missing {field}"
   ```

4. **Check Thresholds**:
   ```python
   print(f"Fraud score: {fraud_score} (threshold: 0.6)")
   print(f"Compliance score: {compliance_score} (threshold: 0.5)")
   ```

---

## Related Documentation

- **SKILLS.md**: Comprehensive skill documentation
- **AGENTS.md**: Agent architecture and roles
- **CLAUDE.md**: Project overview and setup
- **architecture_diagram.png**: System architecture visualization

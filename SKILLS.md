# Insurance Claim Assessment System — Skills Modules

## Overview

The Skills framework provides specialized, reusable modules that enhance agent capabilities with domain-specific analysis, calculations, and pattern matching. Each skill encapsulates a distinct functional domain and integrates seamlessly with the multi-agent system.

---

## Architecture

```
skills/
├── __init__.py                    # Module exports
├── risk_analysis.py              # RiskAnalyzer class
├── compliance_validation.py       # ComplianceValidator class
├── fraud_detection.py            # FraudDetector class
└── financial_assessment.py       # FinancialAssessor class
```

### Integration Points

- **RiskAgent** ← RiskAnalyzer
- **ComplianceAgent** ← ComplianceValidator
- **DecisionAgent** ← FinancialAssessor
- **FraudDetection** ← FraudDetector (via RiskAgent)

---

## Skill Modules

### 1. Risk Analysis (`risk_analysis.py`)

**Purpose**: Multi-dimensional risk scoring and fraud assessment

**Class**: `RiskAnalyzer`

#### Key Methods

**`calculate_fraud_score(claim_data, customer_history, fraud_patterns)`**
- Calculates weighted fraud score (0.0-1.0)
- Identifies fraud indicators with severity levels
- Returns anomalies detected in claim
- Generates risk level classification (critical/high/medium/low)
- Provides reasoning for fraud assessment

**Risk Factors**:
- High claim amount (threshold: $100k, weight: 15%)
- New customer status (weight: 10%)
- Rapid filing velocity (weight: 12%)
- Incomplete information (weight: 8%)
- Suspicious timing (weight: 15%)
- Behavioral red flags (weight: 18%)

**Velocity Analysis**:
- Multiple claims detection (>2 in 90 days)
- Rapid filing patterns (<30 days between claims)
- Amount inflation detection

**Output Example**:
```python
{
    "fraud_score": 0.4523,
    "risk_level": "medium",
    "fraud_indicators": [
        {"indicator": "High Claim Amount", "severity": "high", "weight": 0.15},
        {"indicator": "Rapid Filing Pattern", "severity": "medium", "weight": 0.12}
    ],
    "investigation_required": False,
    "velocity_checks": {
        "multiple_claims_flag": True,
        "rapid_filing_flag": False,
        "amount_inflation_flag": False
    }
}
```

#### Integration with RiskAgent

The RiskAgent uses RiskAnalyzer to:
1. Calculate base fraud scores before Claude analysis
2. Perform pattern matching against known fraud signatures
3. Analyze velocity patterns for rapid claims
4. Calculate financial exposure and reserve recommendations
5. Provide structured input to Claude for enhanced reasoning

---

### 2. Compliance Validation (`compliance_validation.py`)

**Purpose**: Regulatory compliance checking (IRDAI, SOX, AML)

**Class**: `ComplianceValidator`

#### Regulatory Frameworks

**IRDAI (Insurance Regulatory and Development Authority of India)**
- Settlement timeline compliance (30 days standard)
- Policy active verification
- Required documentation checks
- Claim amount within policy limits
- Claim type validity

**SOX (Sarbanes-Oxley Act)**
- Dual approval requirement for large claims (>$1M)
- Audit trail completeness (automatic)
- Financial reporting requirements
- Data retention compliance (7+ years)

**AML (Anti-Money Laundering)**
- KYC (Know Your Customer) completion
- AML screening passage
- PEP (Politically Exposed Person) detection
- Structuring detection
- High-value transaction alerts (>$100k)

#### Key Methods

**`validate_compliance(claim_data, regulations, customer_data)`**
- Performs IRDAI, SOX, and AML checks
- Identifies blocking violations (fail conditions)
- Calculates overall compliance score (0.0-1.0)
- Returns compliance status (pass/fail)
- Generates mandatory actions for remediation

**Output Example**:
```python
{
    "overall_compliance": "pass",
    "compliance_score": 0.92,
    "irdai_checks": {
        "claim_time_limit_ok": True,
        "policy_active_ok": True,
        "documentation_ok": True,
        "violations": []
    },
    "sox_checks": {
        "dual_approval_required": False,
        "audit_trail_complete": True,
        "violations": []
    },
    "aml_checks": {
        "kyc_completed": True,
        "aml_screening_passed": True,
        "pep_status": False,
        "violations": []
    },
    "blocking_violations": [],
    "mandatory_actions": []
}
```

#### Integration with ComplianceAgent

The ComplianceAgent uses ComplianceValidator to:
1. Perform structured regulatory checks
2. Identify blocking violations early
3. Calculate compliance confidence scores
4. Determine mandatory actions for resolution
5. Provide pre-validation before Claude's detailed assessment

---

### 3. Fraud Detection (`fraud_detection.py`)

**Purpose**: Advanced fraud pattern recognition and behavioral analysis

**Class**: `FraudDetector`

#### Fraud Patterns Detected

**Staged Incidents** (Severity: Critical)
- Suspicious timing language ("conveniently", "fortunately")
- Total loss claims (unusually severe)
- High-value claims shortly after policy issuance
- Missing witness information

**Amount Inflation** (Severity: High)
- Claim significantly exceeds estimate (>150%)
- Amount far exceeds customer's historical average (>2.5x)
- Suspiciously round numbers (multiples of $1000)
- Minimal description for high-value claims

**Identity Fraud** (Severity: Critical)
- Changed contact information (multiple phone numbers)
- Address mismatch vs. policy address
- Unusual filing device/location
- Account changes before claiming
- Account reactivation fraud

**Documentation Fraud** (Severity: High)
- Poor quality documentation
- Missing standard documentation
- Date inconsistencies
- Document alterations detected
- Failed signature verification

**Behavioral Anomalies** (Severity: Medium)
- Unusual claim frequency changes
- Significant claim amount variance
- Recent behavioral changes

#### Key Methods

**`detect_fraud_indicators(claim_data, customer_behavioral_data)`**
- Detects multiple fraud patterns in parallel
- Scores each pattern (0.0-1.0)
- Identifies high-risk indicators (>0.7)
- Determines investigation priority (critical/high/medium/low)

**`generate_investigation_brief(fraud_analysis)`**
- Produces investigation team briefing
- Prioritizes findings by severity
- Recommends investigation depth

**Output Example**:
```python
{
    "fraud_patterns_detected": [
        {
            "pattern": "Amount Inflation",
            "score": 0.72,
            "severity": "high",
            "indicators": [
                "Claim amount 45% higher than estimate",
                "Minimal description for $500k claim"
            ]
        }
    ],
    "overall_fraud_confidence": 0.65,
    "high_risk_indicators": [...],
    "patterns_count": 2,
    "requires_investigation": True,
    "investigation_priority": "high"
}
```

#### Integration with RiskAgent

The RiskAgent uses FraudDetector to:
1. Identify specific fraud patterns in claims
2. Score behavioral anomalies
3. Generate investigation briefs for high-risk claims
4. Provide detailed indicators for fraud alerts

---

### 4. Financial Assessment (`financial_assessment.py`)

**Purpose**: Claim valuation, reserves, and financial risk analysis

**Class**: `FinancialAssessor`

#### Claim Valuation Methods

**Auto Insurance**
- Vehicle depreciation calculation (15% per year)
- Damage type assessment (total loss, collision, comprehensive)
- Market comparable valuation
- Repair estimates
- Salvage value consideration

**Property Insurance**
- Actual Cash Value (ACV) with depreciation (2% per year)
- Replacement cost calculation
- Damage percentage assessment
- Building age/condition factors

**Health Insurance**
- Network negotiated rates
- Service type validation
- Multiple fee schedule support
- Annual benefit maximum enforcement

**Life Insurance**
- Death benefit verification
- Exclusion clause checking (suicide clause, etc.)
- Policy type validation (term, whole life, universal)

**Travel Insurance**
- Receipt and documentation validation
- Claim reason verification
- Travel cost substantiation

#### Reserve Calculations

**Case Reserve**: Amount set aside for approved claim
**IBNR Reserve**: Incurred But Not Reported (0-50% of case reserve based on confidence)
**Litigation Reserve**: For disputed claims (25% of case reserve)
**Investigation Reserve**: For fraud-suspected claims (0-30% based on fraud risk)

**Total Reserve** = Case + IBNR + Litigation + Investigation

#### Key Methods

**`assess_claim_value(claim_data, policy_data, market_data)`**
- Selects appropriate valuation method by claim type
- Calculates adjusted amount after deductible and limits
- Recommends payment strategy
- Assesses financial risk exposure

**`calculate_reserves(claim_data, adjusted_value, valuation)`**
- Computes all reserve types
- Factors in valuation confidence
- Adjusts for litigation risk
- Incorporates fraud risk factors

**Output Example**:
```python
{
    "claimed_amount": 50000.00,
    "valuation": {
        "method": "auto_valuation",
        "estimated_value": 42000.00,
        "confidence": 0.88
    },
    "adjusted_approved_amount": 41500.00,  # After deductible
    "approval_percentage": 83.0,
    "reserve_recommendations": {
        "case_reserve": 41500.00,
        "ibnr_reserve": 1248.00,
        "litigation_reserve": 0.00,
        "investigation_reserve": 0.00,
        "total_reserve": 42748.00
    },
    "payment_recommendations": {
        "recommendation": "approve",
        "status": "ready_for_payment"
    }
}
```

#### Integration with DecisionAgent

The DecisionAgent uses FinancialAssessor to:
1. Calculate final approved amounts
2. Determine deductible applications
3. Recommend reserve levels
4. Provide financial risk context for decisions
5. Enable data-driven approval determinations

---

## Data Flow

### Claims Processing Pipeline

```
Claim Submission
    ↓
Customer Validation (CustomerAgent)
    ↓
┌─→ Risk Analysis (RiskAnalyzer)
│   ├─ Fraud Score Calculation
│   ├─ Velocity Analysis
│   └─ Financial Exposure
│
├─→ Compliance Validation (ComplianceValidator)
│   ├─ IRDAI Checks
│   ├─ SOX Validation
│   └─ AML Screening
│
├─→ Knowledge Retrieval (KnowledgeAgent)
│   └─ Regulatory Rules
│
└─→ Final Decision (DecisionAgent)
    ├─ Financial Assessment (FinancialAssessor)
    ├─ Multi-factor synthesis
    ├─ Approved amount calculation
    └─ Comprehensive justification
```

---

## Extension Points

### Adding New Fraud Patterns

```python
# In FraudDetector initialization
FRAUD_INDICATORS["new_pattern"] = {
    "severity": "high",
    "keywords": ["keyword1", "keyword2"],
    "weight": 0.20
}

# Add detection method
def _detect_new_pattern(self, claim_data) -> Tuple[float, List[str]]:
    # Pattern implementation
    pass

# Call from detect_fraud_indicators()
```

### Adding New Valuation Methods

```python
# In FinancialAssessor
elif claim_type == "new_type":
    return self._value_new_type(claim_data, market_data)

def _value_new_type(self, claim_data, market_data) -> Dict[str, Any]:
    # Valuation logic
    pass
```

### Adding New Compliance Rules

```python
# In ComplianceValidator
def _check_new_regulation(self, claim_data) -> Dict[str, Any]:
    violations = []
    # Compliance checks
    return {
        "rule_checks": {...},
        "violations": violations,
        "blocking_violations": [...]
    }
```

---

## Performance Considerations

- **Fraud Detection**: ~50-100ms per claim (pattern matching)
- **Compliance Validation**: ~30-50ms per claim (rule checking)
- **Risk Analysis**: ~50-100ms per claim (calculation-intensive)
- **Financial Assessment**: ~30-50ms per claim (valuation)

**Total Skill Processing**: ~200-300ms for typical claim

---

## Error Handling

All skills implement graceful degradation:
- If pattern matching fails, uses fallback rules
- If valuation method unavailable, uses conservative estimate
- Missing data treated as neutral (score unchanged vs. negative)
- Exceptions logged without failing claim processing

---

## Testing

Test each skill independently:

```python
# Test RiskAnalyzer
from skills.risk_analysis import RiskAnalyzer
analyzer = RiskAnalyzer()
result = analyzer.calculate_fraud_score(claim, history, patterns)

# Test ComplianceValidator
from skills.compliance_validation import ComplianceValidator
validator = ComplianceValidator()
result = validator.validate_compliance(claim, regs, customer)

# Test FraudDetector
from skills.fraud_detection import FraudDetector
detector = FraudDetector()
result = detector.detect_fraud_indicators(claim, behavior)

# Test FinancialAssessor
from skills.financial_assessment import FinancialAssessor
assessor = FinancialAssessor()
result = assessor.assess_claim_value(claim, policy, market)
```

---

## Future Enhancements

1. **Machine Learning Integration**: Train models on historical claims for pattern weights
2. **Real-time Market Data**: Integrate API for live vehicle/property valuations
3. **Social Network Analysis**: Detect collusion rings via claim network patterns
4. **Explainability**: Generate LIME/SHAP explanations for scores
5. **Benchmarking**: Performance comparison with industry standards
6. **Audit Reports**: Generate regulatory audit trails for each claim

---

## References

- IRDAI Guidelines: Insurance Regulatory and Development Authority of India
- SOX Compliance: Sarbanes-Oxley Act requirements for financial services
- AML/KYC: Anti-Money Laundering and Know Your Customer regulations
- Financial Valuation: Blue Book auto valuation, NADA adjustments, repair estimates

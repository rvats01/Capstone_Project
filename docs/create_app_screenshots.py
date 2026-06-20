"""
Create visual mockups of the application pages as PNG images for embedding in presentation.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Colors matching the app
NAVY = (25, 55, 109)
LIGHT_BLUE = (59, 89, 152)
ORANGE = (255, 127, 39)
WHITE = (255, 255, 255)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (242, 242, 242)
GREEN = (76, 175, 80)
RED = (244, 67, 54)

def create_dashboard_screenshot():
    """Create dashboard page mockup."""
    img = Image.new('RGB', (1280, 960), color=WHITE)
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([(0, 0), (1280, 80)], fill=NAVY)
    draw.text((20, 15), "🛡️ ClaimAI Insurance Assessment System", fill=WHITE, font=None)
    draw.text((1000, 25), "● Live", fill=GREEN, font=None)
    
    # Navigation
    nav_items = ["Dashboard", "Submit Claim", "All Claims", "Regulations", "API Docs"]
    for i, item in enumerate(nav_items):
        draw.text((20 + i*200, 100), item, fill=NAVY, font=None)
    
    # Title
    draw.text((50, 130), "System Dashboard", fill=NAVY, font=None)
    draw.text((50, 160), "Real-time insurance claim assessment monitoring", fill=DARK_GRAY, font=None)
    
    # Metrics boxes
    metrics = [
        ("Total Claims", "2", "0 pending"),
        ("Approved", "0", "0% approval rate"),
        ("Rejected", "0", "0 fraud suspected"),
        ("Avg Fraud Score", "0.000", "$6,000 avg claim"),
    ]
    
    y = 210
    for title, value, desc in metrics:
        draw.rectangle([(50, y), (280, y+80)], outline=LIGHT_GRAY, width=2)
        draw.text((70, y+10), title, fill=DARK_GRAY, font=None)
        draw.text((70, y+35), value, fill=NAVY, font=None)
        draw.text((70, y+55), desc, fill=LIGHT_GRAY, font=None)
        y += 90
    
    # Agents status
    draw.rectangle([(350, 210), (1250, 520)], outline=LIGHT_BLUE, width=2)
    draw.text((370, 220), "✓ Active Agents (6) - All Operational", fill=GREEN, font=None)
    
    agents = [
        "👤 CustomerAgent - Identity validation & claim extraction",
        "📚 KnowledgeAgent - MCP regulatory knowledge retrieval",
        "⚖️ ComplianceAgent - IRDAI / SOX / AML validation",
        "🔍 RiskAgent - Fraud detection & risk scoring",
        "⚡ DecisionAgent - Final assessment synthesis",
        "📋 AuditAgent - Immutable audit trail generation",
    ]
    
    y = 260
    for agent in agents:
        draw.text((370, y), agent, fill=DARK_GRAY, font=None)
        y += 40
    
    # Recent claims table
    draw.text((50, 550), "Recent Claims", fill=NAVY, font=None)
    draw.rectangle([(50, 590), (1250, 700)], outline=LIGHT_GRAY, width=1)
    
    headers = ["Claim #", "Customer", "Type", "Amount", "Fraud Score", "Status", "Action"]
    x = 70
    for header in headers:
        draw.text((x, 600), header, fill=NAVY, font=None)
        x += 170
    
    claims = [
        ["CLM-20260614-9FB40756", "Robert Williams", "auto", "$8,500", "0.000", "under review", "View"],
        ["CLM-20260614-3C4F3C72", "Sarah Johnson", "health", "$3,500", "0.000", "under review", "View"],
    ]
    
    y = 640
    for claim in claims:
        x = 70
        for item in claim:
            draw.text((x, y), item, fill=DARK_GRAY, font=None)
            x += 170
        y += 40
    
    # Footer
    draw.text((50, 920), "Insurance Claim Assessment System v1.0 | Multi-Agent AI | Powered by Claude", 
              fill=LIGHT_GRAY, font=None)
    
    return img


def create_submit_claim_screenshot():
    """Create submit claim form mockup."""
    img = Image.new('RGB', (1280, 960), color=WHITE)
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([(0, 0), (1280, 80)], fill=NAVY)
    draw.text((20, 15), "🛡️ ClaimAI Insurance Assessment System", fill=WHITE, font=None)
    
    # Navigation
    nav_items = ["Dashboard", "Submit Claim", "All Claims", "Regulations", "API Docs"]
    for i, item in enumerate(nav_items):
        draw.text((20 + i*200, 100), item, fill=NAVY, font=None)
    
    # Title
    draw.text((50, 130), "Submit Insurance Claim", fill=NAVY, font=None)
    draw.text((50, 160), "All fields required. Your claim will be processed by 6 AI agents.", 
              fill=DARK_GRAY, font=None)
    
    # Example buttons
    draw.rectangle([(50, 200), (200, 240)], fill=LIGHT_BLUE)
    draw.text((60, 210), "Low Risk Example", fill=WHITE, font=None)
    draw.rectangle([(220, 200), (370, 240)], fill=LIGHT_BLUE)
    draw.text((230, 210), "High Risk Example", fill=WHITE, font=None)
    draw.rectangle([(390, 200), (520, 240)], fill=RED)
    draw.text((400, 210), "Fraud Example", fill=WHITE, font=None)
    
    # Form fields
    y = 280
    fields = [
        ("Full Name *", "John Smith"),
        ("Email Address *", "john.smith@email.com"),
        ("Customer ID", "CUST-12345 (auto-generated if empty)"),
        ("Policy Number *", "POL-2024-XXXXXXXX"),
        ("Claim Type *", "Select claim type..."),
        ("Incident Date *", ""),
        ("Claim Amount (USD) *", "$"),
        ("Incident Description * (Minimum 10 characters)", "Describe the incident in detail..."),
    ]
    
    for label, value in fields:
        draw.text((70, y), label, fill=NAVY, font=None)
        draw.rectangle([(70, y+25), (1200, y+50)], outline=LIGHT_GRAY, width=1)
        draw.text((80, y+30), value, fill=DARK_GRAY, font=None)
        y += 65
    
    # Buttons
    draw.rectangle([(70, y), (180, y+40)], fill=LIGHT_GRAY)
    draw.text((80, y+10), "Cancel", fill=DARK_GRAY, font=None)
    
    draw.rectangle([(200, y), (400, y+40)], fill=GREEN)
    draw.text((220, y+10), "🚀 Submit & Assess Claim", fill=WHITE, font=None)
    
    # Footer
    draw.text((50, 920), "Insurance Claim Assessment System v1.0", fill=LIGHT_GRAY, font=None)
    
    return img


def create_claims_list_screenshot():
    """Create claims list page mockup."""
    img = Image.new('RGB', (1280, 960), color=WHITE)
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([(0, 0), (1280, 80)], fill=NAVY)
    draw.text((20, 15), "🛡️ ClaimAI Insurance Assessment System", fill=WHITE, font=None)
    
    # Navigation
    nav_items = ["Dashboard", "Submit Claim", "All Claims", "Regulations", "API Docs"]
    for i, item in enumerate(nav_items):
        draw.text((20 + i*200, 100), item, fill=NAVY, font=None)
    
    # Title
    draw.text((50, 130), "All Claims", fill=NAVY, font=None)
    draw.text((50, 160), "2 claims", fill=DARK_GRAY, font=None)
    
    draw.rectangle([(1100, 130), (1250, 170)], fill=GREEN)
    draw.text((1110, 140), "+ Submit New Claim", fill=WHITE, font=None)
    
    # Table headers
    draw.rectangle([(50, 200), (1250, 240)], fill=LIGHT_GRAY)
    headers = ["Claim #", "Customer", "Type", "Amount", "Approved", "Fraud Score", "Compliance", "Status", "Action"]
    x = 70
    for header in headers:
        draw.text((x, 210), header, fill=NAVY, font=None)
        x += 130
    
    # Table rows
    claims = [
        ["CLM-20260614-9FB40756", "Robert Williams", "auto", "$8,500", "—", "0.000", "0.842", "under review", "View"],
        ["CLM-20260614-3C4F3C72", "Sarah Johnson", "health", "$3,500", "—", "0.000", "0.880", "under review", "View"],
    ]
    
    y = 260
    for claim in claims:
        draw.rectangle([(50, y), (1250, y+40)], outline=LIGHT_GRAY, width=1)
        x = 70
        for item in claim:
            draw.text((x, y+10), item, fill=DARK_GRAY, font=None)
            x += 130
        y += 50
    
    # Footer
    draw.text((50, 920), "Insurance Claim Assessment System v1.0", fill=LIGHT_GRAY, font=None)
    
    return img


def create_claim_detail_screenshot():
    """Create claim detail page mockup."""
    img = Image.new('RGB', (1280, 960), color=WHITE)
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([(0, 0), (1280, 80)], fill=NAVY)
    draw.text((20, 15), "🛡️ ClaimAI Insurance Assessment System", fill=WHITE, font=None)
    
    # Navigation
    nav_items = ["Dashboard", "Submit Claim", "All Claims", "Regulations", "API Docs"]
    for i, item in enumerate(nav_items):
        draw.text((20 + i*200, 100), item, fill=NAVY, font=None)
    
    # Breadcrumb
    draw.text((50, 130), "← All Claims / CLM-20260614-9FB40756", fill=DARK_GRAY, font=None)
    draw.text((50, 160), "Auto Insurance Claim", fill=NAVY, font=None)
    
    status_color = (255, 193, 7)  # Yellow for under review
    draw.rectangle([(1100, 130), (1250, 170)], fill=status_color)
    draw.text((1110, 140), "under review", fill=WHITE, font=None)
    
    # Tabs
    tabs = ["Overview", "Assessment Results", "Agent Reasoning", "Audit Trail"]
    for i, tab in enumerate(tabs):
        color = NAVY if i == 0 else LIGHT_GRAY
        draw.text((50 + i*250, 200), tab, fill=color, font=None)
    
    # Claim Information
    draw.text((50, 240), "Claim Information", fill=NAVY, font=None)
    y = 280
    info = [
        ("Customer", "Robert Williams"),
        ("Policy Number", "AUTO-2024-X9981K"),
        ("Claim Type", "auto"),
        ("Claim Amount", "$8,500"),
        ("Incident Date", "6/10/2026"),
        ("Status", "under review"),
        ("Submitted", "6/14/2026, 7:05:46 AM"),
        ("Assessed", "6/14/2026, 7:09:24 AM"),
    ]
    
    for label, value in info:
        draw.text((70, y), label, fill=DARK_GRAY, font=None)
        draw.text((350, y), value, fill=NAVY, font=None)
        y += 35
    
    # Assessment Scores
    draw.text((650, 240), "Assessment Scores", fill=NAVY, font=None)
    y = 280
    scores = [
        ("Final Score", "0.842", GREEN),
        ("Compliance Score", "0.740", GREEN),
        ("Fraud Score", "0.000", GREEN),
        ("Risk Score", "0.000", GREEN),
        ("Identity Confidence", "0.500", GREEN),
    ]
    
    for label, value, color in scores:
        draw.rectangle([(650, y), (900, y+30)], outline=color, width=2)
        draw.text((670, y+8), label, fill=DARK_GRAY, font=None)
        draw.text((800, y+8), value, fill=color, font=None)
        y += 40
    
    # Compliance Status
    draw.text((650, 500), "Compliance Status", fill=NAVY, font=None)
    compliance = ["✓ IRDAI: Pass", "✓ SOX: Pass", "✓ AML: Pass", "✓ KYC: Pass"]
    y = 540
    for comp in compliance:
        draw.text((670, y), comp, fill=GREEN, font=None)
        y += 30
    
    # Footer
    draw.text((50, 920), "Insurance Claim Assessment System v1.0", fill=LIGHT_GRAY, font=None)
    
    return img


def create_api_docs_screenshot():
    """Create API documentation page mockup."""
    img = Image.new('RGB', (1280, 960), color=WHITE)
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([(0, 0), (1280, 80)], fill=NAVY)
    draw.text((20, 15), "Swagger UI - Insurance Claim Assessment API", fill=WHITE, font=None)
    
    # Navigation
    nav_items = ["Dashboard", "Submit Claim", "All Claims", "Regulations", "API Docs"]
    for i, item in enumerate(nav_items):
        draw.text((20 + i*200, 100), item, fill=NAVY, font=None)
    
    # Title
    draw.text((50, 130), "Insurance Claim Assessment System API", fill=NAVY, font=None)
    draw.text((50, 160), "Version 1.0.0 | Production-ready multi-agent AI system for BFSI", 
              fill=DARK_GRAY, font=None)
    
    # API Endpoints
    endpoints = [
        ("POST", "/api/claims/submit", "Submit new insurance claim"),
        ("GET", "/api/claims/{id}", "Get claim by ID with assessment"),
        ("POST", "/api/claims/{id}/assess", "Trigger assessment pipeline"),
        ("GET", "/api/claims/{id}/audit", "Get immutable audit trail"),
        ("GET", "/api/dashboard", "System dashboard and metrics"),
    ]
    
    y = 230
    for method, path, desc in endpoints:
        method_color = LIGHT_BLUE
        draw.rectangle([(50, y), (150, y+30)], fill=method_color)
        draw.text((60, y+8), method, fill=WHITE, font=None)
        
        draw.rectangle([(160, y), (700, y+30)], outline=LIGHT_GRAY, width=1)
        draw.text((170, y+8), path, fill=DARK_GRAY, font=None)
        
        draw.text((720, y+8), desc, fill=DARK_GRAY, font=None)
        y += 50
    
    # Request/Response example
    draw.text((50, 530), "Example Request", fill=NAVY, font=None)
    draw.rectangle([(50, 560), (1250, 730)], outline=LIGHT_GRAY, width=1, fill=LIGHT_GRAY)
    
    example = """POST /api/claims/submit
{
  "customer_name": "John Smith",
  "email": "john@example.com",
  "policy_number": "POL-2024-123456",
  "claim_type": "auto",
  "claim_amount": 8500,
  "incident_description": "Car accident on highway"
}"""
    
    draw.text((70, 570), example, fill=DARK_GRAY, font=None)
    
    # Footer
    draw.text((50, 920), "Insurance Claim Assessment System v1.0 | API Docs", 
              fill=LIGHT_GRAY, font=None)
    
    return img


def main():
    """Generate all screenshot images."""
    screenshots = {
        "screenshot_dashboard.png": create_dashboard_screenshot(),
        "screenshot_submit_claim.png": create_submit_claim_screenshot(),
        "screenshot_claims_list.png": create_claims_list_screenshot(),
        "screenshot_claim_detail.png": create_claim_detail_screenshot(),
        "screenshot_api_docs.png": create_api_docs_screenshot(),
    }
    
    for filename, img in screenshots.items():
        filepath = os.path.join(os.path.dirname(__file__), filename)
        img.save(filepath)
        print(f"✅ Created: {filename}")
    
    return list(screenshots.keys())


if __name__ == "__main__":
    main()

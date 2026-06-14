# Insurance Claim Assessment System
## Deployment Guide

**Document Version:** 1.0  
**Date:** June 2026  
**Classification:** Operations - Confidential  
**Audience:** DevOps Engineers, System Administrators, Operations Teams

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Running the System](#running-the-system)
6. [Database Setup](#database-setup)
7. [MCP Server Deployment](#mcp-server-deployment)
8. [Monitoring & Logging](#monitoring--logging)
9. [Troubleshooting](#troubleshooting)
10. [Backup & Recovery](#backup--recovery)
11. [Scaling & Load Balancing](#scaling--load-balancing)
12. [Post-Deployment Validation](#post-deployment-validation)

---

## Pre-Deployment Checklist

Before deploying to production, verify the following:

### Infrastructure
- [ ] Server(s) with minimum requirements met
- [ ] Network connectivity and firewall rules configured
- [ ] SSL/TLS certificates obtained
- [ ] DNS entries configured
- [ ] Load balancer configured (if applicable)

### Dependencies
- [ ] Python 3.10+ installed
- [ ] pip package manager available
- [ ] SQLite3 installed
- [ ] Git installed (for version control)

### Credentials & Secrets
- [ ] Anthropic API key obtained
- [ ] Database encryption key generated
- [ ] JWT secret key generated
- [ ] SSL certificate key pair ready
- [ ] OAuth credentials (if using SSO)

### Access & Permissions
- [ ] Database user created with appropriate permissions
- [ ] Application service account created
- [ ] File system permissions configured
- [ ] Firewall rules allowing required ports
- [ ] Log aggregation service credentials (if applicable)

### Compliance & Documentation
- [ ] Security review completed
- [ ] Compliance sign-off obtained
- [ ] Incident response procedures documented
- [ ] Rollback plan prepared
- [ ] Communication plan ready

### Testing
- [ ] All tests passing in staging environment
- [ ] Performance baselines established
- [ ] Security scan completed
- [ ] Load test passed
- [ ] Failover scenarios tested

---

## System Requirements

### Minimum Hardware Requirements

**Single Server Deployment:**
```
CPU:          2 cores (4+ cores recommended)
Memory:       2 GB RAM (4+ GB for production)
Storage:      10 GB available (20+ GB recommended)
Network:      100 Mbps connection minimum
Availability: 99.5% uptime SLA
```

**Load-Balanced Deployment:**
```
Load Balancer: 
  CPU:        2 cores
  Memory:     2 GB
  
Application Servers (minimum 2):
  CPU:        4 cores per instance
  Memory:     4 GB per instance
  
Database Server:
  CPU:        4 cores
  Memory:     8 GB
  Storage:    50 GB+ (depends on retention policy)
  
Monitoring/Logging:
  CPU:        2 cores
  Memory:     4 GB
  Storage:    100+ GB (log retention dependent)
```

### Software Requirements

```
Operating System:   Linux (Ubuntu 20.04 LTS or equivalent)
Python:             3.10+ (3.11 recommended)
FastAPI:            0.100.0+
Uvicorn:            0.23.0+
SQLAlchemy:         2.0+
SQLite:             3.37+
```

### Network Requirements

```
Outbound:
  - HTTPS to api.anthropic.com (Claude API)
  - HTTPS to any external knowledge base services
  
Inbound:
  - HTTP/HTTPS on port 80/443 (API)
  - Optional: SSH on port 22 (management)
  
Firewall Rules:
  - Allow traffic only from authorized IP ranges
  - Rate limiting enabled
  - DDoS protection recommended
```

---

## Installation Steps

### Step 1: Clone Repository

```bash
# Navigate to deployment directory
cd /opt/applications

# Clone the repository
git clone https://github.com/your-org/insurance-claim-assessment.git
cd insurance-claim-assessment

# Checkout production branch
git checkout main
git pull origin main
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel
```

### Step 3: Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list | grep -E "anthropic|fastapi|sqlalchemy|uvicorn"
```

### Step 4: Create Directory Structure

```bash
# Create necessary directories
mkdir -p logs
mkdir -p data
mkdir -p config
mkdir -p backups

# Set appropriate permissions
chmod 755 logs data config backups
chown application:application logs data config backups
```

### Step 5: Initialize Database

```bash
# Run database initialization
python -c "from database.setup import init_db; import asyncio; asyncio.run(init_db())"

# Verify database creation
ls -la data/

# Sample output:
# -rw-r--r-- application application 1.2M claims.db
```

---

## Configuration

### Step 1: Environment File (.env)

Create `.env` file in the application root:

```bash
# .env - Production Configuration

# API Configuration
APP_PORT=8000
APP_HOST=0.0.0.0
APP_ENV=production
APP_LOG_LEVEL=INFO

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-... (your actual key)
ANTHROPIC_MODEL=claude-sonnet-4-6

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/claims.db
DATABASE_ECHO=false
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Security
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=1
JWT_REFRESH_EXPIRATION_DAYS=7

# CORS Configuration
CORS_ORIGINS=["https://yourdomain.com"]
CORS_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_PER_USER=100  # per hour
RATE_LIMIT_PER_IP=1000   # per hour

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # or 'text'
LOG_FILE=logs/app.log

# Security
ENABLE_HTTPS=true
SSL_CERT_FILE=/etc/ssl/certs/cert.pem
SSL_KEY_FILE=/etc/ssl/private/key.pem

# PII Encryption
ENCRYPTION_KEY=your-32-char-base64-encoded-encryption-key
ENCRYPTION_ALGORITHM=AES-256

# MCP Server
MCP_SERVER_ENABLED=true
MCP_SERVER_PORT=8001
MCP_SERVER_HOST=localhost

# Email (for notifications)
EMAIL_PROVIDER=smtp  # or 'sendgrid'
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@example.com
EMAIL_PASSWORD=your-password
EMAIL_FROM=noreply@yourdomain.com

# Audit Configuration
AUDIT_RETENTION_DAYS=3650  # 10 years
AUDIT_ARCHIVE_FREQUENCY=monthly

# Feature Flags
ENABLE_DOCUMENT_PROCESSING=true
ENABLE_FRAUD_DETECTION=true
ENABLE_SANDBOX_MODE=false
```

### Step 2: Generate Security Keys

```bash
# Generate JWT secret (32+ characters)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Output: example_jwt_key_here

# Generate encryption key
python3 -c "
import base64
import secrets
key = secrets.token_bytes(32)
b64_key = base64.b64encode(key).decode()
print(f'ENCRYPTION_KEY={b64_key}')
"
# Output: ENCRYPTION_KEY=base64_encoded_key_here
```

### Step 3: SSL/TLS Certificates

**Option A: Using Let's Encrypt (Recommended)**

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificate locations:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem (cert)
# /etc/letsencrypt/live/yourdomain.com/privkey.pem (key)

# Update .env:
SSL_CERT_FILE=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
SSL_KEY_FILE=/etc/letsencrypt/live/yourdomain.com/privkey.pem

# Setup auto-renewal
sudo certbot renew --dry-run
```

**Option B: Self-Signed Certificate (Development Only)**

```bash
# Generate self-signed certificate (valid 365 days)
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365 \
  -subj "/CN=localhost"

# Update .env:
SSL_CERT_FILE=./cert.pem
SSL_KEY_FILE=./key.pem
```

### Step 4: Database Configuration

```bash
# Create database user (if using separate DB)
sudo sqlite3 data/claims.db "PRAGMA journal_mode=WAL;"

# Set file permissions
sudo chown application:application data/claims.db
sudo chmod 600 data/claims.db

# Backup database location
sudo mkdir -p /var/backups/claims-db
sudo chown application:application /var/backups/claims-db
sudo chmod 700 /var/backups/claims-db
```

---

## Running the System

### Option 1: Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run with uvicorn directly
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# Press CTRL+C to quit
```

### Option 2: Production Mode (Systemd Service)

Create systemd service file: `/etc/systemd/system/claim-assessment.service`

```ini
[Unit]
Description=Insurance Claim Assessment System
After=network.target

[Service]
Type=notify
User=application
WorkingDirectory=/opt/applications/insurance-claim-assessment
Environment="PATH=/opt/applications/insurance-claim-assessment/venv/bin"
EnvironmentFile=/opt/applications/insurance-claim-assessment/.env
ExecStart=/opt/applications/insurance-claim-assessment/venv/bin/uvicorn \
  main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --loop uvloop \
  --http httptools

# Restart policy
Restart=on-failure
RestartSec=10s
StartLimitInterval=60s
StartLimitBurst=5

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true

[Install]
WantedBy=multi-user.target
```

Deploy the service:

```bash
# Copy service file
sudo cp claim-assessment.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable claim-assessment

# Start service
sudo systemctl start claim-assessment

# Check status
sudo systemctl status claim-assessment

# View logs
sudo journalctl -u claim-assessment -f
```

### Option 3: Docker Container

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m application && chown -R application:application /app
USER application

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
# Build image
docker build -t claim-assessment:1.0.0 .

# Run container
docker run -d \
  --name claim-assessment \
  -p 8000:8000 \
  --env-file .env \
  -v /var/data:/app/data \
  -v /var/logs:/app/logs \
  claim-assessment:1.0.0

# View logs
docker logs -f claim-assessment

# Stop container
docker stop claim-assessment
```

### Option 4: Kubernetes Deployment

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: claim-assessment
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: claim-assessment
  template:
    metadata:
      labels:
        app: claim-assessment
    spec:
      containers:
      - name: api
        image: claim-assessment:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: anthropic-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

Deploy to Kubernetes:

```bash
# Apply deployment
kubectl apply -f deployment.yaml

# Check deployment status
kubectl get deployments -n production
kubectl get pods -n production

# View logs
kubectl logs -n production deployment/claim-assessment -f
```

---

## Database Setup

### SQLite Setup

```bash
# Initialize database with schema
python database/setup.py

# Verify schema creation
sqlite3 data/claims.db ".schema"

# Insert seed data (regulatory knowledge)
python -c "from database.setup import seed_regulatory_knowledge; import asyncio; asyncio.run(seed_regulatory_knowledge())"

# Check data
sqlite3 data/claims.db "SELECT COUNT(*) FROM regulatory_knowledge;"
```

### Database Backup

```bash
# Automated daily backup (crontab)
0 2 * * * /opt/applications/insurance-claim-assessment/backup.sh

# Contents of backup.sh:
#!/bin/bash
BACKUP_DIR="/var/backups/claims-db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/claims_$TIMESTAMP.db"

# Create backup
cp /opt/applications/insurance-claim-assessment/data/claims.db "$BACKUP_FILE"

# Compress
gzip "$BACKUP_FILE"

# Keep last 30 backups
find "$BACKUP_DIR" -name "claims_*.db.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

---

## MCP Server Deployment

### Deploy MCP Server

```bash
# The MCP server runs alongside the main application

# In main.py, ensure MCP server is initialized:
from mcp_server.regulatory_knowledge_mcp import mcp_server

# Start MCP server (automatic with main app)
# Listens on port 8001 by default

# Test MCP connectivity
curl http://localhost:8001/health

# Expected output:
# {"status": "healthy", "version": "1.0.0"}
```

### Configure MCP Server

In `.env`:

```
MCP_SERVER_ENABLED=true
MCP_SERVER_PORT=8001
MCP_SERVER_HOST=0.0.0.0
```

---

## Monitoring & Logging

### Application Logging

```python
# Logs are written to: logs/app.log

# Log levels:
# DEBUG    - Detailed debugging information
# INFO     - General informational messages
# WARNING  - Warning messages
# ERROR    - Error messages
# CRITICAL - Critical errors

# Example log entries:
# 2026-06-14 10:30:45,123 [INFO] Insurance Claim Assessment System started
# 2026-06-14 10:31:02,456 [INFO] [Orchestrator] Claim CLM-2026-001234 submitted
# 2026-06-14 10:31:05,789 [INFO] [CustomerAgent] Customer validation passed
```

### Structured Logging

Enable JSON logging in production:

```bash
# In .env:
LOG_FORMAT=json

# Logs output as JSON for easy parsing:
{
  "timestamp": "2026-06-14T10:31:05.789Z",
  "level": "INFO",
  "logger": "assessment_orchestrator",
  "message": "Assessment completed",
  "claim_id": "CLM-2026-001234",
  "duration_ms": 245000,
  "decision": "approved",
  "confidence": 0.94
}
```

### Monitoring Dashboard

**Key Metrics to Monitor:**

```
Application Metrics:
  - API response time (p95, p99)
  - Request throughput (req/sec)
  - Error rate (%)
  - Active connections
  
Business Metrics:
  - Claims submitted per day
  - Average assessment time
  - Decision distribution (approved/rejected/review)
  - Fraud detection rate
  
System Metrics:
  - CPU usage (%)
  - Memory usage (%)
  - Disk usage (%)
  - Database connection pool
  - Database query time
```

### Health Check Endpoint

```bash
# Health check available at:
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "timestamp": "2026-06-14T10:31:05Z",
  "components": {
    "database": "healthy",
    "mcp_server": "healthy",
    "api": "operational"
  }
}
```

---

## Troubleshooting

### Common Issues & Solutions

**Issue: "Cannot connect to Anthropic API"**

```bash
# Check:
1. ANTHROPIC_API_KEY is set correctly
   echo $ANTHROPIC_API_KEY
   
2. API key has not expired
   Contact: support@anthropic.com
   
3. Network connectivity
   curl https://api.anthropic.com/health
   
4. Firewall rules
   sudo ufw allow out to api.anthropic.com
```

**Issue: "Database locked"**

```bash
# Check for stale connections
sqlite3 data/claims.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
cp /var/backups/claims-db/latest.db data/claims.db

# Enable WAL mode
sqlite3 data/claims.db "PRAGMA journal_mode=WAL;"
```

**Issue: "High memory usage"**

```bash
# Check for memory leaks
ps aux | grep uvicorn

# Restart application
sudo systemctl restart claim-assessment

# If persistent, check logs
grep -i "memory\|leak" logs/app.log
```

**Issue: "Slow assessment times"**

```bash
# Check database query performance
sqlite3 data/claims.db ".timer on"
sqlite3 data/claims.db "SELECT * FROM assessments LIMIT 10;"

# Verify indexes are present
sqlite3 data/claims.db ".schema insurance_claims"

# Check API response times
grep "duration_ms" logs/app.log | tail -20
```

**Issue: "Authentication failures"**

```bash
# Check JWT secret is consistent
grep JWT_SECRET .env

# Verify token validity
# Include token in request:
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/claims

# Check token expiration
# Tokens valid for 1 hour by default
```

---

## Backup & Recovery

### Backup Strategy

**Frequency:**
- Database: Daily at 02:00 UTC
- Logs: Weekly archival
- Configuration: Versioned in Git

**Retention:**
- Daily backups: 30 days
- Weekly archives: 6 months
- Configuration: Indefinite (Git)

### Restore Procedure

```bash
# 1. Identify backup to restore
ls -lah /var/backups/claims-db/

# 2. Stop application
sudo systemctl stop claim-assessment

# 3. Restore database
cp /var/backups/claims-db/claims_20260614_020000.db.gz /tmp/
gunzip /tmp/claims_20260614_020000.db.gz
cp /tmp/claims_20260614_020000.db data/claims.db

# 4. Verify integrity
sqlite3 data/claims.db "PRAGMA integrity_check;"

# 5. Start application
sudo systemctl start claim-assessment

# 6. Verify restoration
curl http://localhost:8000/health
```

---

## Scaling & Load Balancing

### Horizontal Scaling

**Architecture:**
```
[Internet] 
    ↓
[Load Balancer - Nginx/HAProxy]
    ↓
[App Instance 1] [App Instance 2] [App Instance 3]
    ↓               ↓               ↓
[Shared Database - SQLite/PostgreSQL]
```

### Load Balancer Configuration (Nginx)

```nginx
upstream claim_assessment {
    least_conn;  # Load balancing algorithm
    server app1.internal:8000;
    server app2.internal:8000;
    server app3.internal:8000;
    
    # Health check
    check interval=3000 rise=2 fall=5 timeout=1000 type=http;
    check_http_send "GET /health HTTP/1.0\r\n\r\n";
    check_http_expect_alive http_2xx http_3xx;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    location / {
        proxy_pass http://claim_assessment;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
```

### Database Optimization for Multiple Instances

```bash
# Configure SQLite for concurrent access
sqlite3 data/claims.db "PRAGMA journal_mode=WAL;"
sqlite3 data/claims.db "PRAGMA synchronous=NORMAL;"
sqlite3 data/claims.db "PRAGMA cache_size=10000;"
sqlite3 data/claims.db "PRAGMA temp_store=MEMORY;"

# Create indexes for common queries
sqlite3 data/claims.db "CREATE INDEX IF NOT EXISTS idx_claim_customer ON insurance_claims(customer_id);"
sqlite3 data/claims.db "CREATE INDEX IF NOT EXISTS idx_claim_status ON insurance_claims(status);"
sqlite3 data/claims.db "CREATE INDEX IF NOT EXISTS idx_assessment_claim ON assessments(claim_id);"
```

---

## Post-Deployment Validation

### Validation Checklist

```
✓ Application started successfully
  sudo systemctl status claim-assessment

✓ API endpoints responding
  curl http://localhost:8000/api/claims

✓ Database initialized with seed data
  sqlite3 data/claims.db "SELECT COUNT(*) FROM regulatory_knowledge;"

✓ MCP server operational
  curl http://localhost:8001/health

✓ Logging configured
  tail -f logs/app.log

✓ SSL/TLS working
  curl https://localhost:8000 -k

✓ Authentication functioning
  curl -H "Authorization: Bearer <token>" http://localhost:8000/api/claims

✓ Rate limiting active
  # Send >100 requests in 1 minute, should get 429 response

✓ Audit trail recording
  sqlite3 data/claims.db "SELECT COUNT(*) FROM audit_logs;"

✓ Backups running
  ls -la /var/backups/claims-db/

✓ Monitoring alerts configured
  # Verify alert rules are active
```

### Performance Baseline

```bash
# Establish baseline metrics
# Load test with 10 concurrent users
locust -f loadtest.py --host=http://localhost:8000 \
  --clients=10 --hatch-rate=1 --run-time=5m

# Record metrics:
# - Average response time: ________
# - p95 response time: ________
# - p99 response time: ________
# - Throughput (req/sec): ________
# - Error rate: ________
```

---

## Post-Deployment Support

### On-Call Support

- **Primary**: DevOps Lead
- **Secondary**: System Administrator
- **Escalation**: Engineering Manager

### Incident Response

1. **Detection**: Monitoring alerts
2. **Notification**: PagerDuty/On-call system
3. **Assessment**: Determine severity level
4. **Mitigation**: Execute mitigation procedures
5. **Resolution**: Fix root cause
6. **Communication**: Update stakeholders
7. **Post-mortem**: Document learnings

### Knowledge Base

- Common issues and solutions documented
- Runbooks for emergency procedures
- Performance optimization tips
- Scaling procedures

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Jun 2026 | DevOps Team | Initial release |

---

## Related Documents

- Architecture Diagram & Overview
- Technical Design Document
- Governance Report
- Testing & Evaluation Report

---

## Sign-Off

**Prepared By**: DevOps Team  
**Reviewed By**: System Architect  
**Approved By**: Operations Manager  
**Date**: June 2026

---

## Contact Information

For deployment support or questions:
- **Email**: devops@yourdomain.com
- **Slack**: #infrastructure-support
- **Wiki**: https://wiki.yourdomain.com/claim-assessment

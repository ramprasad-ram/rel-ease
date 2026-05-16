# Release Orchestration Platform - Runbook

**Version:** 1.0.0  
**Last Updated:** 2026-05-16  
**Purpose:** Complete operational guide for running the Semicolons Release Orchestrator

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Requirements](#system-requirements)
3. [Initial Setup](#initial-setup)
4. [Running the Application](#running-the-application)
5. [Configuration](#configuration)
6. [API Endpoints](#api-endpoints)
7. [Testing & Validation](#testing--validation)
8. [Troubleshooting](#troubleshooting)
9. [Production Deployment](#production-deployment)
10. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Project Overview

The Release Orchestration Platform is an AI-powered system for managing deployment lifecycles with intelligent automation. It uses specialized agents to handle release planning, validation, deployment, rollback, and post-mortem analysis.

**Key Features:**
- Release planning with dependency analysis
- Pre-flight validation with memory leak detection
- Canary deployments with progressive traffic shifting
- Autonomous rollback on error detection
- Post-mortem analysis with root cause identification
- Real-time monitoring via Server-Sent Events

**Technology Stack:**
- **Backend:** FastAPI (Python 3.10+), SQLAlchemy, Pydantic
- **Frontend:** React 19, Vite, React Router
- **Database:** SQLite (dev), PostgreSQL (prod)
- **Communication:** REST API, Server-Sent Events (SSE)

---

## System Requirements

### Minimum Requirements

**Backend:**
- Python 3.10 or higher
- pip (Python package manager)
- 2GB RAM
- 1GB disk space

**Frontend:**
- Node.js 18+ or higher
- npm 9+ or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

**Operating Systems:**
- macOS (tested on Sequoia)
- Linux (Ubuntu 20.04+, Debian 11+)
- Windows 10/11 (with WSL2 recommended)

---

## Initial Setup

### 1. Clone or Navigate to Project

```bash
# If cloning from repository
git clone <repository-url>
cd rel-ease

# If already have the project
cd /path/to/rel-ease
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd semicolons-release-orchestrator/backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment configuration
cp .env.example .env

# (Optional) Edit .env file for custom configuration
# nano .env  # or use your preferred editor
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd semicolons-release-orchestrator/frontend

# Install dependencies
npm install

# Verify installation
npm list --depth=0
```

### 4. Database Initialization

The database is automatically initialized on first run. No manual setup required for development (SQLite).

---

## Running the Application

### Starting the Backend

**Option 1: Using Python directly (Recommended for development)**

```bash
# From backend directory with venv activated
cd semicolons-release-orchestrator/backend
source venv/bin/activate  # if not already activated
python3 main.py
```

**Option 2: Using uvicorn directly**

```bash
cd semicolons-release-orchestrator/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Starting Release Orchestration Platform...
INFO:     Initializing database...
INFO:     Database initialized successfully
INFO:     Application started: Release Orchestration Platform v1.0.0
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Backend URLs:**
- API Root: http://localhost:8000
- API Documentation (Swagger): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Starting the Frontend

**From a new terminal window:**

```bash
# Navigate to frontend directory
cd semicolons-release-orchestrator/frontend

# Start development server
npm run dev -- --host 0.0.0.0

# Alternative (without host binding):
npm run dev
```

**Expected Output:**
```
VITE v8.0.12  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
➜  press h + enter to show help
```

**Frontend URL:**
- Dashboard: http://localhost:5173

### Verifying the Setup

1. **Check Backend Health:**
   ```bash
   curl http://localhost:8000/health
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "environment": "development"
   }
   ```

2. **Check Frontend:**
   - Open http://localhost:5173 in your browser
   - You should see the Release Orchestration Platform dashboard

3. **Check API Documentation:**
   - Open http://localhost:8000/docs
   - You should see interactive Swagger UI with all endpoints

---

## Configuration

### Backend Configuration (.env)

Located at: `semicolons-release-orchestrator/backend/.env`

**Essential Settings:**

```env
# Application
APP_NAME=Release Orchestration Platform
APP_VERSION=1.0.0
DEBUG=true

# API
API_V1_PREFIX=/api/v1

# Database
DATABASE_URL=sqlite+aiosqlite:///./release_orchestrator.db
DATABASE_ECHO=false

# Mock CI/CD (for demo/testing)
MOCK_CICD_ENABLED=true
MOCK_CICD_DELAY_MIN=2
MOCK_CICD_DELAY_MAX=5
MOCK_CICD_FAILURE_RATE=0.1

# AI Agents
AI_AGENT_ENABLED=true
AI_AGENT_CONFIDENCE_THRESHOLD=0.7
AI_AGENT_TIMEOUT=30

# Rollback Thresholds
ROLLBACK_ERROR_THRESHOLD=0.15
ROLLBACK_CRITICAL_THRESHOLD=0.30

# Slack Integration (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_ENABLED=false

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# CORS (adjust for your frontend URL)
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8080"]
```

### Frontend Configuration

The frontend automatically connects to `http://localhost:8000` for the backend API. To change this, edit:

`semicolons-release-orchestrator/frontend/src/components/*.jsx`

Look for API base URL configurations (typically using axios).

---

## API Endpoints

### Core Endpoints

**Health & Info:**
- `GET /health` - Health check
- `GET /` - API root information
- `GET /api/v1/` - API version information

**Release Planning:**
- `POST /api/v1/release-planning/analyze` - Analyze release readiness
  ```json
  {
    "repository": "owner/repo",
    "sprint_id": "SPRINT-1"
  }
  ```

**Pre-Flight Validation:**
- `POST /api/v1/pre-flight/check` - Run pre-flight validation
  ```json
  {
    "deployment_id": "uuid",
    "repository": "owner/repo"
  }
  ```

**Canary Deployment:**
- `POST /api/v1/canary/start` - Start canary deployment
- `GET /api/v1/canary/{deployment_id}/status` - Get deployment status
- `GET /api/v1/canary/{deployment_id}/stream` - Real-time updates (SSE)

**Rollback:**
- `POST /api/v1/rollback/start-monitoring` - Start monitoring for auto-rollback
- `POST /api/v1/rollback/inject-errors` - Inject errors (testing only)
- `GET /api/v1/rollback/status/{monitor_id}` - Check rollback status
- `GET /api/v1/rollback/active-monitors` - List active monitors

**Post-Mortem:**
- `POST /api/v1/postmortem/analyze` - Trigger post-mortem analysis
- `GET /api/v1/postmortem/report/{deployment_id}` - Get full report
- `GET /api/v1/postmortem/summary/{deployment_id}` - Get summary

**Demo/Dashboard:**
- `GET /api/v1/demo/dashboard` - Get complete dashboard data (mock)

### Using the API

**Via Swagger UI (Recommended for testing):**
1. Open http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

**Via curl:**
```bash
# Health check
curl http://localhost:8000/health

# Release planning analysis
curl -X POST http://localhost:8000/api/v1/release-planning/analyze \
  -H "Content-Type: application/json" \
  -d '{"repository": "ramprasad-ram/rel-ease", "sprint_id": "SPRINT-1"}'

# Get dashboard data
curl http://localhost:8000/api/v1/demo/dashboard
```

---

## Testing & Validation

### Backend Tests

```bash
cd semicolons-release-orchestrator/backend
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
python test_canary_deployment.py
python test_rollback_agent.py
python test_postmortem_agent.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Manual Testing Workflow

**1. Test Release Planning:**
```bash
curl -X POST http://localhost:8000/api/v1/release-planning/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "ramprasad-ram/rel-ease",
    "sprint_id": "SPRINT-1"
  }'
```

**2. Test Pre-Flight Validation:**
- Use Swagger UI at http://localhost:8000/docs
- Navigate to Pre-Flight endpoints
- Execute validation checks

**3. Test Canary Deployment:**
- Start a canary deployment via API or frontend
- Monitor progress via SSE stream
- Verify traffic shifting (10% → 25% → 50% → 100%)

**4. Test Rollback:**
```bash
# Start monitoring
curl -X POST http://localhost:8000/api/v1/rollback/start-monitoring \
  -H "Content-Type: application/json" \
  -d '{
    "deployment_id": "test-deployment",
    "service_name": "test-service"
  }'

# Inject errors to trigger rollback
curl -X POST http://localhost:8000/api/v1/rollback/inject-errors \
  -H "Content-Type: application/json" \
  -d '{
    "monitor_id": "monitor-id-from-previous-response",
    "error_rate": 0.25
  }'
```

### Frontend Testing

```bash
cd semicolons-release-orchestrator/frontend

# Run linter
npm run lint

# Build for production (validates build)
npm run build

# Preview production build
npm run preview
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Problem:** `Address already in use` error

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux

# Or use different port
uvicorn main:app --port 8001
```

#### 2. Module Not Found Errors

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt

# If still failing, recreate venv
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Database Errors

**Problem:** Database corruption or schema issues

**Solution:**
```bash
cd semicolons-release-orchestrator/backend

# Remove database file
rm release_orchestrator.db

# Restart application (will recreate database)
python3 main.py
```

#### 4. Frontend Not Connecting to Backend

**Problem:** API calls failing with CORS or connection errors

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in backend `.env`:
   ```env
   CORS_ORIGINS=["http://localhost:5173"]
   ```
3. Restart backend after changing CORS settings
4. Clear browser cache and reload frontend

#### 5. npm Install Failures

**Problem:** `npm install` fails with dependency errors

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install

# If still failing, try with legacy peer deps
npm install --legacy-peer-deps
```

### Logs and Debugging

**Backend Logs:**
- Console output (stdout)
- Log file: `semicolons-release-orchestrator/backend/backend.log`

**View logs:**
```bash
# Real-time log monitoring
tail -f semicolons-release-orchestrator/backend/backend.log

# Search logs
grep "ERROR" semicolons-release-orchestrator/backend/backend.log
```

**Enable Debug Mode:**
```env
# In .env file
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_ECHO=true
```

---

## Production Deployment

### Pre-Production Checklist

- [ ] Switch to PostgreSQL database
- [ ] Set `DEBUG=false` in `.env`
- [ ] Configure production CORS origins
- [ ] Set up Slack webhooks (if using)
- [ ] Enable authentication/authorization
- [ ] Configure rate limiting
- [ ] Set up monitoring (Datadog, New Relic, etc.)
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline
- [ ] Load test the application
- [ ] Security audit

### Production Configuration

**Backend (.env):**
```env
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL_PROD=postgresql://user:password@host:5432/release_orchestrator
SLACK_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/REAL/WEBHOOK/URL
CORS_ORIGINS=["https://your-production-domain.com"]
```

**Database Migration:**
```bash
# Export data from SQLite (if needed)
sqlite3 release_orchestrator.db .dump > backup.sql

# Set up PostgreSQL
createdb release_orchestrator

# Update DATABASE_URL_PROD in .env
# Restart application (will initialize PostgreSQL schema)
```

**Running with Multiple Workers:**
```bash
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

**Using Docker (Recommended):**
```dockerfile
# Create Dockerfile in backend directory
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```bash
# Build and run
docker build -t release-orchestrator-backend .
docker run -p 8000:8000 --env-file .env release-orchestrator-backend
```

---

## Monitoring & Maintenance

### Health Checks

**Automated Health Check:**
```bash
# Add to cron or monitoring system
*/5 * * * * curl -f http://localhost:8000/health || alert-system
```

**Metrics to Monitor:**
- API response times
- Database connection pool
- Active deployments
- Error rates
- Memory usage
- CPU usage

### Database Maintenance

**Backup SQLite (Development):**
```bash
sqlite3 release_orchestrator.db ".backup backup_$(date +%Y%m%d).db"
```

**Backup PostgreSQL (Production):**
```bash
pg_dump release_orchestrator > backup_$(date +%Y%m%d).sql
```

### Log Rotation

**Setup logrotate (Linux):**
```bash
# Create /etc/logrotate.d/release-orchestrator
/path/to/backend/backend.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### Updates and Upgrades

**Update Dependencies:**
```bash
# Backend
cd semicolons-release-orchestrator/backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Frontend
cd semicolons-release-orchestrator/frontend
npm update
```

**Version Control:**
- Always test updates in development first
- Keep backups before major updates
- Document all configuration changes

---

## Quick Reference Commands

### Start Everything
```bash
# Terminal 1 - Backend
cd semicolons-release-orchestrator/backend && source venv/bin/activate && python3 main.py

# Terminal 2 - Frontend
cd semicolons-release-orchestrator/frontend && npm run dev -- --host 0.0.0.0
```

### Stop Everything
```bash
# Press Ctrl+C in each terminal
# Or kill processes:
pkill -f "python3 main.py"
pkill -f "vite"
```

### Reset Everything
```bash
# Backend
cd semicolons-release-orchestrator/backend
rm release_orchestrator.db backend.log
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd semicolons-release-orchestrator/frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Support and Documentation

**Additional Documentation:**
- Backend README: `semicolons-release-orchestrator/backend/README.md`
- Quick Start: `semicolons-release-orchestrator/backend/QUICKSTART.md`
- Project Overview: `semicolons-release-orchestrator/docs/PROJECT_OVERVIEW.md`
- Feature Docs: `semicolons-release-orchestrator/docs/`

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Key Files:**
- Backend entry: `semicolons-release-orchestrator/backend/main.py`
- Configuration: `semicolons-release-orchestrator/backend/config.py`
- Frontend entry: `semicolons-release-orchestrator/frontend/src/main.jsx`

---

## Notes for BOB Instances

This runbook is designed to be comprehensive and self-contained. When using this runbook:

1. **Always verify prerequisites** before starting
2. **Follow the order** of operations in Initial Setup
3. **Check logs** if something doesn't work as expected
4. **Use the Troubleshooting section** for common issues
5. **Test each component** individually before integration
6. **Keep this runbook updated** as the project evolves

**Environment Assumptions:**
- Working directory: `/Users/meenalgupta/Desktop/rel-ease` (adjust as needed)
- Python 3.9+ available as `python3`
- Node.js and npm installed
- Sufficient permissions to create files and run processes

**Success Indicators:**
- Backend responds to health checks
- Frontend loads in browser
- API documentation accessible
- No error messages in logs
- All tests pass

---

**Last Verified:** 2026-05-16  
**Platform:** macOS Sequoia  
**Python Version:** 3.9+  
**Node Version:** 18+

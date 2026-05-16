# Release Orchestration Platform - Documentation

This is an AI-powered release orchestration platform that actually makes deployment decisions instead of just following scripts. Think of it as having a DevOps team that never sleeps and can process information way faster than humans.

## Why This Exists

Traditional DevOps automation breaks when something unexpected happens. You've got rigid scripts that work great until they don't, and then you're stuck debugging at 2 AM. We built this to handle the unexpected - agents that can reason through problems and make decisions autonomously.

The difference? Automation follows rules. Orchestration adapts to situations.

## What's Inside

### Core Features

**Release Planning** - Analyzes your Jira sprint and GitHub repo to figure out if you're actually ready to deploy. Catches circular dependencies, incomplete work, and other issues that'll bite you in production.

**Pre-Flight Validation** - Digs through your CI/CD history looking for memory leaks, performance regressions, and test coverage problems. It's like having someone review the last 50 builds before you deploy.

**Canary Deployment** - Gradually shifts traffic to the new version (10% → 25% → 50% → 100%) while monitoring health. If something looks wrong, it stops and rolls back automatically.

**Autonomous Rollback** - This is the killer feature. The agent monitors production in real-time and if error rates spike, it doesn't wait for approval - it just rolls back. No more 3 AM wake-up calls.

**Post-Mortem Analysis** - After a failed deployment, it analyzes logs and code changes to pinpoint exactly what went wrong. You get a report with the specific file and line number that caused the problem.

## Quick Start

Get the backend running:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Start the frontend:
```bash
cd frontend
npm install
npm run dev
```

Then check out:
- Frontend dashboard: http://localhost:5173
- API documentation: http://localhost:8000/docs
- API endpoints: http://localhost:8000/api/v1

## Demo Flow

Here's how to show off the platform:

**1. Release Planning**
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"github_repo": "mycompany/api", "jira_sprint": "SPRINT-123"}'
```
Watch it detect circular dependencies and incomplete tickets.

**2. Pre-Flight Check**
```bash
curl -X POST http://localhost:8000/api/v1/deployments/test-123/pre-flight-check
```
See it catch memory leaks and performance regressions.

**3. Canary Deployment**
```bash
cd backend
python test_canary_deployment.py
```
Real-time traffic shifting with health monitoring.

**4. Autonomous Rollback** (The wow moment)
```bash
cd backend
python test_rollback_agent.py
```
Inject errors, watch the agent detect the spike and roll back automatically.

**5. Post-Mortem**
```bash
cd backend
python test_postmortem_agent.py
```
Get a detailed analysis with the exact line that caused the failure.

## Documentation

- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - How everything fits together
- **[RELEASE_PLANNING_FEATURE.md](RELEASE_PLANNING_FEATURE.md)** - Sprint and dependency analysis
- **[PRE_FLIGHT_VALIDATION_FEATURE.md](PRE_FLIGHT_VALIDATION_FEATURE.md)** - CI/CD validation
- **[CANARY_DEPLOYMENT_FEATURE.md](CANARY_DEPLOYMENT_FEATURE.md)** - Progressive rollouts
- **[AUTONOMOUS_ROLLBACK_FEATURE.md](AUTONOMOUS_ROLLBACK_FEATURE.md)** - Automatic error detection and rollback
- **[POSTMORTEM_ANALYSIS_FEATURE.md](POSTMORTEM_ANALYSIS_FEATURE.md)** - Root cause analysis
- **[ROLLBACK_QUICKSTART.md](ROLLBACK_QUICKSTART.md)** - Quick guide to the rollback demo

## What Makes This "Agentic"

Most deployment tools are just fancy scripts. They follow a path and break when something unexpected happens. Our agents actually reason through situations.

**Traditional automation:**
- Follows rigid scripts
- Binary pass/fail decisions
- Waits for human intervention
- Breaks on unexpected events

**Our platform:**
- Reasons through situations
- Uses confidence scores and probabilistic decisions
- Makes autonomous decisions
- Adapts to anomalies
- Learns from failures

For example, when the Rollback Agent sees error rates climbing, it doesn't just check a threshold. It looks at the pattern, considers deployment timing, checks if it's affecting all users or just some, and then decides whether to roll back or keep monitoring.

## Architecture

```
Frontend (React Dashboard)
    ↓
FastAPI Backend
    ↓
AI Agents Layer
    ├── Release Planning Agent
    ├── Pre-Flight Validation Agent
    ├── Canary Deployment Agent
    ├── Rollback Agent
    ├── Anomaly Detection Agent
    └── Post-Mortem Agent
    ↓
Services Layer
    ├── State Machine
    ├── Canary Controller
    ├── CI/CD Simulator
    └── Workflow Orchestrator
    ↓
Integrations
    ├── GitHub
    ├── Jira
    └── Slack
```

## Configuration

Create a `.env` file in the backend directory:

```bash
# Slack notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_ENABLED=true

# Rollback thresholds
ROLLBACK_ERROR_THRESHOLD=0.15      # 15% error rate triggers warning
ROLLBACK_CRITICAL_THRESHOLD=0.30   # 30% triggers automatic rollback

# Database
DATABASE_URL=sqlite+aiosqlite:///./release_orchestrator.db

# API
API_V1_PREFIX=/api/v1
DEBUG=true
```

## Key Metrics

The platform tracks:
- **Release Confidence Score** - Overall readiness assessment
- **Error Rate** - Real-time error tracking
- **Traffic Distribution** - Canary vs stable traffic split
- **Health Score** - Service health percentage
- **Latency** - Response time monitoring
- **Rollback Frequency** - How often automatic rollbacks trigger

## Testing

Run the test suite:
```bash
cd backend
pytest
```

Test individual features:
```bash
python test_rollback_agent.py
python test_canary_deployment.py
python test_postmortem_agent.py
```

Use the interactive API docs for manual testing:
```
http://localhost:8000/docs
```

## Presenting This

When demoing the platform, focus on these points:

**Opening:** "Who here has deployed on a Friday afternoon and regretted it? That's because traditional automation breaks when the unexpected happens."

**Key message:** This isn't automation, it's orchestration. The agents make decisions, not just follow rules.

**The wow moment:** Show the autonomous rollback. Inject errors, watch the agent detect the spike and roll back without any human intervention. That's when people get it.

**The learning aspect:** Show the post-mortem analysis. It doesn't just tell you something broke - it tells you exactly which line of code caused the problem.

## What's Next

Current status: Core agents are working, API is functional, using mock data for integrations.

To make this production-ready:
- Connect to real Jira and GitHub APIs
- Add more sophisticated ML models for pattern recognition
- Build out environment monitoring agent
- Expand change communication agent
- Add authentication and multi-tenancy
- Connect to actual Kubernetes clusters
- Add comprehensive error handling
- Implement rate limiting

## Contributing

This is a hackathon project demonstrating agentic orchestration. For production use, you'll want to add proper authentication, rate limiting, and real integrations.

The code is structured to make it easy to extend. Each agent is independent, services are modular, and the API is well-documented.

## Support

Having issues?
- Check the feature-specific docs above
- Review the API docs at `/docs`
- Look at the logs in `backend/logs/`
- Run the test scripts to verify everything works

---

Built by the Semicolons team. Making DevOps less painful, one deployment at a time.
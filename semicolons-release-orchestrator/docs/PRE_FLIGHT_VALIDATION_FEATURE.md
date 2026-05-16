# Pre-Flight Validation - Catching Problems Before They Hit Production

Nobody wants to find out their deployment has a memory leak after it's already in production. This feature analyzes your CI/CD history to catch issues before you deploy.

## What It Does

The Pre-Flight Validation agent looks at your last 10 CI runs and checks for patterns that indicate problems:

- Memory usage creeping up over time (potential leaks)
- Performance getting slower
- Test coverage dropping
- Build failures becoming more frequent

It's like having someone review all your recent builds before you hit deploy, except it happens in seconds instead of hours.

## Quick Start

Start the backend:
```bash
cd backend
uvicorn main:app --reload
```

Start the frontend:
```bash
cd frontend
npm run dev
```

Navigate to the Pre-Flight Check section, enter a deployment ID, and click "Run Pre-Flight Check".

## The Memory Leak Detection

This is the interesting part. The agent doesn't just look at current memory usage - it looks at the trend.

Say your auth-service used 220MB three builds ago, 235MB two builds ago, and 256MB now. That's a 15% increase. The agent flags this as a potential memory leak and tells you exactly which module is affected.

The algorithm:
1. Group CI runs by module
2. Calculate memory trend using linear regression
3. Flag anything growing >10%
4. Assign severity based on growth rate:
   - High: >20% increase
   - Medium: 10-20% increase
   - Low: 5-10% increase

## API Usage

**Run a pre-flight check:**
```bash
POST /api/v1/deployments/{deployment_id}/pre-flight-check
```

No request body needed. The agent fetches CI history based on the deployment ID.

**Response:**
```json
{
  "deployment_id": "deploy-12345",
  "validation_score": 72.5,
  "confidence_score": 0.85,
  "ci_runs_analyzed": 10,
  "memory_analysis": {
    "leaks_detected": 2,
    "modules_affected": ["auth-service", "payment-service"]
  },
  "issues": [
    {
      "severity": "high",
      "module": "auth-service",
      "description": "Memory usage increased 15.5% over last 10 builds",
      "current_mb": 256.8,
      "baseline_mb": 220.0
    }
  ],
  "recommendations": [
    {
      "title": "Investigate memory leak in auth-service",
      "priority": "critical",
      "action": "Profile memory usage and check for unclosed connections"
    }
  ],
  "ready_to_deploy": false
}
```

## What Gets Checked

**Memory Analysis**: Tracks memory usage per module across builds. Flags upward trends that indicate leaks.

**Performance Analysis**: Monitors build times and test execution times. Catches performance regressions.

**Test Coverage**: Ensures coverage isn't dropping. A sudden drop often means new code isn't being tested.

**Build Stability**: Looks at pass/fail rates. Flaky tests or frequent failures are red flags.

## The Frontend

The UI shows:
- Overall validation score (color-coded: green >80%, yellow 60-80%, red <60%)
- Memory leak warnings with severity indicators
- Test results breakdown
- Specific recommendations with priority levels

Each issue includes the module name, severity, and what to do about it.

## How It Decides

The validation score is weighted:
- Test pass rate: 40%
- Memory health: 30%
- Performance: 20%
- Build stability: 10%

If the score is below 70% or there are critical issues, `ready_to_deploy` is false.

## Mock Data vs Real Integration

Currently uses mock CI data for demo purposes. The structure is:

```python
{
    "run_id": "ci-run-001",
    "module": "auth-service",
    "status": "passed",
    "duration_seconds": 245,
    "memory_mb": 256.8,
    "test_passed": 95,
    "test_failed": 5,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

For production, you'd connect to Jenkins, GitHub Actions, GitLab CI, or whatever you're using. The agent interface stays the same - just swap out the data source.

## Example Scenario

You're about to deploy auth-service v2.1.0. You run pre-flight validation:

```
Validation Score: 68%
Ready to Deploy: NO

Issues Found:
- HIGH: Memory leak in auth-service (15.5% increase)
- MEDIUM: Test coverage dropped from 87% to 82%
- LOW: Build time increased by 8%

Recommendations:
1. CRITICAL: Investigate memory leak before deploying
2. HIGH: Add tests for new code to restore coverage
3. MEDIUM: Profile build to identify slow steps
```

You investigate, find an unclosed database connection, fix it, and run validation again. Score jumps to 92%, ready to deploy.

## What's Next

Current implementation uses simulated data. For production:

- Connect to real CI/CD systems
- Add historical trending (track scores over time)
- Machine learning for better pattern detection
- Custom thresholds per service
- Integration with monitoring tools

## Files

- `backend/agents/cicd_validation_agent.py` - The analysis logic
- `backend/routes/pre_flight.py` - API endpoints
- `frontend/src/components/PreFlightCheck.jsx` - UI component

## Troubleshooting

**Validation always passes**: Check if mock data is being used. Real CI data might show different patterns.

**Memory leaks not detected**: Increase the number of CI runs analyzed or lower the threshold.

**Slow response**: Analysis of 10 runs should take <2 seconds. If slower, check database performance.

---

This is about catching problems early when they're cheap to fix, not after they've caused a production incident.
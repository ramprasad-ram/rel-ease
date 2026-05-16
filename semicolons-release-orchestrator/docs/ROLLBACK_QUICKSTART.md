# Autonomous Rollback - Quick Start

Get the autonomous rollback feature running in 5 minutes.

## Install and Run

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

In another terminal:

```bash
cd backend
python test_rollback_agent.py
```

Select option 1 for the full demo.

## Optional: Slack Notifications

If you want Slack notifications (recommended for the full experience), create a `.env` file:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_ENABLED=true
```

Get a webhook URL at https://api.slack.com/apps - create an app, enable incoming webhooks, copy the URL.

The feature works fine without Slack - notifications just go to the logs instead.

## What Happens in the Demo

The script simulates a production deployment that goes wrong:

1. Deploys Auth-Service v1.0.3 to production
2. Starts the Rollback Agent monitoring
3. Simulates normal traffic (everything's fine)
4. Injects 200 errors to simulate a production incident
5. Agent detects error rate at 80% (way above the 30% threshold)
6. Agent autonomously triggers rollback to v1.0.2
7. Sends Slack notification (if configured)

The whole thing takes about 30 seconds. The key moment is when the agent decides to roll back without any human intervention.

## Understanding the Output

```
Deploying Auth-Service v1.0.3
Deployment ID: 123e4567-e89b-12d3-a456-426614174000

Starting Rollback Agent monitoring...
Error Threshold: 15.0%
Critical Threshold: 30.0%

Simulating normal traffic...
Current Error Rate: 0.0%
Status: Healthy

INJECTING CRITICAL ERRORS
Injecting 200 5xx errors...

ERRORS INJECTED
Total Errors: 200
Error Rate: 80.0%
Will Trigger Rollback: true

Rollback Agent is analyzing...
[0s] Monitoring... Error Rate: 80.0%
[2s] Monitoring... Error Rate: 80.0%
ROLLBACK TRIGGERED (after 4 seconds)

AUTONOMOUS ROLLBACK COMPLETED
Service: Auth-Service
Failed Version: v1.0.3
Rolled Back To: v1.0.2
Error Rate at Rollback: 80.0%
```

## The Thresholds

**Warning (15%)**: Agent logs a warning but doesn't act. Maybe it's a temporary spike.

**Critical (30%)**: Agent immediately triggers rollback. This is bad enough that waiting is riskier than rolling back.

In the demo, we inject enough errors to hit 80% - way above critical.

## Verify It's Working

Check the API docs at http://localhost:8000/docs

You should see these endpoints:
- POST /api/v1/rollback/start-monitoring
- POST /api/v1/rollback/inject-errors
- GET /api/v1/rollback/status/{deployment_id}
- GET /api/v1/rollback/active-monitors

Test with curl:
```bash
curl http://localhost:8000/api/v1/rollback/active-monitors
```

## Customize the Demo

Edit `test_rollback_agent.py`:

```python
# Change service name
service_name = "Your-Service"

# Change versions
current_version = "2.0.0"
rollback_version = "1.9.5"

# Adjust error injection
error_count = 150  # Lower to test different scenarios
```

## Common Issues

**Server won't start**: Port 8000 might be in use. Kill the process or use a different port.

**Demo script fails**: Make sure the server is running first. Check `curl http://localhost:8000/` works.

**No Slack notifications**: Verify `SLACK_WEBHOOK_URL` is correct in `.env` and `SLACK_ENABLED=true`. Test the webhook URL directly.

**Rollback not triggering**: Check the error rate actually exceeds 30%. Use the status endpoint to see current metrics.

## Next Steps

Read the full documentation in AUTONOMOUS_ROLLBACK_FEATURE.md for:
- How the decision algorithm works
- API endpoint details
- Production deployment considerations
- Integration with other agents

## What Makes This Special

Most deployment tools can roll back, but they require someone to notice the problem and trigger it manually. This agent makes the decision autonomously based on real-time metrics.

It's the difference between automation (following a script) and orchestration (making decisions).

---

That's it. You now have an agent that can detect production issues and fix them automatically, without waking anyone up at 3 AM.
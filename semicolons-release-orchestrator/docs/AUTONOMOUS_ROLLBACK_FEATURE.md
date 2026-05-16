# Autonomous Rollback

This is the feature that makes people sit up and pay attention. Your service starts throwing errors in production, and before anyone even notices, the system has already rolled back to the last stable version. No 3 AM phone calls, no scrambling to find who has deploy access, no manual intervention at all.

## How It Works

You deploy Auth-Service v1.0.3 to production. Unknown to you, there's a bug that causes 500 errors to spike. Here's what happens:

1. The Rollback Agent is monitoring production metrics in real-time
2. It sees error rates climbing - 10%, 20%, 30%...
3. At 30%, it crosses the critical threshold
4. The agent makes an autonomous decision: this deployment is bad
5. It triggers a rollback to v1.0.2
6. Your Slack channel gets a notification explaining what happened
7. Service is back to normal in under 30 seconds

All of this happens automatically. Nobody had to wake up, nobody had to approve anything, nobody even had to be online.

## Quick Start

Set up your Slack webhook (optional but recommended):

```bash
# backend/.env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_ENABLED=true

ROLLBACK_ERROR_THRESHOLD=0.15      # Warning at 15%
ROLLBACK_CRITICAL_THRESHOLD=0.30   # Auto-rollback at 30%
```

Get a Slack webhook at https://api.slack.com/apps - create an app, enable incoming webhooks, and copy the URL.

Run the demo:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# In another terminal
python test_rollback_agent.py
```

Pick option 1 and watch the magic happen.

## The API

**Start monitoring a deployment:**

```bash
POST /api/v1/rollback/start-monitoring

{
  "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Auth-Service",
  "version": "1.0.3",
  "rollback_version": "1.0.2",
  "target_environment": "production"
}
```

The agent starts watching this deployment. Every 10 seconds, it checks error rates and decides if action is needed.

**Inject errors (for testing):**

```bash
POST /api/v1/rollback/inject-errors

{
  "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
  "error_count": 200,
  "error_type": "5xx"
}
```

This simulates a production incident. Inject enough errors to cross the threshold and watch the agent respond.

**Check status:**

```bash
GET /api/v1/rollback/status/{deployment_id}
```

See current error rates, thresholds, and whether rollback has been triggered.

## What You'll See in Slack

When the agent detects an error spike:

```
⚠️ Error Spike Detected

Service: Auth-Service
Error Rate: 40.0%
Threshold: 30.0%

🤖 Rollback Agent is analyzing the situation...
```

When it decides to roll back:

```
🚨 Automatic Rollback Initiated

Service: Auth-Service
Failed Version: v1.0.3
Rollback To: v1.0.2

Error Details:
Error Rate: 40.0%
Total Requests: 500
Error Count: 200
500-level Errors: Yes
```

When it's done:

```
✅ Rollback completed successfully for Auth-Service to v1.0.2
```

## How It Decides

The agent uses two thresholds:

**Warning (15%)**: Logs a warning but doesn't take action. Maybe it's a temporary spike, maybe it's expected load. The agent watches and waits.

**Critical (30%)**: This is bad enough that waiting is riskier than rolling back. The agent acts immediately.

You can adjust these in your `.env` file based on your service's normal error patterns.

## The Decision Loop

```python
while monitoring:
    error_rate = calculate_error_rate()
    
    if error_rate > CRITICAL_THRESHOLD:
        send_slack_alert()
        execute_rollback()
        break
    elif error_rate > WARNING_THRESHOLD:
        log_warning()
    
    await asyncio.sleep(10)
```

Every 10 seconds, check. If things are bad, act. If things are okay, keep watching.

## Demo Script

For presentations:

```bash
# Terminal 1
cd backend
uvicorn main:app --reload

# Terminal 2
cd backend
python test_rollback_agent.py
```

Select option 1. The script will:
1. Start monitoring a deployment
2. Inject errors to simulate a production incident
3. Show the agent detecting the spike
4. Trigger automatic rollback
5. Send Slack notification (if configured)

The whole thing takes about 30 seconds. It's the "wow moment" that makes people understand what autonomous orchestration means.

## What Makes This Different

Most deployment tools have rollback capabilities, but they require human intervention. Someone has to notice the problem, decide to roll back, and execute the rollback.

This agent makes the decision autonomously. It's not just automation (following a script), it's orchestration (making decisions based on the situation).

The agent considers:
- Current error rate vs historical baseline
- How quickly errors are climbing
- Whether errors correlate with the deployment timing
- Severity of errors (5xx vs 4xx)

Then it decides: roll back or keep monitoring.

## Production Considerations

**Thresholds**: Start conservative (higher thresholds) and tune based on your service's behavior. A 30% error rate might be catastrophic for one service but normal for another during peak load.

**Monitoring Window**: The agent checks every 10 seconds. For services with high traffic, this is fine. For low-traffic services, you might need a longer window to get meaningful error rates.

**Rollback Speed**: The actual rollback takes seconds, but DNS propagation and cache clearing might take longer. Factor this into your SLAs.

**False Positives**: The agent might roll back when it shouldn't. That's okay - a false positive (unnecessary rollback) is better than a false negative (missing a real problem).

## What's Next

Current implementation uses simulated metrics. For production:

- Connect to real monitoring systems (Datadog, New Relic, Prometheus)
- Add machine learning for adaptive thresholds
- Support multiple notification channels (PagerDuty, email, Teams)
- Add approval workflows for non-critical rollbacks
- Track rollback history and patterns
- Integrate with canary deployments for smarter decisions

## Files

- `backend/agents/rollback_agent.py` - The agent that makes decisions
- `backend/integrations/slack_client.py` - Slack notifications
- `backend/routes/rollback.py` - API endpoints
- `backend/test_rollback_agent.py` - Demo script

## Troubleshooting

**Slack notifications not working**: Check your webhook URL is correct and `SLACK_ENABLED=true` in `.env`

**Agent not rolling back**: Check the error rate actually exceeds the threshold. Use the status endpoint to see current metrics.

**Can't inject errors**: Make sure the deployment is being monitored first. Start monitoring, then inject errors.

---

This is what makes DevOps less painful. When your agents can detect and fix problems automatically, you can actually deploy on Friday afternoons without regret.
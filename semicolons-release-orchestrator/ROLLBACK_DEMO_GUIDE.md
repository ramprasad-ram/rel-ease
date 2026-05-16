# 🚨 Autonomous Rollback Demo Guide

## Quick Demo (5 minutes)

This is the **"WOW MOMENT"** of your platform - autonomous error detection and rollback without human intervention.

### Prerequisites
✅ Backend running on `http://localhost:8000`
✅ Frontend running on `http://localhost:5173`
✅ Both terminals visible for the demo

---

## Method 1: Automated Test Script (Recommended for Demos)

### Step 1: Run the Demo Script
```bash
cd semicolons-release-orchestrator/backend
python3 test_rollback_agent.py
```

### Step 2: Select Option 1
```
Select option (1-3): 1
```

### What Happens (30 seconds):
1. **Deploys** Auth-Service v1.0.3 to production
2. **Starts monitoring** with Rollback Agent
3. **Simulates normal traffic** (everything healthy)
4. **Injects 200 errors** (simulates production incident)
5. **Agent detects** error rate at 80% (threshold: 30%)
6. **Autonomous rollback** to v1.0.2 triggered
7. **Slack notification** sent (if configured)

### Expected Output:
```
🚀 AUTONOMOUS ROLLBACK AGENT DEMO
================================================================================

📦 Step 1: Deploying Auth-Service v1.0.3
   Deployment ID: 123e4567-e89b-12d3-a456-426614174000
   Rollback Version: v1.0.2

👁️  Step 2: Starting Rollback Agent monitoring...
✅ Monitoring started successfully
   Error Threshold: 15.0%
   Critical Threshold: 30.0%

📊 Step 3: Simulating normal traffic...
   Current Error Rate: 0.0%
   Status: 🟢 Healthy

💥 Step 4: INJECTING CRITICAL ERRORS (Simulating Production Issue)
   Injecting 200 5xx errors to trigger automatic rollback...

⚠️  ERRORS INJECTED!
   Total Errors: 200
   Error Rate: 80.0%
   Will Trigger Rollback: true

🤖 Step 5: Rollback Agent is analyzing...
   [0s] Monitoring... Error Rate: 80.0%
   [2s] Monitoring... Error Rate: 80.0%
   🚨 ROLLBACK TRIGGERED! (after 4 seconds)

================================================================================
✅ AUTONOMOUS ROLLBACK COMPLETED
================================================================================
   Service: Auth-Service
   Failed Version: v1.0.3
   Rolled Back To: v1.0.2
   Error Rate at Rollback: 80.0%

📬 Slack Notification Sent:
   '🚨 Rollback initiated. Error detected in 'Auth-Service'.
    Reverting to v1.0.2.'
```

---

## Method 2: Frontend UI Demo (Visual Demo)

### Step 1: Open Frontend
Navigate to: `http://localhost:5173`

### Step 2: Go to Rollback Tab
Click on the "Rollback Demo" or "Crisis & Recovery" tab

### Step 3: Start Monitoring
1. Click **"Start Monitoring"** button
2. Watch the dashboard initialize
3. See real-time metrics: Error Rate: 0%

### Step 4: Inject Errors (The WOW Moment)
1. Click **"Inject Errors"** button
2. Watch error rate spike to 40%+
3. See the Rollback Agent detect the spike
4. Watch autonomous rollback trigger
5. See Slack notification appear

### Step 5: View Results
- ✅ Service rolled back to v1.0.2
- ✅ Error rate returns to normal
- ✅ Post-mortem analysis triggered

---

## Method 3: API Testing (Technical Demo)

### Step 1: Start Monitoring
```bash
curl -X POST http://localhost:8000/api/v1/rollback/start-monitoring \
  -H "Content-Type: application/json" \
  -d '{
    "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Auth-Service",
    "version": "1.0.3",
    "rollback_version": "1.0.2",
    "target_environment": "production"
  }'
```

### Step 2: Check Status (Healthy)
```bash
curl http://localhost:8000/api/v1/rollback/status/123e4567-e89b-12d3-a456-426614174000
```

### Step 3: Inject Errors
```bash
curl -X POST http://localhost:8000/api/v1/rollback/inject-errors \
  -H "Content-Type: application/json" \
  -d '{
    "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
    "error_count": 200,
    "error_type": "5xx"
  }'
```

### Step 4: Watch Rollback (Check status every 2 seconds)
```bash
watch -n 2 curl -s http://localhost:8000/api/v1/rollback/status/123e4567-e89b-12d3-a456-426614174000
```

### Step 5: View Active Monitors
```bash
curl http://localhost:8000/api/v1/rollback/active-monitors
```

---

## Demo Script for Presentations

### Opening (30 seconds)
> "Let me show you the autonomous rollback feature - this is where the AI truly acts autonomously. Watch what happens when a production deployment goes wrong."

### The Demo (2 minutes)
1. **Start monitoring**: "I'm deploying Auth-Service v1.0.3 and the Rollback Agent starts monitoring"
2. **Show healthy state**: "Everything's normal - 0% error rate"
3. **Inject errors**: "Now I'm simulating a production incident - injecting 200 errors"
4. **Watch the magic**: "Watch this - the agent detects the spike..."
5. **Autonomous action**: "And there it is - AUTONOMOUS ROLLBACK triggered. No human intervention needed."
6. **Show notification**: "It even sent a Slack notification explaining what happened"

### Closing (30 seconds)
> "This is the difference between automation and orchestration. The agent didn't just alert someone - it detected the problem, made the decision, and fixed it. All in under 30 seconds."

---

## Key Talking Points

### 1. Autonomous Decision Making
- "The agent monitors error rates in real-time"
- "When it crosses 30% threshold, it acts immediately"
- "No human approval needed - it makes the decision"

### 2. Speed
- "From error spike to rollback: under 30 seconds"
- "Faster than any human could respond"
- "Prevents extended outages"

### 3. Intelligence
- "Distinguishes between temporary spikes and real problems"
- "Uses thresholds: 15% warning, 30% critical"
- "Correlates errors with deployment timing"

### 4. Notifications
- "Slack notification with full context"
- "Explains what happened and why"
- "Team is informed, not woken up at 3 AM"

---

## Customizing the Demo

### Change Service Name
Edit `test_rollback_agent.py`:
```python
service_name = "Payment-Service"  # Your service
current_version = "2.0.0"
rollback_version = "1.9.5"
```

### Adjust Error Threshold
Edit `backend/.env`:
```bash
ROLLBACK_ERROR_THRESHOLD=0.15      # Warning at 15%
ROLLBACK_CRITICAL_THRESHOLD=0.30   # Auto-rollback at 30%
```

### Change Error Count
Edit `test_rollback_agent.py`:
```python
error_count = 150  # Lower for different scenarios
```

---

## Troubleshooting

### Backend Not Responding
```bash
cd semicolons-release-orchestrator/backend
python3 main.py
```

### Demo Script Fails
- Ensure backend is running first
- Check: `curl http://localhost:8000/`
- Verify port 8000 is not in use

### Rollback Not Triggering
- Check error rate exceeds 30%
- Use status endpoint to verify metrics
- Ensure deployment is being monitored

### No Slack Notifications
- Verify `SLACK_WEBHOOK_URL` in `.env`
- Set `SLACK_ENABLED=true`
- Test webhook URL directly
- Feature works without Slack (logs only)

---

## Optional: Slack Setup

### Get Webhook URL
1. Go to https://api.slack.com/apps
2. Create new app
3. Enable "Incoming Webhooks"
4. Add webhook to workspace
5. Copy webhook URL

### Configure
Create `backend/.env`:
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_ENABLED=true
```

---

## Success Criteria

- [ ] Error injection increases error rate to 80%
- [ ] Rollback Agent detects spike within 2-4 seconds
- [ ] Autonomous rollback triggered
- [ ] Service rolled back to previous version
- [ ] Slack notification sent (if configured)
- [ ] Demo completes in under 1 minute

---

## What Makes This Special

**Most deployment tools can rollback** - but they require:
- Someone to notice the problem
- Someone to decide to rollback
- Someone to execute the rollback

**This agent does all three autonomously:**
- Detects the problem in real-time
- Makes the decision based on thresholds
- Executes the rollback immediately

**This is orchestration, not just automation.**

---

## Next Steps

After the demo:
1. Show the post-mortem analysis (auto-generated)
2. Explain integration with other agents
3. Discuss production deployment considerations
4. Review the decision algorithm

---

**Remember:** The autonomous rollback is your "WOW MOMENT" - build up to it, let it happen naturally, and emphasize the autonomous decision-making aspect.

🚀 **Good luck with your demo!**
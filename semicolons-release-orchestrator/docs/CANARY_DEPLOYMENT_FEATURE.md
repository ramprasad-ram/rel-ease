# Canary Deployment - Progressive Rollouts with Real-Time Monitoring

Deploying straight to 100% of production traffic is risky. Canary deployments let you test the new version on a small percentage of traffic first, then gradually increase if everything looks good.

## The Concept

Instead of switching all traffic at once, you:
1. Deploy the new version alongside the old one
2. Send 10% of traffic to the new version
3. Monitor health metrics
4. If it looks good, increase to 25%, then 50%, then 100%
5. If anything looks wrong, roll back immediately

The "canary" name comes from coal miners using canaries to detect toxic gas. If the canary dies, you know there's a problem before it kills the miners. Same idea here - if 10% of your traffic has issues, you catch it before it affects everyone.

## How It Works

Start a canary deployment:

```bash
POST /api/v1/deployments/{deployment_id}/execute-canary

{
  "version": "2.1.0",
  "environment": "production",
  "canary_replicas": 1,
  "stable_replicas": 3
}
```

The system:
1. Deploys canary pods (new version)
2. Shifts 10% traffic, monitors for 10 seconds
3. If health > 95%, shifts to 25%, monitors for 10 seconds
4. If still healthy, shifts to 50%, monitors for 10 seconds
5. If still healthy, shifts to 100%
6. Marks deployment complete

If health drops below 95% at any stage, it automatically rolls back.

## Real-Time Updates

The deployment streams progress via Server-Sent Events (SSE):

```bash
GET /api/v1/deployments/{deployment_id}/stream
```

You get events like:

```javascript
// Connection established
{ event: "connected", deployment_id: "deploy-123" }

// Traffic shifted
{ event: "traffic_shifted", traffic_percentage: 25 }

// Health update
{
  event: "metrics_update",
  metrics: {
    canary_health: 98.5,
    error_rate: 0.5,
    latency_ms: 145
  }
}

// Stage completed
{ event: "stage_complete", stage: "canary_25" }

// Deployment done
{ event: "deployment_complete", status: "completed" }
```

## The Frontend Dashboard

The React component shows:

**Current Stage**: Which traffic percentage you're at, with a progress bar

**Traffic Distribution**: Visual bar showing canary vs stable traffic split

**Health Metrics**: Real-time health percentage, error rate, and latency

**Event Log**: Running list of what's happening (traffic shifts, health checks, etc.)

Everything updates in real-time as the deployment progresses.

## Health Monitoring

At each stage, the system checks:

**Health Score**: Success rate percentage. Must be > 95%.

**Error Rate**: Percentage of failed requests. Should be < 5%.

**Latency**: Response time. Shouldn't increase significantly.

If any metric looks bad, rollback triggers automatically.

## The Traffic Stages

**Initializing (2 seconds)**: Deploy canary pods, prepare infrastructure

**10% Traffic (10 seconds)**: First real test with production traffic. Most issues show up here.

**25% Traffic (10 seconds)**: Increased load test. Catches issues that only appear under higher traffic.

**50% Traffic (10 seconds)**: Critical validation point. If it works at 50%, it'll probably work at 100%.

**100% Traffic (2 seconds)**: Complete rollout. All traffic on new version.

**Completed**: Mark successful, clean up old version.

Total time: About 45 seconds for a full rollout.

## Running the Test

```bash
cd backend
python test_canary_deployment.py
```

The script:
1. Starts a canary deployment via API
2. Connects to the SSE stream
3. Prints each event as it happens
4. Verifies completion

You'll see traffic shift from 0% → 10% → 25% → 50% → 100% with health metrics at each stage.

## Using the Frontend

Start both backend and frontend:

```bash
# Terminal 1
cd backend
uvicorn main:app --reload

# Terminal 2
cd frontend
npm run dev
```

Navigate to the Canary Deployment section:
1. Enter deployment ID (e.g., "deploy-prod-001")
2. Specify version (e.g., "2.1.0")
3. Select environment
4. Click "Start Canary Deployment"
5. Watch the real-time dashboard

The traffic bar animates as traffic shifts. Health metrics update every 2 seconds. The event log shows everything that's happening.

## Why SSE Instead of WebSockets

Server-Sent Events are simpler for one-way communication (server to client). They:
- Work over regular HTTP
- Automatically reconnect if connection drops
- Have native browser support
- Don't require special server infrastructure

For deployment monitoring, we only need server → client updates, so SSE is perfect.

## Rollback Triggers

Automatic rollback happens if:
- Health drops below 95%
- Error rate exceeds 5%
- Latency increases > 50%
- Manual intervention (future feature)

Rollback takes < 5 seconds. Traffic immediately shifts back to the stable version.

## Production Considerations

**Replica Counts**: The demo uses 1 canary + 3 stable. In production, scale based on your traffic. More replicas = more stable traffic distribution.

**Monitoring Windows**: 10 seconds per stage works for high-traffic services. Low-traffic services might need longer windows to get meaningful metrics.

**Health Thresholds**: 95% health is conservative. Adjust based on your service's normal behavior.

**Rollback Speed**: The system rolls back fast, but DNS propagation and cache clearing take time. Factor this into your SLAs.

## What's Next

Current implementation uses simulated metrics. For production:

- Connect to real Kubernetes clusters
- Pull actual metrics from Prometheus/Datadog
- Support custom health check functions
- Add A/B testing capabilities
- Multi-region rollouts
- Integration with service meshes (Istio, Linkerd)

## Files

- `backend/services/canary_controller.py` - Orchestration logic
- `backend/routes/canary_deployment.py` - API endpoints
- `frontend/src/components/CanaryDashboard.jsx` - UI component
- `backend/test_canary_deployment.py` - Test script

## Troubleshooting

**SSE connection fails**: Add a 2-second delay after starting deployment before connecting to the stream.

**Health metrics not updating**: Check the background task is running. Look for errors in server logs.

**Rollback not triggering**: Verify health threshold is set correctly. Use the status endpoint to check current metrics.

---

Canary deployments turn "deploy and pray" into "deploy and verify." You catch problems when they affect 10% of traffic, not 100%.
# 🎯 Demo Preparation Checklist

## Pre-Demo Setup (15 minutes before)

### 1. Environment Check
- [ ] Backend server running on `http://localhost:8000`
- [ ] Frontend running on `http://localhost:5173`
- [ ] Database initialized with mock data
- [ ] All terminals visible and organized

### 2. Run Test Suite
```bash
cd semicolons-release-orchestrator/backend
python3 run_demo_tests.py
```
Expected: All 5 steps should pass ✅

### 3. Browser Setup
- [ ] Open frontend: `http://localhost:5173`
- [ ] Open API docs: `http://localhost:8000/docs`
- [ ] Clear browser cache
- [ ] Test all tabs load correctly

### 4. Demo Data Verification
```bash
# Verify mock data exists
cd semicolons-release-orchestrator/backend
python3 init_mock_data.py
```

---

## The Demo Flow (The "Golden Path")

### 🎬 STEP 1: Release Planning (2 minutes)
**Goal:** Show AI detecting circular dependencies

**Actions:**
1. Navigate to "Release Planning" tab
2. Enter:
   - GitHub Repo: `demo-org/demo-app`
   - Jira Sprint: `SPRINT-123`
3. Click "Analyze Release Readiness"

**Expected Results:**
- ✅ Readiness Score displayed (60-80%)
- ✅ Circular dependency detected: `PROJ-1001 → PROJ-1002 → PROJ-1003 → PROJ-1001`
- ✅ Issues list shows: "Task A is done, but Task B has a circular dependency"
- ✅ Recommendations provided

**Key Talking Points:**
- "The Planning Agent analyzes Jira tickets and GitHub repos"
- "It automatically detects circular dependencies that would block release"
- "Notice the AI provides a readiness score and specific recommendations"

---

### 🔍 STEP 2: Pre-Flight Check (2 minutes)
**Goal:** Show AI detecting memory leaks from CI logs

**Actions:**
1. Navigate to "Pre-Flight Check" tab
2. Click "Run Validation"

**Expected Results:**
- ✅ Validation score displayed
- ✅ Memory analysis shows 10%+ increase
- ✅ Warning: "Potential memory leak detected in module X"
- ✅ Specific module identified (e.g., auth-service)

**Key Talking Points:**
- "The Validation Agent scans the last 5 CI runs"
- "It detected a 10% memory increase - potential leak"
- "Notice it identifies the specific module causing the issue"
- "This prevents deploying broken code to production"

---

### 🚀 STEP 3: Canary Deployment (2 minutes)
**Goal:** Show progressive traffic shifting

**Actions:**
1. Navigate to "Canary Deployment" tab
2. Click "Start Canary Deployment"
3. Watch the real-time dashboard

**Expected Results:**
- ✅ Traffic shifts: 10% → 25% → 50% → 100%
- ✅ Real-time metrics displayed
- ✅ Health checks pass at each stage
- ✅ Dashboard shows traffic distribution

**Key Talking Points:**
- "The Deployment Agent uses canary strategy"
- "It progressively shifts traffic: 10%, 25%, 50%, 100%"
- "At each stage, it monitors health metrics"
- "If issues detected, it automatically rolls back"

---

### ⚠️ STEP 4: Autonomous Rollback - THE WOW MOMENT (3 minutes)
**Goal:** Show autonomous error detection and rollback

**Actions:**
1. Navigate to "Rollback Demo" tab
2. Click "Start Monitoring"
3. Click "Inject Errors" (simulates production spike)
4. Watch the autonomous rollback happen

**Expected Results:**
- ✅ Error rate spikes to 40%+
- ✅ Rollback Agent detects the spike automatically
- ✅ System autonomously triggers rollback
- ✅ Slack notification: "Rollback initiated. Error detected in 'Auth-Service'. Reverting to v1.0.2"
- ✅ Post-mortem analysis automatically triggered

**Key Talking Points:**
- "Now watch this - the WOW moment"
- "I'm injecting errors to simulate a production failure"
- "The Rollback Agent is monitoring in real-time"
- "Notice: It detected the spike and AUTONOMOUSLY rolled back"
- "No human intervention needed - this is the agentic behavior"
- "It even posted to Slack with details"

---

### 📊 STEP 5: Post-Mortem Analysis (2 minutes)
**Goal:** Show AI root cause analysis with specific fixes

**Actions:**
1. View the post-mortem report (auto-generated after rollback)
2. Show the analysis details

**Expected Results:**
- ✅ Root cause identified: "Null pointer in auth.py"
- ✅ Specific line number: "Line 42"
- ✅ Detailed explanation of the failure
- ✅ Actionable fix: "Add a null-check at line 42 of auth.py"
- ✅ Code example provided

**Key Talking Points:**
- "The Post-Mortem Agent analyzed the failure"
- "It identified the exact cause: null pointer at line 42"
- "Notice it provides the specific fix needed"
- "This helps developers quickly resolve the issue"
- "The AI correlated logs with code changes"

---

## Demo Script Summary

### Opening (30 seconds)
"We built an AI-powered release orchestration platform that autonomously manages deployments. Let me show you the complete flow from planning to recovery."

### The Flow (10 minutes)
1. **Planning** - "AI detects circular dependencies"
2. **Validation** - "AI finds memory leaks before deployment"
3. **Deployment** - "Progressive canary rollout with monitoring"
4. **Crisis** - "Autonomous rollback when errors spike" ⭐ WOW MOMENT
5. **Analysis** - "AI identifies root cause with specific fixes"

### Closing (30 seconds)
"This is true agentic AI - it doesn't just alert, it acts. It detected the failure, rolled back autonomously, and provided the exact fix. All without human intervention."

---

## Troubleshooting

### Backend not responding
```bash
cd semicolons-release-orchestrator/backend
python3 main.py
```

### Frontend not loading
```bash
cd semicolons-release-orchestrator/frontend
npm run dev -- --host 0.0.0.0
```

### Database issues
```bash
cd semicolons-release-orchestrator/backend
rm release_orchestrator.db
python3 init_mock_data.py
```

### Test failures
```bash
cd semicolons-release-orchestrator/backend
python3 run_demo_tests.py
```

---

## API Endpoints for Manual Testing

### Release Planning
```bash
curl -X POST http://localhost:8000/api/release-planning/analyze \
  -H "Content-Type: application/json" \
  -d '{"github_repo": "demo-org/demo-app", "jira_sprint": "SPRINT-123"}'
```

### Pre-Flight Check
```bash
curl -X POST http://localhost:8000/api/pre-flight/validate \
  -H "Content-Type: application/json" \
  -d '{"deployment_id": "test-123"}'
```

### Canary Deployment
```bash
curl -X POST http://localhost:8000/api/canary/start \
  -H "Content-Type: application/json" \
  -d '{"deployment_id": "test-123", "version": "1.0.3"}'
```

---

## Success Criteria

- [ ] All 5 steps execute without errors
- [ ] Circular dependencies detected in Step 1
- [ ] Memory leak flagged in Step 2
- [ ] Canary deployment completes in Step 3
- [ ] Autonomous rollback triggers in Step 4
- [ ] Post-mortem provides specific line number in Step 5
- [ ] Demo completes in under 12 minutes
- [ ] All visualizations display correctly

---

## Backup Plan

If live demo fails:
1. Have screenshots/video ready
2. Use the test suite output as proof
3. Show the code structure
4. Explain the architecture

---

## Key Differentiators to Emphasize

1. **Autonomous** - Not just monitoring, but acting
2. **Agentic** - Multiple AI agents working together
3. **Specific** - Provides exact line numbers and fixes
4. **Real-time** - Monitors and responds immediately
5. **Complete** - End-to-end from planning to post-mortem

---

## Questions to Prepare For

**Q: How does it detect circular dependencies?**
A: Uses graph traversal (DFS) to detect cycles in the dependency graph from Jira tickets.

**Q: How does autonomous rollback work?**
A: Monitors error rates in real-time. When threshold exceeded (15%), automatically triggers rollback without human intervention.

**Q: What makes this "agentic"?**
A: Multiple specialized AI agents (Planning, Validation, Deployment, Rollback, Post-Mortem) that autonomously make decisions and take actions.

**Q: Can it integrate with real systems?**
A: Yes, designed with integration points for GitHub, Jira, Kubernetes, Slack. Currently using mock data for demo.

**Q: What's the tech stack?**
A: Python FastAPI backend, React frontend, SQLAlchemy ORM, async/await for real-time monitoring.

---

## Post-Demo

- [ ] Collect feedback
- [ ] Note any issues encountered
- [ ] Update documentation based on questions
- [ ] Prepare for next iteration

---

**Good luck! 🚀**

Remember: The autonomous rollback (Step 4) is your WOW moment. Build up to it!
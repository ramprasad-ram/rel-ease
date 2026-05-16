# Post-Mortem Analysis - Learning from Failures

When a deployment fails and gets rolled back, you need to know why. Fast. This agent analyzes what went wrong and tells you exactly what to fix, including the file and line number.

## The Problem

After a rollback, you're left with questions:
- What caused the failure?
- Which code change broke it?
- How do we prevent this from happening again?

Usually, someone spends hours digging through logs, comparing code diffs, and trying to piece together what happened. This agent does it in seconds.

## How It Works

After a rollback, the Post-Mortem Agent:

1. Grabs the deployment logs and looks for error patterns
2. Compares the failed version's code with the previous version
3. Correlates errors with code changes
4. Identifies the root cause with a confidence score
5. Generates specific recommendations with line numbers
6. Sends a report to Slack

All automatic. No manual log diving required.

## Quick Start

```bash
cd backend
python test_postmortem_agent.py
```

Or trigger it via API after a rollback:

```bash
POST /api/v1/postmortem/analyze

{
  "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Auth-Service",
  "version": "1.0.3",
  "rollback_version": "1.0.2",
  "target_environment": "production"
}
```

## What You Get

The agent returns a detailed analysis:

```json
{
  "root_cause": {
    "type": "null_pointer",
    "description": "Null/None reference error",
    "confidence": 0.9,
    "file": "auth.py",
    "line": 42,
    "suggested_fix": "Add null-check at line 42: if user is not None: email = user.email.lower()"
  },
  "recommendations": [
    {
      "title": "Fix null check in auth.py",
      "priority": "critical",
      "description": "Add null-check at line 42",
      "impact": "Prevent null pointer exceptions"
    },
    {
      "title": "Add unit tests for null handling",
      "priority": "high",
      "description": "Create tests for edge cases with null users",
      "impact": "Catch similar issues before deployment"
    }
  ]
}
```

Notice it doesn't just say "there's a null pointer error somewhere." It tells you the exact file, line number, and what to change.

## Error Pattern Detection

The agent recognizes common failure patterns:

**Null Pointer Errors**: Missing null checks, uninitialized variables. Usually shows up as NullPointerException or AttributeError.

**Connection Refused**: Service not running, wrong port, firewall blocking. Common in microservice deployments.

**Timeouts**: Slow queries, network latency, insufficient timeout values. Often indicates performance issues.

**Missing Keys**: Missing config, API mismatch, validation gaps. Happens when code expects data that isn't there.

**Memory Errors**: Out of memory, memory leaks, insufficient allocation. Shows up as OOM errors.

**Authentication Failures**: Invalid credentials, expired tokens, missing headers. Usually config or integration issues.

**Database Errors**: Invalid SQL, connection issues, missing migrations. Common after schema changes.

Each pattern has a confidence score. Higher confidence means the agent is more certain about the root cause.

## The Analysis Process

**Step 1: Log Analysis**
The agent scans deployment logs looking for error patterns. It counts occurrences, extracts examples, and identifies the most frequent errors.

**Step 2: Code Diff Analysis**
It compares the failed version with the previous version, looking for:
- Removed safety checks (null checks, validations)
- New code that accesses potentially null values
- Changed error handling
- Modified configuration

**Step 3: Correlation**
The agent correlates log errors with code changes. If logs show null pointer errors and the diff shows a removed null check, that's probably your problem.

**Step 4: Root Cause Identification**
Based on the correlation, it identifies the most likely root cause and assigns a confidence score.

**Step 5: Recommendations**
It generates specific, actionable recommendations:
- Immediate fix with code example
- Testing improvements to catch similar issues
- Monitoring enhancements for faster detection

## Integration with Rollback Agent

The Post-Mortem Agent can be automatically triggered after rollbacks:

```python
rollback_agent = RollbackAgent(
    slack_webhook_url="your-webhook",
    enable_postmortem=True
)
```

When a rollback happens, the post-mortem analysis runs automatically and sends results to Slack.

## Slack Notifications

The Slack message includes:
- Service name and versions
- Root cause with confidence score
- Detailed description of what went wrong
- Specific fix suggestion with line numbers
- Number of recommendations generated

Example:
```
📋 Post-Mortem Analysis Complete

Service: Auth-Service
Failed Version: 1.0.3
Rollback Version: 1.0.2

Root Cause: Null/None reference error
Confidence: 90%

The failure was caused by a null pointer error in auth.py at line 42. 
The code change removed a null check, causing the application to attempt 
to access properties on a null object.

Suggested Fix:
Add null-check at line 42 of auth.py
Example: if user is not None: email = user.email.lower()

Recommendations: 3 action items identified
```

## API Endpoints

**Trigger analysis:**
```bash
POST /api/v1/postmortem/analyze
```

**Get full report:**
```bash
GET /api/v1/postmortem/report/{deployment_id}
```

**Get summary:**
```bash
GET /api/v1/postmortem/summary/{deployment_id}
```

**List all analyses:**
```bash
GET /api/v1/postmortem/list
```

**Run demo:**
```bash
POST /api/v1/postmortem/demo
```

## Real Example

Your auth service fails in production. The Post-Mortem Agent analyzes it:

**Logs show:** `AttributeError: 'NoneType' object has no attribute 'email'` at line 42 of auth.py

**Code diff shows:** Line 42 changed from:
```python
if user is not None:
    email = user.email.lower()
```
to:
```python
email = user.email.lower()
```

**Agent identifies:** Removed null check caused the error

**Recommendation:** Add the null check back, plus add a test case for null users

**Confidence:** 90% (high confidence because the error and code change match perfectly)

## What's Next

Current implementation uses simulated logs and diffs. For production:

- Connect to real logging systems (Datadog, Splunk, CloudWatch)
- Pull actual code diffs from Git
- Add machine learning for better pattern recognition
- Support more error types and languages
- Create Jira tickets automatically
- Track patterns across multiple failures

## Files

- `backend/agents/postmortem_agent.py` - Analysis logic
- `backend/routes/postmortem.py` - API endpoints
- `backend/test_postmortem_agent.py` - Demo script

## Troubleshooting

**Low confidence scores**: Means the agent isn't sure about the root cause. Usually happens when logs don't have enough detail or the code diff doesn't show obvious problems.

**Missing Slack notifications**: Check `SLACK_WEBHOOK_URL` is set and `SLACK_ENABLED=true` in your `.env` file.

**Analysis takes too long**: Should complete in <5 seconds. If slower, check log volume and code diff size.

---

The goal is to turn "what the hell happened?" into "here's exactly what broke and how to fix it" in seconds instead of hours.
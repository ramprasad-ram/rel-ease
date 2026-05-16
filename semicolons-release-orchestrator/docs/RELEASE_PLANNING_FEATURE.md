# Release Planning - Know If You're Ready Before You Deploy

Point the system at your Jira sprint and GitHub repo, and it tells you if you're actually ready to release. No more "let's deploy and see what happens."

## The Problem

Before a release, someone has to:
- Check if all sprint tickets are done
- Verify dependencies between tickets
- Make sure the build is passing
- Review test coverage
- Check for blockers

This usually involves opening 10 browser tabs, checking Jira, checking GitHub, asking people in Slack, and hoping you didn't miss anything.

## The Solution

```bash
POST /api/v1/analyze

{
  "github_repo": "mycompany/api-service",
  "jira_sprint": "SPRINT-123"
}
```

The agent:
1. Fetches all tickets from the Jira sprint
2. Analyzes dependencies between tickets
3. Detects circular dependencies (Task A needs Task B, but Task B needs Task A)
4. Checks GitHub repo health (build status, test coverage, code quality)
5. Calculates a release readiness score (0-100%)
6. Lists specific issues and recommendations

Takes about 5 seconds. You get a clear answer: ready to deploy or not.

## What You Get Back

```json
{
  "readiness_score": 67.5,
  "confidence_score": 0.85,
  "ticket_analysis": {
    "total_tickets": 12,
    "done": 5,
    "in_progress": 4,
    "blocked": 2,
    "todo": 1,
    "completion_percentage": 41.7
  },
  "repo_health": {
    "build_status": "passing",
    "test_coverage": 87.3,
    "code_quality_score": 8.5
  },
  "circular_dependencies": [
    ["PROJ-1001", "PROJ-1002", "PROJ-1003", "PROJ-1001"]
  ],
  "issues": [
    "Circular dependency detected: PROJ-1001 → PROJ-1002 → PROJ-1003 → PROJ-1001",
    "PROJ-1005 (Implement feature E) is blocked",
    "2 high-priority tickets are incomplete"
  ],
  "recommendations": [
    {
      "title": "Resolve Circular Dependencies",
      "priority": "critical",
      "action": "break_dependency_cycles",
      "impact": "Blocks release progress"
    }
  ]
}
```

## Circular Dependency Detection

This is the interesting part. The agent builds a dependency graph from Jira ticket links and uses depth-first search to detect cycles.

Example: Task A depends on Task B, Task B depends on Task C, Task C depends on Task A. That's a cycle. You can't complete any of them until you break the cycle.

The agent shows you the exact chain: PROJ-1001 → PROJ-1002 → PROJ-1003 → PROJ-1001

## The Readiness Score

Calculated from:
- Ticket completion (50% weight): How many tickets are done vs total
- Repository health (30% weight): Build status, test coverage, code quality
- Dependency issues (20% weight): Penalties for circular dependencies and blocked tickets

Score interpretation:
- 80-100%: Good to go
- 60-80%: Proceed with caution, review warnings
- Below 60%: Not ready, fix issues first

## Using the Frontend

The React component shows:

**Score Card**: Big number with color coding (green > 80%, yellow 60-80%, red < 60%)

**Ticket Breakdown**: Visual chart of done/in-progress/blocked/todo tickets

**Repository Health**: Build status, coverage percentage, quality score

**Circular Dependencies**: Highlighted warning with the dependency chains

**Issues List**: All problems found, prioritized

**Recommendations**: What to do about each issue

## Mock Mode vs Real Integration

Currently runs in mock mode with realistic demo data. Perfect for testing and demos.

For real integration, set environment variables:

```bash
GITHUB_TOKEN=your_github_token
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your_email@company.com
JIRA_API_TOKEN=your_jira_token
```

Then update the agent to use real mode:

```python
github_client = GitHubClient(mock_mode=False)
jira_client = JiraClient(mock_mode=False)
```

## API Endpoints

**Analyze release readiness:**
```bash
POST /api/v1/analyze
```

**Health check:**
```bash
GET /api/v1/health
```

## Example Workflow

You're planning to release the API service. Run the analysis:

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "github_repo": "mycompany/api-service",
    "jira_sprint": "SPRINT-123"
  }'
```

Results show:
- Readiness score: 67%
- Issue: Circular dependency between 3 tickets
- Issue: 2 high-priority tickets incomplete
- Recommendation: Break the dependency cycle before releasing

You fix the circular dependency by removing one of the links. Run analysis again:
- Readiness score: 85%
- All clear, ready to deploy

## The Dependency Graph Algorithm

```python
def detect_cycles(tickets):
    graph = build_dependency_graph(tickets)
    visited = set()
    path = []
    cycles = []
    
    for ticket in graph:
        if ticket not in visited:
            dfs(ticket, graph, visited, path, cycles)
    
    return cycles
```

Standard depth-first search with cycle detection. When you revisit a node that's in the current path, you've found a cycle.

## What's Next

Current implementation uses mock data. For production:

- Real Jira API integration
- Real GitHub API integration
- Historical trending (track readiness over time)
- Webhook triggers (auto-analyze when sprint changes)
- Custom scoring weights per team
- Integration with other project management tools

## Files

- `backend/agents/release_planning_agent.py` - Analysis logic
- `backend/integrations/github_client.py` - GitHub API client
- `backend/integrations/jira_client.py` - Jira API client
- `backend/routes/release_planning.py` - API endpoints
- `frontend/src/components/ReleasePlanningForm.jsx` - UI component

## Troubleshooting

**Analysis fails**: Check that the GitHub repo and Jira sprint IDs are correct.

**No circular dependencies detected**: The mock data might not have cycles. Try with real data or modify the mock data.

**Low readiness score**: Check the ticket completion percentage and repo health. The score reflects actual readiness.

---

This turns "are we ready to release?" from a guessing game into a data-driven decision.
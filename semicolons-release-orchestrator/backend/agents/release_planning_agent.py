"""
Release Planning Agent for analyzing sprint readiness and dependencies.
Integrates with Jira and GitHub to provide release readiness insights.
"""
import random
from typing import Dict, Any, List, Set, Optional
from models.agent import AgentType, RecommendationPriority
from .base_agent import BaseAgent


class ReleasePlanningAgent(BaseAgent):
    """
    AI agent that analyzes release readiness by examining Jira tickets and GitHub repos.
    
    Capabilities:
    - Analyzes sprint progress and ticket completion
    - Detects dependency conflicts and circular dependencies
    - Calculates release readiness score
    - Identifies blockers and risks
    """
    
    def __init__(self):
        super().__init__(AgentType.RELEASE_PLANNING)
    
    async def analyze_release_readiness(
        self,
        github_repo: str,
        jira_sprint: str,
        github_token: Optional[str] = None,
        jira_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze release readiness for a given GitHub repo and Jira sprint.
        
        Args:
            github_repo: GitHub repository (e.g., "owner/repo")
            jira_sprint: Jira sprint identifier (e.g., "SPRINT-123")
            github_token: Optional GitHub API token
            jira_token: Optional Jira API token
            
        Returns:
            Analysis results with readiness score, issues, and recommendations
        """
        self.logger.info(
            f"Starting release planning analysis for {github_repo} / {jira_sprint}"
        )
        
        # Fetch data from integrations (mock for now, real implementation would call APIs)
        jira_tickets: List[Dict[str, Any]] = await self._fetch_jira_tickets(jira_sprint, jira_token)
        github_data: Dict[str, Any] = await self._fetch_github_data(github_repo, github_token)
        
        # Build dependency graph
        dependency_graph: Dict[str, List[str]] = self._build_dependency_graph(jira_tickets)
        
        # Detect circular dependencies
        circular_deps: List[List[str]] = self._detect_circular_dependencies(dependency_graph)
        
        # Analyze ticket status
        ticket_analysis: Dict[str, Any] = self._analyze_ticket_status(jira_tickets)
        
        # Analyze GitHub repo health
        repo_health: Dict[str, Any] = self._analyze_repo_health(github_data)
        
        # Calculate release readiness score
        readiness_score: float = self._calculate_readiness_score(
            ticket_analysis,
            repo_health,
            circular_deps
        )
        
        # Generate recommendations
        recommendations: List[Dict[str, Any]] = self._generate_recommendations(
            readiness_score,
            ticket_analysis,
            circular_deps,
            repo_health
        )
        
        # Identify specific issues
        issues: List[str] = self._identify_issues(
            jira_tickets,
            circular_deps,
            ticket_analysis
        )
        
        self.logger.info(
            msg=f"Release planning analysis complete: readiness={readiness_score:.1f}%, "
            f"issues={len(issues)}, circular_deps={len(circular_deps)}"
        )
        
        return {
            "readiness_score": readiness_score,
            "confidence_score": 0.85,
            "jira_sprint": jira_sprint,
            "github_repo": github_repo,
            "ticket_analysis": ticket_analysis,
            "repo_health": repo_health,
            "circular_dependencies": circular_deps,
            "issues": issues,
            "recommendations": recommendations,
            "dependency_graph": dependency_graph,
        }
    
    async def _fetch_jira_tickets(
        self,
        sprint_id: str,
        token: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Fetch Jira tickets for the sprint (mock implementation)."""
        ticket_types: list[str] = ["Story", "Bug", "Task", "Epic"]
        statuses: list[str] = ["Done", "In Progress", "To Do", "Blocked"]
        
        tickets: list[Any] = []
        for i in range(random.randint(8, 15)):
            ticket_id: str = f"PROJ-{1000 + i}"
            status: str = random.choice(statuses)
            
            depends_on: list[Any] = []
            if i > 0 and random.random() > 0.6:
                depends_on.append(f"PROJ-{1000 + random.randint(0, i-1)}")
            
            tickets.append({
                "id": ticket_id,
                "key": ticket_id,
                "summary": f"Implement feature {chr(65 + i)}",
                "type": random.choice(seq=ticket_types),
                "status": status,
                "priority": random.choice(seq=["High", "Medium", "Low"]),
                "assignee": random.choice(seq=["Alice", "Bob", "Charlie", None]),
                "story_points": random.choice([1, 2, 3, 5, 8]),
                "depends_on": depends_on,
                "sprint": sprint_id,
            })
        
        # Add circular dependency scenario
        if len(tickets) >= 3:
            tickets[1]["depends_on"] = [tickets[2]["key"]]
            tickets[2]["depends_on"] = [tickets[3]["key"]]
            tickets[3]["depends_on"] = [tickets[1]["key"]]
        
        return tickets
    
    async def _fetch_github_data(
        self,
        repo: str,
        token: Optional[str]
    ) -> Dict[str, Any]:
        """Fetch GitHub repository data (mock implementation)."""
        return {
            "repo": repo,
            "open_prs": random.randint(2, 10),
            "merged_prs": random.randint(15, 40),
            "open_issues": random.randint(5, 20),
            "branches": random.randint(3, 8),
            "last_commit_date": "2024-01-15T10:30:00Z",
            "build_status": random.choice(["passing", "passing", "failing"]),
            "test_coverage": round(random.uniform(70, 95), 1),
            "code_quality_score": round(random.uniform(7.5, 9.5), 1),
        }
    
    def _build_dependency_graph(
        self,
        tickets: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Build dependency graph from tickets."""
        graph: dict[Any, Any] = {}
        for ticket in tickets:
            graph[ticket["key"]] = ticket.get("depends_on", [])
        return graph
    
    def _detect_circular_dependencies(
        self,
        graph: Dict[str, List[str]]
    ) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        circular_deps: list[Any] = []
        visited: set[Any] = set()
        rec_stack: set[Any] = set()
        
        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in circular_deps:
                        circular_deps.append(cycle)
            
            rec_stack.remove(node)
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return circular_deps
    
    def _analyze_ticket_status(
        self,
        tickets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze ticket completion and status."""
        total = len(tickets)
        done = sum(1 for t in tickets if t["status"] == "Done")
        in_progress = sum(1 for t in tickets if t["status"] == "In Progress")
        blocked = sum(1 for t in tickets if t["status"] == "Blocked")
        todo = sum(1 for t in tickets if t["status"] == "To Do")
        
        total_points = sum(t.get("story_points", 0) for t in tickets)
        completed_points = sum(
            t.get("story_points", 0) for t in tickets if t["status"] == "Done"
        )
        
        return {
            "total_tickets": total,
            "done": done,
            "in_progress": in_progress,
            "blocked": blocked,
            "todo": todo,
            "completion_percentage": round((done / total) * 100, 1) if total else 0,
            "total_story_points": total_points,
            "completed_story_points": completed_points,
            "points_completion_percentage": round(
                (completed_points / total_points) * 100, 1
            ) if total_points else 0,
        }
    
    def _analyze_repo_health(
        self,
        github_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze GitHub repository health."""
        build_healthy = github_data["build_status"] == "passing"
        coverage_healthy = github_data["test_coverage"] >= 80
        quality_healthy = github_data["code_quality_score"] >= 8.0
        
        health_score = sum([build_healthy, coverage_healthy, quality_healthy]) / 3 * 100
        
        return {
            "build_status": github_data["build_status"],
            "test_coverage": github_data["test_coverage"],
            "code_quality_score": github_data["code_quality_score"],
            "open_prs": github_data["open_prs"],
            "open_issues": github_data["open_issues"],
            "health_score": round(health_score, 1),
            "is_healthy": health_score >= 70,
        }
    
    def _calculate_readiness_score(
        self,
        ticket_analysis: Dict[str, Any],
        repo_health: Dict[str, Any],
        circular_deps: List[List[str]]
    ) -> float:
        """Calculate overall release readiness score."""
        # Weight different factors
        ticket_weight = 0.5
        repo_weight = 0.3
        dependency_weight = 0.2
        
        # Ticket completion score
        ticket_score = ticket_analysis["completion_percentage"]
        
        # Repo health score
        repo_score = repo_health["health_score"]
        
        # Dependency score (penalize circular dependencies)
        dependency_score = 100 - (len(circular_deps) * 15)
        dependency_score = max(0, dependency_score)
        
        # Calculate weighted score
        readiness = (
            ticket_score * ticket_weight +
            repo_score * repo_weight +
            dependency_score * dependency_weight
        )
        
        # Penalize blocked tickets
        if ticket_analysis["blocked"] > 0:
            readiness -= ticket_analysis["blocked"] * 5
        
        return round(max(0, min(100, readiness)), 1)
    
    def _identify_issues(
        self,
        tickets: List[Dict[str, Any]],
        circular_deps: List[List[str]],
        ticket_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify specific issues in the release."""
        issues = []
        
        # Circular dependency issues
        for cycle in circular_deps:
            cycle_str = " → ".join(cycle)
            issues.append(f"Circular dependency detected: {cycle_str}")
        
        # Blocked tickets
        blocked_tickets = [t for t in tickets if t["status"] == "Blocked"]
        for ticket in blocked_tickets:
            issues.append(
                f"{ticket['key']} ({ticket['summary']}) is blocked"
            )
        
        # High priority incomplete tickets
        high_priority_incomplete = [
            t for t in tickets
            if t["priority"] == "High" and t["status"] != "Done"
        ]
        if high_priority_incomplete:
            issues.append(
                f"{len(high_priority_incomplete)} high-priority tickets are incomplete"
            )
        
        # Unassigned tickets
        unassigned = [t for t in tickets if not t.get("assignee")]
        if unassigned:
            issues.append(f"{len(unassigned)} tickets are unassigned")
        
        return issues
    
    def _generate_recommendations(
        self,
        readiness_score: float,
        ticket_analysis: Dict[str, Any],
        circular_deps: List[List[str]],
        repo_health: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Overall readiness recommendation
        if readiness_score >= 80:
            recommendations.append(
                self.create_recommendation(
                    title="Release Ready",
                    description=f"Release readiness score is {readiness_score}%. Sprint is ready for release.",
                    priority=RecommendationPriority.LOW,
                    action="proceed_with_release",
                    impact="Low risk release"
                ).model_dump()
            )
        elif readiness_score >= 60:
            recommendations.append(
                self.create_recommendation(
                    title="Release with Caution",
                    description=f"Release readiness score is {readiness_score}%. Address issues before release.",
                    priority=RecommendationPriority.MEDIUM,
                    action="review_issues",
                    impact="Medium risk release"
                ).model_dump()
            )
        else:
            recommendations.append(
                self.create_recommendation(
                    title="Not Ready for Release",
                    description=f"Release readiness score is {readiness_score}%. Significant issues need resolution.",
                    priority=RecommendationPriority.CRITICAL,
                    action="delay_release",
                    impact="High risk - likely to fail"
                ).model_dump()
            )
        
        # Circular dependency recommendations
        if circular_deps:
            recommendations.append(
                self.create_recommendation(
                    title="Resolve Circular Dependencies",
                    description=f"Found {len(circular_deps)} circular dependency chain(s). Break the cycles to proceed.",
                    priority=RecommendationPriority.CRITICAL,
                    action="break_dependency_cycles",
                    impact="Blocks release progress"
                ).model_dump()
            )
        
        # Blocked tickets
        if ticket_analysis["blocked"] > 0:
            recommendations.append(
                self.create_recommendation(
                    title="Unblock Tickets",
                    description=f"{ticket_analysis['blocked']} tickets are blocked. Resolve blockers immediately.",
                    priority=RecommendationPriority.HIGH,
                    action="resolve_blockers",
                    impact="Delays release timeline"
                ).model_dump()
            )
        
        # Build health
        if repo_health["build_status"] != "passing":
            recommendations.append(
                self.create_recommendation(
                    title="Fix Build Failures",
                    description="Build is failing. Fix build issues before release.",
                    priority=RecommendationPriority.CRITICAL,
                    action="fix_build",
                    impact="Cannot deploy with failing build"
                ).model_dump()
            )
        
        # Test coverage
        if repo_health["test_coverage"] < 80:
            recommendations.append(
                self.create_recommendation(
                    title="Improve Test Coverage",
                    description=f"Test coverage is {repo_health['test_coverage']}%. Aim for 80%+.",
                    priority=RecommendationPriority.MEDIUM,
                    action="add_tests",
                    impact="Increases deployment risk"
                ).model_dump()
            )
        
        return recommendations

    async def analyze(self, deployment) -> Dict[str, Any]:
        """Required by BaseAgent interface."""
        return {
            "confidence_score": 1.0,
            "analysis_data": {"status": "use analyze_release_readiness instead"},
            "recommendations": [],
        }


# Made with Bob
"""
CI/CD Validation Agent for pre-flight deployment checks.
Analyzes CI run history, detects performance regressions, and identifies potential issues.
"""
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from models.agent import AgentType, RecommendationPriority
from models.deployment import Deployment
from .base_agent import BaseAgent


class CICDValidationAgent(BaseAgent):
    """
    AI agent that performs pre-flight validation by analyzing CI/CD run history.
    
    Capabilities:
    - Analyzes last N CI runs
    - Detects memory usage trends and leaks
    - Identifies performance regressions
    - Validates test coverage trends
    - Checks build stability
    - Flags potential issues before deployment
    """
    
    def __init__(self):
        super().__init__(AgentType.CICD_VALIDATION)
    
    async def analyze(self, deployment: Deployment) -> Dict[str, Any]:
        """
        Perform pre-flight validation analysis.
        
        Args:
            deployment: Deployment to validate
            
        Returns:
            Analysis results with warnings and recommendations
        """
        self.log_analysis_start(deployment)
        
        # Fetch CI run history
        ci_runs = await self._fetch_ci_run_history(deployment, num_runs=5)
        
        # Analyze memory usage trends
        memory_analysis = self._analyze_memory_trends(ci_runs)
        
        # Analyze performance metrics
        performance_analysis = self._analyze_performance_trends(ci_runs)
        
        # Analyze test coverage
        coverage_analysis = self._analyze_test_coverage(ci_runs)
        
        # Analyze build stability
        build_analysis = self._analyze_build_stability(ci_runs)
        
        # Detect potential issues
        issues = self._detect_issues(
            memory_analysis,
            performance_analysis,
            coverage_analysis,
            build_analysis
        )
        
        # Calculate validation score
        validation_score = self._calculate_validation_score(
            memory_analysis,
            performance_analysis,
            coverage_analysis,
            build_analysis
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            issues,
            validation_score,
            memory_analysis,
            performance_analysis
        )
        
        confidence = 0.9  # High confidence in CI data analysis
        
        self.log_analysis_complete(deployment, confidence, len(recommendations))
        
        return {
            "confidence_score": confidence,
            "analysis_data": {
                "validation_score": validation_score,
                "ci_runs_analyzed": len(ci_runs),
                "memory_analysis": memory_analysis,
                "performance_analysis": performance_analysis,
                "coverage_analysis": coverage_analysis,
                "build_analysis": build_analysis,
                "issues": issues,
            },
            "recommendations": recommendations,
        }
    
    async def _fetch_ci_run_history(
        self,
        deployment: Deployment,
        num_runs: int = 5
    ) -> List[Dict[str, Any]]:
        """Fetch recent CI run history (mock implementation)."""
        runs = []
        base_memory = 512  # MB
        base_response_time = 150  # ms
        
        for i in range(num_runs):
            run_number = 1000 + num_runs - i
            days_ago = i
            
            # Simulate memory increase trend
            memory_increase = i * random.uniform(8, 15)  # Gradual increase
            memory_usage = base_memory + memory_increase
            
            # Simulate occasional performance degradation
            response_time = base_response_time + (i * random.uniform(5, 15))
            
            runs.append({
                "run_number": run_number,
                "timestamp": (datetime.utcnow() - timedelta(days=days_ago)).isoformat(),
                "status": random.choice(["success", "success", "success", "failed"]),
                "duration_seconds": random.randint(180, 420),
                "metrics": {
                    "memory_usage_mb": round(memory_usage, 1),
                    "peak_memory_mb": round(memory_usage * 1.2, 1),
                    "cpu_usage_percent": round(random.uniform(45, 75), 1),
                    "response_time_ms": round(response_time, 1),
                    "test_coverage_percent": round(random.uniform(78, 85), 1),
                    "tests_passed": random.randint(145, 160),
                    "tests_failed": random.randint(0, 3),
                },
                "logs": {
                    "has_memory_warnings": i >= 3,  # Recent runs have warnings
                    "has_performance_warnings": i >= 2,
                    "error_count": random.randint(0, 5),
                },
                "modules_analyzed": [
                    {
                        "name": "auth-service",
                        "memory_mb": round(memory_usage * 0.3, 1),
                        "has_leak": i >= 3 and random.random() > 0.5,
                    },
                    {
                        "name": "payment-processor",
                        "memory_mb": round(memory_usage * 0.25, 1),
                        "has_leak": False,
                    },
                    {
                        "name": "notification-service",
                        "memory_mb": round(memory_usage * 0.2, 1),
                        "has_leak": i >= 4 and random.random() > 0.7,
                    },
                ],
            })
        
        return runs
    
    def _analyze_memory_trends(self, ci_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze memory usage trends across CI runs."""
        if not ci_runs:
            return {"trend": "unknown", "increase_percent": 0}
        
        memory_values = [run["metrics"]["memory_usage_mb"] for run in ci_runs]
        
        # Calculate trend
        oldest_memory = memory_values[-1]
        newest_memory = memory_values[0]
        increase_percent = ((newest_memory - oldest_memory) / oldest_memory) * 100
        
        # Detect potential leaks by module
        leaky_modules = []
        for run in ci_runs[:2]:  # Check recent runs
            for module in run.get("modules_analyzed", []):
                if module.get("has_leak"):
                    if module["name"] not in leaky_modules:
                        leaky_modules.append(module["name"])
        
        return {
            "trend": "increasing" if increase_percent > 5 else "stable",
            "increase_percent": round(increase_percent, 1),
            "oldest_memory_mb": round(oldest_memory, 1),
            "newest_memory_mb": round(newest_memory, 1),
            "average_memory_mb": round(sum(memory_values) / len(memory_values), 1),
            "peak_memory_mb": round(max(run["metrics"]["peak_memory_mb"] for run in ci_runs), 1),
            "has_potential_leak": increase_percent > 10,
            "leaky_modules": leaky_modules,
            "severity": "critical" if increase_percent > 15 else "warning" if increase_percent > 10 else "normal",
        }
    
    def _analyze_performance_trends(self, ci_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance metrics trends."""
        if not ci_runs:
            return {"trend": "unknown"}
        
        response_times = [run["metrics"]["response_time_ms"] for run in ci_runs]
        
        oldest_rt = response_times[-1]
        newest_rt = response_times[0]
        degradation_percent = ((newest_rt - oldest_rt) / oldest_rt) * 100
        
        return {
            "trend": "degrading" if degradation_percent > 10 else "stable",
            "degradation_percent": round(degradation_percent, 1),
            "oldest_response_time_ms": round(oldest_rt, 1),
            "newest_response_time_ms": round(newest_rt, 1),
            "average_response_time_ms": round(sum(response_times) / len(response_times), 1),
            "has_regression": degradation_percent > 15,
            "severity": "warning" if degradation_percent > 15 else "normal",
        }
    
    def _analyze_test_coverage(self, ci_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test coverage trends."""
        if not ci_runs:
            return {"trend": "unknown"}
        
        coverage_values = [run["metrics"]["test_coverage_percent"] for run in ci_runs]
        
        return {
            "current_coverage": round(coverage_values[0], 1),
            "average_coverage": round(sum(coverage_values) / len(coverage_values), 1),
            "trend": "improving" if coverage_values[0] > coverage_values[-1] else "declining",
            "meets_threshold": coverage_values[0] >= 80,
        }
    
    def _analyze_build_stability(self, ci_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze build stability."""
        if not ci_runs:
            return {"stability": "unknown"}
        
        total_runs = len(ci_runs)
        successful_runs = sum(1 for run in ci_runs if run["status"] == "success")
        success_rate = (successful_runs / total_runs) * 100
        
        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": total_runs - successful_runs,
            "success_rate": round(success_rate, 1),
            "is_stable": success_rate >= 80,
            "recent_failures": [
                run["run_number"] for run in ci_runs if run["status"] == "failed"
            ],
        }
    
    def _detect_issues(
        self,
        memory_analysis: Dict[str, Any],
        performance_analysis: Dict[str, Any],
        coverage_analysis: Dict[str, Any],
        build_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect specific issues from analysis."""
        issues = []
        
        # Memory leak detection
        if memory_analysis.get("has_potential_leak"):
            for module in memory_analysis.get("leaky_modules", []):
                issues.append({
                    "type": "memory_leak",
                    "severity": memory_analysis["severity"],
                    "title": f"Potential memory leak detected in {module}",
                    "description": (
                        f"Memory usage increased by {memory_analysis['increase_percent']}% "
                        f"over the last 5 CI runs. Module '{module}' shows signs of memory leak."
                    ),
                    "metric": f"{memory_analysis['increase_percent']}% increase",
                })
        
        # Performance regression
        if performance_analysis.get("has_regression"):
            issues.append({
                "type": "performance_regression",
                "severity": performance_analysis["severity"],
                "title": "Performance regression detected",
                "description": (
                    f"Response time increased by {performance_analysis['degradation_percent']}% "
                    f"from {performance_analysis['oldest_response_time_ms']}ms to "
                    f"{performance_analysis['newest_response_time_ms']}ms."
                ),
                "metric": f"{performance_analysis['degradation_percent']}% slower",
            })
        
        # Test coverage issues
        if not coverage_analysis.get("meets_threshold"):
            issues.append({
                "type": "low_coverage",
                "severity": "warning",
                "title": "Test coverage below threshold",
                "description": (
                    f"Current test coverage is {coverage_analysis['current_coverage']}%, "
                    "which is below the recommended 80% threshold."
                ),
                "metric": f"{coverage_analysis['current_coverage']}% coverage",
            })
        
        # Build instability
        if not build_analysis.get("is_stable"):
            issues.append({
                "type": "build_instability",
                "severity": "warning",
                "title": "Build instability detected",
                "description": (
                    f"Only {build_analysis['success_rate']}% of recent builds succeeded. "
                    f"{build_analysis['failed_runs']} out of {build_analysis['total_runs']} runs failed."
                ),
                "metric": f"{build_analysis['success_rate']}% success rate",
            })
        
        return issues
    
    def _calculate_validation_score(
        self,
        memory_analysis: Dict[str, Any],
        performance_analysis: Dict[str, Any],
        coverage_analysis: Dict[str, Any],
        build_analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall validation score."""
        score = 100.0
        
        # Penalize memory issues
        if memory_analysis.get("has_potential_leak"):
            score -= memory_analysis["increase_percent"] * 2
        
        # Penalize performance regressions
        if performance_analysis.get("has_regression"):
            score -= performance_analysis["degradation_percent"]
        
        # Penalize low coverage
        if not coverage_analysis.get("meets_threshold"):
            score -= (80 - coverage_analysis["current_coverage"]) * 0.5
        
        # Penalize build instability
        if not build_analysis.get("is_stable"):
            score -= (100 - build_analysis["success_rate"]) * 0.3
        
        return round(max(0, min(100, score)), 1)
    
    def _generate_recommendations(
        self,
        issues: List[Dict[str, Any]],
        validation_score: float,
        memory_analysis: Dict[str, Any],
        performance_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Overall validation recommendation
        if validation_score >= 80:
            recommendations.append(
                self.create_recommendation(
                    title="Pre-Flight Validation Passed",
                    description=f"Validation score is {validation_score}%. Deployment is ready to proceed.",
                    priority=RecommendationPriority.LOW,
                    action="proceed_with_deployment",
                    impact="Low risk deployment"
                ).model_dump()
            )
        elif validation_score >= 60:
            recommendations.append(
                self.create_recommendation(
                    title="Proceed with Caution",
                    description=f"Validation score is {validation_score}%. Review warnings before deploying.",
                    priority=RecommendationPriority.MEDIUM,
                    action="review_warnings",
                    impact="Medium risk - monitor closely"
                ).model_dump()
            )
        else:
            recommendations.append(
                self.create_recommendation(
                    title="Deployment Not Recommended",
                    description=f"Validation score is {validation_score}%. Critical issues must be resolved.",
                    priority=RecommendationPriority.CRITICAL,
                    action="fix_issues_before_deployment",
                    impact="High risk - likely to fail"
                ).model_dump()
            )
        
        # Issue-specific recommendations
        for issue in issues:
            if issue["type"] == "memory_leak":
                recommendations.append(
                    self.create_recommendation(
                        title=issue["title"],
                        description=issue["description"],
                        priority=RecommendationPriority.CRITICAL if issue["severity"] == "critical" else RecommendationPriority.HIGH,
                        action="investigate_memory_leak",
                        impact="May cause out-of-memory errors in production"
                    ).model_dump()
                )
            
            elif issue["type"] == "performance_regression":
                recommendations.append(
                    self.create_recommendation(
                        title=issue["title"],
                        description=issue["description"],
                        priority=RecommendationPriority.HIGH,
                        action="profile_and_optimize",
                        impact="Degraded user experience"
                    ).model_dump()
                )
            
            elif issue["type"] == "low_coverage":
                recommendations.append(
                    self.create_recommendation(
                        title=issue["title"],
                        description=issue["description"],
                        priority=RecommendationPriority.MEDIUM,
                        action="add_more_tests",
                        impact="Increased risk of undetected bugs"
                    ).model_dump()
                )
            
            elif issue["type"] == "build_instability":
                recommendations.append(
                    self.create_recommendation(
                        title=issue["title"],
                        description=issue["description"],
                        priority=RecommendationPriority.HIGH,
                        action="stabilize_build_pipeline",
                        impact="Unreliable deployments"
                    ).model_dump()
                )
        
        return recommendations


# Made with Bob
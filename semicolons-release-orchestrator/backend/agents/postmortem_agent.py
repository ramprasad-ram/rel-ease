"""
Post-Mortem Analysis Agent.
Analyzes failed deployments, logs, and code diffs to identify root causes and provide actionable recommendations.
"""
import re
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from uuid import UUID

from models.deployment import Deployment, DeploymentState
from models.agent import AgentType, AgentRecommendation, RecommendationPriority
from agents.base_agent import BaseAgent
from integrations.slack_client import SlackClient

logger = logging.getLogger(__name__)


class PostmortemAgent(BaseAgent):
    """
    AI agent that performs post-mortem analysis on failed deployments.
    
    Features:
    - Log analysis and error pattern detection
    - Code diff analysis
    - Root cause identification
    - Actionable recommendations with specific line numbers
    - Comprehensive failure reports
    """
    
    # Common error patterns and their root causes
    ERROR_PATTERNS = {
        r"NullPointerException|null pointer|NoneType.*None": {
            "type": "null_pointer",
            "description": "Null/None reference error",
            "common_causes": [
                "Missing null/None checks",
                "Uninitialized variables",
                "Optional values not handled"
            ]
        },
        r"ConnectionRefusedError|ECONNREFUSED|connection refused": {
            "type": "connection_refused",
            "description": "Connection refused error",
            "common_causes": [
                "Service not running",
                "Wrong port configuration",
                "Firewall blocking connection"
            ]
        },
        r"TimeoutError|timeout|timed out": {
            "type": "timeout",
            "description": "Operation timeout",
            "common_causes": [
                "Slow database queries",
                "Network latency",
                "Insufficient timeout configuration"
            ]
        },
        r"KeyError|key.*not found|missing key": {
            "type": "missing_key",
            "description": "Missing dictionary/object key",
            "common_causes": [
                "Missing validation for required fields",
                "API contract mismatch",
                "Configuration missing"
            ]
        },
        r"MemoryError|OutOfMemoryError|OOM": {
            "type": "memory",
            "description": "Out of memory error",
            "common_causes": [
                "Memory leak",
                "Insufficient memory allocation",
                "Large data processing without pagination"
            ]
        },
        r"AuthenticationError|Unauthorized|401": {
            "type": "authentication",
            "description": "Authentication failure",
            "common_causes": [
                "Invalid credentials",
                "Expired tokens",
                "Missing authentication headers"
            ]
        },
        r"DatabaseError|SQL.*error|query failed": {
            "type": "database",
            "description": "Database operation failure",
            "common_causes": [
                "Invalid SQL syntax",
                "Database connection issues",
                "Missing database migrations"
            ]
        }
    }
    
    def __init__(self, slack_webhook_url: Optional[str] = None):
        """
        Initialize Post-Mortem Agent.
        
        Args:
            slack_webhook_url: Slack webhook URL for notifications
        """
        super().__init__(AgentType.POSTMORTEM)
        self.slack_client = SlackClient(webhook_url=slack_webhook_url)
    
    async def analyze(self, deployment: Deployment) -> Dict[str, Any]:
        """
        Perform comprehensive post-mortem analysis on a failed deployment.
        
        Args:
            deployment: Failed deployment to analyze
            
        Returns:
            Analysis results with root cause and recommendations
        """
        deployment_id = str(deployment.id)
        
        logger.info(f"Starting post-mortem analysis for deployment {deployment_id}")
        
        # Collect all available data
        logs = self._get_deployment_logs(deployment_id)
        code_diff = self._get_code_diff(deployment)
        error_metrics = self._get_error_metrics(deployment_id)
        
        # Analyze logs for error patterns
        log_analysis = self._analyze_logs(logs)
        
        # Analyze code changes
        diff_analysis = self._analyze_code_diff(code_diff)
        
        # Identify root cause
        root_cause = self._identify_root_cause(log_analysis, diff_analysis, error_metrics)
        
        # Generate specific recommendations
        recommendations = self._generate_recommendations(root_cause, diff_analysis)
        
        analysis = {
            "deployment_id": deployment_id,
            "service_name": deployment.name,
            "failed_version": deployment.version,
            "rollback_version": deployment.rollback_version,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "log_analysis": log_analysis,
            "code_diff_analysis": diff_analysis,
            "root_cause": root_cause,
            "recommendations": recommendations,
            "confidence_score": root_cause.get("confidence", 0.0)
        }
        
        logger.info(
            f"Post-mortem analysis complete for {deployment.name}: "
            f"Root cause: {root_cause.get('type', 'unknown')}"
        )
        
        return analysis
    
    async def generate_recommendations(
        self,
        deployment: Deployment,
        analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations based on post-mortem analysis.
        
        Args:
            deployment: Deployment being analyzed
            analysis_data: Post-mortem analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        root_cause = analysis_data.get("root_cause", {})
        
        # Add primary recommendation based on root cause
        if root_cause.get("type"):
            recommendations.append(
                self.create_recommendation(
                    title=f"Fix {root_cause['description']}",
                    description=root_cause.get("detailed_description", ""),
                    priority=RecommendationPriority.CRITICAL,
                    action=root_cause.get("suggested_fix", ""),
                    impact="Prevent similar failures in future deployments"
                ).model_dump()
            )
        
        # Add code-specific recommendations
        for rec in analysis_data.get("recommendations", []):
            recommendations.append(
                self.create_recommendation(
                    title=rec["title"],
                    description=rec["description"],
                    priority=RecommendationPriority.HIGH,
                    action=rec.get("action", ""),
                    impact=rec.get("impact", "Improve code quality and reliability")
                ).model_dump()
            )
        
        return recommendations
    
    def _get_deployment_logs(self, deployment_id: str) -> List[str]:
        """
        Retrieve deployment logs (simulated for demo).
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            List of log lines
        """
        # In production, this would fetch from logging system (ELK, CloudWatch, etc.)
        # For demo, return simulated logs
        return [
            "2024-01-15 10:30:00 INFO Starting Auth-Service v1.0.3",
            "2024-01-15 10:30:05 INFO Connecting to database",
            "2024-01-15 10:30:10 ERROR NullPointerException in auth.py:42",
            "2024-01-15 10:30:10 ERROR   at validateUser(auth.py:42)",
            "2024-01-15 10:30:10 ERROR   user.email accessed but user is None",
            "2024-01-15 10:30:15 ERROR Request failed with 500 Internal Server Error",
            "2024-01-15 10:30:20 ERROR Multiple authentication failures detected",
            "2024-01-15 10:30:25 WARN Error rate exceeding threshold: 40%"
        ]
    
    def _get_code_diff(self, deployment: Deployment) -> Dict[str, Any]:
        """
        Get code diff between failed and previous version (simulated).
        
        Args:
            deployment: Deployment object
            
        Returns:
            Code diff information
        """
        # In production, this would fetch from Git/GitHub
        # For demo, return simulated diff
        return {
            "files_changed": ["auth.py", "config.py"],
            "changes": {
                "auth.py": {
                    "additions": [
                        {
                            "line": 42,
                            "code": "    email = user.email.lower()",
                            "context": "validateUser function"
                        },
                        {
                            "line": 45,
                            "code": "    return authenticate(email, password)",
                            "context": "validateUser function"
                        }
                    ],
                    "deletions": [
                        {
                            "line": 42,
                            "code": "    if user:",
                            "context": "validateUser function"
                        },
                        {
                            "line": 43,
                            "code": "        email = user.email.lower()",
                            "context": "validateUser function"
                        }
                    ]
                }
            }
        }
    
    def _get_error_metrics(self, deployment_id: str) -> Dict[str, Any]:
        """
        Get error metrics for the deployment.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Error metrics
        """
        return {
            "total_errors": 200,
            "error_rate": 0.40,
            "error_types": {
                "5xx": 180,
                "4xx": 20
            },
            "affected_endpoints": ["/api/auth/login", "/api/auth/validate"]
        }
    
    def _analyze_logs(self, logs: List[str]) -> Dict[str, Any]:
        """
        Analyze logs to identify error patterns.
        
        Args:
            logs: List of log lines
            
        Returns:
            Log analysis results
        """
        errors = []
        error_patterns_found = {}
        
        for log_line in logs:
            # Check for error level
            if "ERROR" in log_line or "CRITICAL" in log_line:
                errors.append(log_line)
                
                # Match against known patterns
                for pattern, info in self.ERROR_PATTERNS.items():
                    if re.search(pattern, log_line, re.IGNORECASE):
                        error_type = info["type"]
                        if error_type not in error_patterns_found:
                            error_patterns_found[error_type] = {
                                "count": 0,
                                "examples": [],
                                "info": info
                            }
                        error_patterns_found[error_type]["count"] += 1
                        if len(error_patterns_found[error_type]["examples"]) < 3:
                            error_patterns_found[error_type]["examples"].append(log_line)
        
        return {
            "total_errors": len(errors),
            "error_patterns": error_patterns_found,
            "sample_errors": errors[:5]
        }
    
    def _analyze_code_diff(self, code_diff: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code changes to identify potential issues.
        
        Args:
            code_diff: Code diff information
            
        Returns:
            Code diff analysis
        """
        risky_changes = []
        
        for file_name, changes in code_diff.get("changes", {}).items():
            # Check deletions for removed safety checks
            for deletion in changes.get("deletions", []):
                code = deletion["code"].strip()
                if re.search(r"if\s+\w+:", code) or "is not None" in code or "is None" in code:
                    risky_changes.append({
                        "file": file_name,
                        "line": deletion["line"],
                        "type": "removed_null_check",
                        "description": f"Removed null/None check at line {deletion['line']}",
                        "code": code
                    })
            
            # Check additions for potential issues
            for addition in changes.get("additions", []):
                code = addition["code"].strip()
                # Check for direct property access without null check
                if re.search(r"\w+\.\w+", code) and "if" not in code:
                    risky_changes.append({
                        "file": file_name,
                        "line": addition["line"],
                        "type": "unsafe_property_access",
                        "description": f"Property access without null check at line {addition['line']}",
                        "code": code
                    })
        
        return {
            "files_changed": code_diff.get("files_changed", []),
            "risky_changes": risky_changes,
            "total_risky_changes": len(risky_changes)
        }
    
    def _identify_root_cause(
        self,
        log_analysis: Dict[str, Any],
        diff_analysis: Dict[str, Any],
        error_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Identify the root cause by correlating logs and code changes.
        
        Args:
            log_analysis: Log analysis results
            diff_analysis: Code diff analysis results
            error_metrics: Error metrics
            
        Returns:
            Root cause identification
        """
        # Find the most common error pattern
        error_patterns = log_analysis.get("error_patterns", {})
        if not error_patterns:
            return {
                "type": "unknown",
                "description": "Unable to identify specific root cause",
                "confidence": 0.3
            }
        
        # Get the most frequent error type
        most_common_error = max(
            error_patterns.items(),
            key=lambda x: x[1]["count"]
        )
        error_type, error_data = most_common_error
        
        # Correlate with code changes
        risky_changes = diff_analysis.get("risky_changes", [])
        correlated_change = None
        
        for change in risky_changes:
            if error_type == "null_pointer" and change["type"] in ["removed_null_check", "unsafe_property_access"]:
                correlated_change = change
                break
        
        # Build root cause report
        root_cause = {
            "type": error_type,
            "description": error_data["info"]["description"],
            "confidence": 0.9 if correlated_change else 0.6,
            "error_count": error_data["count"],
            "affected_endpoints": error_metrics.get("affected_endpoints", [])
        }
        
        if correlated_change:
            root_cause["detailed_description"] = (
                f"The failure was caused by {error_data['info']['description']} "
                f"in {correlated_change['file']} at line {correlated_change['line']}. "
                f"The code change removed a null check, causing the application to "
                f"attempt to access properties on a null/None object."
            )
            root_cause["suggested_fix"] = (
                f"Add a null-check at line {correlated_change['line']} of {correlated_change['file']}. "
                f"Example: if user is not None: email = user.email.lower()"
            )
            root_cause["file"] = correlated_change["file"]
            root_cause["line"] = correlated_change["line"]
            root_cause["problematic_code"] = correlated_change["code"]
        else:
            root_cause["detailed_description"] = (
                f"The failure was caused by {error_data['info']['description']}. "
                f"Common causes: {', '.join(error_data['info']['common_causes'])}"
            )
            root_cause["suggested_fix"] = f"Review and address: {', '.join(error_data['info']['common_causes'])}"
        
        return root_cause
    
    def _generate_recommendations(
        self,
        root_cause: Dict[str, Any],
        diff_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate specific, actionable recommendations.
        
        Args:
            root_cause: Identified root cause
            diff_analysis: Code diff analysis
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Add specific code fix recommendation
        if root_cause.get("file") and root_cause.get("line"):
            recommendations.append({
                "title": f"Fix null check in {root_cause['file']}",
                "description": root_cause.get("suggested_fix", ""),
                "action": f"Add null-check at line {root_cause['line']}",
                "impact": "Prevent null pointer exceptions",
                "code_example": self._generate_code_fix_example(root_cause)
            })
        
        # Add testing recommendation
        recommendations.append({
            "title": "Add unit tests for null handling",
            "description": "Create tests that verify null/None handling in authentication flow",
            "action": "Add test cases for edge cases with null users",
            "impact": "Catch similar issues before deployment"
        })
        
        # Add monitoring recommendation
        recommendations.append({
            "title": "Enhance error monitoring",
            "description": "Add specific alerts for null pointer exceptions in authentication",
            "action": "Configure alerts for NullPointerException in auth module",
            "impact": "Faster detection of similar issues"
        })
        
        return recommendations
    
    def _generate_code_fix_example(self, root_cause: Dict[str, Any]) -> str:
        """
        Generate a code example showing the fix.
        
        Args:
            root_cause: Root cause information
            
        Returns:
            Code fix example
        """
        if root_cause.get("type") == "null_pointer":
            return """
# Before (problematic):
email = user.email.lower()

# After (fixed):
if user is not None:
    email = user.email.lower()
else:
    raise ValueError("User cannot be None")
"""
        return "See suggested fix in root cause analysis"
    
    async def generate_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generate a formatted post-mortem report.
        
        Args:
            analysis: Post-mortem analysis results
            
        Returns:
            Formatted report text
        """
        root_cause = analysis.get("root_cause", {})
        
        report = f"""
# Post-Mortem Analysis Report

## Deployment Information
- Service: {analysis['service_name']}
- Failed Version: {analysis['failed_version']}
- Rollback Version: {analysis['rollback_version']}
- Analysis Time: {analysis['analyzed_at']}

## Root Cause
**Type:** {root_cause.get('description', 'Unknown')}
**Confidence:** {root_cause.get('confidence', 0) * 100:.0f}%

{root_cause.get('detailed_description', 'No detailed description available')}

## Suggested Fix
{root_cause.get('suggested_fix', 'No specific fix suggested')}

## Recommendations
"""
        
        for i, rec in enumerate(analysis.get('recommendations', []), 1):
            report += f"\n{i}. **{rec['title']}**\n"
            report += f"   - {rec['description']}\n"
            report += f"   - Action: {rec['action']}\n"
        
        return report
    
    async def send_postmortem_notification(self, analysis: Dict[str, Any]) -> None:
        """
        Send post-mortem analysis to Slack.
        
        Args:
            analysis: Post-mortem analysis results
        """
        root_cause = analysis.get("root_cause", {})
        
        message = f"""
📋 *Post-Mortem Analysis Complete*

*Service:* {analysis['service_name']}
*Failed Version:* {analysis['failed_version']}
*Rollback Version:* {analysis['rollback_version']}

*Root Cause:* {root_cause.get('description', 'Unknown')}
*Confidence:* {root_cause.get('confidence', 0) * 100:.0f}%

*Summary:*
{root_cause.get('detailed_description', 'Analysis in progress')}

*Suggested Fix:*
{root_cause.get('suggested_fix', 'See full report')}

*Recommendations:* {len(analysis.get('recommendations', []))} action items identified
"""
        
        await self.slack_client.send_message(text=message)


# Made with Bob
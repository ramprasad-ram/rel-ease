"""
Pre-defined workflow templates for common deployment scenarios.
"""
from typing import List, Dict, Any
from models.workflow import WorkflowType, WorkflowStepBase


class WorkflowTemplates:
    """
    Collection of pre-defined workflow templates.
    """
    
    @staticmethod
    def standard_deployment() -> Dict[str, Any]:
        """
        Standard deployment workflow: Build → Test → Deploy → Health Check
        """
        return {
            "name": "Standard Deployment",
            "workflow_type": WorkflowType.SEQUENTIAL,
            "description": "Standard deployment pipeline with build, test, and deploy steps",
            "steps": [
                {
                    "name": "Build Application",
                    "description": "Compile and build application artifacts",
                    "step_type": "build",
                    "order": 0,
                    "config": {
                        "build_tool": "maven",
                        "target": "production",
                    },
                    "retry_count": 2,
                    "timeout_seconds": 600,
                },
                {
                    "name": "Run Tests",
                    "description": "Execute full test suite",
                    "step_type": "test",
                    "order": 1,
                    "config": {
                        "test_suite": "full",
                        "coverage_threshold": 80,
                    },
                    "retry_count": 1,
                    "timeout_seconds": 900,
                },
                {
                    "name": "Deploy to Environment",
                    "description": "Deploy application to target environment",
                    "step_type": "deploy",
                    "order": 2,
                    "config": {
                        "platform": "kubernetes",
                        "replicas": 3,
                    },
                    "retry_count": 2,
                    "timeout_seconds": 600,
                },
                {
                    "name": "Health Check",
                    "description": "Verify deployment health",
                    "step_type": "health_check",
                    "order": 3,
                    "config": {
                        "timeout": 60,
                        "retries": 5,
                    },
                    "retry_count": 3,
                    "timeout_seconds": 120,
                },
            ],
        }
    
    @staticmethod
    def canary_deployment() -> Dict[str, Any]:
        """
        Canary deployment workflow with gradual rollout.
        """
        return {
            "name": "Canary Deployment",
            "workflow_type": WorkflowType.SEQUENTIAL,
            "description": "Gradual rollout with canary testing",
            "steps": [
                {
                    "name": "Build Application",
                    "step_type": "build",
                    "order": 0,
                    "config": {},
                    "retry_count": 2,
                },
                {
                    "name": "Run Tests",
                    "step_type": "test",
                    "order": 1,
                    "config": {"test_suite": "full"},
                    "retry_count": 1,
                },
                {
                    "name": "Deploy Canary (10%)",
                    "step_type": "deploy",
                    "order": 2,
                    "config": {
                        "platform": "kubernetes",
                        "replicas": 1,
                        "traffic_percentage": 10,
                    },
                    "retry_count": 2,
                },
                {
                    "name": "Monitor Canary",
                    "step_type": "health_check",
                    "order": 3,
                    "config": {"duration": 300},
                    "retry_count": 0,
                },
                {
                    "name": "Deploy Full (100%)",
                    "step_type": "deploy",
                    "order": 4,
                    "config": {
                        "platform": "kubernetes",
                        "replicas": 3,
                        "traffic_percentage": 100,
                    },
                    "retry_count": 2,
                },
            ],
        }
    
    @staticmethod
    def blue_green_deployment() -> Dict[str, Any]:
        """
        Blue-green deployment workflow.
        """
        return {
            "name": "Blue-Green Deployment",
            "workflow_type": WorkflowType.SEQUENTIAL,
            "description": "Zero-downtime deployment using blue-green strategy",
            "steps": [
                {
                    "name": "Build Application",
                    "step_type": "build",
                    "order": 0,
                    "config": {},
                    "retry_count": 2,
                },
                {
                    "name": "Run Tests",
                    "step_type": "test",
                    "order": 1,
                    "config": {"test_suite": "full"},
                    "retry_count": 1,
                },
                {
                    "name": "Deploy to Green Environment",
                    "step_type": "deploy",
                    "order": 2,
                    "config": {
                        "platform": "kubernetes",
                        "environment": "green",
                        "replicas": 3,
                    },
                    "retry_count": 2,
                },
                {
                    "name": "Verify Green Environment",
                    "step_type": "health_check",
                    "order": 3,
                    "config": {"environment": "green"},
                    "retry_count": 3,
                },
                {
                    "name": "Switch Traffic to Green",
                    "step_type": "deploy",
                    "order": 4,
                    "config": {
                        "action": "switch_traffic",
                        "from": "blue",
                        "to": "green",
                    },
                    "retry_count": 1,
                },
            ],
        }
    
    @staticmethod
    def rollback_workflow() -> Dict[str, Any]:
        """
        Rollback workflow to revert to previous version.
        """
        return {
            "name": "Rollback Deployment",
            "workflow_type": WorkflowType.ROLLBACK,
            "description": "Rollback to previous stable version",
            "steps": [
                {
                    "name": "Stop Current Deployment",
                    "step_type": "deploy",
                    "order": 0,
                    "config": {"action": "stop"},
                    "retry_count": 1,
                },
                {
                    "name": "Restore Previous Version",
                    "step_type": "deploy",
                    "order": 1,
                    "config": {"action": "rollback"},
                    "retry_count": 2,
                },
                {
                    "name": "Verify Rollback",
                    "step_type": "health_check",
                    "order": 2,
                    "config": {},
                    "retry_count": 3,
                },
            ],
        }
    
    @staticmethod
    def parallel_test_workflow() -> Dict[str, Any]:
        """
        Parallel testing workflow for faster execution.
        """
        return {
            "name": "Parallel Test Suite",
            "workflow_type": WorkflowType.PARALLEL,
            "description": "Run multiple test suites in parallel",
            "steps": [
                {
                    "name": "Unit Tests",
                    "step_type": "test",
                    "order": 0,
                    "config": {"test_suite": "unit"},
                    "retry_count": 1,
                },
                {
                    "name": "Integration Tests",
                    "step_type": "test",
                    "order": 0,
                    "config": {"test_suite": "integration"},
                    "retry_count": 1,
                },
                {
                    "name": "Security Scan",
                    "step_type": "test",
                    "order": 0,
                    "config": {"test_suite": "security"},
                    "retry_count": 0,
                },
                {
                    "name": "Performance Tests",
                    "step_type": "test",
                    "order": 0,
                    "config": {"test_suite": "performance"},
                    "retry_count": 1,
                },
            ],
        }
    
    @staticmethod
    def get_all_templates() -> Dict[str, Dict[str, Any]]:
        """Get all available workflow templates."""
        return {
            "standard": WorkflowTemplates.standard_deployment(),
            "canary": WorkflowTemplates.canary_deployment(),
            "blue_green": WorkflowTemplates.blue_green_deployment(),
            "rollback": WorkflowTemplates.rollback_workflow(),
            "parallel_test": WorkflowTemplates.parallel_test_workflow(),
        }
    
    @staticmethod
    def get_template(template_name: str) -> Dict[str, Any]:
        """
        Get a specific workflow template by name.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template configuration
            
        Raises:
            ValueError: If template not found
        """
        templates = WorkflowTemplates.get_all_templates()
        if template_name not in templates:
            raise ValueError(
                f"Template '{template_name}' not found. "
                f"Available templates: {', '.join(templates.keys())}"
            )
        return templates[template_name]

# Made with Bob

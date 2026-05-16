"""
Mock data generator for testing and development.
"""
import random
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from typing import List, Optional
from models.deployment import (
    Deployment,
    DeploymentState,
    DeploymentPlatform,
)
from models.workflow import (
    Workflow,
    WorkflowStep,
    WorkflowType,
    WorkflowStatus,
    StepStatus,
)


class MockDataGenerator:
    """Generate mock data for testing and development."""
    
    @staticmethod
    def generate_deployment(
        state: DeploymentState = DeploymentState.PENDING,
        platform: DeploymentPlatform = DeploymentPlatform.KUBERNETES
    ) -> Deployment:
        """Generate a mock deployment."""
        deployment_id = uuid4()
        
        return Deployment(
            id=deployment_id,
            name=f"deployment-{random.choice(['api', 'web', 'worker', 'service'])}-{random.randint(1, 100)}",
            version=f"{random.randint(1, 5)}.{random.randint(0, 20)}.{random.randint(0, 50)}",
            state=state,
            target_environment=random.choice(["development", "staging", "production"]),
            target_platform=platform,
            description=f"Deploy {random.choice(['new features', 'bug fixes', 'performance improvements', 'security updates'])}",
            metadata={
                "replicas": random.randint(2, 5),
                "namespace": random.choice(["default", "production", "staging"]),
                "image": f"myapp/service:{random.randint(1, 100)}",
                "resources": {
                    "cpu": f"{random.randint(1, 4)}",
                    "memory": f"{random.randint(1, 8)}Gi"
                }
            },
            rollback_version=f"{random.randint(1, 5)}.{random.randint(0, 20)}.{random.randint(0, 50)}" if random.choice([True, False]) else None,
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
            updated_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 60)),
            deployed_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 30)) if state == DeploymentState.DEPLOYED else None,
            created_by=random.choice(["alice@example.com", "bob@example.com", "charlie@example.com"]),
        )
    
    @staticmethod
    def generate_deployments(count: int = 10) -> List[Deployment]:
        """Generate multiple mock deployments."""
        states = list(DeploymentState)
        platforms = list(DeploymentPlatform)
        
        return [
            MockDataGenerator.generate_deployment(
                state=random.choice(states),
                platform=random.choice(platforms)
            )
            for _ in range(count)
        ]
    
    @staticmethod
    def generate_workflow(
        deployment_id: Optional[UUID] = None,
        workflow_type: WorkflowType = WorkflowType.SEQUENTIAL,
        status: WorkflowStatus = WorkflowStatus.PENDING
    ) -> Workflow:
        """Generate a mock workflow."""
        if deployment_id is None:
            deployment_id = uuid4()
        
        return Workflow(
            id=uuid4(),
            name=f"{workflow_type.value.title()} Deployment Workflow",
            workflow_type=workflow_type,
            deployment_id=deployment_id,
            status=status,
            current_step=random.randint(0, 3) if status == WorkflowStatus.RUNNING else 0,
            description=f"Automated {workflow_type.value} workflow for deployment",
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
            updated_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 60)),
            started_at=datetime.utcnow() - timedelta(minutes=random.randint(10, 120)) if status != WorkflowStatus.PENDING else None,
            completed_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 10)) if status == WorkflowStatus.COMPLETED else None,
        )
    
    @staticmethod
    def generate_workflow_steps(
        workflow_id: UUID,
        count: int = 4
    ) -> List[WorkflowStep]:
        """Generate mock workflow steps."""
        step_types = ["build", "test", "deploy", "health_check"]
        steps = []
        
        for i in range(count):
            step = WorkflowStep(
                id=uuid4(),
                workflow_id=workflow_id,
                name=f"{step_types[i % len(step_types)].title()} Step",
                description=f"Execute {step_types[i % len(step_types)]} phase",
                step_type=step_types[i % len(step_types)],
                order=i,
                status=random.choice(list(StepStatus)),
                config={
                    "timeout": random.randint(300, 900),
                    "retry_on_failure": True,
                },
                retry_count=random.randint(0, 2),
                timeout_seconds=random.randint(300, 900),
                started_at=datetime.utcnow() - timedelta(minutes=random.randint(5, 30)),
                completed_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 5)) if random.choice([True, False]) else None,
            )
            steps.append(step)
        
        return steps
    
    @staticmethod
    def generate_sample_data() -> dict:
        """Generate a complete set of sample data."""
        deployments = MockDataGenerator.generate_deployments(10)
        workflows = []
        workflow_steps = []
        
        for deployment in deployments[:5]:  # Create workflows for first 5 deployments
            workflow = MockDataGenerator.generate_workflow(
                deployment_id=deployment.id,
                workflow_type=random.choice(list(WorkflowType)),
                status=random.choice(list(WorkflowStatus))
            )
            workflows.append(workflow)
            
            steps = MockDataGenerator.generate_workflow_steps(
                workflow_id=workflow.id,
                count=random.randint(3, 5)
            )
            workflow_steps.extend(steps)
        
        return {
            "deployments": deployments,
            "workflows": workflows,
            "workflow_steps": workflow_steps,
        }

# Made with Bob

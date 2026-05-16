"""
Workflow models and schemas.
Defines workflow orchestration structures and execution states.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class WorkflowType(str, Enum):
    """Types of workflow execution patterns."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ROLLBACK = "rollback"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Individual step status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStepBase(BaseModel):
    """Base workflow step schema."""
    name: str = Field(..., description="Step name")
    description: Optional[str] = Field(None, description="Step description")
    step_type: str = Field(..., description="Type of step (build, test, deploy, etc.)")
    config: Dict[str, Any] = Field(default_factory=dict, description="Step configuration")
    retry_count: int = Field(default=0, ge=0, le=5, description="Number of retries on failure")
    timeout_seconds: int = Field(default=300, ge=1, description="Step timeout in seconds")


class WorkflowStep(WorkflowStepBase):
    """Full workflow step model."""
    id: UUID = Field(default_factory=uuid4)
    workflow_id: UUID
    order: int = Field(..., ge=0, description="Execution order")
    status: StepStatus = Field(default=StepStatus.PENDING)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output: Dict[str, Any] = Field(default_factory=dict, description="Step output data")
    
    class Config:
        from_attributes = True


class WorkflowBase(BaseModel):
    """Base workflow schema."""
    name: str = Field(..., min_length=1, max_length=255, description="Workflow name")
    workflow_type: WorkflowType = Field(default=WorkflowType.SEQUENTIAL)
    description: Optional[str] = Field(None, max_length=1000)


class WorkflowCreate(WorkflowBase):
    """Schema for creating a new workflow."""
    deployment_id: UUID = Field(..., description="Associated deployment ID")
    steps: List[WorkflowStepBase] = Field(..., min_length=1, description="Workflow steps")


class Workflow(WorkflowBase):
    """Full workflow model."""
    id: UUID = Field(default_factory=uuid4)
    deployment_id: UUID
    status: WorkflowStatus = Field(default=WorkflowStatus.PENDING)
    current_step: int = Field(default=0, ge=0, description="Current step index")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "Production Deployment Workflow",
                "workflow_type": "sequential",
                "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "running",
                "current_step": 2,
                "description": "Standard production deployment workflow",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:35:00Z",
                "started_at": "2024-01-15T10:31:00Z"
            }
        }


class WorkflowResponse(Workflow):
    """Response schema for workflow with steps."""
    steps: List[WorkflowStep] = Field(default_factory=list)
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    
    @classmethod
    def from_workflow(cls, workflow: Workflow, steps: List[WorkflowStep]) -> "WorkflowResponse":
        """Create response from workflow with steps and computed fields."""
        data = workflow.model_dump()
        
        # Calculate progress
        if steps:
            completed_steps = sum(1 for step in steps if step.status == StepStatus.COMPLETED)
            progress = (completed_steps / len(steps)) * 100
        else:
            progress = 0.0
        
        return cls(
            **data,
            steps=steps,
            progress_percentage=round(progress, 2)
        )


class WorkflowExecutionRequest(BaseModel):
    """Request to execute a workflow."""
    workflow_id: UUID
    force: bool = Field(default=False, description="Force execution even if already running")


class WorkflowActionResponse(BaseModel):
    """Response for workflow actions (pause, resume, cancel)."""
    workflow_id: UUID
    action: str
    status: WorkflowStatus
    message: str

# Made with Bob

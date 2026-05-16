"""
Deployment models and schemas.
Defines the deployment lifecycle states and data structures.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field


class DeploymentState(str, Enum):
    """Deployment lifecycle states."""
    PENDING = "pending"
    VALIDATING = "validating"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    MONITORING = "monitoring"


class DeploymentPlatform(str, Enum):
    """Supported deployment platforms."""
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    GENERIC = "generic"


class DeploymentBase(BaseModel):
    """Base deployment schema."""
    name: str = Field(..., min_length=1, max_length=255, description="Deployment name")
    version: str = Field(..., description="Version to deploy")
    target_environment: str = Field(..., description="Target environment (dev, staging, prod)")
    target_platform: DeploymentPlatform = Field(default=DeploymentPlatform.KUBERNETES)
    description: Optional[str] = Field(None, max_length=1000)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DeploymentCreate(DeploymentBase):
    """Schema for creating a new deployment."""
    rollback_version: Optional[str] = Field(None, description="Version to rollback to if needed")


class DeploymentUpdate(BaseModel):
    """Schema for updating a deployment."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[Dict[str, Any]] = None
    state: Optional[DeploymentState] = None


class Deployment(DeploymentBase):
    """Full deployment model with all fields."""
    id: UUID = Field(default_factory=uuid4)
    state: DeploymentState = Field(default=DeploymentState.PENDING)
    rollback_version: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deployed_at: Optional[datetime] = None
    created_by: Optional[str] = Field(None, description="User who created the deployment")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "api-service-v2",
                "version": "2.1.0",
                "state": "pending",
                "target_environment": "production",
                "target_platform": "kubernetes",
                "description": "Deploy new API service version",
                "metadata": {
                    "replicas": 3,
                    "namespace": "production",
                    "image": "myapp/api:2.1.0",
                },
                "rollback_version": "2.0.5",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        },
    )


class DeploymentResponse(Deployment):
    """Response schema for deployment with additional computed fields."""
    can_approve: bool = Field(default=False, description="Whether deployment can be approved")
    can_deploy: bool = Field(default=False, description="Whether deployment can be deployed")
    can_rollback: bool = Field(default=False, description="Whether deployment can be rolled back")
    
    @classmethod
    def from_deployment(cls, deployment: Deployment) -> "DeploymentResponse":
        """Create response from deployment with computed fields."""
        data = deployment.model_dump()
        
        # Compute action permissions based on state
        can_approve = deployment.state == DeploymentState.VALIDATING
        can_deploy = deployment.state == DeploymentState.APPROVED
        can_rollback = deployment.state in [
            DeploymentState.DEPLOYED,
            DeploymentState.FAILED,
            DeploymentState.MONITORING
        ]
        
        return cls(
            **data,
            can_approve=can_approve,
            can_deploy=can_deploy,
            can_rollback=can_rollback
        )


class DeploymentListResponse(BaseModel):
    """Paginated list of deployments."""
    items: list[DeploymentResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool

# Made with Bob

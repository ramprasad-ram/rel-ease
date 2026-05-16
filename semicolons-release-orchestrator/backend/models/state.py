"""
State transition models for audit trail and state machine tracking.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from .deployment import DeploymentState


class StateTransitionBase(BaseModel):
    """Base state transition schema."""
    from_state: DeploymentState = Field(..., description="Previous state")
    to_state: DeploymentState = Field(..., description="New state")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for transition")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class StateTransitionCreate(StateTransitionBase):
    """Schema for creating a state transition record."""
    deployment_id: UUID = Field(..., description="Associated deployment ID")
    triggered_by: Optional[str] = Field(None, description="User or system that triggered transition")


class StateTransition(StateTransitionBase):
    """Full state transition model."""
    id: UUID = Field(default_factory=uuid4)
    deployment_id: UUID
    triggered_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
                "from_state": "pending",
                "to_state": "validating",
                "reason": "Automatic validation triggered",
                "triggered_by": "system",
                "metadata": {
                    "validation_checks": ["security", "compliance", "dependencies"]
                },
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class StateTransitionHistory(BaseModel):
    """Response schema for state transition history."""
    deployment_id: UUID
    transitions: list[StateTransition]
    total_transitions: int

# Made with Bob

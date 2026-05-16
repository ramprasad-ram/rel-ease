"""
AI Agent models and schemas.
Defines agent types, analysis results, and recommendations.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Types of AI agents."""
    RELEASE_PLANNING = "release_planning"
    DEPLOYMENT_DECISION = "deployment_decision"
    ANOMALY_DETECTION = "anomaly_detection"
    ROLLBACK_RECOMMENDATION = "rollback_recommendation"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    SECURITY_SCAN = "security_scan"
    CICD_VALIDATION = "cicd_validation"
    ENVIRONMENT_MONITORING = "environment_monitoring"
    CHANGE_COMMUNICATION = "change_communication"
    POSTMORTEM = "postmortem"


class AnalysisStatus(str, Enum):
    """Status of agent analysis."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentRecommendation(BaseModel):
    """Individual recommendation from an agent."""
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    priority: RecommendationPriority = Field(default=RecommendationPriority.MEDIUM)
    action: Optional[str] = Field(None, description="Suggested action to take")
    impact: Optional[str] = Field(None, description="Expected impact")


class AgentAnalysisBase(BaseModel):
    """Base agent analysis schema."""
    agent_type: AgentType = Field(..., description="Type of agent")
    analysis_data: Dict[str, Any] = Field(default_factory=dict, description="Raw analysis data")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")


class AgentAnalysisCreate(AgentAnalysisBase):
    """Schema for creating an agent analysis."""
    deployment_id: UUID = Field(..., description="Associated deployment ID")
    recommendations: List[AgentRecommendation] = Field(default_factory=list)


class AgentAnalysis(AgentAnalysisBase):
    """Full agent analysis model."""
    id: UUID = Field(default_factory=uuid4)
    deployment_id: UUID
    status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    recommendations: List[AgentRecommendation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174003",
                "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
                "agent_type": "deployment_decision",
                "status": "completed",
                "confidence_score": 0.85,
                "analysis_data": {
                    "risk_score": 0.15,
                    "readiness_score": 0.92,
                    "dependencies_validated": True,
                    "security_checks_passed": True
                },
                "recommendations": [
                    {
                        "title": "Proceed with deployment",
                        "description": "All checks passed. Deployment is ready.",
                        "priority": "high",
                        "action": "approve_deployment",
                        "impact": "Low risk deployment"
                    }
                ],
                "created_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:30:15Z"
            }
        }


class AgentAnalysisRequest(BaseModel):
    """Request to trigger agent analysis."""
    deployment_id: UUID
    agent_types: List[AgentType] = Field(..., min_length=1, description="Agent types to run")
    force: bool = Field(default=False, description="Force re-analysis")


class AgentAnalysisResponse(BaseModel):
    """Response for agent analysis request."""
    deployment_id: UUID
    analyses: List[AgentAnalysis]
    overall_confidence: float = Field(ge=0.0, le=1.0)
    recommendation_summary: str


class AgentHealthCheck(BaseModel):
    """Health check response for AI agents."""
    agent_type: AgentType
    is_available: bool
    response_time_ms: float
    last_check: datetime

# Made with Bob

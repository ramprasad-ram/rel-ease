"""
API routes for release planning and analysis.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from agents.release_planning_agent import ReleasePlanningAgent
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ReleasePlanningRequest(BaseModel):
    """Request model for release planning analysis."""
    github_repo: str = Field(
        ...,
        description="GitHub repository in format 'owner/repo'"
    )
    jira_sprint: str = Field(
        ...,
        description="Jira sprint identifier"
    )
    github_token: Optional[str] = Field(
        None,
        description="Optional GitHub API token for private repos"
    )
    jira_token: Optional[str] = Field(
        None,
        description="Optional Jira API token"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "github_repo": "mycompany/api-service",
                "jira_sprint": "SPRINT-123"
            }]
        }
    }


class ReleasePlanningResponse(BaseModel):
    """Response model for release planning analysis."""
    readiness_score: float = Field(..., description="Release readiness score (0-100)")
    confidence_score: float = Field(..., description="Confidence in analysis (0-1)")
    jira_sprint: str
    github_repo: str
    ticket_analysis: Dict[str, Any]
    repo_health: Dict[str, Any]
    circular_dependencies: list
    issues: list[str]
    recommendations: list[Dict[str, Any]]
    dependency_graph: Dict[str, list]


@router.post(
    "/analyze",
    response_model=ReleasePlanningResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Release Readiness",
    description="""
    Analyze release readiness by examining Jira sprint tickets and GitHub repository health.
    
    This endpoint:
    - Fetches tickets from the specified Jira sprint
    - Analyzes GitHub repository metrics (build status, test coverage, etc.)
    - Detects circular dependencies between tickets
    - Calculates an overall release readiness score
    - Provides actionable recommendations
    
    Example issues detected:
    - "Task A is done, but Task B has a circular dependency"
    - "3 high-priority tickets are incomplete"
    - "Build is failing"
    """
)
async def analyze_release_readiness(
    request: ReleasePlanningRequest
) -> ReleasePlanningResponse:
    """
    Analyze release readiness for a GitHub repo and Jira sprint.
    
    Args:
        request: Release planning request with repo and sprint info
        
    Returns:
        Detailed analysis with readiness score and recommendations
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(
            f"Received release planning request: {request.github_repo} / {request.jira_sprint}"
        )
        
        # Initialize agent
        agent = ReleasePlanningAgent()
        
        # Perform analysis
        result = await agent.analyze_release_readiness(
            github_repo=request.github_repo,
            jira_sprint=request.jira_sprint,
            github_token=request.github_token,
            jira_token=request.jira_token
        )
        
        logger.info(
            f"Release planning analysis complete: readiness={result['readiness_score']}%"
        )
        
        return ReleasePlanningResponse(**result)
        
    except Exception as e:
        logger.error(f"Release planning analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="Release Planning Agent Health Check",
    description="Check if the release planning agent is operational"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check for release planning agent.
    
    Returns:
        Health status information
    """
    try:
        agent = ReleasePlanningAgent()
        return {
            "status": "healthy",
            "agent_type": "release_planning",
            "capabilities": [
                "jira_integration",
                "github_integration",
                "dependency_analysis",
                "circular_dependency_detection",
                "readiness_scoring"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Release planning agent is unavailable"
        )


# Made with Bob
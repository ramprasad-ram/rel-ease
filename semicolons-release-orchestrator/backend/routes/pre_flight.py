"""
API routes for pre-flight deployment validation.
"""
from fastapi import APIRouter, HTTPException, status, Path
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from uuid import UUID
from agents.cicd_validation_agent import CICDValidationAgent
from models.deployment import Deployment, DeploymentState, DeploymentPlatform
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class PreFlightValidationResponse(BaseModel):
    """Response model for pre-flight validation."""
    deployment_id: str
    validation_score: float = Field(..., description="Overall validation score (0-100)")
    confidence_score: float = Field(..., description="Confidence in analysis (0-1)")
    ci_runs_analyzed: int
    memory_analysis: Dict[str, Any]
    performance_analysis: Dict[str, Any]
    coverage_analysis: Dict[str, Any]
    build_analysis: Dict[str, Any]
    issues: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    ready_to_deploy: bool


class PreFlightQuickCheckResponse(BaseModel):
    """Quick check response for deployment readiness."""
    deployment_id: str
    ready_to_deploy: bool
    validation_score: float
    critical_issues_count: int
    warnings_count: int
    summary: str


@router.post(
    "/deployments/{deployment_id}/pre-flight-check",
    response_model=PreFlightValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Pre-Flight Validation",
    description="""
    Perform comprehensive pre-flight validation before deployment.
    
    This endpoint:
    - Analyzes the last 5 CI runs
    - Detects memory usage trends and potential leaks
    - Identifies performance regressions
    - Validates test coverage
    - Checks build stability
    - Provides actionable recommendations
    
    Example issues detected:
    - "Warning: Potential memory leak detected in module X"
    - "10% increase in memory usage detected"
    - "Performance regression: Response time increased by 15%"
    """
)
async def run_pre_flight_check(
    deployment_id: str = Path(..., description="Deployment ID to validate")
) -> PreFlightValidationResponse:
    """
    Run pre-flight validation for a deployment.
    
    Args:
        deployment_id: ID of the deployment to validate
        
    Returns:
        Detailed validation results with issues and recommendations
        
    Raises:
        HTTPException: If validation fails
    """
    try:
        logger.info(f"Starting pre-flight validation for deployment {deployment_id}")
        
        # Create a mock deployment for demo purposes
        # In production, this would fetch from database
        deployment = Deployment(
            name=f"deployment-{deployment_id}",
            version="2.1.0",
            target_environment="production",
            target_platform=DeploymentPlatform.KUBERNETES,
            description="Pre-flight validation check",
            state=DeploymentState.APPROVED,
            created_by="system",
        )
        
        # Initialize validation agent
        agent = CICDValidationAgent()
        
        # Perform validation
        result = await agent.analyze(deployment)
        
        # Extract analysis data
        analysis_data = result["analysis_data"]
        
        # Determine if ready to deploy
        validation_score = analysis_data["validation_score"]
        critical_issues = [
            issue for issue in analysis_data["issues"]
            if issue.get("severity") == "critical"
        ]
        ready_to_deploy = validation_score >= 70 and len(critical_issues) == 0
        
        logger.info(
            f"Pre-flight validation complete: score={validation_score}%, "
            f"ready={ready_to_deploy}, issues={len(analysis_data['issues'])}"
        )
        
        return PreFlightValidationResponse(
            deployment_id=deployment_id,
            validation_score=validation_score,
            confidence_score=result["confidence_score"],
            ci_runs_analyzed=analysis_data["ci_runs_analyzed"],
            memory_analysis=analysis_data["memory_analysis"],
            performance_analysis=analysis_data["performance_analysis"],
            coverage_analysis=analysis_data["coverage_analysis"],
            build_analysis=analysis_data["build_analysis"],
            issues=analysis_data["issues"],
            recommendations=result["recommendations"],
            ready_to_deploy=ready_to_deploy,
        )
        
    except Exception as e:
        logger.error(f"Pre-flight validation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.get(
    "/deployments/{deployment_id}/pre-flight-quick-check",
    response_model=PreFlightQuickCheckResponse,
    summary="Quick Pre-Flight Check",
    description="Get a quick summary of deployment readiness without full analysis"
)
async def quick_pre_flight_check(
    deployment_id: str = Path(..., description="Deployment ID to check")
) -> PreFlightQuickCheckResponse:
    """
    Perform a quick pre-flight check.
    
    Args:
        deployment_id: ID of the deployment to check
        
    Returns:
        Quick summary of deployment readiness
    """
    try:
        # Run full validation
        full_result = await run_pre_flight_check(deployment_id)
        
        # Count issues by severity
        critical_count = sum(
            1 for issue in full_result.issues
            if issue.get("severity") == "critical"
        )
        warning_count = sum(
            1 for issue in full_result.issues
            if issue.get("severity") == "warning"
        )
        
        # Generate summary
        if full_result.ready_to_deploy:
            summary = f"✅ Ready to deploy (Score: {full_result.validation_score}%)"
        elif critical_count > 0:
            summary = f"❌ Not ready: {critical_count} critical issue(s) found"
        else:
            summary = f"⚠️ Proceed with caution: {warning_count} warning(s) found"
        
        return PreFlightQuickCheckResponse(
            deployment_id=deployment_id,
            ready_to_deploy=full_result.ready_to_deploy,
            validation_score=full_result.validation_score,
            critical_issues_count=critical_count,
            warnings_count=warning_count,
            summary=summary,
        )
        
    except Exception as e:
        logger.error(f"Quick pre-flight check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick check failed: {str(e)}"
        )


@router.get(
    "/pre-flight/health",
    summary="Pre-Flight Validation Health Check",
    description="Check if the pre-flight validation service is operational"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check for pre-flight validation service.
    
    Returns:
        Health status information
    """
    try:
        agent = CICDValidationAgent()
        return {
            "status": "healthy",
            "agent_type": "cicd_validation",
            "capabilities": [
                "ci_run_analysis",
                "memory_leak_detection",
                "performance_regression_detection",
                "test_coverage_validation",
                "build_stability_analysis"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pre-flight validation service is unavailable"
        )


# Made with Bob
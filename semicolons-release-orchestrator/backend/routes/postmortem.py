"""
Post-Mortem Analysis API Routes.
Endpoints for triggering and retrieving post-mortem analysis.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from agents.postmortem_agent import PostmortemAgent
from models.deployment import Deployment, DeploymentState, DeploymentPlatform
from utils.logger import get_logger
from config import settings

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/postmortem", tags=["postmortem"])

# Initialize post-mortem agent
postmortem_agent = PostmortemAgent(
    slack_webhook_url=settings.slack_webhook_url if settings.slack_enabled else None
)

# Store analysis results (in production, use database)
analysis_results: Dict[str, Dict[str, Any]] = {}


class PostmortemRequest(BaseModel):
    """Request to trigger post-mortem analysis."""
    deployment_id: UUID = Field(..., description="Deployment ID to analyze")
    name: str = Field(..., description="Service name")
    version: str = Field(..., description="Failed version")
    rollback_version: Optional[str] = Field(None, description="Version rolled back to")
    target_environment: str = Field(default="production", description="Target environment")
    target_platform: DeploymentPlatform = Field(default=DeploymentPlatform.KUBERNETES, description="Target platform")


class PostmortemResponse(BaseModel):
    """Response for post-mortem analysis."""
    success: bool
    message: str
    deployment_id: str
    analysis: Optional[Dict[str, Any]] = None


@router.post("/analyze", response_model=PostmortemResponse)
async def trigger_postmortem_analysis(
    request: PostmortemRequest,
    background_tasks: BackgroundTasks
) -> PostmortemResponse:
    """
    Trigger post-mortem analysis for a failed deployment.
    
    This endpoint analyzes logs, code diffs, and error patterns to identify
    the root cause of a deployment failure and provide actionable recommendations.
    """
    try:
        deployment_id = str(request.deployment_id)
        
        logger.info(f"Triggering post-mortem analysis for deployment {deployment_id}")
        
        # Create deployment object
        deployment = Deployment(
            id=request.deployment_id,
            name=request.name,
            version=request.version,
            rollback_version=request.rollback_version,
            target_environment=request.target_environment,
            target_platform=request.target_platform,
            state=DeploymentState.ROLLED_BACK,
            description=f"Post-mortem analysis for {request.name}",
            created_by="postmortem_agent"
        )
        
        # Perform analysis
        analysis = await postmortem_agent.analyze(deployment)
        
        # Generate recommendations
        recommendations = await postmortem_agent.generate_recommendations(
            deployment,
            analysis
        )
        analysis["recommendations"] = recommendations
        
        # Store results
        analysis_results[deployment_id] = analysis
        
        # Send Slack notification in background
        if settings.slack_enabled:
            background_tasks.add_task(
                postmortem_agent.send_postmortem_notification,
                analysis
            )
        
        logger.info(
            f"Post-mortem analysis complete for {request.name}: "
            f"Root cause: {analysis['root_cause'].get('type', 'unknown')}"
        )
        
        return PostmortemResponse(
            success=True,
            message=f"Post-mortem analysis completed for {request.name}",
            deployment_id=deployment_id,
            analysis=analysis
        )
    
    except Exception as e:
        logger.error(f"Error during post-mortem analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Post-mortem analysis failed: {str(e)}"
        )


@router.get("/report/{deployment_id}")
async def get_postmortem_report(deployment_id: str) -> Dict[str, Any]:
    """
    Get post-mortem analysis report for a deployment.
    
    Returns the complete analysis including root cause, recommendations,
    and detailed findings.
    """
    if deployment_id not in analysis_results:
        raise HTTPException(
            status_code=404,
            detail=f"No post-mortem analysis found for deployment {deployment_id}"
        )
    
    analysis = analysis_results[deployment_id]
    
    # Generate formatted report
    report_text = await postmortem_agent.generate_report(analysis)
    
    return {
        "deployment_id": deployment_id,
        "service_name": analysis["service_name"],
        "failed_version": analysis["failed_version"],
        "rollback_version": analysis.get("rollback_version"),
        "analyzed_at": analysis["analyzed_at"],
        "root_cause": analysis["root_cause"],
        "recommendations": analysis["recommendations"],
        "report": report_text,
        "confidence_score": analysis["confidence_score"]
    }


@router.get("/summary/{deployment_id}")
async def get_postmortem_summary(deployment_id: str) -> Dict[str, Any]:
    """
    Get a brief summary of post-mortem analysis.
    
    Returns only the key findings without detailed logs and diffs.
    """
    if deployment_id not in analysis_results:
        raise HTTPException(
            status_code=404,
            detail=f"No post-mortem analysis found for deployment {deployment_id}"
        )
    
    analysis = analysis_results[deployment_id]
    root_cause = analysis["root_cause"]
    
    return {
        "deployment_id": deployment_id,
        "service_name": analysis["service_name"],
        "root_cause_type": root_cause.get("type"),
        "root_cause_description": root_cause.get("description"),
        "confidence": root_cause.get("confidence"),
        "suggested_fix": root_cause.get("suggested_fix"),
        "file": root_cause.get("file"),
        "line": root_cause.get("line"),
        "recommendation_count": len(analysis.get("recommendations", []))
    }


@router.get("/list")
async def list_postmortem_analyses() -> Dict[str, Any]:
    """
    List all post-mortem analyses.
    
    Returns a summary of all analyses performed.
    """
    analyses = []
    
    for deployment_id, analysis in analysis_results.items():
        root_cause = analysis.get("root_cause", {})
        analyses.append({
            "deployment_id": deployment_id,
            "service_name": analysis["service_name"],
            "failed_version": analysis["failed_version"],
            "analyzed_at": analysis["analyzed_at"],
            "root_cause_type": root_cause.get("type"),
            "confidence": root_cause.get("confidence"),
            "has_fix": bool(root_cause.get("suggested_fix"))
        })
    
    return {
        "total_analyses": len(analyses),
        "analyses": analyses
    }


@router.delete("/clear/{deployment_id}")
async def clear_postmortem_analysis(deployment_id: str) -> Dict[str, Any]:
    """
    Clear post-mortem analysis for a deployment.
    
    Removes the analysis from memory.
    """
    if deployment_id not in analysis_results:
        raise HTTPException(
            status_code=404,
            detail=f"No post-mortem analysis found for deployment {deployment_id}"
        )
    
    del analysis_results[deployment_id]
    
    return {
        "success": True,
        "message": f"Post-mortem analysis cleared for deployment {deployment_id}"
    }


@router.post("/demo")
async def run_postmortem_demo(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Run a demo post-mortem analysis with simulated data.
    
    This demonstrates the post-mortem agent's capabilities with a
    realistic failure scenario.
    """
    # Create demo deployment
    demo_deployment_id = UUID("123e4567-e89b-12d3-a456-426614174999")
    
    demo_request = PostmortemRequest(
        deployment_id=demo_deployment_id,
        name="Auth-Service",
        version="1.0.3",
        rollback_version="1.0.2",
        target_environment="production",
        target_platform=DeploymentPlatform.KUBERNETES
    )
    
    # Trigger analysis
    result = await trigger_postmortem_analysis(demo_request, background_tasks)
    
    return {
        "message": "Demo post-mortem analysis completed",
        "deployment_id": str(demo_deployment_id),
        "view_report": f"/api/v1/postmortem/report/{demo_deployment_id}",
        "view_summary": f"/api/v1/postmortem/summary/{demo_deployment_id}",
        "analysis": result.analysis
    }


# Made with Bob
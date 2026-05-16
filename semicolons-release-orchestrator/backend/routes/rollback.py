"""
Rollback API routes.
Handles automatic rollback operations and error injection for demos.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
import logging

from models.deployment import Deployment, DeploymentState, DeploymentPlatform
from agents.rollback_agent import RollbackAgent
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rollback", tags=["rollback"])

# Global rollback agent instance
rollback_agent: Optional[RollbackAgent] = None


def get_rollback_agent() -> RollbackAgent:
    """Get or create the rollback agent instance."""
    global rollback_agent
    if rollback_agent is None:
        slack_webhook = getattr(settings, 'slack_webhook_url', None)
        rollback_agent = RollbackAgent(slack_webhook_url=slack_webhook)
    return rollback_agent


class StartMonitoringRequest(BaseModel):
    """Request to start monitoring a deployment."""
    deployment_id: UUID
    name: str
    version: str
    rollback_version: Optional[str] = None
    target_environment: str = "production"
    target_platform: DeploymentPlatform = DeploymentPlatform.KUBERNETES


class InjectErrorRequest(BaseModel):
    """Request to inject errors for testing."""
    deployment_id: UUID
    error_count: int = Field(default=100, ge=1, le=1000, description="Number of errors to inject")
    error_type: str = Field(default="5xx", description="Type of error (5xx, 4xx, critical)")


class RollbackResponse(BaseModel):
    """Response for rollback operations."""
    success: bool
    message: str
    deployment_id: str
    details: Optional[Dict[str, Any]] = None


@router.post("/start-monitoring", response_model=RollbackResponse)
async def start_monitoring(
    request: StartMonitoringRequest,
    background_tasks: BackgroundTasks
) -> RollbackResponse:
    """
    Start monitoring a deployment for errors.
    
    The Rollback Agent will continuously monitor the deployment and
    automatically trigger a rollback if critical errors are detected.
    """
    try:
        agent = get_rollback_agent()
        
        # Create a deployment object for monitoring
        deployment = Deployment(
            id=request.deployment_id,
            name=request.name,
            version=request.version,
            rollback_version=request.rollback_version,
            state=DeploymentState.DEPLOYED,
            target_environment=request.target_environment,
            target_platform=request.target_platform,
            description=f"Monitoring deployment {request.name} v{request.version}",
            created_by="rollback-agent"
        )
        
        # Start monitoring in background
        background_tasks.add_task(agent.start_monitoring, deployment)
        
        logger.info(f"Started monitoring deployment {request.deployment_id}")
        
        return RollbackResponse(
            success=True,
            message=f"Started monitoring {request.name} v{request.version}",
            deployment_id=str(request.deployment_id),
            details={
                "service": request.name,
                "version": request.version,
                "rollback_version": request.rollback_version,
                "error_threshold": f"{agent.ERROR_RATE_THRESHOLD:.1%}",
                "critical_threshold": f"{agent.CRITICAL_ERROR_RATE:.1%}"
            }
        )
    
    except Exception as e:
        logger.error(f"Failed to start monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop-monitoring/{deployment_id}", response_model=RollbackResponse)
async def stop_monitoring(deployment_id: UUID) -> RollbackResponse:
    """
    Stop monitoring a deployment.
    """
    try:
        agent = get_rollback_agent()
        await agent.stop_monitoring(str(deployment_id))
        
        return RollbackResponse(
            success=True,
            message=f"Stopped monitoring deployment",
            deployment_id=str(deployment_id)
        )
    
    except Exception as e:
        logger.error(f"Failed to stop monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inject-errors", response_model=RollbackResponse)
async def inject_errors(request: InjectErrorRequest) -> RollbackResponse:
    """
    Inject errors into a monitored deployment for testing/demo purposes.
    
    This endpoint simulates error spikes to demonstrate the automatic
    rollback functionality. Use this to trigger the "Wow Moment" demo.
    
    Example:
    ```
    POST /rollback/inject-errors
    {
        "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
        "error_count": 150,
        "error_type": "5xx"
    }
    ```
    """
    try:
        agent = get_rollback_agent()
        
        success = agent.inject_error(
            deployment_id=str(request.deployment_id),
            error_count=request.error_count,
            error_type=request.error_type
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Deployment {request.deployment_id} is not being monitored"
            )
        
        # Get current metrics
        metrics = agent._get_deployment_metrics(str(request.deployment_id))
        error_rate = metrics["error_count"] / metrics["total_requests"] if metrics["total_requests"] > 0 else 0
        
        logger.info(
            f"Injected {request.error_count} {request.error_type} errors. "
            f"New error rate: {error_rate:.1%}"
        )
        
        return RollbackResponse(
            success=True,
            message=f"Injected {request.error_count} {request.error_type} errors",
            deployment_id=str(request.deployment_id),
            details={
                "error_count": request.error_count,
                "error_type": request.error_type,
                "total_requests": metrics["total_requests"],
                "total_errors": metrics["error_count"],
                "error_rate": f"{error_rate:.1%}",
                "will_trigger_rollback": error_rate > agent.CRITICAL_ERROR_RATE
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to inject errors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{deployment_id}")
async def get_monitoring_status(deployment_id: UUID) -> Dict[str, Any]:
    """
    Get the current monitoring status for a deployment.
    """
    try:
        agent = get_rollback_agent()
        deployment_id_str = str(deployment_id)
        
        if deployment_id_str not in agent.active_deployments:
            raise HTTPException(
                status_code=404,
                detail=f"Deployment {deployment_id} is not being monitored"
            )
        
        metrics = agent._get_deployment_metrics(deployment_id_str)
        deployment_data = agent.active_deployments[deployment_id_str]
        
        error_rate = metrics["error_count"] / metrics["total_requests"] if metrics["total_requests"] > 0 else 0
        
        return {
            "deployment_id": deployment_id_str,
            "service_name": deployment_data["deployment"].name,
            "version": deployment_data["deployment"].version,
            "rollback_version": deployment_data["deployment"].rollback_version,
            "monitoring_since": deployment_data["start_time"].isoformat(),
            "metrics": {
                "total_requests": metrics["total_requests"],
                "error_count": metrics["error_count"],
                "error_rate": f"{error_rate:.1%}",
                "error_types": metrics["error_types"]
            },
            "thresholds": {
                "warning": f"{agent.ERROR_RATE_THRESHOLD:.1%}",
                "critical": f"{agent.CRITICAL_ERROR_RATE:.1%}"
            },
            "status": {
                "exceeds_warning": error_rate > agent.ERROR_RATE_THRESHOLD,
                "exceeds_critical": error_rate > agent.CRITICAL_ERROR_RATE,
                "rollback_triggered": deployment_data["rollback_triggered"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get monitoring status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-monitors")
async def get_active_monitors() -> Dict[str, Any]:
    """
    Get all active monitoring sessions.
    """
    try:
        agent = get_rollback_agent()
        
        monitors = []
        for deployment_id, data in agent.active_deployments.items():
            deployment = data["deployment"]
            metrics = agent._get_deployment_metrics(deployment_id)
            error_rate = metrics["error_count"] / metrics["total_requests"] if metrics["total_requests"] > 0 else 0
            
            monitors.append({
                "deployment_id": deployment_id,
                "service_name": deployment.name,
                "version": deployment.version,
                "error_rate": f"{error_rate:.1%}",
                "rollback_triggered": data["rollback_triggered"]
            })
        
        return {
            "active_monitors": len(monitors),
            "monitors": monitors
        }
    
    except Exception as e:
        logger.error(f"Failed to get active monitors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob

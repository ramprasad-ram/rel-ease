"""
API routes for canary deployment execution with real-time updates.
"""
import asyncio
from fastapi import APIRouter, HTTPException, status, Path
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import json
from services.canary_controller import CanaryController, CanaryStatus
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Global canary controller instance
canary_controller = CanaryController()


class CanaryDeploymentRequest(BaseModel):
    """Request model for canary deployment."""
    version: str = Field(..., description="Version to deploy")
    environment: str = Field(default="production", description="Target environment")
    canary_replicas: int = Field(default=1, description="Number of canary replicas")
    stable_replicas: int = Field(default=3, description="Number of stable replicas")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "version": "2.1.0",
                "environment": "production",
                "canary_replicas": 1,
                "stable_replicas": 3
            }]
        }
    }


class CanaryDeploymentResponse(BaseModel):
    """Response model for canary deployment."""
    deployment_id: str
    status: str
    message: str
    stream_url: str


class CanaryStatusResponse(BaseModel):
    """Response model for canary status."""
    deployment_id: str
    status: str
    stage: str
    traffic_percentage: int
    current_metrics: Dict[str, Any]
    stage_history: list
    health_checks: list


@router.post(
    "/deployments/{deployment_id}/execute-canary",
    response_model=CanaryDeploymentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Execute Canary Deployment",
    description="""
    Execute a canary deployment with progressive traffic shifting.
    
    This endpoint:
    - Deploys canary version alongside stable version
    - Progressively shifts traffic: 10% → 25% → 50% → 100%
    - Monitors health at each stage
    - Automatically rolls back on failure
    - Provides real-time updates via Server-Sent Events
    
    Traffic Shifting Stages:
    1. Deploy canary pods
    2. Shift 10% traffic, monitor for 10 seconds
    3. Shift 25% traffic, monitor for 10 seconds
    4. Shift 50% traffic, monitor for 10 seconds
    5. Shift 100% traffic, complete deployment
    
    Use the stream_url to get real-time updates.
    """
)
async def execute_canary_deployment(
    deployment_id: str,
    request: CanaryDeploymentRequest
) -> CanaryDeploymentResponse:
    """
    Execute a canary deployment.
    
    Args:
        deployment_id: Unique deployment identifier
        request: Deployment configuration
        
    Returns:
        Deployment initiation response with stream URL
    """
    try:
        logger.info(f"Initiating canary deployment {deployment_id}")
        
        # Start deployment in background
        config = {
            "canary_replicas": request.canary_replicas,
            "stable_replicas": request.stable_replicas,
        }
        
        # Start async deployment (fire and forget)
        asyncio.create_task(
            canary_controller.execute_canary_deployment(
                deployment_id=deployment_id,
                version=request.version,
                environment=request.environment,
                config=config,
            )
        )
        
        return CanaryDeploymentResponse(
            deployment_id=deployment_id,
            status="initiated",
            message=f"Canary deployment initiated for version {request.version}",
            stream_url=f"/api/v1/canary/deployments/{deployment_id}/stream"
        )
        
    except Exception as e:
        logger.error(f"Failed to initiate canary deployment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate deployment: {str(e)}"
        )


@router.get(
    "/deployments/{deployment_id}/stream",
    summary="Stream Canary Deployment Progress",
    description="Get real-time updates for canary deployment via Server-Sent Events (SSE)"
)
async def stream_canary_progress(
    deployment_id: str = Path(..., description="Deployment ID")
):
    """
    Stream real-time canary deployment progress.
    
    Args:
        deployment_id: Deployment ID to monitor
        
    Returns:
        Server-Sent Events stream with deployment updates
    """
    async def event_generator():
        """Generate Server-Sent Events for deployment progress."""
        try:
            logger.info(f"Starting SSE stream for deployment {deployment_id}")
            
            # Wait for deployment to start
            max_wait = 30  # seconds
            waited = 0
            status_data = None
            while waited < max_wait:
                status_data = canary_controller.get_deployment_status(deployment_id)
                if status_data:
                    break
                await asyncio.sleep(0.5)
                waited += 0.5
            
            if status_data is None:
                yield f"data: {json.dumps({'error': 'Deployment not found'})}\n\n"
                return
            
            # Send initial status
            yield f"data: {json.dumps({'event': 'connected', 'deployment_id': deployment_id})}\n\n"
            
            # Stream updates until deployment completes
            last_stage = None
            last_traffic = 0
            
            while True:
                status_data = canary_controller.get_deployment_status(deployment_id)
                
                if not status_data:
                    break
                
                # Send stage updates
                current_stage = status_data.get("stage")
                if current_stage != last_stage:
                    yield f"data: {json.dumps({'event': 'stage_changed', 'stage': current_stage, 'timestamp': status_data.get('started_at')})}\n\n"
                    last_stage = current_stage
                
                # Send traffic updates
                current_traffic = status_data.get("traffic_percentage", 0)
                if current_traffic != last_traffic:
                    yield f"data: {json.dumps({'event': 'traffic_shifted', 'traffic_percentage': current_traffic})}\n\n"
                    last_traffic = current_traffic
                
                # Send metrics updates
                if status_data.get("current_metrics"):
                    yield f"data: {json.dumps({'event': 'metrics_update', 'metrics': status_data['current_metrics']})}\n\n"
                
                # Check if deployment is complete
                deployment_status = status_data.get("status")
                if deployment_status in [CanaryStatus.COMPLETED, CanaryStatus.FAILED, CanaryStatus.ROLLED_BACK]:
                    yield f"data: {json.dumps({'event': 'deployment_complete', 'status': deployment_status, 'final_traffic': current_traffic})}\n\n"
                    break
                
                await asyncio.sleep(1)  # Update every second
            
            logger.info(f"SSE stream ended for deployment {deployment_id}")
            
        except Exception as e:
            logger.error(f"Error in SSE stream: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get(
    "/deployments/{deployment_id}/status",
    response_model=CanaryStatusResponse,
    summary="Get Canary Deployment Status",
    description="Get current status of a canary deployment"
)
async def get_canary_status(
    deployment_id: str = Path(..., description="Deployment ID")
) -> CanaryStatusResponse:
    """
    Get current canary deployment status.
    
    Args:
        deployment_id: Deployment ID
        
    Returns:
        Current deployment status
    """
    status_data = canary_controller.get_deployment_status(deployment_id)
    
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found"
        )
    
    return CanaryStatusResponse(
        deployment_id=deployment_id,
        status=status_data.get("status", "unknown"),
        stage=status_data.get("stage", "unknown"),
        traffic_percentage=status_data.get("traffic_percentage", 0),
        current_metrics=status_data.get("current_metrics", {}),
        stage_history=status_data.get("stage_history", []),
        health_checks=status_data.get("health_checks", []),
    )


@router.get(
    "/deployments",
    summary="List All Canary Deployments",
    description="Get list of all active canary deployments"
)
async def list_canary_deployments() -> Dict[str, Any]:
    """
    List all canary deployments.
    
    Returns:
        Dictionary of all deployments
    """
    deployments = canary_controller.get_all_deployments()
    return {
        "total": len(deployments),
        "deployments": deployments
    }


@router.get(
    "/health",
    summary="Canary Deployment Service Health",
    description="Check if the canary deployment service is operational"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check for canary deployment service.
    
    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "service": "canary_deployment",
        "capabilities": [
            "progressive_traffic_shifting",
            "real_time_monitoring",
            "automatic_rollback",
            "health_checks",
            "sse_streaming"
        ],
        "active_deployments": len(canary_controller.get_all_deployments())
    }


# Made with Bob
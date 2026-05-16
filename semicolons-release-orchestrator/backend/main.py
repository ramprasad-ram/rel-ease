"""
FastAPI application entry point for the Release Orchestration Platform.

This is a scalable backend starter project with:
- Modular architecture
- Deployment lifecycle management
- Workflow orchestration
- Mock CI/CD simulation
- AI agent support
- Rollback capabilities
"""
from fastapi.applications import FastAPI


from typing import Any, AsyncGenerator


from logging import Logger


from contextlib import asynccontextmanager
from statistics import mean
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from mock_data.fixtures import MockDataGenerator
from models.deployment import DeploymentState
from models.workflow import StepStatus, WorkflowStatus
from utils.database import init_db, close_db
from utils.logger import setup_logging, get_logger

# Import routes
from routes import release_planning, pre_flight, canary_deployment, rollback, postmortem

logger: Logger = get_logger(name=__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(msg="Starting Release Orchestration Platform...")
    setup_logging()
    
    # Initialize database
    logger.info(msg="Initializing database...")
    await init_db()
    logger.info(msg="Database initialized successfully")
    
    logger.info(f"Application started: {settings.app_name} v{settings.app_version}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Release Orchestration Platform...")
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI application
app: FastAPI = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## AI-Powered Release Orchestration Platform
    
    A scalable backend for managing deployment lifecycles with intelligent automation.
    
    ### Features
    
    * **Deployment Management**: Create, track, and manage deployments
    * **State Machine**: Robust deployment lifecycle with validation
    * **Workflow Orchestration**: Sequential, parallel, and conditional workflows
    * **Mock CI/CD**: Simulated build, test, and deployment pipelines
    * **AI Agents**: Intelligent deployment analysis and recommendations
    * **Rollback Support**: Safe rollback to previous versions
    * **Real-time Monitoring**: Track deployment progress and health
    
    ### Architecture
    
    - Clean architecture with separation of concerns
    - Async/await for high performance
    - Modular and extensible design
    - Production-ready with proper error handling
    
    ### Getting Started
    
    1. Create a deployment: `POST /api/v1/deployments`
    2. Trigger AI analysis: `POST /api/v1/agents/analyze`
    3. Approve deployment: `POST /api/v1/deployments/{id}/approve`
    4. Execute workflow: `POST /api/v1/workflows/{id}/execute`

    5. Monitor progress: `GET /api/v1/deployments/{id}`
    6. Test Statement
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(release_planning.router, prefix=settings.api_v1_prefix)
app.include_router(pre_flight.router, prefix=settings.api_v1_prefix)
app.include_router(canary_deployment.router, prefix=settings.api_v1_prefix)
app.include_router(rollback.router, prefix=settings.api_v1_prefix)
app.include_router(postmortem.router, prefix=settings.api_v1_prefix)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
        "api": settings.api_v1_prefix,
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": "development" if settings.debug else "production",
    }


# API version info
@app.get(f"{settings.api_v1_prefix}/", tags=["API Info"])
async def api_info():
    """
    API version information.
    """
    return {
        "version": "v1",
        "endpoints": {
            "deployments": f"{settings.api_v1_prefix}/deployments",
            "workflows": f"{settings.api_v1_prefix}/workflows",
            "agents": f"{settings.api_v1_prefix}/agents",
            "rollbacks": f"{settings.api_v1_prefix}/deployments/{{id}}/rollback",
            "postmortem": f"{settings.api_v1_prefix}/postmortem",
        },
        "features": [
            "Deployment lifecycle management",
            "Workflow orchestration",
            "AI-powered analysis",
            "Mock CI/CD simulation",
            "Rollback support",
            "Post-mortem analysis",
        ],
    }


@app.get(f"{settings.api_v1_prefix}/demo/dashboard", tags=["Demo"])
async def demo_dashboard():
    """
    Hackathon/demo endpoint that returns a full orchestration dashboard payload.
    """
    sample: dict[Any, Any] = MockDataGenerator.generate_sample_data()
    deployments = sample["deployments"]
    workflows = sample["workflows"]
    workflow_steps = sample["workflow_steps"]

    total_deployments: int = len(deployments)
    deployment_state_counts: dict[str, int] = {
        state.value: sum(1 for deployment in deployments if deployment.state == state)
        for state in DeploymentState
    }
    workflow_status_counts: dict[str, int] = {
        status.value: sum(1 for workflow in workflows if workflow.status == status)
        for status in WorkflowStatus
    }

    completed_steps = sum(1 for step in workflow_steps if step.status == StepStatus.COMPLETED)
    total_steps = len(workflow_steps)
    progress_percentage = round((completed_steps / total_steps) * 100, 2) if total_steps else 0.0

    release_confidence = round(
        min(
            96,
            45
            + deployment_state_counts.get("approved", 0) * 6
            + deployment_state_counts.get("deployed", 0) * 5
            + workflow_status_counts.get("completed", 0) * 4
            - deployment_state_counts.get("failed", 0) * 7
            - workflow_status_counts.get("failed", 0) * 6,
        ),
        2,
    )

    healthy_ratio = round(
        (
            deployment_state_counts.get("approved", 0)
            + deployment_state_counts.get("deployed", 0)
            + deployment_state_counts.get("monitoring", 0)
        )
        / total_deployments
        * 100,
        2,
    ) if total_deployments else 0.0

    lead_times = [
        round((deployment.updated_at - deployment.created_at).total_seconds() / 3600, 1)
        for deployment in deployments
    ]

    latest_deployments = sorted(
        deployments,
        key=lambda deployment: deployment.updated_at,
        reverse=True,
    )[:5]

    latest_workflows = sorted(
        workflows,
        key=lambda workflow: workflow.updated_at,
        reverse=True,
    )[:4]

    agent_cards = [
        {
            "name": "Release Planning Agent",
            "status": "ready",
            "summary": "Analyzes sprint scope, dependencies, and blockers for release planning.",
        },
        {
            "name": "CI/CD Validation Agent",
            "status": "running" if workflow_status_counts.get("running", 0) else "ready",
            "summary": "Validates builds, tests, and security gates before promotion.",
        },
        {
            "name": "Environment Monitoring Agent",
            "status": "watching",
            "summary": "Monitors infrastructure health, config drift, and compatibility.",
        },
        {
            "name": "Deployment Agent",
            "status": "scheduled" if deployment_state_counts.get("approved", 0) else "standby",
            "summary": "Executes blue-green, rolling, and canary deployments.",
        },
        {
            "name": "Rollback Agent",
            "status": "standby",
            "summary": "Triggers rollback automatically when post-release anomalies spike.",
        },
        {
            "name": "Change Communication Agent",
            "status": "ready",
            "summary": "Generates release notes and stakeholder notifications.",
        },
        {
            "name": "Postmortem Agent",
            "status": "learning",
            "summary": "Analyzes failed releases and recommends process improvements.",
        },
    ]

    return {
        "platform": {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "operational",
        },
        "summary": {
            "release_confidence": release_confidence,
            "healthy_release_ratio": healthy_ratio,
            "workflow_progress": progress_percentage,
            "active_deployments": deployment_state_counts.get("deploying", 0)
            + deployment_state_counts.get("monitoring", 0),
            "avg_lead_time_hours": round(mean(lead_times), 1) if lead_times else 0.0,
        },
        "deployment_state_counts": deployment_state_counts,
        "workflow_status_counts": workflow_status_counts,
        "latest_deployments": [
            {
                "id": str(deployment.id),
                "name": deployment.name,
                "version": deployment.version,
                "state": deployment.state.value,
                "environment": deployment.target_environment,
                "platform": deployment.target_platform.value,
                "updated_at": deployment.updated_at.isoformat(),
            }
            for deployment in latest_deployments
        ],
        "latest_workflows": [
            {
                "id": str(workflow.id),
                "name": workflow.name,
                "type": workflow.workflow_type.value,
                "status": workflow.status.value,
                "current_step": workflow.current_step,
                "updated_at": workflow.updated_at.isoformat(),
            }
            for workflow in latest_workflows
        ],
        "agent_cards": agent_cards,
        "timeline": [
            {"phase": "Plan", "detail": "Map Jira scope, risks, and dependencies"},
            {"phase": "Validate", "detail": "Confirm CI/CD, test, and scan readiness"},
            {"phase": "Monitor", "detail": "Check infra health and config drift"},
            {"phase": "Deploy", "detail": "Promote canary/rolling/blue-green release"},
            {"phase": "Rollback", "detail": "Auto-revert when anomaly thresholds are breached"},
            {"phase": "Communicate", "detail": "Share release notes and deployment summaries"},
        ],
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "type": type(exc).__name__,
        },
    )


# Include routers
app.include_router(
    release_planning.router,
    prefix=f"{settings.api_v1_prefix}/release-planning",
    tags=["Release Planning"]
)

app.include_router(
    pre_flight.router,
    prefix=f"{settings.api_v1_prefix}/pre-flight",
    tags=["Pre-Flight Validation"]
)

app.include_router(
    canary_deployment.router,
    prefix=f"{settings.api_v1_prefix}/canary",
    tags=["Canary Deployment"]
)

# Other routers (to be implemented)
# app.include_router(
#     deployments.router,
#     prefix=f"{settings.api_v1_prefix}/deployments",
#     tags=["Deployments"]
# )
# app.include_router(
#     workflows.router,
#     prefix=f"{settings.api_v1_prefix}/workflows",
#     tags=["Workflows"]
# )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

# Made with Bob

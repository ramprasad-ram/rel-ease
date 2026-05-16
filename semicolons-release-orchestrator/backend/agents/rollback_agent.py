"""
Autonomous Rollback Agent.
Monitors deployments for critical errors and automatically triggers rollbacks.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from uuid import UUID

from models.deployment import Deployment, DeploymentState
from models.agent import AgentType, AgentRecommendation, RecommendationPriority
from agents.base_agent import BaseAgent
from integrations.slack_client import SlackClient
from services.cicd_simulator import CICDSimulator

logger = logging.getLogger(__name__)

# Import PostmortemAgent for post-rollback analysis
POSTMORTEM_AVAILABLE = False
PostmortemAgentClass = None

try:
    from agents.postmortem_agent import PostmortemAgent as PostmortemAgentClass
    POSTMORTEM_AVAILABLE = True
except ImportError:
    logger.warning("PostmortemAgent not available - post-mortem analysis will be skipped")


class RollbackAgent(BaseAgent):
    """
    Autonomous agent that monitors deployments and triggers automatic rollbacks.
    
    Features:
    - Real-time error monitoring
    - Automatic correlation with recent deployments
    - Autonomous rollback decision-making
    - Slack notifications
    """
    
    # Thresholds for automatic rollback
    ERROR_RATE_THRESHOLD = 0.15  # 15% error rate
    CRITICAL_ERROR_RATE = 0.30   # 30% error rate (immediate rollback)
    MONITORING_WINDOW_SECONDS = 300  # 5 minutes
    
    def __init__(self, slack_webhook_url: Optional[str] = None, enable_postmortem: bool = True):
        """
        Initialize Rollback Agent.
        
        Args:
            slack_webhook_url: Slack webhook URL for notifications
            enable_postmortem: Enable automatic post-mortem analysis after rollbacks
        """
        super().__init__(AgentType.ROLLBACK_RECOMMENDATION)
        self.slack_client = SlackClient(webhook_url=slack_webhook_url)
        self.cicd_simulator = CICDSimulator()
        
        # Track active deployments and their metrics
        self.active_deployments: Dict[str, Dict[str, Any]] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        # Initialize post-mortem agent if available and enabled
        self.enable_postmortem = enable_postmortem and POSTMORTEM_AVAILABLE
        if self.enable_postmortem and PostmortemAgentClass is not None:
            self.postmortem_agent = PostmortemAgentClass(slack_webhook_url=slack_webhook_url)
            logger.info("Post-mortem analysis enabled for rollback agent")
        else:
            self.postmortem_agent = None
            if enable_postmortem and not POSTMORTEM_AVAILABLE:
                logger.warning("Post-mortem analysis requested but PostmortemAgent not available")
    
    async def analyze(self, deployment: Deployment) -> Dict[str, Any]:
        """
        Analyze deployment for potential issues.
        
        Args:
            deployment: Deployment to analyze
            
        Returns:
            Analysis results with error metrics
        """
        deployment_id = str(deployment.id)
        
        # Get current metrics
        metrics = self._get_deployment_metrics(deployment_id)
        
        # Calculate error rate
        total_requests = metrics.get("total_requests", 0)
        error_count = metrics.get("error_count", 0)
        error_rate = error_count / total_requests if total_requests > 0 else 0.0
        
        # Analyze error patterns
        error_types = metrics.get("error_types", {})
        has_500_errors = error_types.get("5xx", 0) > 0
        has_critical_errors = error_types.get("critical", 0) > 0
        
        analysis = {
            "deployment_id": deployment_id,
            "service_name": deployment.name,
            "version": deployment.version,
            "error_rate": error_rate,
            "total_requests": total_requests,
            "error_count": error_count,
            "error_types": error_types,
            "has_500_errors": has_500_errors,
            "has_critical_errors": has_critical_errors,
            "exceeds_threshold": error_rate > self.ERROR_RATE_THRESHOLD,
            "exceeds_critical_threshold": error_rate > self.CRITICAL_ERROR_RATE,
            "rollback_recommended": error_rate > self.ERROR_RATE_THRESHOLD,
            "immediate_rollback_required": error_rate > self.CRITICAL_ERROR_RATE or has_critical_errors,
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(
            f"Rollback Agent analysis for {deployment.name}: "
            f"error_rate={error_rate:.1%}, "
            f"threshold_exceeded={analysis['exceeds_threshold']}"
        )
        
        return analysis
    
    async def generate_recommendations(
        self,
        deployment: Deployment,
        analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate rollback recommendations based on analysis.
        
        Args:
            deployment: Deployment being analyzed
            analysis_data: Analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if analysis_data.get("immediate_rollback_required"):
            recommendations.append(
                self.create_recommendation(
                    title="CRITICAL: Immediate Rollback Required",
                    description=(
                        f"Critical error rate detected: {analysis_data['error_rate']:.1%}. "
                        f"Automatic rollback will be initiated."
                    ),
                    priority=RecommendationPriority.CRITICAL,
                    action="immediate_rollback",
                    impact="Prevent catastrophic service degradation"
                ).model_dump()
            )
        elif analysis_data.get("rollback_recommended"):
            recommendations.append(
                self.create_recommendation(
                    title="Rollback Recommended",
                    description=(
                        f"Error rate {analysis_data['error_rate']:.1%} exceeds threshold "
                        f"{self.ERROR_RATE_THRESHOLD:.1%}. Consider rollback."
                    ),
                    priority=RecommendationPriority.HIGH,
                    action="initiate_rollback",
                    impact="Restore service stability"
                ).model_dump()
            )
        
        return recommendations
    
    async def start_monitoring(self, deployment: Deployment) -> None:
        """
        Start monitoring a deployment for errors.
        
        Args:
            deployment: Deployment to monitor
        """
        deployment_id = str(deployment.id)
        
        if deployment_id in self.monitoring_tasks:
            logger.warning(f"Already monitoring deployment {deployment_id}")
            return
        
        # Initialize metrics
        self.active_deployments[deployment_id] = {
            "deployment": deployment,
            "start_time": datetime.now(timezone.utc),
            "total_requests": 0,
            "error_count": 0,
            "error_types": {},
            "rollback_triggered": False
        }
        
        # Start monitoring task
        task = asyncio.create_task(self._monitor_deployment(deployment))
        self.monitoring_tasks[deployment_id] = task
        
        logger.info(f"Started monitoring deployment {deployment_id} ({deployment.name})")
    
    async def stop_monitoring(self, deployment_id: str) -> None:
        """
        Stop monitoring a deployment.
        
        Args:
            deployment_id: Deployment ID to stop monitoring
        """
        if deployment_id in self.monitoring_tasks:
            self.monitoring_tasks[deployment_id].cancel()
            del self.monitoring_tasks[deployment_id]
        
        if deployment_id in self.active_deployments:
            del self.active_deployments[deployment_id]
        
        logger.info(f"Stopped monitoring deployment {deployment_id}")
    
    async def _monitor_deployment(self, deployment: Deployment) -> None:
        """
        Continuously monitor a deployment for errors.
        
        Args:
            deployment: Deployment to monitor
        """
        deployment_id = str(deployment.id)
        
        try:
            while True:
                # Analyze current state
                analysis = await self.analyze(deployment)
                
                # Check if rollback is needed
                if analysis["immediate_rollback_required"] and not self.active_deployments[deployment_id]["rollback_triggered"]:
                    logger.critical(
                        f"CRITICAL ERROR DETECTED in {deployment.name}! "
                        f"Error rate: {analysis['error_rate']:.1%}. Initiating automatic rollback."
                    )
                    
                    # Mark as triggered to prevent duplicate rollbacks
                    self.active_deployments[deployment_id]["rollback_triggered"] = True
                    
                    # Send Slack alert about error spike
                    await self.slack_client.send_error_spike_detected(
                        service_name=deployment.name,
                        error_rate=analysis["error_rate"],
                        threshold=self.CRITICAL_ERROR_RATE,
                        deployment_id=deployment_id
                    )
                    
                    # Trigger automatic rollback
                    await self._execute_automatic_rollback(deployment, analysis)
                    
                    # Stop monitoring after rollback
                    break
                
                elif analysis["exceeds_threshold"]:
                    logger.warning(
                        f"Error threshold exceeded for {deployment.name}: "
                        f"{analysis['error_rate']:.1%}"
                    )
                
                # Wait before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except asyncio.CancelledError:
            logger.info(f"Monitoring cancelled for deployment {deployment_id}")
        except Exception as e:
            logger.error(f"Error monitoring deployment {deployment_id}: {str(e)}")
    
    async def _execute_automatic_rollback(
        self,
        deployment: Deployment,
        analysis: Dict[str, Any]
    ) -> None:
        """
        Execute automatic rollback for a deployment.
        
        Args:
            deployment: Deployment to rollback
            analysis: Analysis data with error details
        """
        deployment_id = str(deployment.id)
        
        if not deployment.rollback_version:
            logger.error(f"No rollback version specified for {deployment.name}")
            await self.slack_client.send_message(
                text=f"❌ Cannot rollback {deployment.name}: No rollback version specified"
            )
            return
        
        logger.info(
            f"Executing automatic rollback for {deployment.name} "
            f"from v{deployment.version} to v{deployment.rollback_version}"
        )
        
        # Prepare error details
        error_details = (
            f"Error Rate: {analysis['error_rate']:.1%}\n"
            f"Total Requests: {analysis['total_requests']}\n"
            f"Error Count: {analysis['error_count']}\n"
            f"500-level Errors: {'Yes' if analysis['has_500_errors'] else 'No'}"
        )
        
        # Send Slack rollback alert
        await self.slack_client.send_rollback_alert(
            service_name=deployment.name,
            current_version=deployment.version,
            rollback_version=deployment.rollback_version,
            error_details=error_details,
            deployment_id=deployment_id
        )
        
        # Execute rollback via CI/CD simulator
        try:
            rollback_result = await self.cicd_simulator.rollback(
                deployment_id=deployment_id,
                current_version=deployment.version,
                target_version=deployment.rollback_version,
                platform=deployment.target_platform,
                environment=deployment.target_environment
            )
            
            if rollback_result["success"]:
                logger.info(f"Rollback successful for {deployment.name}")
                
                # Store original version before updating
                failed_version = deployment.version
                
                # Update deployment state
                deployment.state = DeploymentState.ROLLED_BACK
                deployment.version = deployment.rollback_version
                
                # Send success notification
                await self.slack_client.send_message(
                    text=f"✅ Rollback completed successfully for {deployment.name} to v{deployment.rollback_version}"
                )
                
                # Trigger post-mortem analysis
                if self.enable_postmortem and self.postmortem_agent:
                    logger.info(f"Triggering post-mortem analysis for {deployment.name}")
                    try:
                        # Create a copy of deployment with failed version for analysis
                        failed_deployment = Deployment(
                            id=deployment.id,
                            name=deployment.name,
                            version=failed_version,
                            rollback_version=deployment.rollback_version,
                            target_environment=deployment.target_environment,
                            target_platform=deployment.target_platform,
                            state=DeploymentState.ROLLED_BACK,
                            description=f"Failed deployment - rolled back from v{failed_version}",
                            created_by="rollback_agent"
                        )
                        
                        postmortem_analysis = await self.postmortem_agent.analyze(failed_deployment)
                        
                        # Generate and send post-mortem report
                        await self.postmortem_agent.send_postmortem_notification(postmortem_analysis)
                        
                        logger.info(
                            f"Post-mortem analysis complete for {deployment.name}: "
                            f"Root cause: {postmortem_analysis['root_cause'].get('type', 'unknown')}"
                        )
                    except Exception as pm_error:
                        logger.error(f"Post-mortem analysis failed: {str(pm_error)}")
                        # Don't fail the rollback if post-mortem fails
            else:
                logger.error(f"Rollback failed for {deployment.name}: {rollback_result.get('error')}")
                await self.slack_client.send_message(
                    text=f"❌ Rollback failed for {deployment.name}: {rollback_result.get('error')}"
                )
        
        except Exception as e:
            logger.error(f"Exception during rollback execution: {str(e)}")
            await self.slack_client.send_message(
                text=f"❌ Rollback exception for {deployment.name}: {str(e)}"
            )
    
    def _get_deployment_metrics(self, deployment_id: str) -> Dict[str, Any]:
        """
        Get current metrics for a deployment.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Current metrics
        """
        if deployment_id not in self.active_deployments:
            return {
                "total_requests": 0,
                "error_count": 0,
                "error_types": {}
            }
        
        return self.active_deployments[deployment_id]
    
    def inject_error(
        self,
        deployment_id: str,
        error_count: int = 100,
        error_type: str = "5xx"
    ) -> bool:
        """
        Inject errors for testing/demo purposes.
        
        Args:
            deployment_id: Deployment ID
            error_count: Number of errors to inject
            error_type: Type of error (5xx, 4xx, critical)
            
        Returns:
            True if errors injected successfully
        """
        if deployment_id not in self.active_deployments:
            logger.error(f"Deployment {deployment_id} not being monitored")
            return False
        
        metrics = self.active_deployments[deployment_id]
        metrics["error_count"] += error_count
        metrics["total_requests"] += error_count + 50  # Add some successful requests too
        
        if error_type not in metrics["error_types"]:
            metrics["error_types"][error_type] = 0
        metrics["error_types"][error_type] += error_count
        
        logger.info(
            f"Injected {error_count} {error_type} errors into deployment {deployment_id}. "
            f"New error rate: {metrics['error_count'] / metrics['total_requests']:.1%}"
        )
        
        return True

# Made with Bob

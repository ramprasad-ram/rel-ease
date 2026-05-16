"""
Canary Deployment Controller for progressive traffic shifting.
Manages canary rollouts with automatic monitoring and rollback capabilities.
"""
import asyncio
import random
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from utils.logger import get_logger

logger = get_logger(__name__)


class CanaryStage(str, Enum):
    """Canary deployment stages."""
    INITIALIZING = "initializing"
    DEPLOYING_CANARY = "deploying_canary"
    TRAFFIC_10 = "traffic_10"
    MONITORING_10 = "monitoring_10"
    TRAFFIC_25 = "traffic_25"
    MONITORING_25 = "monitoring_25"
    TRAFFIC_50 = "traffic_50"
    MONITORING_50 = "monitoring_50"
    TRAFFIC_100 = "traffic_100"
    COMPLETED = "completed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class CanaryStatus(str, Enum):
    """Canary deployment status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class CanaryController:
    """
    Controls canary deployment execution with progressive traffic shifting.
    
    Capabilities:
    - Progressive traffic rollout (10% → 25% → 50% → 100%)
    - Real-time health monitoring at each stage
    - Automatic rollback on failure
    - Metrics collection and analysis
    """
    
    def __init__(self):
        self.deployments: Dict[str, Dict[str, Any]] = {}
        self.monitoring_interval = 5  # seconds
        self.health_check_threshold = 0.95  # 95% success rate required
    
    async def execute_canary_deployment(
        self,
        deployment_id: str,
        version: str,
        environment: str,
        config: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute a canary deployment with progressive traffic shifting.
        
        Args:
            deployment_id: Unique deployment identifier
            version: Version to deploy
            environment: Target environment
            config: Deployment configuration
            progress_callback: Optional callback for progress updates
            
        Returns:
            Deployment result with final status
        """
        logger.info(f"Starting canary deployment {deployment_id} for version {version}")
        
        # Initialize deployment state
        deployment_state = {
            "deployment_id": deployment_id,
            "version": version,
            "environment": environment,
            "status": CanaryStatus.IN_PROGRESS,
            "stage": CanaryStage.INITIALIZING,
            "traffic_percentage": 0,
            "started_at": datetime.utcnow().isoformat(),
            "current_metrics": {},
            "stage_history": [],
            "health_checks": [],
        }
        
        self.deployments[deployment_id] = deployment_state
        
        try:
            # Stage 1: Deploy canary pods
            await self._update_stage(deployment_id, CanaryStage.DEPLOYING_CANARY, progress_callback)
            await self._deploy_canary_pods(deployment_id, version, config)
            
            # Stage 2: Shift 10% traffic
            await self._shift_traffic(deployment_id, 10, progress_callback)
            await self._monitor_stage(deployment_id, 10, progress_callback)
            
            # Stage 3: Shift 25% traffic
            await self._shift_traffic(deployment_id, 25, progress_callback)
            await self._monitor_stage(deployment_id, 25, progress_callback)
            
            # Stage 4: Shift 50% traffic
            await self._shift_traffic(deployment_id, 50, progress_callback)
            await self._monitor_stage(deployment_id, 50, progress_callback)
            
            # Stage 5: Shift 100% traffic
            await self._shift_traffic(deployment_id, 100, progress_callback)
            
            # Mark as completed
            await self._update_stage(deployment_id, CanaryStage.COMPLETED, progress_callback)
            deployment_state["status"] = CanaryStatus.COMPLETED
            deployment_state["completed_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Canary deployment {deployment_id} completed successfully")
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "status": CanaryStatus.COMPLETED,
                "final_traffic": 100,
                "stages_completed": len(deployment_state["stage_history"]),
            }
            
        except Exception as e:
            logger.error(f"Canary deployment {deployment_id} failed: {str(e)}")
            
            # Attempt rollback
            await self._rollback_deployment(deployment_id, progress_callback)
            
            deployment_state["status"] = CanaryStatus.FAILED
            deployment_state["error"] = str(e)
            deployment_state["failed_at"] = datetime.utcnow().isoformat()
            
            return {
                "success": False,
                "deployment_id": deployment_id,
                "status": CanaryStatus.ROLLED_BACK,
                "error": str(e),
            }
    
    async def _deploy_canary_pods(
        self,
        deployment_id: str,
        version: str,
        config: Dict[str, Any]
    ) -> None:
        """Deploy canary pods (simulated)."""
        logger.info(f"Deploying canary pods for {deployment_id}")
        
        # Simulate pod deployment
        await asyncio.sleep(2)
        
        # Simulate occasional deployment failure
        if random.random() < 0.05:  # 5% failure rate
            raise Exception("Failed to deploy canary pods: insufficient resources")
        
        deployment_state = self.deployments[deployment_id]
        deployment_state["canary_pods"] = config.get("canary_replicas", 1)
        deployment_state["stable_pods"] = config.get("stable_replicas", 3)
        
        logger.info(f"Canary pods deployed successfully for {deployment_id}")
    
    async def _shift_traffic(
        self,
        deployment_id: str,
        percentage: int,
        progress_callback: Optional[Callable] = None
    ) -> None:
        """Shift traffic to canary version."""
        stage_map = {
            10: CanaryStage.TRAFFIC_10,
            25: CanaryStage.TRAFFIC_25,
            50: CanaryStage.TRAFFIC_50,
            100: CanaryStage.TRAFFIC_100,
        }
        
        stage = stage_map.get(percentage, CanaryStage.TRAFFIC_10)
        await self._update_stage(deployment_id, stage, progress_callback)
        
        logger.info(f"Shifting {percentage}% traffic to canary for {deployment_id}")
        
        # Simulate traffic shift
        await asyncio.sleep(1)
        
        deployment_state = self.deployments[deployment_id]
        deployment_state["traffic_percentage"] = percentage
        
        if progress_callback:
            await progress_callback({
                "deployment_id": deployment_id,
                "event": "traffic_shifted",
                "traffic_percentage": percentage,
                "timestamp": datetime.utcnow().isoformat(),
            })
    
    async def _monitor_stage(
        self,
        deployment_id: str,
        traffic_percentage: int,
        progress_callback: Optional[Callable] = None
    ) -> None:
        """Monitor canary health at current traffic level."""
        stage_map = {
            10: CanaryStage.MONITORING_10,
            25: CanaryStage.MONITORING_25,
            50: CanaryStage.MONITORING_50,
        }
        
        stage = stage_map.get(traffic_percentage)
        if stage:
            await self._update_stage(deployment_id, stage, progress_callback)
        
        logger.info(f"Monitoring canary at {traffic_percentage}% traffic for {deployment_id}")
        
        # Monitor for a period
        monitoring_duration = 10  # seconds
        checks = 3
        
        for i in range(checks):
            await asyncio.sleep(monitoring_duration / checks)
            
            # Collect metrics
            metrics = await self._collect_metrics(deployment_id, traffic_percentage)
            
            # Check health
            is_healthy = await self._check_health(deployment_id, metrics)
            
            if progress_callback:
                await progress_callback({
                    "deployment_id": deployment_id,
                    "event": "health_check",
                    "traffic_percentage": traffic_percentage,
                    "metrics": metrics,
                    "is_healthy": is_healthy,
                    "check_number": i + 1,
                    "total_checks": checks,
                    "timestamp": datetime.utcnow().isoformat(),
                })
            
            if not is_healthy:
                raise Exception(
                    f"Health check failed at {traffic_percentage}% traffic: "
                    f"Error rate {metrics['error_rate']:.2%} exceeds threshold"
                )
        
        logger.info(f"Monitoring passed for {traffic_percentage}% traffic")
    
    async def _collect_metrics(
        self,
        deployment_id: str,
        traffic_percentage: int
    ) -> Dict[str, Any]:
        """Collect real-time metrics (simulated)."""
        # Simulate metrics collection
        base_error_rate = 0.01  # 1% base error rate
        
        # Simulate potential issues at higher traffic
        error_rate_increase = (traffic_percentage / 100) * random.uniform(0, 0.03)
        error_rate = base_error_rate + error_rate_increase
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "traffic_percentage": traffic_percentage,
            "requests_per_second": random.randint(100, 500),
            "error_rate": error_rate,
            "response_time_ms": random.uniform(50, 200),
            "cpu_usage_percent": random.uniform(30, 70),
            "memory_usage_mb": random.uniform(400, 600),
            "success_rate": 1 - error_rate,
        }
        
        deployment_state = self.deployments[deployment_id]
        deployment_state["current_metrics"] = metrics
        deployment_state["health_checks"].append(metrics)
        
        return metrics
    
    async def _check_health(
        self,
        deployment_id: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """Check if canary is healthy based on metrics."""
        # Check success rate
        if metrics["success_rate"] < self.health_check_threshold:
            logger.warning(
                f"Health check failed for {deployment_id}: "
                f"Success rate {metrics['success_rate']:.2%} below threshold"
            )
            return False
        
        # Check response time
        if metrics["response_time_ms"] > 500:
            logger.warning(
                f"Health check failed for {deployment_id}: "
                f"Response time {metrics['response_time_ms']}ms too high"
            )
            return False
        
        return True
    
    async def _rollback_deployment(
        self,
        deployment_id: str,
        progress_callback: Optional[Callable] = None
    ) -> None:
        """Rollback canary deployment."""
        await self._update_stage(deployment_id, CanaryStage.ROLLING_BACK, progress_callback)
        
        logger.info(f"Rolling back canary deployment {deployment_id}")
        
        # Simulate rollback
        await asyncio.sleep(2)
        
        deployment_state = self.deployments[deployment_id]
        deployment_state["traffic_percentage"] = 0
        deployment_state["status"] = CanaryStatus.ROLLED_BACK
        
        await self._update_stage(deployment_id, CanaryStage.ROLLED_BACK, progress_callback)
        
        if progress_callback:
            await progress_callback({
                "deployment_id": deployment_id,
                "event": "rollback_completed",
                "timestamp": datetime.utcnow().isoformat(),
            })
        
        logger.info(f"Rollback completed for {deployment_id}")
    
    async def _update_stage(
        self,
        deployment_id: str,
        stage: CanaryStage,
        progress_callback: Optional[Callable] = None
    ) -> None:
        """Update deployment stage."""
        deployment_state = self.deployments[deployment_id]
        deployment_state["stage"] = stage
        deployment_state["stage_history"].append({
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        logger.info(f"Deployment {deployment_id} stage updated to {stage}")
        
        if progress_callback:
            await progress_callback({
                "deployment_id": deployment_id,
                "event": "stage_changed",
                "stage": stage,
                "timestamp": datetime.utcnow().isoformat(),
            })
    
    def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get current deployment status."""
        return self.deployments.get(deployment_id)
    
    def get_all_deployments(self) -> Dict[str, Dict[str, Any]]:
        """Get all active deployments."""
        return self.deployments


# Made with Bob
"""
Anomaly detection agent for identifying deployment issues.
"""
import random
from typing import Dict, Any, List
from models.agent import AgentType, RecommendationPriority
from models.deployment import Deployment, DeploymentState
from .base_agent import BaseAgent


class AnomalyDetectionAgent(BaseAgent):
    """
    AI agent that detects anomalies in deployments and running applications.
    
    This is a mock implementation that simulates anomaly detection.
    In production, this would integrate with monitoring systems and ML models.
    """
    
    def __init__(self):
        super().__init__(AgentType.ANOMALY_DETECTION)
    
    async def analyze(self, deployment: Deployment) -> Dict[str, Any]:
        """
        Detect anomalies in deployment or running application.
        
        Monitors:
        - Error rates
        - Response times
        - Resource usage
        - Traffic patterns
        - System metrics
        
        Args:
            deployment: Deployment to analyze
            
        Returns:
            Analysis results with detected anomalies and recommendations
        """
        self.log_analysis_start(deployment)
        
        # Only analyze deployed or monitoring states
        if deployment.state not in [DeploymentState.DEPLOYED, DeploymentState.MONITORING]:
            return {
                "confidence_score": 1.0,
                "analysis_data": {"status": "not_applicable"},
                "recommendations": [],
            }
        
        # Simulate anomaly detection
        analysis_data = await self._detect_anomalies(deployment)
        
        # Calculate confidence in anomaly detection
        confidence = self._calculate_confidence(analysis_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(deployment, analysis_data, confidence)
        
        self.log_analysis_complete(deployment, confidence, len(recommendations))
        
        return {
            "confidence_score": confidence,
            "analysis_data": analysis_data,
            "recommendations": recommendations,
        }
    
    async def _detect_anomalies(self, deployment: Deployment) -> Dict[str, Any]:
        """Perform mock anomaly detection."""
        # Simulate various metrics
        error_rate = random.uniform(0.0, 0.05)
        response_time_ms = random.uniform(50, 500)
        cpu_usage = random.uniform(0.2, 0.9)
        memory_usage = random.uniform(0.3, 0.85)
        
        # Detect anomalies
        anomalies_detected = []
        
        if error_rate > 0.02:
            anomalies_detected.append({
                "type": "high_error_rate",
                "severity": "high" if error_rate > 0.03 else "medium",
                "value": error_rate,
                "threshold": 0.02,
            })
        
        if response_time_ms > 300:
            anomalies_detected.append({
                "type": "slow_response_time",
                "severity": "high" if response_time_ms > 400 else "medium",
                "value": response_time_ms,
                "threshold": 300,
            })
        
        if cpu_usage > 0.8:
            anomalies_detected.append({
                "type": "high_cpu_usage",
                "severity": "critical" if cpu_usage > 0.9 else "high",
                "value": cpu_usage,
                "threshold": 0.8,
            })
        
        if memory_usage > 0.8:
            anomalies_detected.append({
                "type": "high_memory_usage",
                "severity": "critical" if memory_usage > 0.9 else "high",
                "value": memory_usage,
                "threshold": 0.8,
            })
        
        return {
            "error_rate": error_rate,
            "response_time_ms": response_time_ms,
            "cpu_usage_percent": cpu_usage * 100,
            "memory_usage_percent": memory_usage * 100,
            "request_count": random.randint(1000, 10000),
            "anomalies_detected": anomalies_detected,
            "anomaly_count": len(anomalies_detected),
            "health_score": self._calculate_health_score(
                error_rate, response_time_ms, cpu_usage, memory_usage
            ),
            "baseline_comparison": random.choice(["normal", "normal", "elevated"]),
        }
    
    def _calculate_health_score(
        self,
        error_rate: float,
        response_time: float,
        cpu: float,
        memory: float
    ) -> float:
        """Calculate overall health score."""
        # Simple scoring algorithm
        score = 1.0
        
        # Penalize high error rates
        score -= min(error_rate * 10, 0.3)
        
        # Penalize slow response times
        if response_time > 300:
            score -= min((response_time - 300) / 1000, 0.2)
        
        # Penalize high resource usage
        if cpu > 0.8:
            score -= min((cpu - 0.8) * 0.5, 0.2)
        if memory > 0.8:
            score -= min((memory - 0.8) * 0.5, 0.2)
        
        return max(0.0, min(1.0, score))
    
    def _calculate_confidence(self, analysis_data: Dict[str, Any]) -> float:
        """Calculate confidence in anomaly detection."""
        # Higher confidence when more data points are available
        base_confidence = 0.85
        
        # Adjust based on anomaly count
        anomaly_count = analysis_data.get("anomaly_count", 0)
        if anomaly_count > 0:
            base_confidence += 0.1
        
        # Add some randomness
        confidence = base_confidence + random.uniform(-0.05, 0.05)
        
        return round(max(0.0, min(1.0, confidence)), 3)
    
    def _generate_recommendations(
        self,
        deployment: Deployment,
        analysis_data: Dict[str, Any],
        confidence: float
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on detected anomalies."""
        recommendations = []
        anomalies = analysis_data.get("anomalies_detected", [])
        
        if not anomalies:
            recommendations.append(
                self.create_recommendation(
                    title="No Anomalies Detected",
                    description="Deployment is operating normally within expected parameters.",
                    priority=RecommendationPriority.LOW,
                    action="continue_monitoring",
                    impact="System is healthy"
                ).model_dump()
            )
            return recommendations
        
        # Generate recommendations for each anomaly
        for anomaly in anomalies:
            if anomaly["type"] == "high_error_rate":
                recommendations.append(
                    self.create_recommendation(
                        title="High Error Rate Detected",
                        description=(
                            f"Error rate ({anomaly['value']:.2%}) exceeds threshold "
                            f"({anomaly['threshold']:.2%}). Investigate application logs."
                        ),
                        priority=RecommendationPriority.CRITICAL if anomaly["severity"] == "high" else RecommendationPriority.HIGH,
                        action="investigate_errors",
                        impact="User experience degradation, potential data loss"
                    ).model_dump()
                )
            
            elif anomaly["type"] == "slow_response_time":
                recommendations.append(
                    self.create_recommendation(
                        title="Slow Response Times",
                        description=(
                            f"Average response time ({anomaly['value']:.0f}ms) exceeds "
                            f"threshold ({anomaly['threshold']:.0f}ms)."
                        ),
                        priority=RecommendationPriority.HIGH,
                        action="optimize_performance",
                        impact="Poor user experience, potential timeouts"
                    ).model_dump()
                )
            
            elif anomaly["type"] == "high_cpu_usage":
                recommendations.append(
                    self.create_recommendation(
                        title="High CPU Usage",
                        description=(
                            f"CPU usage ({anomaly['value']:.1%}) is critically high. "
                            "Consider scaling or optimizing."
                        ),
                        priority=RecommendationPriority.CRITICAL,
                        action="scale_resources",
                        impact="System instability, potential crashes"
                    ).model_dump()
                )
            
            elif anomaly["type"] == "high_memory_usage":
                recommendations.append(
                    self.create_recommendation(
                        title="High Memory Usage",
                        description=(
                            f"Memory usage ({anomaly['value']:.1%}) is critically high. "
                            "Check for memory leaks."
                        ),
                        priority=RecommendationPriority.CRITICAL,
                        action="investigate_memory_leak",
                        impact="Out of memory errors, application crashes"
                    ).model_dump()
                )
        
        # Overall health recommendation
        health_score = analysis_data.get("health_score", 1.0)
        if health_score < 0.6:
            recommendations.append(
                self.create_recommendation(
                    title="Consider Rollback",
                    description=(
                        f"Overall health score is low ({health_score:.1%}). "
                        "Multiple issues detected. Consider rolling back."
                    ),
                    priority=RecommendationPriority.CRITICAL,
                    action="initiate_rollback",
                    impact="Prevent further degradation and user impact"
                ).model_dump()
            )
        
        return recommendations

# Made with Bob

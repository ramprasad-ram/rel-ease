"""
Base agent interface for AI-powered deployment analysis.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from models.agent import AgentType, AgentRecommendation, RecommendationPriority
from models.deployment import Deployment
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for AI agents.
    All agents must implement the analyze method.
    """
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.logger = get_logger(f"{__name__}.{agent_type.value}")
    
    @abstractmethod
    async def analyze(self, deployment: Deployment) -> Dict[str, Any]:
        """
        Analyze a deployment and return analysis results.
        
        Args:
            deployment: Deployment to analyze
            
        Returns:
            Analysis results dictionary containing:
                - confidence_score: float (0-1)
                - analysis_data: dict with analysis details
                - recommendations: list of recommendations
        """
        pass
    
    def create_recommendation(
        self,
        title: str,
        description: str,
        priority: RecommendationPriority = RecommendationPriority.MEDIUM,
        action: Optional[str] = None,
        impact: Optional[str] = None
    ) -> AgentRecommendation:
        """
        Create a recommendation object.
        
        Args:
            title: Recommendation title
            description: Detailed description
            priority: Priority level
            action: Suggested action
            impact: Expected impact
            
        Returns:
            AgentRecommendation object
        """
        return AgentRecommendation(
            title=title,
            description=description,
            priority=priority,
            action=action,
            impact=impact
        )
    
    def log_analysis_start(self, deployment: Deployment) -> None:
        """Log the start of analysis."""
        self.logger.info(
            f"Starting {self.agent_type.value} analysis for deployment "
            f"{deployment.id} ({deployment.name})"
        )
    
    def log_analysis_complete(
        self,
        deployment: Deployment,
        confidence: float,
        recommendation_count: int
    ) -> None:
        """Log the completion of analysis."""
        self.logger.info(
            f"Completed {self.agent_type.value} analysis for deployment "
            f"{deployment.id}: confidence={confidence:.2f}, "
            f"recommendations={recommendation_count}"
        )

# Made with Bob

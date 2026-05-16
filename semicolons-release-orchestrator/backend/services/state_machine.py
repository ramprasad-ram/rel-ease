"""
State machine for deployment lifecycle management.
Defines valid state transitions and enforces business rules.
"""
from logging import Logger


from typing import Dict, Set, Optional
from models.deployment import DeploymentState
from utils.logger import get_logger

logger: Logger = get_logger(name=__name__)


class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class StateMachine:
    """
    Manages deployment state transitions with validation.
    
    State Flow:
        PENDING → VALIDATING → APPROVED → DEPLOYING → DEPLOYED → MONITORING
                      ↓           ↓          ↓           ↓
                  REJECTED    CANCELLED   FAILED    ROLLING_BACK → ROLLED_BACK
    """
    
    # Define valid state transitions
    TRANSITIONS: Dict[DeploymentState, Set[DeploymentState]] = {
        DeploymentState.PENDING: {
            DeploymentState.VALIDATING,
            DeploymentState.CANCELLED,
        },
        DeploymentState.VALIDATING: {
            DeploymentState.APPROVED,
            DeploymentState.REJECTED,
            DeploymentState.CANCELLED,
        },
        DeploymentState.APPROVED: {
            DeploymentState.DEPLOYING,
            DeploymentState.CANCELLED,
        },
        DeploymentState.REJECTED: set(),  # Terminal state
        DeploymentState.CANCELLED: set(),  # Terminal state
        DeploymentState.DEPLOYING: {
            DeploymentState.DEPLOYED,
            DeploymentState.FAILED,
        },
        DeploymentState.DEPLOYED: {
            DeploymentState.MONITORING,
            DeploymentState.ROLLING_BACK,
        },
        DeploymentState.FAILED: {
            DeploymentState.ROLLING_BACK,
            DeploymentState.DEPLOYING,  # Retry
        },
        DeploymentState.ROLLING_BACK: {
            DeploymentState.ROLLED_BACK,
            DeploymentState.FAILED,
        },
        DeploymentState.ROLLED_BACK: {
            DeploymentState.DEPLOYING,  # Can retry after rollback
        },
        DeploymentState.MONITORING: {
            DeploymentState.ROLLING_BACK,
        },
    }
    
    @classmethod
    def can_transition(
        cls,
        from_state: DeploymentState,
        to_state: DeploymentState
    ) -> bool:
        """
        Check if a state transition is valid.
        
        Args:
            from_state: Current state
            to_state: Desired state
            
        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions = cls.TRANSITIONS.get(from_state, set())
        return to_state in valid_transitions
    
    @classmethod
    def validate_transition(
        cls,
        from_state: DeploymentState,
        to_state: DeploymentState,
        reason: Optional[str] = None
    ) -> None:
        """
        Validate a state transition and raise exception if invalid.
        
        Args:
            from_state: Current state
            to_state: Desired state
            reason: Optional reason for transition
            
        Raises:
            StateTransitionError: If transition is not valid
        """
        if not cls.can_transition(from_state, to_state):
            error_msg = (
                f"Invalid state transition from {from_state.value} to {to_state.value}"
            )
            if reason:
                error_msg += f". Reason: {reason}"
            
            logger.warning(error_msg)
            raise StateTransitionError(error_msg)
        
        logger.info(
            f"Valid state transition: {from_state.value} → {to_state.value}"
            + (f" ({reason})" if reason else "")
        )
    
    @classmethod
    def get_next_states(cls, current_state: DeploymentState) -> Set[DeploymentState]:
        """
        Get all valid next states from the current state.
        
        Args:
            current_state: Current deployment state
            
        Returns:
            Set of valid next states
        """
        return cls.TRANSITIONS.get(current_state, set())
    
    @classmethod
    def is_terminal_state(cls, state: DeploymentState) -> bool:
        """
        Check if a state is terminal (no further transitions).
        
        Args:
            state: State to check
            
        Returns:
            True if state is terminal
        """
        return len(cls.TRANSITIONS.get(state, set())) == 0
    
    @classmethod
    def can_approve(cls, state: DeploymentState) -> bool:
        """Check if deployment can be approved from current state."""
        return state == DeploymentState.VALIDATING
    
    @classmethod
    def can_deploy(cls, state: DeploymentState) -> bool:
        """Check if deployment can be deployed from current state."""
        return state == DeploymentState.APPROVED
    
    @classmethod
    def can_rollback(cls, state: DeploymentState) -> bool:
        """Check if deployment can be rolled back from current state."""
        return state in {
            DeploymentState.DEPLOYED,
            DeploymentState.FAILED,
            DeploymentState.MONITORING,
        }
    
    @classmethod
    def get_state_description(cls, state: DeploymentState) -> str:
        """
        Get human-readable description of a state.
        
        Args:
            state: Deployment state
            
        Returns:
            Description string
        """
        descriptions = {
            DeploymentState.PENDING: "Deployment created, awaiting validation",
            DeploymentState.VALIDATING: "Running validation checks",
            DeploymentState.APPROVED: "Approved and ready for deployment",
            DeploymentState.REJECTED: "Deployment rejected, cannot proceed",
            DeploymentState.CANCELLED: "Deployment cancelled by user",
            DeploymentState.DEPLOYING: "Deployment in progress",
            DeploymentState.DEPLOYED: "Successfully deployed",
            DeploymentState.FAILED: "Deployment failed",
            DeploymentState.ROLLING_BACK: "Rolling back to previous version",
            DeploymentState.ROLLED_BACK: "Successfully rolled back",
            DeploymentState.MONITORING: "Deployed and under monitoring",
        }
        return descriptions.get(state, "Unknown state")

# Made with Bob

"""
Workflow orchestration engine.
Manages workflow execution, step coordination, and error handling.
"""
from logging import Logger


import asyncio
from types import CoroutineType
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.workflow import (
    Workflow,
    WorkflowStep,
    WorkflowType,
    WorkflowStatus,
    StepStatus,
)
from services.cicd_simulator import CICDSimulator
from config import settings
from utils.logger import get_logger

logger: Logger = get_logger(name=__name__)


class WorkflowOrchestrator:
    """
    Orchestrates workflow execution with support for different execution patterns.
    """
    
    def __init__(self):
        self.cicd_simulator = CICDSimulator()
        self.max_retries = settings.workflow_max_retries
        self.retry_delay = settings.workflow_retry_delay
    
    async def execute_workflow(
        self,
        workflow: Workflow,
        steps: List[WorkflowStep]
    ) -> Dict[str, Any]:
        """
        Execute a workflow based on its type.
        
        Args:
            workflow: Workflow to execute
            steps: Workflow steps to execute
            
        Returns:
            Execution result with status and details
        """
        logger.info(
            f"Starting workflow execution: {workflow.name} "
            f"(type: {workflow.workflow_type.value})"
        )
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        
        try:
            if workflow.workflow_type == WorkflowType.SEQUENTIAL:
                result = await self._execute_sequential(workflow, steps)
            elif workflow.workflow_type == WorkflowType.PARALLEL:
                result = await self._execute_parallel(workflow, steps)
            elif workflow.workflow_type == WorkflowType.CONDITIONAL:
                result = await self._execute_conditional(workflow, steps)
            elif workflow.workflow_type == WorkflowType.ROLLBACK:
                result = await self._execute_rollback(workflow, steps)
            else:
                raise ValueError(f"Unknown workflow type: {workflow.workflow_type}")
            
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()
            
            logger.info(f"Workflow completed successfully: {workflow.name}")
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {workflow.name} - {str(e)}")
            workflow.status = WorkflowStatus.FAILED
            workflow.error_message = str(e)
            workflow.completed_at = datetime.utcnow()
            raise
    
    async def _execute_sequential(
        self,
        workflow: Workflow,
        steps: List[WorkflowStep]
    ) -> Dict[str, Any]:
        """Execute steps sequentially, one after another."""
        results = []
        
        for idx, step in enumerate(sorted(steps, key=lambda s: s.order)):
            workflow.current_step = idx
            logger.info(f"Executing step {idx + 1}/{len(steps)}: {step.name}")
            
            step_result = await self._execute_step(step)
            results.append(step_result)
            
            if not step_result["success"]:
                logger.error(f"Step failed: {step.name}")
                raise Exception(f"Step {step.name} failed: {step_result.get('error')}")
        
        return {
            "workflow_type": "sequential",
            "total_steps": len(steps),
            "completed_steps": len(results),
            "results": results,
        }
    
    async def _execute_parallel(
        self,
        workflow: Workflow,
        steps: List[WorkflowStep]
    ) -> Dict[str, Any]:
        """Execute all steps in parallel."""
        logger.info(f"Executing {len(steps)} steps in parallel")
        
        tasks: list[CoroutineType[Any, Any, Dict[str, Any]]] = [self._execute_step(step) for step in steps]
        results: list[Dict[str, Any] | BaseException] = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for failures
        failures: list[Exception | Dict[str, Any]] = [
            r
            for r in results
            if isinstance(r, Exception)
            or (isinstance(r, dict) and not r.get("success", False))
        ]
        if failures:
            logger.error(msg=f"Parallel execution had {len(failures)} failures")
            raise Exception(f"{len(failures)} step(s) failed in parallel execution")
        
        return {
            "workflow_type": "parallel",
            "total_steps": len(steps),
            "completed_steps": len(results),
            "results": results,
        }
    
    async def _execute_conditional(
        self,
        workflow: Workflow,
        steps: List[WorkflowStep]
    ) -> Dict[str, Any]:
        """Execute steps with conditional logic based on previous results."""
        results = []
        context = {}  # Shared context for conditional decisions
        
        for idx, step in enumerate(sorted(steps, key=lambda s: s.order)):
            workflow.current_step = idx
            
            # Check if step should be executed based on conditions
            if self._should_execute_step(step, context):
                logger.info(f"Executing conditional step: {step.name}")
                step_result = await self._execute_step(step)
                results.append(step_result)
                
                # Update context with step result
                context[step.name] = step_result
                
                if not step_result["success"]:
                    logger.warning(f"Conditional step failed: {step.name}")
                    # Continue with other steps based on config
                    if not step.config.get("continue_on_failure", False):
                        raise Exception(f"Step {step.name} failed")
            else:
                logger.info(f"Skipping conditional step: {step.name}")
                step.status = StepStatus.SKIPPED
        
        return {
            "workflow_type": "conditional",
            "total_steps": len(steps),
            "executed_steps": len(results),
            "skipped_steps": len(steps) - len(results),
            "results": results,
        }
    
    async def _execute_rollback(
        self,
        workflow: Workflow,
        steps: List[WorkflowStep]
    ) -> Dict[str, Any]:
        """Execute rollback steps in reverse order."""
        logger.info("Executing rollback workflow")
        results = []
        
        # Execute steps in reverse order
        for idx, step in enumerate(reversed(sorted(steps, key=lambda s: s.order))):
            workflow.current_step = idx
            logger.info(f"Executing rollback step {idx + 1}/{len(steps)}: {step.name}")
            
            step_result = await self._execute_step(step)
            results.append(step_result)
            
            # Continue rollback even if individual steps fail
            if not step_result["success"]:
                logger.warning(f"Rollback step failed: {step.name}, continuing...")
        
        return {
            "workflow_type": "rollback",
            "total_steps": len(steps),
            "completed_steps": len(results),
            "results": results,
        }
    
    async def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """
        Execute a single workflow step with retry logic.
        
        Args:
            step: Step to execute
            
        Returns:
            Step execution result
        """
        step.status = StepStatus.RUNNING
        step.started_at = datetime.utcnow()
        
        for attempt in range(step.retry_count + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retrying step {step.name} (attempt {attempt + 1})")
                    await asyncio.sleep(self.retry_delay)
                
                # Execute step based on type
                result = await self._execute_step_by_type(step)
                
                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.utcnow()
                step.output = result
                
                return {
                    "success": True,
                    "step_name": step.name,
                    "step_type": step.step_type,
                    "attempt": attempt + 1,
                    "result": result,
                }
                
            except Exception as e:
                logger.error(f"Step execution failed: {step.name} - {str(e)}")
                
                if attempt >= step.retry_count:
                    step.status = StepStatus.FAILED
                    step.completed_at = datetime.utcnow()
                    step.error_message = str(e)
                    
                    return {
                        "success": False,
                        "step_name": step.name,
                        "step_type": step.step_type,
                        "attempt": attempt + 1,
                        "error": str(e),
                    }
        
        # Should not reach here
        return {"success": False, "error": "Unknown error"}
    
    async def _execute_step_by_type(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute step based on its type."""
        step_type = step.step_type.lower()
        
        if step_type == "build":
            return await self.cicd_simulator.build(
                deployment_id=str(step.workflow_id),
                version=step.config.get("version", "1.0.0"),
                metadata=step.config,
            )
        elif step_type == "test":
            return await self.cicd_simulator.test(
                deployment_id=str(step.workflow_id),
                version=step.config.get("version", "1.0.0"),
                test_suite=step.config.get("test_suite", "full"),
            )
        elif step_type == "deploy":
            from models.deployment import DeploymentPlatform
            return await self.cicd_simulator.deploy(
                deployment_id=str(step.workflow_id),
                version=step.config.get("version", "1.0.0"),
                platform=DeploymentPlatform(step.config.get("platform", "kubernetes")),
                environment=step.config.get("environment", "production"),
                metadata=step.config,
            )
        elif step_type == "health_check":
            return await self.cicd_simulator.health_check(
                deployment_id=str(step.workflow_id),
                environment=step.config.get("environment", "production"),
            )
        else:
            # Generic step execution
            await asyncio.sleep(1)
            return {
                "step_type": step_type,
                "status": "completed",
                "message": f"Step {step.name} executed successfully",
            }
    
    def _should_execute_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> bool:
        """Determine if a conditional step should be executed."""
        conditions = step.config.get("conditions", {})
        
        if not conditions:
            return True
        
        # Check all conditions
        for key, expected_value in conditions.items():
            if key in context:
                actual_value = context[key].get("success", False)
                if actual_value != expected_value:
                    return False
        
        return True
    
    async def pause_workflow(self, workflow: Workflow) -> None:
        """Pause workflow execution."""
        logger.info(f"Pausing workflow: {workflow.name}")
        workflow.status = WorkflowStatus.PAUSED
        workflow.updated_at = datetime.utcnow()
    
    async def resume_workflow(
        self,
        workflow: Workflow,
        steps: List[WorkflowStep]
    ) -> Dict[str, Any]:
        """Resume paused workflow execution."""
        logger.info(f"Resuming workflow: {workflow.name}")
        workflow.status = WorkflowStatus.RUNNING
        workflow.updated_at = datetime.utcnow()
        
        # Resume from current step
        remaining_steps = [s for s in steps if s.order > workflow.current_step]
        return await self.execute_workflow(workflow, remaining_steps)
    
    async def cancel_workflow(self, workflow: Workflow) -> None:
        """Cancel workflow execution."""
        logger.info(f"Cancelling workflow: {workflow.name}")
        workflow.status = WorkflowStatus.CANCELLED
        workflow.completed_at = datetime.utcnow()

# Made with Bob

#!/usr/bin/env python3
"""
Demo Test Runner
Quick script to verify all demo features are working before the hackathon presentation.
"""
import asyncio
import sys
from datetime import datetime
from uuid import uuid4

from agents.release_planning_agent import ReleasePlanningAgent
from agents.cicd_validation_agent import CICDValidationAgent
from agents.rollback_agent import RollbackAgent
from agents.postmortem_agent import PostmortemAgent
from models.deployment import Deployment, DeploymentState, DeploymentPlatform
from services.canary_controller import CanaryController


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_step(step_num, title):
    """Print a step header"""
    print(f"\n{'='*70}")
    print(f"  STEP {step_num}: {title}")
    print(f"{'='*70}")


def print_success(message):
    """Print success message"""
    print(f"✅ {message}")


def print_info(message, indent=1):
    """Print info message"""
    prefix = "   " * indent
    print(f"{prefix}• {message}")


def print_error(message):
    """Print error message"""
    print(f"❌ {message}")


async def test_step1_release_planning():
    """Test Step 1: Release Planning"""
    print_step(1, "Release Planning - Circular Dependency Detection")
    
    try:
        agent = ReleasePlanningAgent()
        
        result = await agent.analyze_release_readiness(
            github_repo="demo-org/demo-app",
            jira_sprint="SPRINT-123"
        )
        
        print_success("Release Planning Agent Analysis Complete")
        print_info(f"Readiness Score: {result['readiness_score']}%")
        print_info(f"Circular Dependencies Found: {len(result['circular_dependencies'])}")
        print_info(f"Total Issues: {len(result['issues'])}")
        
        # Show circular dependency example
        if result['circular_dependencies']:
            cycle = result['circular_dependencies'][0]
            cycle_str = " → ".join(cycle)
            print_info(f"Example Cycle: {cycle_str}", indent=2)
        
        # Show key issues
        if result['issues']:
            print_info("Key Issues:", indent=1)
            for issue in result['issues'][:3]:
                print_info(issue, indent=2)
        
        return True
        
    except Exception as e:
        print_error(f"Step 1 Failed: {str(e)}")
        return False


async def test_step2_preflight_check():
    """Test Step 2: Pre-Flight Validation"""
    print_step(2, "Pre-Flight Check - Memory Leak Detection")
    
    try:
        agent = CICDValidationAgent()
        
        deployment = Deployment(
            id=uuid4(),
            name="auth-service",
            version="1.0.3",
            target_environment="staging",
            target_platform=DeploymentPlatform.KUBERNETES,
            state=DeploymentState.PENDING,
            rollback_version="1.0.2",
            created_by="demo@example.com"
        )
        
        result = await agent.analyze(deployment)
        analysis = result["analysis_data"]
        memory = analysis["memory_analysis"]
        
        print_success("Pre-Flight Validation Complete")
        print_info(f"CI Runs Analyzed: {analysis['ci_runs_analyzed']}")
        print_info(f"Memory Increase: {memory['increase_percent']}%")
        print_info(f"Potential Memory Leak: {memory.get('has_potential_leak', False)}")
        
        if memory.get('leaky_modules'):
            print_info("Leaky Modules Detected:", indent=1)
            for module in memory['leaky_modules']:
                print_info(module, indent=2)
        
        # Show validation score
        print_info(f"Validation Score: {analysis['validation_score']}/100")
        
        return True
        
    except Exception as e:
        print_error(f"Step 2 Failed: {str(e)}")
        return False


async def test_step3_canary_deployment():
    """Test Step 3: Canary Deployment"""
    print_step(3, "Canary Deployment - Progressive Traffic Shift")
    
    try:
        controller = CanaryController()
        deployment_id = str(uuid4())
        
        print_info("Starting canary deployment...")
        
        # Execute canary deployment
        result = await controller.execute_canary_deployment(
            deployment_id=deployment_id,
            version="1.0.3",
            environment="production",
            config={
                "canary_replicas": 1,
                "stable_replicas": 3
            }
        )
        
        status = controller.get_deployment_status(deployment_id)
        
        print_success("Canary Deployment Complete")
        print_info(f"Deployment Success: {result.get('success', False)}")
        print_info(f"Final Traffic: {status.get('traffic_percentage', 0)}%")
        print_info(f"Stages Completed: {result.get('stages_completed', 0)}")
        print_info(f"Status: {status.get('status', 'unknown')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print_error(f"Step 3 Failed: {str(e)}")
        return False


async def test_step4_autonomous_rollback():
    """Test Step 4: Autonomous Rollback"""
    print_step(4, "Autonomous Rollback - Error Detection & Recovery")
    
    try:
        agent = RollbackAgent()
        
        deployment = Deployment(
            id=uuid4(),
            name="auth-service",
            version="1.0.3",
            target_environment="production",
            target_platform=DeploymentPlatform.KUBERNETES,
            state=DeploymentState.DEPLOYED,
            rollback_version="1.0.2",
            created_by="demo@example.com"
        )
        
        deployment_id = str(deployment.id)
        
        # Start monitoring
        await agent.start_monitoring(deployment)
        print_info("Monitoring started...")
        
        # Inject errors to simulate production issue
        agent.inject_error(
            deployment_id=deployment_id,
            error_count=150,
            error_type="5xx"
        )
        print_info("Errors injected (simulating production spike)...")
        
        # Analyze
        analysis = await agent.analyze(deployment)
        
        print_success("Error Detection Complete")
        print_info(f"Error Rate: {analysis['error_rate']:.1%}")
        print_info(f"Total Requests: {analysis['total_requests']}")
        print_info(f"Error Count: {analysis['error_count']}")
        print_info(f"500-level Errors: {analysis['has_500_errors']}")
        print_info(f"Rollback Recommended: {analysis['rollback_recommended']}")
        print_info(f"Immediate Rollback Required: {analysis.get('immediate_rollback_required', False)}")
        
        # Stop monitoring
        await agent.stop_monitoring(deployment_id)
        
        return True
        
    except Exception as e:
        print_error(f"Step 4 Failed: {str(e)}")
        return False


async def test_step5_postmortem():
    """Test Step 5: Post-Mortem Analysis"""
    print_step(5, "Post-Mortem Analysis - Root Cause Identification")
    
    try:
        agent = PostmortemAgent()
        
        deployment = Deployment(
            id=uuid4(),
            name="auth-service",
            version="1.0.3",
            target_environment="production",
            target_platform=DeploymentPlatform.KUBERNETES,
            state=DeploymentState.ROLLED_BACK,
            rollback_version="1.0.2",
            created_by="demo@example.com"
        )
        
        analysis = await agent.analyze(deployment)
        root_cause = analysis["root_cause"]
        
        print_success("Post-Mortem Analysis Complete")
        print_info(f"Root Cause Type: {root_cause['description']}")
        print_info(f"Confidence: {root_cause['confidence'] * 100:.0f}%")
        
        if 'file' in root_cause and 'line' in root_cause:
            print_info(f"Problem Location: {root_cause['file']}:{root_cause['line']}")
        
        if 'suggested_fix' in root_cause:
            print_info("Suggested Fix:", indent=1)
            print_info(root_cause['suggested_fix'], indent=2)
        
        print_info(f"Total Recommendations: {len(analysis['recommendations'])}")
        
        return True
        
    except Exception as e:
        print_error(f"Step 5 Failed: {str(e)}")
        return False


async def run_all_tests():
    """Run all demo tests"""
    print_header("🎯 DEMO PREPARATION TEST SUITE 🎯")
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run each step
    results['step1'] = await test_step1_release_planning()
    results['step2'] = await test_step2_preflight_check()
    results['step3'] = await test_step3_canary_deployment()
    results['step4'] = await test_step4_autonomous_rollback()
    results['step5'] = await test_step5_postmortem()
    
    # Print summary
    print_header("📊 TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for step, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {step.upper()}: {status}")
    
    print(f"\n  Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print_header("🎉 ALL TESTS PASSED - DEMO READY! 🎉")
        return 0
    else:
        print_header("⚠️  SOME TESTS FAILED - REVIEW REQUIRED")
        return 1


def main():
    """Main entry point"""
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
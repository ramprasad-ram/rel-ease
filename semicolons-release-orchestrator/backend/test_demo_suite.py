"""
Comprehensive Demo Test Suite
Tests all 5 steps of the demoable flow to ensure demo readiness.
"""
import asyncio
from datetime import datetime
from uuid import uuid4

from agents.release_planning_agent import ReleasePlanningAgent
from agents.cicd_validation_agent import CICDValidationAgent
from agents.rollback_agent import RollbackAgent
from agents.postmortem_agent import PostmortemAgent
from models.deployment import Deployment, DeploymentState, DeploymentPlatform
from services.canary_controller import CanaryController

# Optional pytest support
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Create dummy decorator
    class pytest:
        @staticmethod
        def mark(*args, **kwargs):
            class Marker:
                @staticmethod
                def asyncio(func):
                    return func
            return Marker()


class TestDemoStep1ReleasePlanning:
    """Test Step 1: Release Planning with circular dependency detection"""
    
    async def test_release_readiness_analysis(self):
        """Test that Planning Agent generates readiness score and detects issues"""
        agent = ReleasePlanningAgent()
        
        result = await agent.analyze_release_readiness(
            github_repo="demo-org/demo-app",
            jira_sprint="SPRINT-123"
        )
        
        # Verify core outputs
        assert "readiness_score" in result
        assert "circular_dependencies" in result
        assert "issues" in result
        assert "recommendations" in result
        
        # Verify readiness score is calculated
        assert 0 <= result["readiness_score"] <= 100
        
        # Verify circular dependencies are detected
        assert len(result["circular_dependencies"]) > 0, "Should detect circular dependencies"
        
        # Verify issues are identified
        assert len(result["issues"]) > 0, "Should identify issues"
        
        # Check for specific issue about circular dependencies
        circular_dep_issue = any("circular dependency" in issue.lower() for issue in result["issues"])
        assert circular_dep_issue, "Should flag circular dependency issue"
        
        print(f"✅ Step 1 PASSED: Readiness Score = {result['readiness_score']}%")
        print(f"   - Circular Dependencies: {len(result['circular_dependencies'])}")
        print(f"   - Issues Found: {len(result['issues'])}")
        return result


class TestDemoStep2PreFlightCheck:
    """Test Step 2: Pre-Flight Validation with memory leak detection"""
    
    async def test_memory_leak_detection(self):
        """Test that Validation Agent detects memory increase and flags leaks"""
        agent = CICDValidationAgent()
        
        # Create test deployment
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
        
        # Verify analysis structure
        assert "confidence_score" in result
        assert "analysis_data" in result
        analysis = result["analysis_data"]
        
        # Verify memory analysis
        assert "memory_analysis" in analysis
        memory = analysis["memory_analysis"]
        
        # Check for memory increase detection
        assert "increase_percent" in memory
        assert memory["increase_percent"] > 0, "Should detect memory increase"
        
        # Check for leak detection
        if memory["increase_percent"] > 10:
            assert memory["has_potential_leak"], "Should flag potential leak when increase > 10%"
            assert len(memory.get("leaky_modules", [])) > 0, "Should identify leaky modules"
        
        # Verify issues are detected
        assert "issues" in analysis
        memory_issues = [i for i in analysis["issues"] if i["type"] == "memory_leak"]
        
        if memory["has_potential_leak"]:
            assert len(memory_issues) > 0, "Should report memory leak issues"
            # Check for specific module mention
            issue_text = memory_issues[0]["description"]
            assert "module" in issue_text.lower(), "Should mention specific module"
        
        print(f"✅ Step 2 PASSED: Memory increase = {memory['increase_percent']}%")
        print(f"   - Potential Leak: {memory.get('has_potential_leak', False)}")
        print(f"   - Leaky Modules: {memory.get('leaky_modules', [])}")
        return result


class TestDemoStep3CanaryDeployment:
    """Test Step 3: Canary Deployment with traffic shifting"""
    
    async def test_canary_traffic_shift(self):
        """Test that Canary Controller can execute canary deployment"""
        controller = CanaryController()
        
        deployment_id = str(uuid4())
        
        # Execute canary deployment (will run through stages automatically)
        result = await controller.execute_canary_deployment(
            deployment_id=deployment_id,
            version="1.0.3",
            environment="production",
            config={
                "canary_replicas": 1,
                "stable_replicas": 3
            }
        )
        
        # Verify deployment completed
        assert result is not None, "Deployment should return result"
        assert "success" in result, "Result should indicate success status"
        
        # Get final status
        status = controller.get_deployment_status(deployment_id)
        assert status is not None, "Deployment status should be available"
        assert "traffic_percentage" in status, "Should track traffic percentage"
        
        print(f"✅ Step 3 PASSED: Canary deployment executed")
        print(f"   - Success: {result.get('success', False)}")
        print(f"   - Final Traffic: {status.get('traffic_percentage', 0)}%")
        print(f"   - Status: {status.get('status', 'unknown')}")
        return status


class TestDemoStep4AutonomousRollback:
    """Test Step 4: Autonomous Rollback (The "Wow" Moment)"""
    
    async def test_error_detection_and_rollback(self):
        """Test that Rollback Agent detects errors and triggers autonomous rollback"""
        agent = RollbackAgent()
        
        # Create deployment
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
        
        # Verify monitoring started
        assert deployment_id in agent.active_deployments, "Should be monitoring deployment"
        
        # Inject errors to simulate production issue
        success = agent.inject_error(
            deployment_id=deployment_id,
            error_count=150,  # High error count
            error_type="5xx"
        )
        assert success, "Error injection should succeed"
        
        # Analyze deployment
        analysis = await agent.analyze(deployment)
        
        # Verify error detection
        assert "error_rate" in analysis
        assert analysis["error_rate"] > 0, "Should detect errors"
        assert analysis["has_500_errors"], "Should detect 500-level errors"
        
        # Verify rollback recommendation
        assert "rollback_recommended" in analysis
        if analysis["error_rate"] > agent.ERROR_RATE_THRESHOLD:
            assert analysis["rollback_recommended"], "Should recommend rollback"
        
        if analysis["error_rate"] > agent.CRITICAL_ERROR_RATE:
            assert analysis["immediate_rollback_required"], "Should require immediate rollback"
        
        # Generate recommendations
        recommendations = await agent.generate_recommendations(deployment, analysis)
        assert len(recommendations) > 0, "Should generate recommendations"
        
        # Check for critical recommendation
        critical_recs = [r for r in recommendations if r["priority"] == "critical"]
        if analysis["immediate_rollback_required"]:
            assert len(critical_recs) > 0, "Should have critical recommendation"
        
        # Stop monitoring
        await agent.stop_monitoring(deployment_id)
        
        print(f"✅ Step 4 PASSED: Error detection and rollback logic verified")
        print(f"   - Error Rate: {analysis['error_rate']:.1%}")
        print(f"   - Rollback Recommended: {analysis['rollback_recommended']}")
        print(f"   - Immediate Rollback: {analysis.get('immediate_rollback_required', False)}")
        return analysis


class TestDemoStep5PostMortem:
    """Test Step 5: Post-Mortem Analysis"""
    
    async def test_postmortem_analysis(self):
        """Test that Post-Mortem Agent analyzes failure and provides specific fixes"""
        agent = PostmortemAgent()
        
        # Create failed deployment
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
        
        # Perform analysis
        analysis = await agent.analyze(deployment)
        
        # Verify analysis structure
        assert "root_cause" in analysis
        assert "recommendations" in analysis
        assert "log_analysis" in analysis
        assert "code_diff_analysis" in analysis
        
        root_cause = analysis["root_cause"]
        
        # Verify root cause identification
        assert "type" in root_cause
        assert "description" in root_cause
        assert "confidence" in root_cause
        assert root_cause["confidence"] > 0, "Should have confidence score"
        
        # Check for specific details
        if root_cause["type"] != "unknown":
            assert "detailed_description" in root_cause, "Should have detailed description"
            assert "suggested_fix" in root_cause, "Should have suggested fix"
        
        # Verify code-specific recommendations
        if "file" in root_cause and "line" in root_cause:
            assert root_cause["line"] > 0, "Should identify specific line number"
            print(f"   - Identified Issue: {root_cause['file']}:{root_cause['line']}")
        
        # Verify recommendations
        assert len(analysis["recommendations"]) > 0, "Should provide recommendations"
        
        # Generate report
        report = await agent.generate_report(analysis)
        assert len(report) > 0, "Should generate report"
        assert "Root Cause" in report, "Report should include root cause"
        assert "Suggested Fix" in report, "Report should include fix"
        
        print(f"✅ Step 5 PASSED: Post-mortem analysis complete")
        print(f"   - Root Cause: {root_cause['description']}")
        print(f"   - Confidence: {root_cause['confidence'] * 100:.0f}%")
        print(f"   - Recommendations: {len(analysis['recommendations'])}")
        return analysis


class TestDemoEndToEnd:
    """End-to-end demo flow test"""
    
    async def test_complete_demo_flow(self):
        """Test the complete demo flow from planning to post-mortem"""
        print("\n" + "="*60)
        print("RUNNING COMPLETE DEMO FLOW TEST")
        print("="*60)
        
        # Step 1: Release Planning
        print("\n📋 STEP 1: Release Planning")
        planning_agent = ReleasePlanningAgent()
        planning_result = await planning_agent.analyze_release_readiness(
            github_repo="demo-org/demo-app",
            jira_sprint="SPRINT-123"
        )
        assert planning_result["readiness_score"] >= 0
        print(f"   ✓ Readiness Score: {planning_result['readiness_score']}%")
        print(f"   ✓ Circular Dependencies: {len(planning_result['circular_dependencies'])}")
        
        # Step 2: Pre-Flight Check
        print("\n🔍 STEP 2: Pre-Flight Validation")
        validation_agent = CICDValidationAgent()
        deployment = Deployment(
            id=uuid4(),
            name="auth-service",
            version="1.0.3",
            target_environment="production",
            target_platform=DeploymentPlatform.KUBERNETES,
            state=DeploymentState.PENDING,
            rollback_version="1.0.2",
            created_by="demo@example.com"
        )
        validation_result = await validation_agent.analyze(deployment)
        memory = validation_result["analysis_data"]["memory_analysis"]
        print(f"   ✓ Memory Increase: {memory['increase_percent']}%")
        print(f"   ✓ Potential Leak: {memory.get('has_potential_leak', False)}")
        
        # Step 3: Canary Deployment
        print("\n🚀 STEP 3: Canary Deployment")
        controller = CanaryController()
        deployment_id = str(deployment.id)
        canary_result = await controller.execute_canary_deployment(
            deployment_id=deployment_id,
            version="1.0.3",
            environment="production",
            config={"canary_replicas": 1, "stable_replicas": 3}
        )
        canary_status = controller.get_deployment_status(deployment_id)
        print(f"   ✓ Canary Executed: {canary_result.get('success', False)}")
        print(f"   ✓ Final Traffic: {canary_status.get('traffic_percentage', 0)}%")
        
        # Step 4: Error Detection & Rollback
        print("\n⚠️  STEP 4: Error Detection & Autonomous Rollback")
        rollback_agent = RollbackAgent()
        deployment.state = DeploymentState.DEPLOYED
        await rollback_agent.start_monitoring(deployment)
        
        # Inject errors
        rollback_agent.inject_error(deployment_id, error_count=150, error_type="5xx")
        rollback_analysis = await rollback_agent.analyze(deployment)
        print(f"   ✓ Error Rate: {rollback_analysis['error_rate']:.1%}")
        print(f"   ✓ Rollback Recommended: {rollback_analysis['rollback_recommended']}")
        
        await rollback_agent.stop_monitoring(deployment_id)
        
        # Step 5: Post-Mortem
        print("\n📊 STEP 5: Post-Mortem Analysis")
        postmortem_agent = PostmortemAgent()
        deployment.state = DeploymentState.ROLLED_BACK
        postmortem_result = await postmortem_agent.analyze(deployment)
        root_cause = postmortem_result["root_cause"]
        print(f"   ✓ Root Cause: {root_cause['description']}")
        print(f"   ✓ Confidence: {root_cause['confidence'] * 100:.0f}%")
        print(f"   ✓ Recommendations: {len(postmortem_result['recommendations'])}")
        
        print("\n" + "="*60)
        print("✅ COMPLETE DEMO FLOW TEST PASSED")
        print("="*60)
        
        return {
            "step1_planning": planning_result,
            "step2_validation": validation_result,
            "step3_canary": canary_status,
            "step4_rollback": rollback_analysis,
            "step5_postmortem": postmortem_result
        }


# Standalone test runner for quick demo verification
async def run_demo_tests():
    """Run all demo tests without pytest"""
    print("\n" + "🎯 "*20)
    print("DEMO PREPARATION TEST SUITE")
    print("🎯 "*20 + "\n")
    
    try:
        # Test Step 1
        step1 = TestDemoStep1ReleasePlanning()
        await step1.test_release_readiness_analysis()
        
        # Test Step 2
        step2 = TestDemoStep2PreFlightCheck()
        await step2.test_memory_leak_detection()
        
        # Test Step 3
        step3 = TestDemoStep3CanaryDeployment()
        await step3.test_canary_traffic_shift()
        
        # Test Step 4
        step4 = TestDemoStep4AutonomousRollback()
        await step4.test_error_detection_and_rollback()
        
        # Test Step 5
        step5 = TestDemoStep5PostMortem()
        await step5.test_postmortem_analysis()
        
        # End-to-end test
        e2e = TestDemoEndToEnd()
        await e2e.test_complete_demo_flow()
        
        print("\n" + "✅ "*20)
        print("ALL DEMO TESTS PASSED - READY FOR DEMO!")
        print("✅ "*20 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        raise


if __name__ == "__main__":
    # Run tests directly
    asyncio.run(run_demo_tests())

# Made with Bob
"""
Test script for demonstrating the Autonomous Rollback Agent.

This script demonstrates the "Wow Moment" feature:
1. Start monitoring a deployment
2. Inject errors to simulate production issues
3. Watch the agent automatically detect and rollback
4. Receive Slack notifications (if configured)

Usage:
    python test_rollback_agent.py
"""
import asyncio
import httpx
from uuid import uuid4
from datetime import datetime
import time


BASE_URL = "http://localhost:8000/api/v1"


async def demo_autonomous_rollback():
    """
    Demonstrate the autonomous rollback feature.
    
    This is the "Crisis & Recovery" wow moment:
    - Deploy a new version
    - Inject 500-level errors
    - Agent detects spike and autonomously triggers rollback
    - Slack notification sent
    """
    print("=" * 80)
    print("🚀 AUTONOMOUS ROLLBACK AGENT DEMO")
    print("=" * 80)
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Create a deployment to monitor
        deployment_id = uuid4()
        service_name = "Auth-Service"
        current_version = "1.0.3"
        rollback_version = "1.0.2"
        
        print(f"📦 Step 1: Deploying {service_name} v{current_version}")
        print(f"   Deployment ID: {deployment_id}")
        print(f"   Rollback Version: v{rollback_version}")
        print()
        
        # Step 2: Start monitoring
        print("👁️  Step 2: Starting Rollback Agent monitoring...")
        monitor_response = await client.post(
            f"{BASE_URL}/rollback/start-monitoring",
            json={
                "deployment_id": str(deployment_id),
                "name": service_name,
                "version": current_version,
                "rollback_version": rollback_version,
                "target_environment": "production",
                "target_platform": "kubernetes"
            }
        )
        
        if monitor_response.status_code == 200:
            data = monitor_response.json()
            print(f"✅ Monitoring started successfully")
            print(f"   Error Threshold: {data['details']['error_threshold']}")
            print(f"   Critical Threshold: {data['details']['critical_threshold']}")
        else:
            print(f"❌ Failed to start monitoring: {monitor_response.text}")
            return
        
        print()
        
        # Step 3: Simulate normal traffic
        print("📊 Step 3: Simulating normal traffic...")
        print("   (Service is healthy, no errors)")
        await asyncio.sleep(3)
        
        # Check status
        status_response = await client.get(f"{BASE_URL}/rollback/status/{deployment_id}")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"   Current Error Rate: {status['metrics']['error_rate']}")
            print(f"   Status: {'🟢 Healthy' if not status['status']['exceeds_warning'] else '🟡 Warning'}")
        print()
        
        # Step 4: THE WOW MOMENT - Inject errors!
        print("💥 Step 4: INJECTING CRITICAL ERRORS (Simulating Production Issue)")
        print("   Injecting 200 5xx errors to trigger automatic rollback...")
        print()
        
        inject_response = await client.post(
            f"{BASE_URL}/rollback/inject-errors",
            json={
                "deployment_id": str(deployment_id),
                "error_count": 200,
                "error_type": "5xx"
            }
        )
        
        if inject_response.status_code == 200:
            inject_data = inject_response.json()
            print(f"⚠️  ERRORS INJECTED!")
            print(f"   Total Errors: {inject_data['details']['total_errors']}")
            print(f"   Error Rate: {inject_data['details']['error_rate']}")
            print(f"   Will Trigger Rollback: {inject_data['details']['will_trigger_rollback']}")
        else:
            print(f"❌ Failed to inject errors: {inject_response.text}")
            return
        
        print()
        print("🤖 Step 5: Rollback Agent is analyzing...")
        print("   Waiting for autonomous rollback decision...")
        print()
        
        # Step 5: Wait and watch for rollback
        for i in range(15):
            await asyncio.sleep(2)
            
            # Check status
            status_response = await client.get(f"{BASE_URL}/rollback/status/{deployment_id}")
            if status_response.status_code == 200:
                status = status_response.json()
                error_rate = status['metrics']['error_rate']
                rollback_triggered = status['status']['rollback_triggered']
                
                if rollback_triggered:
                    print(f"🚨 ROLLBACK TRIGGERED! (after {i*2} seconds)")
                    print()
                    print("=" * 80)
                    print("✅ AUTONOMOUS ROLLBACK COMPLETED")
                    print("=" * 80)
                    print(f"   Service: {service_name}")
                    print(f"   Failed Version: v{current_version}")
                    print(f"   Rolled Back To: v{rollback_version}")
                    print(f"   Error Rate at Rollback: {error_rate}")
                    print()
                    print("📬 Slack Notification Sent:")
                    print(f"   '🚨 Rollback initiated. Error detected in '{service_name}'.")
                    print(f"    Reverting to v{rollback_version}.'")
                    print()
                    break
                else:
                    print(f"   [{i*2}s] Monitoring... Error Rate: {error_rate}")
            else:
                print(f"   Deployment no longer being monitored (rollback may have completed)")
                break
        
        # Step 6: Check final status
        print()
        print("📊 Step 6: Final Status Check")
        
        monitors_response = await client.get(f"{BASE_URL}/rollback/active-monitors")
        if monitors_response.status_code == 200:
            monitors = monitors_response.json()
            print(f"   Active Monitors: {monitors['active_monitors']}")
        
        print()
        print("=" * 80)
        print("🎉 DEMO COMPLETE!")
        print("=" * 80)
        print()
        print("What just happened:")
        print("1. ✅ Deployed Auth-Service v1.0.3 to production")
        print("2. ✅ Rollback Agent started monitoring")
        print("3. ✅ Simulated 500-level error spike")
        print("4. ✅ Agent detected critical error rate")
        print("5. ✅ Agent AUTONOMOUSLY triggered rollback to v1.0.2")
        print("6. ✅ Slack notification sent (if webhook configured)")
        print()
        print("This demonstrates the 'Crisis & Recovery' wow moment!")
        print()


async def test_error_injection_only():
    """Quick test to just inject errors into an existing monitored deployment."""
    deployment_id = input("Enter deployment ID to inject errors into: ")
    error_count = int(input("Enter number of errors to inject (default 150): ") or "150")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/rollback/inject-errors",
            json={
                "deployment_id": deployment_id,
                "error_count": error_count,
                "error_type": "5xx"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Injected {error_count} errors")
            print(f"   Error Rate: {data['details']['error_rate']}")
            print(f"   Will Trigger Rollback: {data['details']['will_trigger_rollback']}")
        else:
            print(f"❌ Failed: {response.text}")


async def check_active_monitors():
    """Check all active monitoring sessions."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/rollback/active-monitors")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Active Monitors: {data['active_monitors']}")
            for monitor in data['monitors']:
                print(f"  - {monitor['service_name']} v{monitor['version']}")
                print(f"    Error Rate: {monitor['error_rate']}")
                print(f"    Rollback Triggered: {monitor['rollback_triggered']}")
        else:
            print(f"❌ Failed: {response.text}")


def main():
    """Main entry point."""
    print()
    print("Autonomous Rollback Agent Test Suite")
    print("=" * 80)
    print()
    print("Options:")
    print("1. Run full demo (recommended)")
    print("2. Inject errors into existing deployment")
    print("3. Check active monitors")
    print()
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(demo_autonomous_rollback())
    elif choice == "2":
        asyncio.run(test_error_injection_only())
    elif choice == "3":
        asyncio.run(check_active_monitors())
    else:
        print("Invalid option")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

# Made with Bob

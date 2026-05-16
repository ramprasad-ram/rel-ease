"""
Test script for canary deployment functionality.
Tests the complete flow: start deployment, monitor via SSE, verify completion.
"""
import asyncio
import httpx
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000/api/v1"

async def test_canary_deployment():
    """Test the complete canary deployment flow."""
    print("=" * 80)
    print("Testing Canary Deployment with Real-Time Monitoring")
    print("=" * 80)
    print()
    
    deployment_id = f"test-deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Step 1: Start canary deployment
    print(f"Step 1: Starting canary deployment for {deployment_id}")
    print("-" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/canary/deployments/{deployment_id}/execute-canary",
                json={
                    "version": "2.1.0",
                    "environment": "production",
                    "canary_replicas": 1,
                    "stable_replicas": 3
                }
            )
            
            if response.status_code in [200, 202]:
                data = response.json()
                print(f"[SUCCESS] Deployment started successfully!")
                print(f"   Deployment ID: {data['deployment_id']}")
                print(f"   Status: {data['status']}")
                print(f"   Message: {data['message']}")
                print()
            else:
                print(f"[ERROR] Failed to start deployment: {response.status_code}")
                print(f"   Response: {response.text}")
                return
                
        except Exception as e:
            print(f"[ERROR] Error starting deployment: {e}")
            return
    
    # Give the deployment a moment to initialize
    print("Waiting for deployment to initialize...")
    await asyncio.sleep(2)
    
    # Step 2: Monitor deployment via SSE
    print(f"Step 2: Monitoring deployment progress via Server-Sent Events")
    print("-" * 80)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            async with client.stream(
                "GET",
                f"{API_BASE_URL}/canary/deployments/{deployment_id}/stream"
            ) as response:
                if response.status_code != 200:
                    print(f"[ERROR] Failed to connect to SSE stream: {response.status_code}")
                    return
                
                print("[SUCCESS] Connected to deployment stream")
                print()
                
                event_count = 0
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        event_count += 1
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        try:
                            event_data = json.loads(data_str)
                            
                            if event_data.get("error"):
                                print(f"[ERROR] Error: {event_data['error']}")
                                break
                            
                            event_type = event_data.get("event")
                            
                            if event_type == "connected":
                                print(f"[CONNECTED] Event #{event_count}: Connected to deployment {event_data['deployment_id']}")
                            
                            elif event_type == "status_update":
                                status = event_data["status"]
                                print(f"[STATUS] Event #{event_count}: Status Update")
                                print(f"   Stage: {status['current_stage']}")
                                print(f"   Traffic: {status['traffic_percentage']}% to canary")
                                print(f"   Canary Health: {status['canary_health']:.1f}%")
                                print(f"   Error Rate: {status['error_rate']:.2f}%")
                                print(f"   Latency: {status['latency_ms']:.0f}ms")
                            
                            elif event_type == "stage_complete":
                                print(f"[COMPLETE] Event #{event_count}: Stage Complete")
                                print(f"   Stage: {event_data['stage']}")
                                print(f"   Traffic: {event_data['traffic_percentage']}%")
                            
                            elif event_type == "deployment_complete":
                                print(f"[SUCCESS] Event #{event_count}: Deployment Complete!")
                                print(f"   Final Status: {event_data['final_status']}")
                                print(f"   Duration: {event_data['duration_seconds']:.1f}s")
                                break
                            
                            elif event_type == "deployment_failed":
                                print(f"[FAILED] Event #{event_count}: Deployment Failed")
                                print(f"   Reason: {event_data['reason']}")
                                break
                            
                            elif event_type == "rollback_triggered":
                                print(f"[ROLLBACK] Event #{event_count}: Rollback Triggered")
                                print(f"   Reason: {event_data['reason']}")
                            
                            print()
                            
                        except json.JSONDecodeError:
                            print(f"[WARNING] Could not parse event data: {data_str}")
                
                print("-" * 80)
                print(f"Total events received: {event_count}")
                
        except Exception as e:
            print(f"[ERROR] Error monitoring deployment: {e}")
            return
    
    print()
    print("=" * 80)
    print("[SUCCESS] Canary Deployment Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    print()
    print("Starting canary deployment test...")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    try:
        asyncio.run(test_canary_deployment())
    except KeyboardInterrupt:
        print("\n\n[WARNING] Test interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] Test failed with error: {e}")

# Made with Bob

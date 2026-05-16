"""
Test script for Post-Mortem Analysis Agent.
Demonstrates the agent's capabilities in analyzing failed deployments.
"""
import asyncio
import sys
from uuid import UUID
from datetime import datetime

from agents.postmortem_agent import PostmortemAgent
from models.deployment import Deployment, DeploymentState, DeploymentPlatform


async def test_postmortem_analysis():
    """Test post-mortem analysis with a simulated failed deployment."""
    print("\n" + "="*80)
    print("POST-MORTEM ANALYSIS AGENT - DEMO")
    print("="*80 + "\n")
    
    # Initialize agent
    print("🤖 Initializing Post-Mortem Agent...")
    agent = PostmortemAgent()
    
    # Create a failed deployment scenario
    deployment = Deployment(
        id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        name="Auth-Service",
        version="1.0.3",
        rollback_version="1.0.2",
        target_environment="production",
        target_platform=DeploymentPlatform.KUBERNETES,
        state=DeploymentState.ROLLED_BACK,
        description="Failed deployment with null pointer exception",
        created_by="test_user"
    )
    
    print(f"\n📦 Analyzing Failed Deployment:")
    print(f"   Service: {deployment.name}")
    print(f"   Failed Version: {deployment.version}")
    print(f"   Rollback Version: {deployment.rollback_version}")
    print(f"   Environment: {deployment.target_environment}")
    
    # Perform analysis
    print("\n🔍 Performing Post-Mortem Analysis...")
    print("   - Analyzing deployment logs...")
    print("   - Examining code changes...")
    print("   - Identifying error patterns...")
    print("   - Correlating errors with code diffs...")
    
    analysis = await agent.analyze(deployment)
    
    # Display results
    print("\n" + "="*80)
    print("ANALYSIS RESULTS")
    print("="*80)
    
    root_cause = analysis["root_cause"]
    print(f"\n🎯 ROOT CAUSE IDENTIFIED")
    print(f"   Type: {root_cause.get('description', 'Unknown')}")
    print(f"   Confidence: {root_cause.get('confidence', 0) * 100:.0f}%")
    
    if root_cause.get('file') and root_cause.get('line'):
        print(f"\n📍 LOCATION")
        print(f"   File: {root_cause['file']}")
        print(f"   Line: {root_cause['line']}")
        print(f"   Code: {root_cause.get('problematic_code', 'N/A')}")
    
    print(f"\n📝 DETAILED DESCRIPTION")
    print(f"   {root_cause.get('detailed_description', 'No description available')}")
    
    print(f"\n💡 SUGGESTED FIX")
    print(f"   {root_cause.get('suggested_fix', 'No fix suggested')}")
    
    # Generate recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    recommendations = await agent.generate_recommendations(deployment, analysis)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Priority: {rec['priority'].upper()}")
        print(f"   Description: {rec['description']}")
        if rec.get('action'):
            print(f"   Action: {rec['action']}")
        if rec.get('impact'):
            print(f"   Impact: {rec['impact']}")
    
    # Generate full report
    print("\n" + "="*80)
    print("FULL POST-MORTEM REPORT")
    print("="*80)
    
    report = await agent.generate_report(analysis)
    print(report)
    
    # Display metrics
    print("\n" + "="*80)
    print("ANALYSIS METRICS")
    print("="*80)
    
    log_analysis = analysis.get("log_analysis", {})
    print(f"\n📊 Log Analysis:")
    print(f"   Total Errors Found: {log_analysis.get('total_errors', 0)}")
    print(f"   Error Patterns Detected: {len(log_analysis.get('error_patterns', {}))}")
    
    diff_analysis = analysis.get("code_diff_analysis", {})
    print(f"\n📝 Code Diff Analysis:")
    print(f"   Files Changed: {len(diff_analysis.get('files_changed', []))}")
    print(f"   Risky Changes: {diff_analysis.get('total_risky_changes', 0)}")
    
    if diff_analysis.get('risky_changes'):
        print(f"\n⚠️  Risky Changes Detected:")
        for change in diff_analysis['risky_changes'][:3]:  # Show first 3
            print(f"   - {change['file']}:{change['line']} - {change['description']}")
    
    print("\n" + "="*80)
    print("✅ POST-MORTEM ANALYSIS COMPLETE")
    print("="*80 + "\n")
    
    return analysis


async def test_multiple_scenarios():
    """Test post-mortem analysis with different failure scenarios."""
    print("\n" + "="*80)
    print("TESTING MULTIPLE FAILURE SCENARIOS")
    print("="*80 + "\n")
    
    agent = PostmortemAgent()
    
    scenarios = [
        {
            "name": "Auth-Service",
            "version": "1.0.3",
            "description": "Null pointer exception scenario"
        },
        {
            "name": "Payment-Service",
            "version": "2.1.0",
            "description": "Database connection failure"
        },
        {
            "name": "API-Gateway",
            "version": "3.0.1",
            "description": "Memory leak scenario"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Scenario {i}: {scenario['name']} v{scenario['version']}")
        print(f"{'='*60}")
        
        deployment = Deployment(
            id=UUID(f"123e4567-e89b-12d3-a456-42661417400{i}"),
            name=scenario["name"],
            version=scenario["version"],
            rollback_version=f"{scenario['version'][:-1]}{int(scenario['version'][-1])-1}",
            target_environment="production",
            target_platform=DeploymentPlatform.KUBERNETES,
            state=DeploymentState.ROLLED_BACK,
            description=scenario["description"],
            created_by="test_user"
        )
        
        analysis = await agent.analyze(deployment)
        root_cause = analysis["root_cause"]
        
        print(f"Root Cause: {root_cause.get('description', 'Unknown')}")
        print(f"Confidence: {root_cause.get('confidence', 0) * 100:.0f}%")
        print(f"Recommendations: {len(analysis.get('recommendations', []))}")
        
        results.append({
            "service": scenario["name"],
            "root_cause": root_cause.get('type', 'unknown'),
            "confidence": root_cause.get('confidence', 0)
        })
    
    print("\n" + "="*80)
    print("SUMMARY OF ALL SCENARIOS")
    print("="*80 + "\n")
    
    for result in results:
        print(f"✓ {result['service']}: {result['root_cause']} "
              f"(confidence: {result['confidence']*100:.0f}%)")
    
    print("\n✅ All scenarios analyzed successfully!\n")


async def interactive_demo():
    """Interactive demo menu."""
    while True:
        print("\n" + "="*80)
        print("POST-MORTEM ANALYSIS AGENT - INTERACTIVE DEMO")
        print("="*80)
        print("\nSelect an option:")
        print("1. Run single post-mortem analysis")
        print("2. Test multiple failure scenarios")
        print("3. View sample post-mortem report")
        print("4. Exit")
        print("\n" + "="*80)
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            await test_postmortem_analysis()
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            await test_multiple_scenarios()
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            print("\n" + "="*80)
            print("SAMPLE POST-MORTEM REPORT")
            print("="*80)
            print("""
# Post-Mortem Analysis Report

## Deployment Information
- Service: Auth-Service
- Failed Version: 1.0.3
- Rollback Version: 1.0.2
- Analysis Time: 2024-01-15T10:35:00Z

## Root Cause
**Type:** Null/None reference error
**Confidence:** 90%

The failure was caused by Null/None reference error in auth.py at line 42. 
The code change removed a null check, causing the application to attempt to 
access properties on a null/None object.

## Suggested Fix
Add a null-check at line 42 of auth.py. 
Example: if user is not None: email = user.email.lower()

## Recommendations

1. **Fix null check in auth.py**
   - Add null-check at line 42
   - Action: Add null-check at line 42
   - Impact: Prevent null pointer exceptions

2. **Add unit tests for null handling**
   - Create tests that verify null/None handling in authentication flow
   - Action: Add test cases for edge cases with null users
   - Impact: Catch similar issues before deployment

3. **Enhance error monitoring**
   - Add specific alerts for null pointer exceptions in authentication
   - Action: Configure alerts for NullPointerException in auth module
   - Impact: Faster detection of similar issues
""")
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            print("\n👋 Goodbye!\n")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")


def main():
    """Main entry point."""
    print("\n🚀 Starting Post-Mortem Analysis Agent Demo...\n")
    
    try:
        asyncio.run(interactive_demo())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()


# Made with Bob
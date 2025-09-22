"""
Main entry point for UI Regression Agent
"""

import asyncio
import os
import sys

from src.agent import agent


async def run_ui_regression_test(baseline_path: str, updated_path: str):
    """Run UI regression test with provided screenshots"""
    
    # Validate image paths
    if not os.path.exists(baseline_path):
        print(f"Error: Baseline image not found at {baseline_path}")
        return
    
    if not os.path.exists(updated_path):
        print(f"Error: Updated image not found at {updated_path}")
        return
    
    print("🔍 Starting UI Regression Analysis...")
    print(f"📸 Baseline: {baseline_path}")
    print(f"📸 Updated: {updated_path}")
    print("-" * 50)
    
    try:
        # Run the regression test
        result = await agent.run_regression_test(baseline_path, updated_path)
        
        # Display results
        print(f"✅ Status: {result['status']}")
        
        if result['status'] == 'completed':
            print(f"🔍 Differences Found: {result['differences_found']}")
            print(f"⚡ Actions Taken: {result['actions_taken']}")
            print(f"✅ Validation: {'Successful' if result['validation_successful'] else 'Failed'}")
            
            # Show summary
            summary = result['summary']
            print("\n📊 Summary Report:")
            print(f"  • Minor Issues: {summary['minor_issues']}")
            print(f"  • Critical Issues: {summary['critical_issues']}")
            print(f"  • Expected Changes: {summary['expected_changes']}")
            print(f"  • Actions Taken: {summary['actions_taken']}")
            
            # Show specific actions
            if result['details']['actions']:
                print("\n🎯 Actions Taken:")
                for action in result['details']['actions']:
                    action_type = action['action']
                    if action_type == 'jira_ticket_created':
                        print(f"  • 🎫 JIRA Ticket Created: {action['ticket_id']}")
                    elif action_type == 'minor_issue_logged':
                        print(f"  • 📝 Minor Issue Logged")
                    elif action_type == 'expected_change_confirmed':
                        print(f"  • ✅ Expected Change Confirmed (JIRA: {action['jira_ticket']})")
        
        elif result['status'] == 'success':
            print(f"✅ {result['message']}")
        
        else:
            print(f"❌ Error: {result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def main():
    """Main function"""
    if len(sys.argv) != 3:
        print("Usage: python main.py <baseline_image_path> <updated_image_path>")
        print("Example: python main.py screenshots/login_baseline.png screenshots/login_updated.png")
        sys.exit(1)
    
    baseline_path = sys.argv[1]
    updated_path = sys.argv[2]
    
    # Run the async function
    asyncio.run(run_ui_regression_test(baseline_path, updated_path))


if __name__ == "__main__":
    main()

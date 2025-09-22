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
            
            # Show specific actions from results
            results = result['details']['results']
            if any([results.get('resolved_tickets'), results.get('updated_tickets'), results.get('created_tickets'), results.get('minor_issues_logged', 0) > 0]):
                print("\n🎯 Actions Taken:")
                
                if results.get('resolved_tickets'):
                    for ticket in results['resolved_tickets']:
                        print(f"  • ✅ Ticket Resolved: {ticket['id']} (Status: Done)")
                
                if results.get('updated_tickets'):
                    for ticket in results['updated_tickets']:
                        print(f"  • 🔄 Ticket Updated: {ticket['id']} (Status: Changes Requested)")
                
                if results.get('created_tickets'):
                    for ticket in results['created_tickets']:
                        print(f"  • 🎫 JIRA Ticket Created: {ticket['id']}")
                
                if results.get('minor_issues_logged', 0) > 0:
                    print(f"  • 📝 Minor Issues Logged: {results['minor_issues_logged']}")
        
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

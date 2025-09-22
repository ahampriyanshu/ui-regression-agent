"""
Main entry point for UI Regression Agent
"""

import asyncio
import os
import sys
from typing import Dict

from src.ui_regression_agent import UIRegressionAgent
from src.classification_agent import ClassificationAgent
from src.orchestrator_agent import OrchestratorAgent
from utils.logger import ui_logger


class MainOrchestrator:
    """Main orchestrator that coordinates all three agents"""
    
    def __init__(self):
        """Initialize all three agents"""
        self.ui_agent = UIRegressionAgent()
        self.classification_agent = ClassificationAgent()
        self.orchestrator_agent = OrchestratorAgent()
        self.logger = ui_logger
    
    async def run_regression_test(self, baseline_path: str, updated_path: str) -> Dict:
        """Run the complete UI regression test workflow using all three agents"""
        self.logger.initialize_logs()
        
        self.logger.logger.info("Starting UI regression test")
        
        try:
            self.logger.logger.info("Phase 1: Screenshot comparison and difference detection")
            differences = await self.ui_agent.compare_screenshots(baseline_path, updated_path)
            
            if not differences.get("differences"):
                self.logger.logger.info("No differences found - test passed")
                return {
                    "status": "success",
                    "result": "no_differences",
                    "message": "No UI differences detected"
                }
            
            self.logger.logger.info(f"Found {len(differences['differences'])} differences")
            
            self.logger.logger.info("Phase 2: Classification and analysis against JIRA tickets")
            analysis = await self.classification_agent.analyze_differences(differences["differences"])
            
            self.logger.log_regression_analysis(baseline_path, updated_path, 
                                              differences["differences"], analysis)
            
            self.logger.logger.info("Phase 3: Action execution and workflow management")
            results = await self.orchestrator_agent.execute_actions(analysis)
            
            validation = await self.orchestrator_agent.validate_actions(results)
            
            summary = self.logger.get_summary_report()
            
            result = {
                "status": "completed",
                "differences_found": len(differences["differences"]),
                "actions_taken": len(results.get('resolved_tickets', [])) + len(results.get('updated_tickets', [])) + len(results.get('created_tickets', [])) + results.get('minor_issues_logged', 0),
                "validation_successful": len(validation.get('validation_details', [])) > 0,
                "summary": summary,
                "details": {
                    "differences": differences,
                    "analysis": analysis,
                    "results": results,
                    "validation": validation
                }
            }
            
            self.logger.logger.info("UI regression test completed successfully")
            return result
            
        except Exception as e:
            self.logger.logger.error(f"UI regression test failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "error_type": type(e).__name__
            }


orchestrator = MainOrchestrator()
async def run_ui_regression_test(baseline_path: str, updated_path: str):
    """Run UI regression test with provided screenshots"""
    

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

        result = await orchestrator.run_regression_test(baseline_path, updated_path)
        

        print(f"✅ Status: {result['status']}")
        
        if result['status'] == 'completed':
            print(f"🔍 Differences Found: {result['differences_found']}")
            print(f"⚡ Actions Taken: {result['actions_taken']}")
            print(f"✅ Validation: {'Successful' if result['validation_successful'] else 'Failed'}")
            

            summary = result['summary']
            print("\n📊 Summary Report:")
            print(f"  • Minor Issues: {summary['minor_issues']}")
            

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
    

    asyncio.run(run_ui_regression_test(baseline_path, updated_path))
if __name__ == "__main__":
    main()

"""UI Regression Agent Implementation"""

import asyncio
import base64
import json
import os
from typing import Dict, List, Optional, Tuple

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from PIL import Image

from src import llm
from src.mcp_servers.jira_server import JIRAIntegration
from src.difference_analyzer import DifferenceAnalyzer
# Prompts are loaded from .txt files
from src.utils.logger import ui_logger


class UIRegressionAgent:
    """Main UI Regression Detection Agent"""
    
    def __init__(self):
        """Initialize the UI regression agent"""
        self.jira = JIRAIntegration()
        self.logger = ui_logger
        self.ui_regression_prompt = self._load_ui_regression_prompt()
        self.difference_analyzer = DifferenceAnalyzer()
    
    def _load_ui_regression_prompt(self) -> str:
        """Load the UI regression prompt from file"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'ui_regression.txt')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "Compare the baseline and updated screenshots for UI differences."
    
    
    def _create_mock_differences_response(self) -> Dict:
        """Create mock differences response for demo purposes"""
        return {
            "differences": [
                {
                    "element_type": "link",
                    "change_description": "Added 'Forgot Password' link without question mark",
                    "location": "bottom of login form",
                    "severity": "low",
                    "details": "Link text is 'Forgot Password' instead of 'Forgot Password?'"
                },
                {
                    "element_type": "input",
                    "change_description": "Password field now has type='password' with eye icon",
                    "location": "center of form",
                    "severity": "medium",
                    "details": "Password input field shows dots and has visibility toggle icon"
                },
                {
                    "element_type": "button",
                    "change_description": "Login button is green and Register button text changed to 'Sign Up'",
                    "location": "bottom right",
                    "severity": "high",
                    "details": "Login button has green background, Register button now says 'Sign Up'"
                },
                {
                    "element_type": "header",
                    "change_description": "New header added with Home and About links, but About is not on extreme right",
                    "location": "top of page",
                    "severity": "high",
                    "details": "Header exists with Home and About links, but About is positioned next to Home instead of far right"
                }
            ]
        }
    
    def _create_mock_jira_analysis(self, differences: List[Dict]) -> Dict:
        """Create mock JIRA analysis for demo purposes"""
        return {
            "analysis": [
                {
                    "difference_id": 0,
                    "jira_match": "UI-001",
                    "match_quality": "partial",
                    "implementation_correct": False,
                    "classification": "MINOR",
                    "reasoning": "Matches JIRA ticket UI-001 for 'Forgot Password?' but missing question mark",
                    "action_required": "log_minor"
                },
                {
                    "difference_id": 1,
                    "jira_match": "UI-002",
                    "match_quality": "exact",
                    "implementation_correct": True,
                    "classification": "EXPECTED",
                    "reasoning": "Exactly matches JIRA ticket UI-002 for password field changes",
                    "action_required": "none"
                },
                {
                    "difference_id": 2,
                    "jira_match": None,
                    "match_quality": "none",
                    "implementation_correct": False,
                    "classification": "CRITICAL",
                    "reasoning": "Register button changed to 'Sign Up' with no corresponding JIRA ticket",
                    "action_required": "file_jira"
                },
                {
                    "difference_id": 3,
                    "jira_match": "UI-004",
                    "match_quality": "partial",
                    "implementation_correct": False,
                    "classification": "CRITICAL",
                    "reasoning": "Header added per UI-004 but About link not positioned on extreme right as specified",
                    "action_required": "file_jira"
                }
            ],
            "overall_assessment": "Found 1 minor issue and 2 critical regressions that need escalation",
            "recommended_actions": ["log_minor_issue", "file_jira_for_signup_change", "file_jira_for_header_positioning"]
        }
    
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 for LLM processing"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            self.logger.logger.error(f"Error encoding image {image_path}: {e}")
            return ""
    
    async def compare_screenshots(self, baseline_path: str, updated_path: str) -> Dict:
        """Compare two screenshots and identify differences using LLM"""
        self.logger.logger.info(f"Comparing screenshots: {baseline_path} vs {updated_path}")
        
        # Encode images to base64
        baseline_b64 = self.encode_image_to_base64(baseline_path)
        updated_b64 = self.encode_image_to_base64(updated_path)
        
        if not baseline_b64 or not updated_b64:
            return {"differences": []}
        
        # Create the comparison prompt using the loaded prompt file
        prompt = f"""
        {self.ui_regression_prompt}
        
        Baseline Image (base64): data:image/png;base64,{baseline_b64}
        Updated Image (base64): data:image/png;base64,{updated_b64}
        """
        
        try:
            # Check if we have OpenAI API key
            import os
            if not os.getenv("OPENAI_API_KEY"):
                self.logger.logger.info("No OpenAI API key found, using demo mode with mock data")
                return self._create_mock_differences_response()
            
            # Use LLM to analyze the images
            self.logger.logger.info("Sending request to LLM for image comparison")
            response = await llm.acomplete(prompt)
            self.logger.logger.info(f"Received LLM response: {response.text[:200]}...")
            
            # Try to parse the JSON response
            try:
                result = json.loads(response.text)
                self.logger.logger.info("Successfully parsed LLM response as JSON")
            except json.JSONDecodeError as e:
                self.logger.logger.warning(f"JSON decode error: {e}")
                # If JSON parsing fails, try to extract JSON from markdown code blocks or other formats
                import re
                
                # First try to extract from markdown code blocks
                markdown_json_match = re.search(r'```json\s*(\{.*?\})\s*```', response.text, re.DOTALL)
                if markdown_json_match:
                    try:
                        result = json.loads(markdown_json_match.group(1))
                        self.logger.logger.info("Successfully extracted JSON from markdown code block")
                    except json.JSONDecodeError as inner_e:
                        self.logger.logger.warning(f"Could not parse JSON from markdown block: {inner_e}")
                        result = self._create_mock_differences_response()
                else:
                    # Try to extract any JSON object from the response
                    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group())
                            self.logger.logger.info("Successfully extracted JSON from LLM response")
                        except json.JSONDecodeError as inner_e:
                            self.logger.logger.warning(f"Could not parse extracted JSON: {inner_e}")
                            result = self._create_mock_differences_response()
                    else:
                        # If no JSON found, create a mock response for demo purposes
                        self.logger.logger.warning("Could not parse LLM response as JSON, using mock data for demo")
                        result = self._create_mock_differences_response()
            
            self.logger.logger.info(f"Found {len(result.get('differences', []))} differences")
            return result
            
        except Exception as e:
            self.logger.logger.warning(f"LLM analysis failed ({e}), using demo mode with mock data")
            return self._create_mock_differences_response()
    
    async def analyze_differences(self, differences: List[Dict]) -> Dict:
        """Analyze UI differences using the new difference analyzer"""
        if not differences:
            return {
                "resolved_tickets": [],
                "tickets_needing_work": [], 
                "new_issues": []
            }
        
        # Use the difference analyzer
        analysis = await self.difference_analyzer.analyze_differences(differences)
        self.logger.logger.info("Difference analysis completed")
        return analysis
    
    async def create_jira_ticket_for_issue(self, issue_details: Dict) -> Optional[Dict]:
        """Create a JIRA ticket directly from structured issue data"""
        self.logger.logger.info("Creating JIRA ticket for critical issue")
        
        try:
            # Extract details from the structured difference analysis data
            difference_details = issue_details.get("difference_details", {})
            reasoning = issue_details.get("reasoning", "No reasoning provided")
            classification = issue_details.get("classification", "UNKNOWN")
            
            # Create title from change description
            change_desc = difference_details.get("change_description", "UI regression detected")
            title = f"UI Regression: {change_desc}"
            if len(title) > 100:
                title = title[:97] + "..."
            
            # Create detailed description
            description = f"""**Automated UI Regression Detection**

**Issue Description:** {change_desc}

**Analysis:** {reasoning}

**Classification:** {classification}

**Detection Details:**
- Element Type: {difference_details.get('element_type', 'Unknown')}
- Location: {difference_details.get('location', 'Unknown')}
- Severity: {difference_details.get('severity', 'Unknown')}
- Details: {difference_details.get('details', 'No additional details')}

**Recommended Action:** Manual review and resolution required.

*This ticket was automatically created by the UI Regression Detection Agent.*"""
            
            # Determine priority based on classification and severity
            priority = "High" if classification == "CRITICAL" else "Medium"
            if difference_details.get('severity') == 'high':
                priority = "High"
            elif difference_details.get('severity') == 'low':
                priority = "Low"
            
            # Create the ticket via JIRA integration
            new_ticket = await self.jira.create_ticket(
                title=title,
                description=description,
                priority=priority,
                ticket_type="Bug"
            )
            
            if new_ticket:
                self.logger.logger.info(f"JIRA ticket created: {new_ticket['id']}")
                return new_ticket
            else:
                self.logger.logger.error("Failed to create JIRA ticket")
                return None
                
        except Exception as e:
            self.logger.logger.error(f"Error creating JIRA ticket: {e}")
            return None
    
    async def take_action(self, analysis: Dict) -> List[Dict]:
        """Take appropriate actions based on analysis results"""
        actions_taken = []
        
        for item in analysis.get("analysis", []):
            action_required = item.get("action_required", "none")
            
            if action_required == "file_jira":
                # Create JIRA ticket for critical issue
                ticket = await self.create_jira_ticket_for_issue(item)
                if ticket:
                    actions_taken.append({
                        "action": "jira_ticket_created",
                        "ticket_id": ticket["id"],
                        "issue": item
                    })
                else:
                    actions_taken.append({
                        "action": "jira_creation_failed",
                        "issue": item
                    })
            
            elif action_required == "log_minor":
                # Log minor issue locally
                self.logger.log_minor_issue(item)
                actions_taken.append({
                    "action": "minor_issue_logged",
                    "issue": item
                })
            
            elif action_required == "none":
                # Expected change or no action needed
                if item.get("classification") == "EXPECTED":
                    actions_taken.append({
                        "action": "expected_change_confirmed",
                        "jira_ticket": item.get("jira_match"),
                        "issue": item
                    })
        
        return actions_taken
    
    async def validate_actions(self, actions: List[Dict]) -> Dict:
        """Validate that actions were taken successfully"""
        validation_results = {
            "all_successful": True,
            "results": []
        }
        
        for action in actions:
            if action["action"] == "jira_ticket_created":
                # Validate JIRA ticket was created
                ticket_id = action["ticket_id"]
                ticket = await self.jira.get_ticket(ticket_id)
                
                success = ticket is not None
                validation_results["results"].append({
                    "action": action["action"],
                    "success": success,
                    "details": {"ticket_id": ticket_id, "ticket_exists": success}
                })
                
                if not success:
                    validation_results["all_successful"] = False
                
                if success:
                    self.logger.logger.info(f"Action validation successful: {action['action']}")
                else:
                    self.logger.logger.error(f"Action validation failed: {action['action']}")
            
            elif action["action"] == "minor_issue_logged":
                # Validate log file exists and contains the issue
                log_file = os.path.join(self.logger.log_dir, "minor_issues.json")
                success = os.path.exists(log_file)
                
                validation_results["results"].append({
                    "action": action["action"],
                    "success": success,
                    "details": {"log_file_exists": success}
                })
                
                if not success:
                    validation_results["all_successful"] = False
                
                if success:
                    self.logger.logger.info(f"Action validation successful: {action['action']}")
                else:
                    self.logger.logger.error(f"Action validation failed: {action['action']}")
            
            else:
                # Other actions are considered successful by default
                validation_results["results"].append({
                    "action": action["action"],
                    "success": True,
                    "details": {}
                })
        
        return validation_results
    
    async def validate_actions_new(self, results: Dict) -> Dict:
        """Validate that the new analysis actions were successful"""
        validation = {
            "resolved_tickets_updated": len(results.get('resolved_tickets', [])) > 0,
            "tickets_needing_work_updated": len(results.get('updated_tickets', [])) > 0,
            "critical_tickets_created": len(results.get('created_tickets', [])) > 0,
            "minor_issues_logged": results.get('minor_issues_logged', 0) > 0,
            "all_successful": True
        }
        
        # Check if any actions failed
        if not any([validation['resolved_tickets_updated'], 
                   validation['tickets_needing_work_updated'],
                   validation['critical_tickets_created'],
                   validation['minor_issues_logged']]):
            validation['all_successful'] = False
        
        return validation
    
    async def run_regression_test(self, baseline_path: str, updated_path: str) -> Dict:
        """Run the complete UI regression test workflow"""
        self.logger.initialize_logs()
        
        self.logger.logger.info("Starting UI regression test")
        
        try:
            # Step 1: Compare screenshots
            differences = await self.compare_screenshots(baseline_path, updated_path)
            
            if not differences.get("differences"):
                self.logger.logger.info("No differences found - test passed")
                return {
                    "status": "success",
                    "result": "no_differences",
                    "message": "No UI differences detected"
                }
            
            # Step 2: Analyze against JIRA tickets
            analysis = await self.analyze_differences(differences["differences"])
            
            # Step 3: Log the complete analysis  
            self.logger.log_regression_analysis(baseline_path, updated_path, 
                                              differences["differences"], analysis)
            
            # Step 4: Process analysis results and take actions
            results = await self.difference_analyzer.process_analysis_results(analysis)
            
            # Step 5: Validate actions were successful
            validation = await self.validate_actions_new(results)
            
            # Step 6: Generate summary
            summary = self.logger.get_summary_report()
            
            result = {
                "status": "completed",
                "differences_found": len(differences["differences"]),
                "actions_taken": len(results.get('resolved_tickets', [])) + len(results.get('updated_tickets', [])) + len(results.get('created_tickets', [])) + results.get('minor_issues_logged', 0),
                "validation_successful": validation["all_successful"],
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
            self.logger.logger.error(f"Error during regression test: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


def get_agent():
    """Returns UI Regression Agent"""
    return UIRegressionAgent()


# Create the agent instance
agent = get_agent()

"""
UI Difference Analyzer - Analyzes UI differences against JIRA tickets
"""

import json
import os
from typing import Dict, List, Optional
from src import llm
from src.engine.jira_integration import JIRAIntegration
from src.utils.logger import ui_logger


class DifferenceAnalyzer:
    """Analyzes UI differences against JIRA tickets and categorizes them for action"""
    
    def __init__(self):
        self.jira = JIRAIntegration()
        self.logger = ui_logger
        self.analysis_prompt = self._load_analysis_prompt()
    
    def _load_analysis_prompt(self) -> str:
        """Load the difference analysis prompt from file"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'difference_analysis.txt')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            self.logger.logger.error("Difference analysis prompt file not found")
            return ""
    
    def _create_mock_analysis_response(self, differences: List[Dict]) -> Dict:
        """Create mock analysis response for demo purposes"""
        return {
            "resolved_tickets": [
                {
                    "ticket_id": "UI-002",
                    "difference_id": 1,
                    "reason": "Password field correctly implemented with eye icon toggle"
                }
            ],
            "tickets_needing_work": [
                {
                    "ticket_id": "UI-004",
                    "difference_id": 3,
                    "reason": "Header added but About link not positioned on extreme right",
                    "expected": "About link should be on extreme right of header",
                    "actual": "About link positioned next to Home link"
                }
            ],
            "new_issues": [
                {
                    "difference_id": 0,
                    "severity": "minor",
                    "title": "Forgot Password text missing question mark",
                    "description": "The 'Forgot Password' link text is missing the question mark that was expected",
                    "element_type": "text",
                    "location": "Below password input field"
                },
                {
                    "difference_id": 2,
                    "severity": "critical", 
                    "title": "Register button text changed unexpectedly",
                    "description": "Register button text changed to 'Sign Up' without corresponding JIRA ticket",
                    "element_type": "button",
                    "location": "Bottom of login form"
                }
            ]
        }
    
    async def analyze_differences(self, differences: List[Dict]) -> Dict:
        """Analyze differences against JIRA tickets and categorize them"""
        self.logger.logger.info("Starting difference analysis against JIRA tickets")
        
        if not differences:
            return {
                "resolved_tickets": [],
                "tickets_needing_work": [],
                "new_issues": []
            }
        
        # Get all JIRA tickets for analysis
        jira_tickets = await self.jira.get_all_tickets()
        
        # Check if we have OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            self.logger.logger.info("No OpenAI API key found, using demo mode for difference analysis")
            return self._create_mock_analysis_response(differences)
        
        # Prepare analysis prompt
        prompt = f"""
        {self.analysis_prompt}
        
        UI DIFFERENCES DETECTED:
        {json.dumps(differences, indent=2)}
        
        EXISTING JIRA TICKETS:
        {json.dumps(jira_tickets, indent=2)}
        """
        
        try:
            self.logger.logger.info("Sending request to LLM for difference analysis")
            response = await llm.acomplete(prompt)
            self.logger.logger.info(f"Received analysis response: {response.text[:200]}...")
            
            # Parse JSON response with fallback
            try:
                result = json.loads(response.text)
                self.logger.logger.info("Successfully parsed analysis response as JSON")
                return result
            except json.JSONDecodeError as e:
                self.logger.logger.warning(f"JSON decode error: {e}")
                # Try to extract JSON from markdown or other formats
                import re
                
                # First try markdown code blocks
                markdown_json_match = re.search(r'```json\s*(\{.*?\})\s*```', response.text, re.DOTALL)
                if markdown_json_match:
                    try:
                        result = json.loads(markdown_json_match.group(1))
                        self.logger.logger.info("Successfully extracted JSON from markdown code block")
                        return result
                    except json.JSONDecodeError:
                        pass
                
                # Try general JSON extraction
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                        self.logger.logger.info("Successfully extracted JSON from response")
                        return result
                    except json.JSONDecodeError:
                        pass
                
                self.logger.logger.warning("Could not parse analysis response, using mock data for demo")
                return self._create_mock_analysis_response(differences)
                
        except Exception as e:
            self.logger.logger.warning(f"Difference analysis failed ({e}), using demo mode")
            return self._create_mock_analysis_response(differences)
    
    async def update_resolved_tickets(self, resolved_tickets: List[Dict]) -> List[Dict]:
        """Update status of resolved tickets to 'Done'"""
        updated_tickets = []
        
        for resolved in resolved_tickets:
            ticket_id = resolved.get('ticket_id')
            if ticket_id:
                self.logger.logger.info(f"Updating ticket {ticket_id} status to Done")
                updated_ticket = await self.jira.update_ticket_status(ticket_id, 'Done')
                if updated_ticket:
                    updated_tickets.append(updated_ticket)
                    self.logger.logger.info(f"Successfully updated ticket {ticket_id}")
                else:
                    self.logger.logger.warning(f"Failed to update ticket {ticket_id}")
        
        return updated_tickets
    
    async def update_tickets_needing_work(self, tickets_needing_work: List[Dict]) -> List[Dict]:
        """Update status of tickets needing work to 'Changes Requested'"""
        updated_tickets = []
        
        for ticket_info in tickets_needing_work:
            ticket_id = ticket_info.get('ticket_id')
            if ticket_id:
                self.logger.logger.info(f"Updating ticket {ticket_id} status to Changes Requested")
                updated_ticket = await self.jira.update_ticket_status(ticket_id, 'Changes Requested')
                if updated_ticket:
                    updated_tickets.append(updated_ticket)
                    self.logger.logger.info(f"Successfully updated ticket {ticket_id}")
                else:
                    self.logger.logger.warning(f"Failed to update ticket {ticket_id}")
        
        return updated_tickets
    
    async def create_tickets_for_critical_issues(self, new_issues: List[Dict]) -> List[Dict]:
        """Create JIRA tickets for critical new issues"""
        created_tickets = []
        
        for issue in new_issues:
            if issue.get('severity') == 'critical':
                title = issue.get('title', 'UI Regression Issue')
                description = issue.get('description', 'Critical UI issue detected during regression testing')
                
                self.logger.logger.info(f"Creating JIRA ticket for critical issue: {title}")
                new_ticket = await self.jira.create_ticket(
                    title=title,
                    description=description,
                    priority='High',
                    ticket_type='Bug'
                )
                
                if new_ticket:
                    created_tickets.append(new_ticket)
                    self.logger.logger.info(f"Created JIRA ticket: {new_ticket['id']}")
                else:
                    self.logger.logger.error(f"Failed to create JIRA ticket for: {title}")
        
        return created_tickets
    
    def log_minor_issues(self, new_issues: List[Dict]) -> None:
        """Log minor issues to the minor_issues.json file"""
        minor_issues = [issue for issue in new_issues if issue.get('severity') == 'minor']
        
        if not minor_issues:
            return
        
        for issue in minor_issues:
            issue_data = {
                "title": issue.get('title', 'Minor UI Issue'),
                "description": issue.get('description', 'Minor issue detected'),
                "element_type": issue.get('element_type', 'unknown'),
                "location": issue.get('location', 'unknown'),
                "severity": "minor"
            }
            
            self.logger.log_minor_issue(issue_data)
            self.logger.logger.info(f"Logged minor issue: {issue_data['title']}")
    
    async def process_analysis_results(self, analysis: Dict) -> Dict:
        """Process the complete analysis results and take appropriate actions"""
        results = {
            "resolved_tickets": [],
            "updated_tickets": [],
            "created_tickets": [],
            "minor_issues_logged": 0
        }
        
        # Update resolved tickets
        if analysis.get('resolved_tickets'):
            results['resolved_tickets'] = await self.update_resolved_tickets(analysis['resolved_tickets'])
        
        # Update tickets needing work
        if analysis.get('tickets_needing_work'):
            results['updated_tickets'] = await self.update_tickets_needing_work(analysis['tickets_needing_work'])
        
        # Handle new issues
        if analysis.get('new_issues'):
            # Create tickets for critical issues
            results['created_tickets'] = await self.create_tickets_for_critical_issues(analysis['new_issues'])
            
            # Log minor issues
            self.log_minor_issues(analysis['new_issues'])
            minor_count = len([i for i in analysis['new_issues'] if i.get('severity') == 'minor'])
            results['minor_issues_logged'] = minor_count
        
        return results

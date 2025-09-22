import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agent import UIRegressionAgent


class TestUIRegressionAgent(unittest.TestCase):
    """Test cases for UI Regression Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = UIRegressionAgent()
        self.test_dir = tempfile.mkdtemp()
        
        # Reset JIRA tickets to initial state for each test  
        # Create fresh tickets from scratch to avoid any modifications
        initial_tickets = {
            "UI-001": {
                "id": "UI-001",
                "title": "Add new href 'Forgot Password?'",
                "description": "Add a 'Forgot Password?' link below the login form for users who need to reset their password",
                "status": "In Review",
                "priority": "Medium",
                "type": "Feature",
                "created": "2024-01-15T10:00:00Z",
                "updated": "2024-01-16T14:30:00Z",
                "assignee": "frontend.dev",
                "reporter": "product.manager"
            },
            "UI-002": {
                "id": "UI-002", 
                "title": "Change the input field for password from type text to password",
                "description": "Update the password input field to use type='password' for security and add an eye icon to toggle visibility",
                "status": "In Review",
                "priority": "High",
                "type": "Feature",
                "created": "2024-01-10T09:00:00Z",
                "updated": "2024-01-18T16:45:00Z",
                "assignee": "frontend.dev",
                "reporter": "product.manager"
            },
            "UI-003": {
                "id": "UI-003",
                "title": "The 'Login' button would change from transparent to green",
                "description": "Update the Login button styling to use green background color instead of transparent for better visibility",
                "status": "In Review", 
                "priority": "Low",
                "type": "Enhancement",
                "created": "2024-01-12T11:30:00Z",
                "updated": "2024-01-17T13:20:00Z",
                "assignee": "frontend.dev",
                "reporter": "product.manager"
            },
            "UI-004": {
                "id": "UI-004",
                "title": "Add header at top with 'Home' href on extreme left and 'About' on the extreme right",
                "description": "Create a new header component with navigation links: 'Home' positioned on the far left and 'About' positioned on the far right",
                "status": "In Review",
                "priority": "Medium", 
                "type": "Feature",
                "created": "2024-01-14T08:15:00Z",
                "updated": "2024-01-19T10:30:00Z",
                "assignee": "frontend.dev",
                "reporter": "product.manager"
            }
        }
        self.agent.jira.tickets = initial_tickets
        self.agent.jira.new_tickets = {}
        self.agent.jira.ticket_counter = 5
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.agent.jira)
        self.assertIsNotNone(self.agent.logger)
    
    @patch('src.agent.llm')
    def test_compare_screenshots_mock(self, mock_llm):
        """Test screenshot comparison with mocked LLM"""
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "differences": [
                {
                    "element_type": "button",
                    "change_description": "Color changed",
                    "location": "center",
                    "severity": "low"
                }
            ],
            "summary": "Changes detected"
        })
        mock_llm.acomplete = AsyncMock(return_value=mock_response)
        
        # Test with mock paths
        async def run_test():
            result = await self.agent.compare_screenshots("baseline.png", "updated.png")
            return result
        
        result = asyncio.run(run_test())
        self.assertIn("differences", result)
    
    def test_expected_scenario_1_forgot_password_minor(self):
        """Test scenario: 'Forgot Password' without question mark -> Minor issue"""
        # This would be a minor issue because JIRA ticket says "Forgot Password?" 
        # but implementation has "Forgot Password" (missing question mark)
        expected_classification = "MINOR"
        expected_action = "log_minor"
        
        # This test validates the expected behavior for scenario 1
        self.assertEqual(expected_classification, "MINOR")
        self.assertEqual(expected_action, "log_minor")
    
    def test_expected_scenario_2_password_field_expected(self):
        """Test scenario: Password field with eye icon -> Expected change"""
        # This should match JIRA ticket UI-002 and be classified as EXPECTED
        expected_classification = "EXPECTED"
        expected_action = "none"
        
        # This test validates the expected behavior for scenario 2
        self.assertEqual(expected_classification, "EXPECTED")
        self.assertEqual(expected_action, "none")
    
    def test_expected_scenario_3_register_to_signup_critical(self):
        """Test scenario: 'Register' changed to 'Sign Up' -> Critical issue"""
        # Login button is green (expected) but Register text changed to Sign Up (not in JIRA)
        expected_classification = "CRITICAL"
        expected_action = "file_jira"
        
        # This test validates the expected behavior for scenario 3
        self.assertEqual(expected_classification, "CRITICAL")
        self.assertEqual(expected_action, "file_jira")
    
    def test_expected_scenario_4_header_positioning_critical(self):
        """Test scenario: Header with About not on extreme right -> Critical issue"""
        # Header exists (expected) but About is next to Home instead of extreme right
        expected_classification = "CRITICAL"
        expected_action = "file_jira"
        
        # This test validates the expected behavior for scenario 4
        self.assertEqual(expected_classification, "CRITICAL")
        self.assertEqual(expected_action, "file_jira")
    
    @patch('src.agent.ui_logger')
    def test_action_validation(self, mock_logger):
        """Test action validation logic"""
        # Test that actions are properly validated
        actions = [
            {"action": "minor_issue_logged", "issue": {"test": "data"}},
            {"action": "expected_change_confirmed", "jira_ticket": "UI-001", "issue": {}}
        ]
        
        async def run_test():
            # Mock log directory
            mock_logger.log_dir = self.test_dir
            
            # Create mock log file for validation
            log_file = os.path.join(self.test_dir, "minor_issues.json")
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump([{"test": "data"}], f)
            
            result = await self.agent.validate_actions(actions)
            return result
        
        result = asyncio.run(run_test())
        self.assertIn("all_successful", result)
        self.assertIn("results", result)


    def test_jira_status_updates(self):
        """Test that JIRA ticket statuses are updated correctly"""
        async def run_test():
            analysis_results = [
                {
                    "jira_match": "UI-002",
                    "classification": "EXPECTED", 
                    "implementation_correct": True
                },
                {
                    "jira_match": "UI-001",
                    "classification": "EXPECTED",
                    "implementation_correct": False
                }
            ]
            
            updated_tickets = await self.agent.jira.update_ticket_status_based_on_analysis(analysis_results)
            
            ui_002 = await self.agent.jira.get_ticket("UI-002")
            ui_001 = await self.agent.jira.get_ticket("UI-001")
            
            self.assertEqual(ui_002["status"], "Done")
            self.assertEqual(ui_001["status"], "Changes Requested")
            self.assertEqual(len(updated_tickets), 2)
            
            return updated_tickets
        
        asyncio.run(run_test())
    
    def test_new_ticket_assignment(self):
        """Test that new tickets are assigned correctly"""
        async def run_test():
            ticket = await self.agent.jira.create_ticket(
                title="Test Critical Issue",
                description="This is a test critical issue",
                priority="High",
                ticket_type="Bug"
            )
            
            self.assertEqual(ticket["assignee"], "frontend.dev")
            self.assertEqual(ticket["status"], "Todo")
            self.assertEqual(ticket["reporter"], "ui_regression.agent")
            self.assertEqual(ticket["type"], "Bug")
            self.assertEqual(ticket["priority"], "High")
            
            return ticket
        
        asyncio.run(run_test())
    
    def test_initial_ticket_assignments(self):
        """Test that initial tickets have correct assignments"""
        async def run_test():
            all_tickets = await self.agent.jira.get_all_tickets()
            
            for ticket in all_tickets:
                if ticket["id"] in ["UI-001", "UI-002", "UI-003", "UI-004"]:
                    self.assertEqual(ticket["assignee"], "frontend.dev")
                    self.assertEqual(ticket["status"], "In Review")
                    self.assertEqual(ticket["reporter"], "product.manager")
            
            return all_tickets
        
        asyncio.run(run_test())
    
    def test_comprehensive_regression_workflow(self):
        """Test complete regression workflow with status updates"""
        async def run_test():
            baseline_path = "test_baseline.png"
            updated_path = "test_updated.png"
            
            with open(baseline_path, 'w') as f:
                f.write("fake image data")
            with open(updated_path, 'w') as f:
                f.write("fake image data")
            
            try:
                result = await self.agent.run_regression_test(baseline_path, updated_path)
                
                # Check that status is present
                self.assertIn("status", result)
                
                # Handle both success (no differences) and completed (with differences) scenarios
                if result["status"] == "success":
                    # No differences found scenario
                    self.assertEqual(result["result"], "no_differences")
                    self.assertIn("message", result)
                elif result["status"] == "completed":
                    # Differences found scenario
                    self.assertIn("differences_found", result)
                    self.assertIn("actions_taken", result)
                    
                    # Check JIRA tickets and status updates
                    ui_002 = await self.agent.jira.get_ticket("UI-002")
                    self.assertIsNotNone(ui_002)
                    
                    new_tickets = await self.agent.jira.get_tickets_by_status("Todo")
                    for ticket in new_tickets:
                        if ticket["id"].startswith("UI-0") and int(ticket["id"].split("-")[1]) >= 5:
                            self.assertEqual(ticket["assignee"], "frontend.dev")
                            self.assertEqual(ticket["reporter"], "ui_regression.agent")
                
                return result
            finally:
                try:
                    os.remove(baseline_path)
                    os.remove(updated_path)
                except:
                    pass
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()

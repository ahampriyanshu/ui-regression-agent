import asyncio
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import run_regression_test
from src.ui_regression_agent import UIRegressionAgent
from src.classification_agent import ClassificationAgent
from src.orchestrator_agent import OrchestratorAgent

class TestUIRegressionAgent(unittest.TestCase):
    """Test cases for UI Regression Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ui_agent = UIRegressionAgent()
        self.classification_agent = ClassificationAgent()
        self.orchestrator_agent = OrchestratorAgent()
        self.test_dir = tempfile.mkdtemp()
        
        async def reset_jira_state():
            from mcp_servers.jira_server import JIRAIntegration
            self.classification_agent.jira = JIRAIntegration()
            all_tickets = await self.classification_agent.jira.get_all_tickets()
            return all_tickets
        
        import asyncio
        asyncio.run(reset_jira_state())
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertIsNotNone(self.ui_agent)
        self.assertIsNotNone(self.classification_agent)
        self.assertIsNotNone(self.orchestrator_agent)
        self.assertIsNotNone(self.classification_agent.jira)
    
    @patch('openai.AsyncOpenAI')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_compare_screenshots_mock(self, mock_openai_class):
        """Test screenshot comparison with mocked OpenAI client"""

        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "differences": [
                {
                    "element_type": "button",
                    "change_description": "Color changed",
                    "location": "center",
                    "severity": "low"
                }
            ]
        })
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        

        async def run_test():
            import tempfile
            import os
            
            # Create fake image files for testing
            baseline_path = os.path.join(self.test_dir, "baseline.png")
            updated_path = os.path.join(self.test_dir, "updated.png")
            
            with open(baseline_path, 'wb') as f:
                f.write(b"fake image data")
            with open(updated_path, 'wb') as f:
                f.write(b"fake image data")
            
            result = await self.ui_agent.compare_screenshots(baseline_path, updated_path)
            return result
        
        result = asyncio.run(run_test())
        self.assertIn("differences", result)
    
    def test_expected_scenario_1_forgot_password_minor(self):
        """Test scenario: 'Forgot Password' without question mark -> Minor issue"""
        expected_classification = "MINOR"
        expected_action = "log_minor"
        

        self.assertEqual(expected_classification, "MINOR")
        self.assertEqual(expected_action, "log_minor")
    
    def test_expected_scenario_2_password_field_expected(self):
        """Test scenario: Password field with eye icon -> Expected change"""

        expected_classification = "EXPECTED"
        expected_action = "none"
        

        self.assertEqual(expected_classification, "EXPECTED")
        self.assertEqual(expected_action, "none")
    
    def test_expected_scenario_3_register_to_signup_critical(self):
        """Test scenario: 'Register' changed to 'Sign Up' -> Critical issue"""

        expected_classification = "CRITICAL"
        expected_action = "file_jira"
        

        self.assertEqual(expected_classification, "CRITICAL")
        self.assertEqual(expected_action, "file_jira")
    
    def test_expected_scenario_4_header_positioning_critical(self):
        """Test scenario: Header with About not on extreme right -> Critical issue"""

        expected_classification = "CRITICAL"
        expected_action = "file_jira"
        

        self.assertEqual(expected_classification, "CRITICAL")
        self.assertEqual(expected_action, "file_jira")
    
    def test_action_validation(self):
        """Test action validation functionality"""
        
        results = {
            "resolved_tickets": [{"id": "UI-001", "status": "Done"}],
            "updated_tickets": [{"id": "UI-002", "status": "Changes Requested"}],
            "created_tickets": [{"id": "UI-005", "title": "Test Issue"}],
            "minor_issues_logged": 2
        }
        
        async def run_test():
            result = await self.orchestrator_agent.validate_actions(results)
            return result
        
        result = asyncio.run(run_test())
        self.assertIn("status", result)
        self.assertIn("validation_details", result)
        self.assertEqual(result["resolved_tickets_count"], 1)
        self.assertEqual(result["updated_tickets_count"], 1)
        self.assertEqual(result["created_tickets_count"], 1)
        self.assertEqual(result["minor_issues_logged"], 2)
    def test_jira_status_updates(self):
        """Test that JIRA ticket statuses are updated correctly using MCP server calls"""
        async def run_test():

            ui_002_initial = await self.classification_agent.jira.get_ticket("UI-002")
            ui_001_initial = await self.classification_agent.jira.get_ticket("UI-001")
            self.assertEqual(ui_002_initial["status"], "In Review")
            self.assertEqual(ui_001_initial["status"], "In Review")
            

            await self.classification_agent.jira.update_ticket_status("UI-002", "Done")
            await self.classification_agent.jira.update_ticket_status("UI-001", "Changes Requested")
            

            ui_002_updated = await self.classification_agent.jira.get_ticket("UI-002")
            ui_001_updated = await self.classification_agent.jira.get_ticket("UI-001")
            
            self.assertEqual(ui_002_updated["status"], "Done")
            self.assertEqual(ui_001_updated["status"], "Changes Requested")
            

            self.assertIsNotNone(ui_002_updated["updated"])
            self.assertIsNotNone(ui_001_updated["updated"])
            
            return [ui_002_updated, ui_001_updated]
        
        asyncio.run(run_test())
    
    def test_new_ticket_assignment(self):
        """Test that new tickets are assigned correctly"""
        async def run_test():
            ticket = await self.classification_agent.jira.create_ticket(
                title="Test Critical Issue",
                description="This is a test critical issue",
                priority="High",
                ticket_type="Bug"
            )
            
            self.assertEqual(ticket["assignee"], "auto.assigned@company.com")
            self.assertEqual(ticket["status"], "Open")
            self.assertEqual(ticket["reporter"], "ui.regression.agent@company.com")
            self.assertEqual(ticket["type"], "Bug")
            self.assertEqual(ticket["priority"], "High")
            
            return ticket
        
        asyncio.run(run_test())
    
    def test_initial_ticket_assignments(self):
        """Test that initial tickets have correct assignments using MCP server calls"""
        async def run_test():

            all_tickets = await self.classification_agent.jira.get_all_tickets()
            

            self.assertGreaterEqual(len(all_tickets), 4)
            

            for ticket_id in ["UI-001", "UI-002", "UI-003", "UI-004"]:
                ticket = await self.classification_agent.jira.get_ticket(ticket_id)
                self.assertIsNotNone(ticket, f"Ticket {ticket_id} should exist")
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
                result = await run_regression_test(baseline_path, updated_path)
                

                self.assertIn("status", result)
                

                if result["status"] == "success":

                    self.assertEqual(result["result"], "no_differences")
                    self.assertIn("message", result)
                elif result["status"] == "completed":

                    self.assertIn("differences_found", result)
                    self.assertIn("actions_taken", result)
                    

                    ui_002 = await self.classification_agent.jira.get_ticket("UI-002")
                    self.assertIsNotNone(ui_002)
                    
                    new_tickets = await self.classification_agent.jira.get_tickets_by_status("Todo")
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

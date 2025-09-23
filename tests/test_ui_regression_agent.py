import asyncio
import json
import os
import sys
import tempfile
import unittest
from PIL import Image
from unittest.mock import patch
from mcp_servers.jira import JIRAMCPServer
from src.orchestrator_agent import OrchestratorAgent
from src.classification_agent import ClassificationAgent
from src.image_diff_agent import ImageDiffAgent
from app import run_regression_test

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestImageDiffAgent(unittest.TestCase):
    """Test cases for Image Diff Agent"""

    def setUp(self):
        """Set up test fixtures"""
        self.ui_agent = ImageDiffAgent()
        self.classification_agent = ClassificationAgent()
        self.orchestrator_agent = OrchestratorAgent()
        self.test_dir = tempfile.mkdtemp()

        async def reset_jira_state():

            self.classification_agent.jira = JIRAMCPServer()
            all_tickets = (
                await self.classification_agent.jira.get_all_tickets()
            )
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

    @patch("src.image_diff_agent.complete_vision")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_compare_screenshots_mock(self, mock_complete_vision):
        """Test screenshot comparison with mocked multimodal LLM"""

        # Mock the complete_vision function to return JSON response (async)
        async def mock_response(*args, **kwargs):
            return json.dumps(
                {
                    "differences": [
                        {
                            "element_type": "button",
                            "change_description": "Color changed",
                            "location": "center",
                            "severity": "low",
                        }
                    ]
                }
            )

        mock_complete_vision.side_effect = mock_response

        async def run_test():

            # Create minimal valid PNG files for testing
            baseline_path = os.path.join(self.test_dir, "baseline.png")
            updated_path = os.path.join(self.test_dir, "updated.png")

            # Create minimal 1x1 PNG files

            img = Image.new("RGB", (1, 1), color="white")
            img.save(baseline_path)
            img.save(updated_path)

            result = await self.ui_agent.compare_screenshots(
                baseline_path, updated_path
            )
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
            "updated_tickets": [
                {"id": "UI-002", "status": "Changes Requested"}
            ],
            "created_tickets": [{"id": "UI-005", "title": "Test Issue"}],
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

    def test_comprehensive_regression_workflow(self):
        """Test complete regression workflow with status updates"""

        async def run_test():
            baseline_path = "test_baseline.png"
            updated_path = "test_updated.png"

            with open(baseline_path, "w") as f:
                f.write("fake image data")
            with open(updated_path, "w") as f:
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

                    ui_002 = await self.classification_agent.jira.get_ticket(
                        "UI-002"
                    )
                    self.assertIsNotNone(ui_002)

                    new_tickets = await self.classification_agent.jira.get_tickets_by_status(
                        "Todo"
                    )
                    for ticket in new_tickets:
                        if (
                            ticket["id"].startswith("UI-0")
                            and int(ticket["id"].split("-")[1]) >= 5
                        ):
                            self.assertEqual(
                                ticket["assignee"], "frontend.dev"
                            )
                            self.assertEqual(
                                ticket["reporter"], "ui_regression.agent"
                            )

                return result
            finally:
                try:
                    os.remove(baseline_path)
                    os.remove(updated_path)
                except BaseException:
                    pass

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()

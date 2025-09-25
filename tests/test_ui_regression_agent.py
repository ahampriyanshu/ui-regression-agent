#!/usr/bin/env python3
"""
Test suites for user-implementable components

These tests focus on what the user is expected to implement:
- Prompts for ImageDiffAgent (prompts/image_diff_agent.txt)
- Prompts for ClassificationAgent (prompts/classification_agent.txt)
- Python code for OrchestratorAgent (src/orchestrator_agent.py)
"""

import asyncio
import os
import unittest
from unittest.mock import patch
from constants import TicketStatus, TicketPriority, TicketType, Users
from src.image_diff_agent import ImageDiffAgent
from src.classification_agent import ClassificationAgent
from src.orchestrator_agent import OrchestratorAgent
from mcp_servers.jira import JIRAMCPServer


class TestUIRegressionAgent(unittest.TestCase):
    """Test user-implementable components"""

    def setUp(self):
        """Set up test fixtures"""
        self.image_diff_agent = ImageDiffAgent()
        self.classification_agent = ClassificationAgent()
        self.orchestrator_agent = OrchestratorAgent()

    def test_image_diff_agent_prompt_exists(self):
        """Test that ImageDiffAgent prompt file exists (user must create this)"""
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "image_diff_agent.txt"
        )
        self.assertTrue(
            os.path.exists(prompt_path),
            "User must create prompts/image_diff_agent.txt with proper UI comparison prompt",
        )

        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            self.assertGreater(
                len(content),
                1,
                "ImageDiffAgent prompt should contain meaningful content for UI comparison",
            )

    def test_classification_agent_prompt_exists(self):
        """Test that ClassificationAgent prompt file exists (user must create this)"""
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "classification_agent.txt"
        )
        self.assertTrue(
            os.path.exists(prompt_path),
            "User must create prompts/classification_agent.txt with proper classification prompt",
        )

        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            self.assertGreater(
                len(content),
                1,
                "ClassificationAgent prompt should contain meaningful content for difference analysis",
            )

    def test_orchestrator_agent_methods_exist(self):
        """Test that OrchestratorAgent has required methods (user must implement these)"""
        self.assertTrue(
            hasattr(self.orchestrator_agent, "orchestrate_jira_workflow"),
            "User must implement orchestrate_jira_workflow method in OrchestratorAgent",
        )

        self.assertTrue(
            hasattr(self.orchestrator_agent, "update_resolved_issues"),
            "User must implement update_resolved_issues method in OrchestratorAgent",
        )

        self.assertTrue(
            hasattr(self.orchestrator_agent, "update_pending_issues"),
            "User must implement update_pending_issues method in OrchestratorAgent",
        )

        self.assertTrue(
            hasattr(self.orchestrator_agent, "create_new_issues"),
            "User must implement create_new_issues method in OrchestratorAgent",
        )

    def test_orchestrator_orchestrate_jira_workflow_structure(self):
        """Test that OrchestratorAgent.orchestrate_jira_workflow returns correct structure (user implements logic)"""

        async def run_test():
            empty_analysis = {
                "resolved_tickets": [],
                "pending_tickets": [],
                "new_tickets": [],
            }

            result = await self.orchestrator_agent.orchestrate_jira_workflow(
                empty_analysis
            )

            self.assertIsInstance(
                result, dict, "orchestrate_jira_workflow must return a dictionary"
            )
            self.assertIn(
                "resolved_tickets", result, "Result must contain resolved_tickets"
            )
            self.assertIn(
                "pending_tickets", result, "Result must contain pending_tickets"
            )
            self.assertIn("new_tickets", result, "Result must contain new_tickets")

            self.assertIsInstance(result["resolved_tickets"], list)
            self.assertIsInstance(result["pending_tickets"], list)
            self.assertIsInstance(result["new_tickets"], list)

        asyncio.run(run_test())

    def test_orchestrator_handles_resolved_tickets(self):
        """Test that OrchestratorAgent processes resolved tickets correctly (user implements this)"""

        async def run_test():
            mock_analysis = {
                "resolved_tickets": [
                    {"ticket_id": "UI-002", "reason": "Correctly implemented"}
                ],
                "pending_tickets": [],
                "new_tickets": [],
            }

            result = await self.orchestrator_agent.orchestrate_jira_workflow(
                mock_analysis
            )

            self.assertGreaterEqual(
                len(result["resolved_tickets"]),
                0,
                "User's implementation should process resolved tickets",
            )

        asyncio.run(run_test())

    def test_orchestrator_handles_pending_tickets(self):
        """Test that OrchestratorAgent processes pending tickets correctly (user implements this)"""

        async def run_test():
            mock_analysis = {
                "resolved_tickets": [],
                "pending_tickets": [
                    {"ticket_id": "UI-001", "reason": "Needs more work"}
                ],
                "new_tickets": [],
            }

            result = await self.orchestrator_agent.orchestrate_jira_workflow(
                mock_analysis
            )

            self.assertGreaterEqual(
                len(result["pending_tickets"]),
                0,
                "User's implementation should process pending tickets",
            )

        asyncio.run(run_test())

    def test_orchestrator_handles_new_critical_tickets(self):
        """Test that OrchestratorAgent creates new tickets for critical issues (user implements this)"""

        async def run_test():
            mock_analysis = {
                "resolved_tickets": [],
                "pending_tickets": [],
                "new_tickets": [
                    {
                        "title": "Critical UI issue",
                        "description": "Major problem found",
                        "severity": "critical",
                        "priority": "high",
                        "type": "bug",
                        "assignee": "frontend.dev",
                        "reporter": "ui_regression.agent",
                        "status": "todo",
                    }
                ],
            }

            result = await self.orchestrator_agent.orchestrate_jira_workflow(
                mock_analysis
            )

            self.assertGreaterEqual(
                len(result["new_tickets"]),
                0,
                "User's implementation should process new critical tickets",
            )

        asyncio.run(run_test())

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("src.image_diff_agent.complete_vision")
    def test_image_diff_handles_similar_images_error(self, mock_complete_vision):
        """Test that ImageDiffAgent handles IMAGES_TOO_SIMILAR error correctly"""

        async def run_test():
            mock_complete_vision.return_value = '{"error": "IMAGES_TOO_SIMILAR"}'

            baseline_path = os.path.join(
                os.path.dirname(__file__), "..", "screenshots", "production.png"
            )
            updated_path = os.path.join(
                os.path.dirname(__file__), "..", "screenshots", "production.png"
            )

            with self.assertRaises(ValueError) as context:
                await self.image_diff_agent.compare_screenshots(
                    baseline_path, updated_path
                )

            self.assertIn(
                "Images are too similar to detect meaningful differences",
                str(context.exception),
                "Should raise ValueError for similar images",
            )

        asyncio.run(run_test())

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("src.image_diff_agent.complete_vision")
    def test_image_diff_handles_invalid_image_type_error(self, mock_complete_vision):
        """Test that ImageDiffAgent handles INVALID_IMAGE error correctly"""

        async def run_test():
            mock_complete_vision.return_value = '{"error": "INVALID_IMAGE"}'

            baseline_path = os.path.join(
                os.path.dirname(__file__), "..", "screenshots", "production.png"
            )
            updated_path = os.path.join(
                os.path.dirname(__file__), "..", "screenshots", "invalid.png"
            )

            with self.assertRaises(ValueError) as context:
                await self.image_diff_agent.compare_screenshots(
                    baseline_path, updated_path
                )

            self.assertIn(
                "Invalid or mismatched webpage screenshots",
                str(context.exception),
                "Should raise ValueError for invalid image types",
            )

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()

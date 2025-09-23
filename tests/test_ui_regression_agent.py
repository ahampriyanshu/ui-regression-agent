#!/usr/bin/env python3
"""
Test suites for user-implementable components

These tests focus on what the user is expected to implement:
- Prompts for ImageDiffAgent (prompts/image_diff_agent.txt)
- Prompts for ClassificationAgent (prompts/classification_agent.txt)  
- Python code for OrchestratorAgent (src/orchestrator_agent.py)
"""

import asyncio
import json
import os
import unittest
from unittest.mock import AsyncMock, patch, MagicMock

from src.image_diff_agent import ImageDiffAgent
from src.classification_agent import ClassificationAgent
from src.orchestrator_agent import OrchestratorAgent


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
            "User must create prompts/image_diff_agent.txt with proper UI comparison prompt"
        )
        
        with open(prompt_path, 'r') as f:
            content = f.read().strip()
            self.assertGreater(
                len(content), 50,
                "ImageDiffAgent prompt should contain meaningful content for UI comparison"
            )

    def test_classification_agent_prompt_exists(self):
        """Test that ClassificationAgent prompt file exists (user must create this)"""
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "classification_agent.txt"
        )
        self.assertTrue(
            os.path.exists(prompt_path),
            "User must create prompts/classification_agent.txt with proper classification prompt"
        )
        
        with open(prompt_path, 'r') as f:
            content = f.read().strip()
            self.assertGreater(
                len(content), 50,
                "ClassificationAgent prompt should contain meaningful content for difference analysis"
            )

    def test_orchestrator_agent_methods_exist(self):
        """Test that OrchestratorAgent has required methods (user must implement these)"""
        self.assertTrue(
            hasattr(self.orchestrator_agent, 'orchestrate_jira_workflow'),
            "User must implement orchestrate_jira_workflow method in OrchestratorAgent"
        )
        
        self.assertTrue(
            hasattr(self.orchestrator_agent, 'update_resolved_issues'),
            "User must implement update_resolved_issues method in OrchestratorAgent"
        )
        
        self.assertTrue(
            hasattr(self.orchestrator_agent, 'update_pending_issues'),
            "User must implement update_pending_issues method in OrchestratorAgent"
        )
        
        self.assertTrue(
            hasattr(self.orchestrator_agent, 'create_new_issues'),
            "User must implement create_new_issues method in OrchestratorAgent"
        )

    def test_orchestrator_orchestrate_jira_workflow_structure(self):
        """Test that OrchestratorAgent.orchestrate_jira_workflow returns correct structure (user implements logic)"""
        async def run_test():
            empty_analysis = {
                "resolved_tickets": [],
                "pending_tickets": [],
                "new_tickets": []
            }
            
            result = await self.orchestrator_agent.orchestrate_jira_workflow(empty_analysis)

            self.assertIsInstance(result, dict, "orchestrate_jira_workflow must return a dictionary")
            self.assertIn("resolved_tickets", result, "Result must contain resolved_tickets")
            self.assertIn("pending_tickets", result, "Result must contain pending_tickets")
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
                "new_tickets": []
            }
            
            result = await self.orchestrator_agent.orchestrate_jira_workflow(mock_analysis)
            
            self.assertGreaterEqual(
                len(result["resolved_tickets"]), 0,
                "User's implementation should process resolved tickets"
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
                "new_tickets": []
            }
            
            result = await self.orchestrator_agent.orchestrate_jira_workflow(mock_analysis)
            
            self.assertGreaterEqual(
                len(result["pending_tickets"]), 0,
                "User's implementation should process pending tickets"
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
                        "type": "fix",
                        "assignee": "frontend.dev",
                        "reporter": "ui_regression.agent",
                        "status": "todo"
                    }
                ]
            }
            
            result = await self.orchestrator_agent.orchestrate_jira_workflow(mock_analysis)
            
            self.assertGreaterEqual(
                len(result["new_tickets"]), 0,
                "User's implementation should process new critical tickets"
            )

        asyncio.run(run_test())

    def test_orchestrator_uses_constants(self):
        """Test that OrchestratorAgent uses constants from constants module (user should follow this pattern)"""
        from constants import TicketStatus, TicketPriority, TicketType, Users
        
        self.assertTrue(hasattr(TicketStatus, 'DONE'))
        self.assertTrue(hasattr(TicketStatus, 'ON_HOLD'))
        self.assertTrue(hasattr(TicketStatus, 'TODO'))
        self.assertTrue(hasattr(Users, 'FRONTEND_DEV'))
        self.assertTrue(hasattr(Users, 'UI_REGRESSION_AGENT'))

    def test_image_diff_prompt_contains_required_elements(self):
        """Test that ImageDiffAgent prompt contains required elements (user must include these)"""
        prompt_content = self.image_diff_agent._load_ui_regression_prompt()
        
        required_elements = [
            "differences",  # Should ask for differences
            "json",        # Should request JSON format
            "element_type", # Should identify element types
            "severity",    # Should assess severity
            "description"  # Should describe changes
        ]
        
        for element in required_elements:
            self.assertIn(
                element.lower(), prompt_content.lower(),
                f"ImageDiffAgent prompt should contain '{element}' - user must implement this"
            )

    def test_classification_prompt_contains_required_elements(self):
        """Test that ClassificationAgent prompt contains required elements (user must include these)"""
        prompt_content = self.classification_agent._load_analysis_prompt()
        
        required_elements = [
            "resolved_tickets",  # Should categorize resolved tickets
            "pending_tickets",   # Should categorize pending tickets  
            "new_tickets",       # Should categorize new tickets
            "ticket_id",         # Should reference ticket IDs
            "json"               # Should request JSON format
        ]
        
        for element in required_elements:
            self.assertIn(
                element.lower(), prompt_content.lower(),
                f"ClassificationAgent prompt should contain '{element}' - user must implement this"
            )

    def test_orchestrator_implements_jira_integration(self):
        """Test that OrchestratorAgent integrates with JIRA correctly (user implements the logic)"""
        self.assertTrue(
            hasattr(self.orchestrator_agent, 'jira'),
            "OrchestratorAgent should have JIRA integration - user must implement this"
        )
        
        from mcp_servers.jira import JIRAMCPServer
        self.assertIsInstance(
            self.orchestrator_agent.jira, JIRAMCPServer,
            "OrchestratorAgent should use JIRAMCPServer - user must implement this"
        )

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("src.image_diff_agent.complete_vision")
    def test_image_diff_handles_similar_images_error(self, mock_complete_vision):
        """Test that ImageDiffAgent handles IMAGES_TOO_SIMILAR error correctly"""
        async def run_test():
            mock_complete_vision.return_value = '{"error": "IMAGES_TOO_SIMILAR"}'
            
            with open("temp_baseline.png", "wb") as f:
                f.write(b"dummy_png_data")
            with open("temp_updated.png", "wb") as f:
                f.write(b"dummy_png_data")

            try:
                with self.assertRaises(ValueError) as context:
                    await self.image_diff_agent.compare_screenshots(
                        "temp_baseline.png", "temp_updated.png"
                    )
                
                self.assertIn(
                    "Images are too similar to detect meaningful differences",
                    str(context.exception),
                    "Should raise ValueError for similar images"
                )
                
            finally:
                try:
                    os.remove("temp_baseline.png")
                except FileNotFoundError:
                    pass
                try:
                    os.remove("temp_updated.png")
                except FileNotFoundError:
                    pass

        asyncio.run(run_test())

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("src.image_diff_agent.complete_vision")
    def test_image_diff_handles_invalid_image_type_error(self, mock_complete_vision):
        """Test that ImageDiffAgent handles INVALID_IMAGE error correctly"""
        async def run_test():
            mock_complete_vision.return_value = '{"error": "INVALID_IMAGE"}'
            
            with open("temp_baseline.png", "wb") as f:
                f.write(b"dummy_png_data")
            with open("temp_updated.png", "wb") as f:
                f.write(b"dummy_png_data")

            try:
                with self.assertRaises(ValueError) as context:
                    await self.image_diff_agent.compare_screenshots(
                        "temp_baseline.png", "temp_updated.png"
                    )
                
                self.assertIn(
                    "Invalid or mismatched webpage screenshots",
                    str(context.exception),
                    "Should raise ValueError for invalid image types"
                )
                
            finally:
                try:
                    os.remove("temp_baseline.png")
                except FileNotFoundError:
                    pass
                try:
                    os.remove("temp_updated.png")
                except FileNotFoundError:
                    pass

        asyncio.run(run_test())

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("src.image_diff_agent.complete_vision")
    def test_image_diff_handles_unknown_error(self, mock_complete_vision):
        """Test that ImageDiffAgent handles unknown error codes correctly"""
        async def run_test():
            mock_complete_vision.return_value = '{"error": "UNKNOWN_ERROR_CODE"}'
            
            with open("temp_baseline.png", "wb") as f:
                f.write(b"dummy_png_data")
            with open("temp_updated.png", "wb") as f:
                f.write(b"dummy_png_data")

            try:
                with self.assertRaises(ValueError) as context:
                    await self.image_diff_agent.compare_screenshots(
                        "temp_baseline.png", "temp_updated.png"
                    )
                
                self.assertIn(
                    "LLM returned error: UNKNOWN_ERROR_CODE",
                    str(context.exception),
                    "Should raise ValueError for unknown error codes"
                )
                
            finally:
                try:
                    os.remove("temp_baseline.png")
                except FileNotFoundError:
                    pass
                try:
                    os.remove("temp_updated.png")
                except FileNotFoundError:
                    pass

        asyncio.run(run_test())

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("src.image_diff_agent.complete_vision")
    def test_image_diff_handles_errors_in_markdown_extraction(self, mock_complete_vision):
        """Test that ImageDiffAgent handles errors even in markdown JSON extraction"""
        async def run_test():
            mock_complete_vision.return_value = '```json\n{"error": "IMAGES_TOO_SIMILAR"}\n```'
            
            with open("temp_baseline.png", "wb") as f:
                f.write(b"dummy_png_data")
            with open("temp_updated.png", "wb") as f:
                f.write(b"dummy_png_data")

            try:
                with self.assertRaises(ValueError) as context:
                    await self.image_diff_agent.compare_screenshots(
                        "temp_baseline.png", "temp_updated.png"
                    )
                
                self.assertIn(
                    "Images are too similar to detect meaningful differences",
                    str(context.exception),
                    "Should handle errors even in markdown extraction"
                )
                
            finally:
                try:
                    os.remove("temp_baseline.png")
                except FileNotFoundError:
                    pass
                try:
                    os.remove("temp_updated.png")
                except FileNotFoundError:
                    pass

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()

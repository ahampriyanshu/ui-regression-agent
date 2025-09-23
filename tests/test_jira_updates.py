#!/usr/bin/env python3
"""
Test suites for JIRA updates functionality in UI regression testing

These tests focus on the final state of JIRA tickets after the UI regression
analysis and ensure proper ticket updates and management.
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import os
import subprocess

from src.image_diff_agent import ImageDiffAgent
from src.classification_agent import ClassificationAgent
from src.orchestrator_agent import OrchestratorAgent
from mcp_servers.jira import JIRAMCPServer


class TestJIRAUpdates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Reset database before running all tests in this class"""
        subprocess.run(["bash", "scripts/cleanup.sh"], check=True, capture_output=True)
        subprocess.run(["bash", "scripts/seed.sh"], check=True, capture_output=True)

    def setUp(self):
        """Set up test fixtures"""
        self.image_diff_agent = ImageDiffAgent()
        self.classification_agent = ClassificationAgent()
        self.orchestrator_agent = OrchestratorAgent()
        self.jira = JIRAMCPServer()

    def test_ui_002_and_ui_003_resolved(self):
        """Test that UI-002 and UI-003 are resolved without changing other details"""
        async def run_test():
            # Mock analysis result that should resolve UI-002 and UI-003
            mock_analysis = {
                "resolved_tickets": [
                    {"ticket_id": "UI-002", "reason": "Password field correctly implemented with eye icon"},
                    {"ticket_id": "UI-003", "reason": "Login button color changed from blue to green as specified"}
                ],
                "pending_tickets": [],
                "new_tickets": []
            }
            
            # Get initial state of UI-002 and UI-003
            ui_002_before = await self.jira.get_ticket("UI-002")
            ui_003_before = await self.jira.get_ticket("UI-003")
            
            # Execute the orchestrator actions
            results = await self.orchestrator_agent.execute_actions(mock_analysis)
            
            # Get final state of UI-002 and UI-003
            ui_002_after = await self.jira.get_ticket("UI-002")
            ui_003_after = await self.jira.get_ticket("UI-003")
            
            # Verify UI-002 was resolved
            self.assertEqual(ui_002_after["status"], "done")
            self.assertEqual(ui_002_after["id"], ui_002_before["id"])
            self.assertEqual(ui_002_after["title"], ui_002_before["title"])
            self.assertEqual(ui_002_after["description"], ui_002_before["description"])
            self.assertEqual(ui_002_after["assignee"], ui_002_before["assignee"])
            self.assertEqual(ui_002_after["priority"], ui_002_before["priority"])
            
            # Verify UI-003 was resolved
            self.assertEqual(ui_003_after["status"], "done")
            self.assertEqual(ui_003_after["id"], ui_003_before["id"])
            self.assertEqual(ui_003_after["title"], ui_003_before["title"])
            self.assertEqual(ui_003_after["description"], ui_003_before["description"])
            self.assertEqual(ui_003_after["assignee"], ui_003_before["assignee"])
            self.assertEqual(ui_003_after["priority"], ui_003_before["priority"])
            
            # Verify the results contain the resolved tickets
            self.assertEqual(len(results["resolved_tickets"]), 2)
            resolved_ids = [ticket["ticket_id"] for ticket in results["resolved_tickets"]]
            self.assertIn("UI-002", resolved_ids)
            self.assertIn("UI-003", resolved_ids)

        asyncio.run(run_test())

    def test_ui_001_moved_to_on_hold_with_comment(self):
        """Test that UI-001 was moved to on_hold with comment message"""
        async def run_test():
            # Mock analysis result that should put UI-001 on hold
            mock_analysis = {
                "resolved_tickets": [],
                "pending_tickets": [
                    {"ticket_id": "UI-001", "reason": "Forgot Password link added but missing question mark"}
                ],
                "new_tickets": []
            }
            
            # Get initial state of UI-001
            ui_001_before = await self.jira.get_ticket("UI-001")
            
            # Execute the orchestrator actions
            results = await self.orchestrator_agent.execute_actions(mock_analysis)
            
            # Get final state of UI-001
            ui_001_after = await self.jira.get_ticket("UI-001")
            
            # Verify UI-001 was moved to on_hold
            self.assertEqual(ui_001_after["status"], "on_hold")
            self.assertEqual(ui_001_after["id"], ui_001_before["id"])
            self.assertEqual(ui_001_after["title"], ui_001_before["title"])
            self.assertEqual(ui_001_after["description"], ui_001_before["description"])
            self.assertEqual(ui_001_after["assignee"], ui_001_before["assignee"])
            self.assertEqual(ui_001_after["priority"], ui_001_before["priority"])
            
            # Verify comment was added
            self.assertIsNotNone(ui_001_after.get("comment"))
            self.assertIn("Forgot Password link added but missing question mark", ui_001_after["comment"])
            
            # Verify the results contain the pending ticket
            self.assertEqual(len(results["pending_tickets"]), 1)
            self.assertEqual(results["pending_tickets"][0]["ticket_id"], "UI-001")

        asyncio.run(run_test())

    def test_new_ui_ticket_raised_for_header_issue(self):
        """Test that a new UI ticket was raised for the header issue"""
        async def run_test():
            # Get initial ticket count
            initial_tickets = await self.jira.get_all_tickets()
            initial_count = len(initial_tickets)
            
            # Mock analysis result that should create a new critical ticket
            mock_analysis = {
                "resolved_tickets": [],
                "pending_tickets": [],
                "new_tickets": [
                    {
                        "title": "Missing About link in header",
                        "description": "About link is missing from the navigation header",
                        "severity": "critical",
                        "priority": "high",
                        "type": "fix",
                        "assignee": "frontend.dev",
                        "reporter": "ui_regression.agent",
                        "status": "todo"
                    }
                ]
            }
            
            # Execute the orchestrator actions
            results = await self.orchestrator_agent.execute_actions(mock_analysis)
            
            # Get final ticket count
            final_tickets = await self.jira.get_all_tickets()
            final_count = len(final_tickets)
            
            # Verify a new ticket was created
            self.assertEqual(final_count, initial_count + 1)
            self.assertEqual(len(results["new_tickets"]), 1)
            
            # Get the new ticket
            new_ticket = results["new_tickets"][0]
            self.assertIn("header", new_ticket["title"].lower())
            self.assertEqual(new_ticket["assignee"], "frontend.dev")
            self.assertEqual(new_ticket["reporter"], "ui_regression.agent")
            self.assertEqual(new_ticket["status"], "todo")
            self.assertEqual(new_ticket["priority"], "high")
            self.assertEqual(new_ticket["type"], "fix")

        asyncio.run(run_test())

    def test_other_tickets_left_untouched(self):
        """Test that all other tickets (BE, DOPS, DATA) were left untouched after the update"""
        async def run_test():
            # Get initial state of all non-UI tickets
            initial_tickets = await self.jira.get_all_tickets()
            non_ui_tickets_before = {
                ticket["id"]: ticket for ticket in initial_tickets 
                if not ticket["id"].startswith("UI-")
            }
            
            # Mock analysis result that only affects UI tickets
            mock_analysis = {
                "resolved_tickets": [
                    {"ticket_id": "UI-002", "reason": "Correctly implemented"}
                ],
                "pending_tickets": [
                    {"ticket_id": "UI-001", "reason": "Needs minor adjustment"}
                ],
                "new_tickets": [
                    {
                        "title": "New UI regression issue",
                        "description": "Critical UI problem detected",
                        "severity": "critical",
                        "priority": "high",
                        "type": "fix",
                        "assignee": "frontend.dev",
                        "reporter": "ui_regression.agent",
                        "status": "todo"
                    }
                ]
            }
            
            # Execute the orchestrator actions
            await self.orchestrator_agent.execute_actions(mock_analysis)
            
            # Get final state of all tickets
            final_tickets = await self.jira.get_all_tickets()
            non_ui_tickets_after = {
                ticket["id"]: ticket for ticket in final_tickets 
                if not ticket["id"].startswith("UI-")
            }
            
            # Verify all non-UI tickets remain unchanged
            self.assertEqual(len(non_ui_tickets_before), len(non_ui_tickets_after))
            
            for ticket_id, before_ticket in non_ui_tickets_before.items():
                after_ticket = non_ui_tickets_after.get(ticket_id)
                self.assertIsNotNone(after_ticket, f"Ticket {ticket_id} should still exist")
                
                # Verify all important fields remain unchanged
                self.assertEqual(before_ticket["status"], after_ticket["status"])
                self.assertEqual(before_ticket["title"], after_ticket["title"])
                self.assertEqual(before_ticket["description"], after_ticket["description"])
                self.assertEqual(before_ticket["assignee"], after_ticket["assignee"])
                self.assertEqual(before_ticket["priority"], after_ticket["priority"])
                self.assertEqual(before_ticket["type"], after_ticket["type"])
                self.assertEqual(before_ticket["reporter"], after_ticket["reporter"])
            
            # Verify expected non-UI tickets are present
            expected_non_ui_ids = ["BE-001", "BE-002", "DOPS-001", "DATA-001"]
            for expected_id in expected_non_ui_ids:
                self.assertIn(expected_id, non_ui_tickets_after, 
                             f"Expected non-UI ticket {expected_id} should be present and untouched")

        asyncio.run(run_test())

    def test_ticket_count_validation(self):
        """Test that ticket count increases after new ticket creation (prevents test failure)"""
        async def run_test():
            # Get initial ticket count
            initial_tickets = await self.jira.get_all_tickets()
            initial_count = len(initial_tickets)
            
            # Mock analysis that should NOT create new tickets (only resolve/pending)
            mock_analysis_no_new = {
                "resolved_tickets": [{"ticket_id": "UI-002", "reason": "Fixed"}],
                "pending_tickets": [{"ticket_id": "UI-001", "reason": "Needs work"}],
                "new_tickets": []
            }
            
            # Execute without new tickets
            await self.orchestrator_agent.execute_actions(mock_analysis_no_new)
            
            # Verify count remains the same (no new tickets created)
            tickets_after_no_new = await self.jira.get_all_tickets()
            self.assertEqual(len(tickets_after_no_new), initial_count)
            
            # Now mock analysis that SHOULD create new tickets
            mock_analysis_with_new = {
                "resolved_tickets": [],
                "pending_tickets": [],
                "new_tickets": [
                    {
                        "title": "Critical UI issue detected",
                        "description": "Major regression found in UI components",
                        "severity": "critical",
                        "priority": "high",
                        "type": "fix",
                        "assignee": "frontend.dev",
                        "reporter": "ui_regression.agent",
                        "status": "todo"
                    }
                ]
            }
            
            # Execute with new tickets
            await self.orchestrator_agent.execute_actions(mock_analysis_with_new)
            
            # Verify count increased (new ticket was created)
            tickets_after_new = await self.jira.get_all_tickets()
            self.assertGreater(len(tickets_after_new), initial_count)
            self.assertEqual(len(tickets_after_new), initial_count + 1)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()

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
from llm import complete_text


class TestJIRAUpdates(unittest.TestCase):


    def setUp(self):
        """Set up test fixtures"""
        self.image_diff_agent = ImageDiffAgent()
        self.classification_agent = ClassificationAgent()
        self.orchestrator_agent = OrchestratorAgent()
        self.jira = JIRAMCPServer()

    def test_ui_002_and_ui_003_resolved(self):
        """Test that UI-002 and UI-003 are resolved without changing other details"""
        async def run_test():
            async def semantic_similarity(a: str, b: str) -> float:
                prompt = (
                    'Return ONLY a float in [0,1] for semantic similarity between two texts.\n'
                    f'Text A: "{a}"\n'
                    f'Text B: "{b}"\n'
                    'Score:'
                )
                response = await complete_text(prompt)
                try:
                    return float(str(response).strip())
                except Exception:
                    return 0.0

            def mock_similarity_from_prompt(prompt: str) -> str:
                import re
                m_a = re.search(r'Text A:\s*"(.*?)"', prompt, re.DOTALL)
                m_b = re.search(r'Text B:\s*"(.*?)"', prompt, re.DOTALL)
                a = m_a.group(1) if m_a else ''
                b = m_b.group(1) if m_b else ''
                ta = set(re.findall(r"\w+", a.lower()))
                tb = set(re.findall(r"\w+", b.lower()))
                score = len(ta & tb) / len(ta | tb) if (ta or tb) else 0.0
                return str(score)

            mock_analysis = {
                "resolved_tickets": [
                    {"ticket_id": "UI-002", "reason": "Password field correctly implemented with eye icon"},
                    {"ticket_id": "UI-003", "reason": "Login button color changed from blue to green as specified"}
                ],
                "pending_tickets": [],
                "new_tickets": []
            }
            
            ui_002_before = await self.jira.get_ticket("UI-002")
            ui_003_before = await self.jira.get_ticket("UI-003")
            
            with patch('llm.complete_text', side_effect=mock_similarity_from_prompt):
                await self.orchestrator_agent.orchestrate_jira_workflow(mock_analysis)
            
            ui_002_after = await self.jira.get_ticket("UI-002")
            ui_003_after = await self.jira.get_ticket("UI-003")
            
            self.assertEqual(ui_002_after["status"], "done")
            self.assertEqual(ui_002_after["id"], ui_002_before["id"])
            sim_title_002 = await semantic_similarity(ui_002_after["title"], ui_002_before["title"]) 
            sim_desc_002 = await semantic_similarity(ui_002_after["description"], ui_002_before["description"]) 
            self.assertGreaterEqual(sim_title_002, 0.9)
            self.assertGreaterEqual(sim_desc_002, 0.9)
            self.assertEqual(ui_002_after["assignee"], ui_002_before["assignee"])
            self.assertEqual(ui_002_after["priority"], ui_002_before["priority"])
            
            self.assertEqual(ui_003_after["status"], "done")
            self.assertEqual(ui_003_after["id"], ui_003_before["id"])
            sim_title_003 = await semantic_similarity(ui_003_after["title"], ui_003_before["title"]) 
            sim_desc_003 = await semantic_similarity(ui_003_after["description"], ui_003_before["description"]) 
            self.assertGreaterEqual(sim_title_003, 0.9)
            self.assertGreaterEqual(sim_desc_003, 0.9)
            self.assertEqual(ui_003_after["assignee"], ui_003_before["assignee"])
            self.assertEqual(ui_003_after["priority"], ui_003_before["priority"])

        asyncio.run(run_test())

    def test_ui_001_moved_to_on_hold_with_comment(self):
        """Test that UI-001 was moved to on_hold with comment message"""
        async def run_test():
            async def semantic_similarity(a: str, b: str) -> float:
                prompt = (
                    'Return ONLY a float in [0,1] for semantic similarity between two texts.\n'
                    f'Text A: "{a}"\n'
                    f'Text B: "{b}"\n'
                    'Score:'
                )
                response = await complete_text(prompt)
                try:
                    return float(str(response).strip())
                except Exception:
                    return 0.0

            def mock_similarity_from_prompt(prompt: str) -> str:
                import re
                m_a = re.search(r'Text A:\s*"(.*?)"', prompt, re.DOTALL)
                m_b = re.search(r'Text B:\s*"(.*?)"', prompt, re.DOTALL)
                a = m_a.group(1) if m_a else ''
                b = m_b.group(1) if m_b else ''
                ta = set(re.findall(r"\w+", a.lower()))
                tb = set(re.findall(r"\w+", b.lower()))
                score = len(ta & tb) / len(ta | tb) if (ta or tb) else 0.0
                return str(score)

            mock_analysis = {
                "resolved_tickets": [],
                "pending_tickets": [
                    {"ticket_id": "UI-001", "reason": "Forgot Password link added but missing question mark"}
                ],
                "new_tickets": []
            }
            
            ui_001_before = await self.jira.get_ticket("UI-001")
            
            with patch('llm.complete_text', side_effect=mock_similarity_from_prompt):
                await self.orchestrator_agent.orchestrate_jira_workflow(mock_analysis)
            
            ui_001_after = await self.jira.get_ticket("UI-001")
            
            self.assertEqual(ui_001_after["status"], "on_hold")
            self.assertEqual(ui_001_after["id"], ui_001_before["id"])
            self.assertEqual(ui_001_after["title"], ui_001_before["title"])
            self.assertEqual(ui_001_after["description"], ui_001_before["description"])
            self.assertEqual(ui_001_after["assignee"], ui_001_before["assignee"])
            self.assertEqual(ui_001_after["priority"], ui_001_before["priority"])
            
            self.assertIsNotNone(ui_001_after.get("comment"))
            similarity = await semantic_similarity(
                "Forgot Password link added but missing question mark",
                ui_001_after["comment"],
            )
            self.assertGreaterEqual(similarity, 0.8)

        asyncio.run(run_test())

    def test_new_ui_ticket_raised_for_header_issue(self):
        """Test that a new UI ticket was raised for the header issue"""
        async def run_test():
            initial_tickets = await self.jira.get_all_tickets()
            initial_count = len(initial_tickets)
            
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
            
            await self.orchestrator_agent.orchestrate_jira_workflow(mock_analysis)
            
            final_tickets = await self.jira.get_all_tickets()
            final_count = len(final_tickets)
            
            self.assertEqual(final_count, initial_count + 1)
            
            new_tickets = await self.jira.get_all_tickets()
            new_ticket_ids = [t["id"] for t in new_tickets if t["id"] not in [t["id"] for t in initial_tickets]]
            self.assertEqual(len(new_ticket_ids), 1)

        asyncio.run(run_test())

    def test_other_tickets_left_untouched(self):
        """Test that all other tickets (BE, DOPS, DATA) were left untouched after the update"""
        async def run_test():
            initial_tickets = await self.jira.get_all_tickets()
            non_ui_tickets_before = {
                ticket["id"]: ticket for ticket in initial_tickets 
                if not ticket["id"].startswith("UI-")
            }
            
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
            
            await self.orchestrator_agent.orchestrate_jira_workflow(mock_analysis)
            
            final_tickets = await self.jira.get_all_tickets()
            non_ui_tickets_after = {
                ticket["id"]: ticket for ticket in final_tickets 
                if not ticket["id"].startswith("UI-")
            }
            
            self.assertEqual(len(non_ui_tickets_before), len(non_ui_tickets_after))
            
            for ticket_id, before_ticket in non_ui_tickets_before.items():
                after_ticket = non_ui_tickets_after.get(ticket_id)
                self.assertIsNotNone(after_ticket, f"Ticket {ticket_id} should still exist")
                
                self.assertEqual(before_ticket["status"], after_ticket["status"])
                self.assertEqual(before_ticket["title"], after_ticket["title"])
                self.assertEqual(before_ticket["description"], after_ticket["description"])
                self.assertEqual(before_ticket["assignee"], after_ticket["assignee"])
                self.assertEqual(before_ticket["priority"], after_ticket["priority"])
                self.assertEqual(before_ticket["type"], after_ticket["type"])
                self.assertEqual(before_ticket["reporter"], after_ticket["reporter"])
            
            expected_non_ui_ids = ["BE-001", "BE-002", "DOPS-001", "DATA-001"]
            for expected_id in expected_non_ui_ids:
                self.assertIn(expected_id, non_ui_tickets_after, 
                             f"Expected non-UI ticket {expected_id} should be present and untouched")

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()

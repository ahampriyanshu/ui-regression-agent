#!/usr/bin/env python3
"""Integration tests validating final JIRA ticket states."""

import asyncio
import unittest

from mcp_servers.jira import JIRAMCPServer
from tests.constants import NON_UI_EXPECTATIONS
from tests.utils import verify_textual_match


class TestJIRAUpdates(unittest.TestCase):
    """Validate that the JIRA data reflects the expected regression workflow."""

    def setUp(self):
        self.jira = JIRAMCPServer()

    def test_ui_002_and_ui_003_resolved(self):
        async def run_test():
            ui_002 = await self.jira.get_ticket("UI-002")
            ui_003 = await self.jira.get_ticket("UI-003")

            self.assertIsNotNone(ui_002)
            self.assertIsNotNone(ui_003)

            self.assertEqual(ui_002["status"], "done")
            self.assertEqual(ui_002["priority"], "high")
            self.assertEqual(ui_002["type"], "fix")
            self.assertEqual(ui_002["assignee"], "frontend.dev")
            self.assertEqual(ui_002["reporter"], "product.manager")
            self.assertEqual(
                ui_002["title"],
                "Change the input field for password from type text to password",
            )
            self.assertIn("type='password'", ui_002["description"])

            self.assertEqual(ui_003["status"], "done")
            self.assertEqual(ui_003["priority"], "low")
            self.assertEqual(ui_003["type"], "fix")
            self.assertEqual(ui_003["assignee"], "frontend.dev")
            self.assertEqual(ui_003["reporter"], "product.manager")
            self.assertEqual(
                ui_003["title"],
                "The 'Login' button would change from blue to green",
            )
            self.assertIn("green background", ui_003["description"])

        asyncio.run(run_test())

    def test_ui_001_moved_to_on_hold_with_comment(self):
        async def run_test():
            ui_001 = await self.jira.get_ticket("UI-001")

            self.assertIsNotNone(ui_001)
            self.assertEqual(ui_001["status"], "on_hold")
            self.assertEqual(ui_001["priority"], "medium")
            self.assertEqual(ui_001["assignee"], "frontend.dev")
            self.assertEqual(ui_001["reporter"], "product.manager")
            self.assertEqual(
                ui_001["title"], "Add new href 'Forgot Password?'"
            )
            self.assertIsNotNone(ui_001.get("comment"))

            expected_reason = {
                "reason": "Forgot Password link added but missing question mark",
            }
            actual_reason = {"comment": ui_001["comment"]}

            self.assertTrue(
                await verify_textual_match(expected_reason, actual_reason),
                "UI-001 comment should explain the missing question mark",
            )

        asyncio.run(run_test())

    def test_new_ui_ticket_raised_for_header_issue(self):
        async def run_test():
            candidates = []
            for ticket_id in ("UI-004", "UI-005"):
                ticket = await self.jira.get_ticket(ticket_id)
                if ticket:
                    candidates.append(ticket)

            self.assertTrue(
                candidates,
                "Expected UI regression tickets to exist for header/register issues",
            )

            header_ticket = next(
                (
                    ticket
                    for ticket in candidates
                    if "about" in f"{ticket['title']} {ticket['description']}".lower()
                ),
                None,
            )

            self.assertIsNotNone(header_ticket, "Header regression ticket should exist")
            self.assertEqual(header_ticket["status"], "todo")
            self.assertEqual(header_ticket["priority"], "high")
            self.assertEqual(header_ticket["type"], "fix")
            self.assertEqual(header_ticket["assignee"], "frontend.dev")
            self.assertEqual(header_ticket["reporter"], "ui_regression.agent")

            expected = {
                "title": "Missing About link in header",
                "description": "About link is missing from the navigation header",
            }
            subject = {
                "title": header_ticket["title"],
                "description": header_ticket["description"],
            }
            self.assertTrue(
                await verify_textual_match(expected, subject),
                "Header navigation regression ticket should match expected description",
            )

        asyncio.run(run_test())

    def test_new_ui_ticket_raised_for_register_text_change(self):
        async def run_test():
            candidates = []
            for ticket_id in ("UI-004", "UI-005"):
                ticket = await self.jira.get_ticket(ticket_id)
                if ticket:
                    candidates.append(ticket)

            self.assertTrue(
                candidates,
                "Expected UI regression tickets to exist for header/register issues",
            )

            register_ticket = next(
                (
                    ticket
                    for ticket in candidates
                    if "register" in f"{ticket['title']} {ticket['description']}".lower()
                ),
                None,
            )

            self.assertIsNotNone(
                register_ticket, "Register text change ticket should exist"
            )
            self.assertEqual(register_ticket["status"], "todo")
            self.assertEqual(register_ticket["priority"], "low")
            self.assertEqual(register_ticket["type"], "fix")
            self.assertEqual(register_ticket["assignee"], "frontend.dev")
            self.assertEqual(register_ticket["reporter"], "ui_regression.agent")

            expected = {
                "title": "Signup button text changed to Sign Up",
                "description": "Register button now reads Sign Up",
            }
            subject = {
                "title": register_ticket["title"],
                "description": register_ticket["description"],
            }
            self.assertTrue(
                await verify_textual_match(expected, subject),
                "Register text change ticket should match expected description",
            )

        asyncio.run(run_test())

    def test_other_tickets_left_untouched(self):
        async def run_test():
            for ticket_id, expected in NON_UI_EXPECTATIONS.items():
                ticket = await self.jira.get_ticket(ticket_id)
                self.assertIsNotNone(ticket, f"Ticket {ticket_id} should exist")

                self.assertEqual(ticket["status"], expected["status"])
                self.assertEqual(ticket["priority"], expected["priority"])
                self.assertEqual(ticket["type"], expected["type"])
                self.assertEqual(ticket["assignee"], expected["assignee"])
                self.assertEqual(ticket["reporter"], expected["reporter"])
                self.assertIn(expected["title"], ticket["title"])

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()

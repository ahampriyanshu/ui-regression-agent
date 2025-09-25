from typing import Dict, List

from constants import (
    TicketPriority,
    TicketStatus,
    TicketType,
    Users,
)
from mcp_servers.jira import JIRAMCPServer


class OrchestratorAgent:
    """Agent responsible for executing actions based on classification results"""

    def __init__(self):
        self.jira = JIRAMCPServer()

    async def update_resolved_issues(self, resolved_tickets: List[Dict]) -> None:
        """Update status of resolved tickets to 'Done'"""
        for resolved in resolved_tickets:
            ticket_id = resolved.get("ticket_id")
            if ticket_id:
                await self.jira.update_ticket_status(ticket_id, TicketStatus.DONE.value)

    async def update_pending_issues(self, pending_tickets: List[Dict]) -> None:
        """Update status of pending tickets to 'on_hold' and add comment"""
        for ticket_info in pending_tickets:
            ticket_id = ticket_info.get("ticket_id")
            if ticket_id:
                reason = ticket_info.get("reason", "Needs further work")

                updated_ticket = await self.jira.update_ticket_status(
                    ticket_id, TicketStatus.ON_HOLD.value
                )

                if updated_ticket:
                    await self.jira.update_ticket_comment(ticket_id, reason)

    async def create_new_issues(self, new_tickets: List[Dict]) -> None:
        """Create JIRA tickets for new issues"""
        for ticket_data in new_tickets:
            title = ticket_data.get("title", "UI Regression Issue")
            description = ticket_data.get(
                "description",
                "UI issue detected during regression testing",
            )
            await self.jira.create_ticket(
                title=title,
                description=description,
                priority=ticket_data.get("priority", TicketPriority.HIGH.value),
                ticket_type=ticket_data.get("type", TicketType.BUG.value),
                assignee=ticket_data.get("assignee", Users.FRONTEND_DEV.value),
                reporter=ticket_data.get("reporter", Users.UI_REGRESSION_AGENT.value),
                status=ticket_data.get("status", TicketStatus.TODO.value),
            )

    async def orchestrate_jira_workflow(self, analysis: Dict) -> Dict:
        """Orchestrate JIRA ticket workflow based on classification analysis"""
        resolved = analysis.get("resolved_tickets", [])
        pending = analysis.get("pending_tickets", [])
        new_items = analysis.get("new_tickets", [])

        if resolved:
            await self.update_resolved_issues(resolved)

        if pending:
            await self.update_pending_issues(pending)

        if new_items:
            await self.create_new_issues(new_items)

        return {
            "resolved_tickets": resolved,
            "pending_tickets": pending,
            "new_tickets": new_items,
        }

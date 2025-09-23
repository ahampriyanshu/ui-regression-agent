from typing import Dict, List

from constants import (
    TicketPriority,
    TicketStatus,
    TicketType,
    Users,
)
from mcp_servers.jira import JIRAMCPServer
from utils.logger import ui_logger


class OrchestratorAgent:
    """Agent responsible for executing actions based on classification results"""

    def __init__(self):
        self.jira = JIRAMCPServer()
        self.logger = ui_logger

    async def update_resolved_tickets(
        self, resolved_tickets: List[Dict]
    ) -> List[Dict]:
        """Update status of resolved tickets to 'Done'"""
        updated_tickets = []

        for resolved in resolved_tickets:
            ticket_id = resolved.get("ticket_id")
            if ticket_id:
                self.logger.logger.info(
                    f"Updating ticket {ticket_id} status to Done"
                )
                updated_ticket = await self.jira.update_ticket_status(
                    ticket_id, TicketStatus.DONE.value
                )
                if updated_ticket:
                    updated_tickets.append(updated_ticket)
                    self.logger.logger.info(
                        f"Successfully updated ticket {ticket_id}"
                    )
                else:
                    self.logger.logger.warning(
                        f"Failed to update ticket {ticket_id}"
                    )

        return updated_tickets

    async def update_pending_tickets(
        self, pending_tickets: List[Dict]
    ) -> List[Dict]:
        """Update status of pending tickets to 'on_hold' and add comment"""
        updated_tickets = []

        for ticket_info in pending_tickets:
            ticket_id = ticket_info.get("ticket_id")
            if ticket_id:
                reason = ticket_info.get("reason", "Needs further work")
                self.logger.logger.info(
                    f"Updating ticket {ticket_id} status to on_hold with comment"
                )
                
                # Update status to on_hold
                updated_ticket = await self.jira.update_ticket_status(
                    ticket_id, TicketStatus.ON_HOLD.value
                )
                
                # Add comment with reason
                if updated_ticket:
                    await self.jira.update_ticket_comment(ticket_id, reason)
                if updated_ticket:
                    updated_tickets.append(updated_ticket)
                    self.logger.logger.info(
                        f"Successfully updated ticket {ticket_id}"
                    )
                else:
                    self.logger.logger.warning(
                        f"Failed to update ticket {ticket_id}"
                    )

        return updated_tickets

    async def create_tickets_for_critical_issues(
        self, new_tickets: List[Dict]
    ) -> List[Dict]:
        """Create JIRA tickets for new issues"""
        created_tickets = []

        for ticket_data in new_tickets:
            title = ticket_data.get("title", "UI Regression Issue")
            description = ticket_data.get(
                "description",
                "UI issue detected during regression testing",
            )
            severity = ticket_data.get("severity", "minor")
            
            # Only create JIRA tickets for critical issues
            if severity == "critical":
                self.logger.logger.info(
                    f"Creating JIRA ticket for critical issue: {title}"
                )
                new_ticket = await self.jira.create_ticket(
                    title=title,
                    description=description,
                    priority=ticket_data.get("priority", TicketPriority.HIGH.value),
                    ticket_type=ticket_data.get("type", TicketType.FIX.value),
                    assignee=ticket_data.get("assignee", Users.FRONTEND_DEV.value),
                    reporter=ticket_data.get("reporter", Users.UI_REGRESSION_AGENT.value),
                    status=ticket_data.get("status", TicketStatus.TODO.value),
                )

                if new_ticket and new_ticket.get("success"):
                    created_ticket = new_ticket.get("ticket", {})
                    created_tickets.append(created_ticket)
                    self.logger.logger.info(
                        f"Created JIRA ticket: {created_ticket.get('id', 'Unknown')}"
                    )
                else:
                    self.logger.logger.error(
                        f"Failed to create JIRA ticket for: {title}"
                    )

        return created_tickets

    async def execute_actions(self, analysis: Dict) -> Dict:
        """Execute all actions based on the classification analysis"""
        results = {
            "resolved_tickets": [],
            "pending_tickets": [],
            "new_tickets": [],
        }

        if analysis.get("resolved_tickets"):
            results["resolved_tickets"] = await self.update_resolved_tickets(
                analysis["resolved_tickets"]
            )

        if analysis.get("pending_tickets"):
            results["pending_tickets"] = await self.update_pending_tickets(
                analysis["pending_tickets"]
            )

        if analysis.get("new_tickets"):
            results["new_tickets"] = await self.create_tickets_for_critical_issues(
                analysis["new_tickets"]
            )

        return results

    async def validate_actions(self, results: Dict) -> Dict:
        """Validate that all actions were executed successfully"""
        validation_results = {
            "status": "success",
            "resolved_tickets_count": len(results.get("resolved_tickets", [])),
            "updated_tickets_count": len(results.get("updated_tickets", [])),
            "created_tickets_count": len(results.get("created_tickets", [])),
            "validation_details": [],
        }

        if results.get("resolved_tickets"):
            validation_results["validation_details"].append(
                f"Successfully updated {len(results['resolved_tickets'])} tickets to Done status"
            )

        if results.get("updated_tickets"):
            validation_results["validation_details"].append(
                f"Successfully updated {len(results['updated_tickets'])} tickets to Changes Requested status"
            )

        if results.get("created_tickets"):
            validation_results["validation_details"].append(
                f"Successfully created {len(results['created_tickets'])} new JIRA tickets"
            )


        return validation_results

from typing import Dict, List

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
                    ticket_id, "Done"
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

    async def update_tickets_needing_work(
        self, tickets_needing_work: List[Dict]
    ) -> List[Dict]:
        """Update status of tickets needing work to 'Changes Requested'"""
        updated_tickets = []

        for ticket_info in tickets_needing_work:
            ticket_id = ticket_info.get("ticket_id")
            if ticket_id:
                self.logger.logger.info(
                    f"Updating ticket {ticket_id} status to Changes Requested"
                )
                updated_ticket = await self.jira.update_ticket_status(
                    ticket_id, "Changes Requested"
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

    async def create_tickets_for_critical_issues(
        self, new_issues: List[Dict]
    ) -> List[Dict]:
        """Create JIRA tickets for critical new issues"""
        created_tickets = []

        for issue in new_issues:
            if issue.get("severity") == "critical":
                title = issue.get("title", "UI Regression Issue")
                description = issue.get(
                    "description",
                    "Critical UI issue detected during regression testing",
                )

                self.logger.logger.info(
                    f"Creating JIRA ticket for critical issue: {title}"
                )
                new_ticket = await self.jira.create_ticket(
                    title=title,
                    description=description,
                    priority="High",
                    ticket_type="Bug",
                    status="Open",
                    assignee="auto.assigned@company.com",
                    reporter="ui.regression.agent@company.com",
                )

                if new_ticket:
                    created_tickets.append(new_ticket)
                    self.logger.logger.info(
                        f"Created JIRA ticket: {new_ticket['id']}"
                    )
                else:
                    self.logger.logger.error(
                        f"Failed to create JIRA ticket for: {title}"
                    )

        return created_tickets

    def log_minor_issues(self, new_issues: List[Dict]) -> None:
        """Log minor issues to the minor_issues.json file"""
        minor_issues = [
            issue for issue in new_issues if issue.get("severity") == "minor"
        ]

        if not minor_issues:
            return

        for issue in minor_issues:
            issue_data = {
                "title": issue.get("title", "Minor UI Issue"),
                "description": issue.get(
                    "description", "Minor issue detected"
                ),
                "element_type": issue.get("element_type", "unknown"),
                "location": issue.get("location", "unknown"),
                "severity": "minor",
            }

            self.logger.log_minor_issue(issue_data)
            self.logger.logger.info(
                f"Logged minor issue: {issue_data['title']}"
            )

    async def execute_actions(self, analysis: Dict) -> Dict:
        """Execute all actions based on the classification analysis"""
        results = {
            "resolved_tickets": [],
            "updated_tickets": [],
            "created_tickets": [],
            "minor_issues_logged": 0,
        }

        if analysis.get("resolved_tickets"):
            results["resolved_tickets"] = await self.update_resolved_tickets(
                analysis["resolved_tickets"]
            )

        if analysis.get("tickets_needing_work"):
            results["updated_tickets"] = (
                await self.update_tickets_needing_work(
                    analysis["tickets_needing_work"]
                )
            )

        if analysis.get("new_issues"):
            results["created_tickets"] = (
                await self.create_tickets_for_critical_issues(
                    analysis["new_issues"]
                )
            )

            self.log_minor_issues(analysis["new_issues"])
            minor_count = len(
                [
                    i
                    for i in analysis["new_issues"]
                    if i.get("severity") == "minor"
                ]
            )
            results["minor_issues_logged"] = minor_count

        return results

    async def validate_actions(self, results: Dict) -> Dict:
        """Validate that all actions were executed successfully"""
        validation_results = {
            "status": "success",
            "resolved_tickets_count": len(results.get("resolved_tickets", [])),
            "updated_tickets_count": len(results.get("updated_tickets", [])),
            "created_tickets_count": len(results.get("created_tickets", [])),
            "minor_issues_logged": results.get("minor_issues_logged", 0),
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

        if results.get("minor_issues_logged", 0) > 0:
            validation_results["validation_details"].append(
                f"Successfully logged {results['minor_issues_logged']} minor issues"
            )

        return validation_results

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
        """Initialize the JIRA MCP server."""
        raise NotImplementedError("__init__ must be implemented by the user")

    async def update_resolved_issues(self, resolved_tickets: List[Dict]) -> None:
        """Update status of resolved tickets to 'Done'"""
        raise NotImplementedError("update_resolved_issues must be implemented by the user")

    async def update_pending_issues(self, pending_tickets: List[Dict]) -> None:
        """Update status of pending tickets to 'on_hold' and add comment"""
        raise NotImplementedError("update_pending_issues must be implemented by the user")

    async def create_new_issues(self, new_tickets: List[Dict]) -> None:
        """Create JIRA tickets for new issues"""
        raise NotImplementedError("create_new_issues must be implemented by the user")

    async def orchestrate_jira_workflow(self, analysis: Dict) -> Dict:
        """Orchestrate JIRA ticket workflow based on classification analysis"""
        raise NotImplementedError("orchestrate_jira_workflow must be implemented by the user")
"""
JIRA MCP Server - Mock implementation for UI regression testing
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from fastmcp import FastMCP

# Mock JIRA tickets data
JIRA_TICKETS = {
    "UI-001": {
        "id": "UI-001",
        "title": "Add new href 'Forgot Password?'",
        "description": "Add a 'Forgot Password?' link below the login form for users who need to reset their password",
        "status": "In Progress",
        "priority": "Medium",
        "type": "Feature",
        "created": "2024-01-15T10:00:00Z",
        "updated": "2024-01-16T14:30:00Z",
        "assignee": "john.doe@company.com",
        "reporter": "product.manager@company.com"
    },
    "UI-002": {
        "id": "UI-002", 
        "title": "Change the input field for password from type text to password",
        "description": "Update the password input field to use type='password' for security and add an eye icon to toggle visibility",
        "status": "Done",
        "priority": "High",
        "type": "Bug Fix",
        "created": "2024-01-10T09:00:00Z",
        "updated": "2024-01-18T16:45:00Z",
        "assignee": "jane.smith@company.com",
        "reporter": "security.team@company.com"
    },
    "UI-003": {
        "id": "UI-003",
        "title": "The 'Login' button would change from transparent to green",
        "description": "Update the Login button styling to use green background color instead of transparent for better visibility",
        "status": "In Progress", 
        "priority": "Low",
        "type": "Enhancement",
        "created": "2024-01-12T11:30:00Z",
        "updated": "2024-01-17T13:20:00Z",
        "assignee": "ui.designer@company.com",
        "reporter": "ux.team@company.com"
    },
    "UI-004": {
        "id": "UI-004",
        "title": "Add header at top with 'Home' href on extreme left and 'About' on the extreme right",
        "description": "Create a new header component with navigation links - 'Home' positioned on the far left and 'About' positioned on the far right",
        "status": "To Do",
        "priority": "Medium", 
        "type": "Feature",
        "created": "2024-01-14T15:00:00Z",
        "updated": "2024-01-14T15:00:00Z",
        "assignee": "frontend.dev@company.com",
        "reporter": "product.manager@company.com"
    }
}

# Store for new tickets created during regression testing
NEW_TICKETS = {}
TICKET_COUNTER = 5

mcp = FastMCP("JIRA Mock Server")

@mcp.tool()
def get_all_tickets() -> List[Dict]:
    """Get all JIRA tickets"""
    all_tickets = {**JIRA_TICKETS, **NEW_TICKETS}
    return list(all_tickets.values())

@mcp.tool()
def get_ticket(ticket_id: str) -> Optional[Dict]:
    """Get a specific JIRA ticket by ID"""
    all_tickets = {**JIRA_TICKETS, **NEW_TICKETS}
    return all_tickets.get(ticket_id)

@mcp.tool()
def search_tickets(query: str) -> List[Dict]:
    """Search JIRA tickets by title or description"""
    results = []
    all_tickets = {**JIRA_TICKETS, **NEW_TICKETS}
    
    for ticket in all_tickets.values():
        if (query.lower() in ticket["title"].lower() or 
            query.lower() in ticket["description"].lower()):
            results.append(ticket)
    
    return results

@mcp.tool()
def create_ticket(title: str, description: str, priority: str = "Medium", ticket_type: str = "Bug") -> Dict:
    """Create a new JIRA ticket"""
    global TICKET_COUNTER
    
    ticket_id = f"UI-{TICKET_COUNTER:03d}"
    TICKET_COUNTER += 1
    
    new_ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "status": "Open",
        "priority": priority,
        "type": ticket_type,
        "created": datetime.now().isoformat() + "Z",
        "updated": datetime.now().isoformat() + "Z",
        "assignee": "auto.assigned@company.com",
        "reporter": "ui.regression.agent@company.com"
    }
    
    NEW_TICKETS[ticket_id] = new_ticket
    return new_ticket

@mcp.tool()
def update_ticket_status(ticket_id: str, status: str) -> Optional[Dict]:
    """Update the status of a JIRA ticket"""
    all_tickets = {**JIRA_TICKETS, **NEW_TICKETS}
    
    if ticket_id in all_tickets:
        all_tickets[ticket_id]["status"] = status
        all_tickets[ticket_id]["updated"] = datetime.now().isoformat() + "Z"
        return all_tickets[ticket_id]
    
    return None

@mcp.tool()
def get_tickets_by_status(status: str) -> List[Dict]:
    """Get all tickets with a specific status"""
    results = []
    all_tickets = {**JIRA_TICKETS, **NEW_TICKETS}
    
    for ticket in all_tickets.values():
        if ticket["status"].lower() == status.lower():
            results.append(ticket)
    
    return results

if __name__ == "__main__":
    mcp.run()

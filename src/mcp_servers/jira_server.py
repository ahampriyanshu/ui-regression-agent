"""
JIRA MCP Server - Mock implementation for UI regression testing
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Mock JIRA tickets data
JIRA_TICKETS = {
    "UI-001": {
        "id": "UI-001",
        "title": "Add new href 'Forgot Password?'",
        "description": "Add a 'Forgot Password?' link below the login form for users who need to reset their password",
        "status": "In Review",
        "priority": "Medium",
        "type": "Feature",
        "created": "2024-01-15T10:00:00Z",
        "updated": "2024-01-16T14:30:00Z",
        "assignee": "frontend.dev",
        "reporter": "product.manager"
    },
    "UI-002": {
        "id": "UI-002", 
        "title": "Change the input field for password from type text to password",
        "description": "Update the password input field to use type='password' for security and add an eye icon to toggle visibility",
        "status": "In Review",
        "priority": "High",
        "type": "Feature",
        "created": "2024-01-10T09:00:00Z",
        "updated": "2024-01-18T16:45:00Z",
        "assignee": "frontend.dev",
        "reporter": "product.manager"
    },
    "UI-003": {
        "id": "UI-003",
        "title": "The 'Login' button would change from transparent to green",
        "description": "Update the Login button styling to use green background color instead of transparent for better visibility",
        "status": "In Review", 
        "priority": "Low",
        "type": "Enhancement",
        "created": "2024-01-12T11:30:00Z",
        "updated": "2024-01-17T13:20:00Z",
        "assignee": "frontend.dev",
        "reporter": "product.manager"
    },
    "UI-004": {
        "id": "UI-004",
        "title": "Add header at top with 'Home' href on extreme left and 'About' on the extreme right",
        "description": "Create a new header component with navigation links - 'Home' positioned on the far left and 'About' positioned on the far right",
        "status": "In Review",
        "priority": "Medium", 
        "type": "Feature",
        "created": "2024-01-14T15:00:00Z",
        "updated": "2024-01-14T15:00:00Z",
        "assignee": "frontend.dev",
        "reporter": "product.manager"
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


class JIRAIntegration:
    """JIRA integration for managing tickets during UI regression testing"""
    
    def __init__(self):
        """Initialize JIRA integration with mock data"""
        self.tickets = JIRA_TICKETS.copy()
        self.new_tickets = NEW_TICKETS.copy()
        self.ticket_counter = TICKET_COUNTER
        
    async def get_all_tickets(self) -> List[Dict]:
        """Retrieve all JIRA tickets"""
        try:
            all_tickets = {**self.tickets, **self.new_tickets}
            return list(all_tickets.values())
        except Exception as e:
            logger.error(f"Error fetching all tickets: {e}")
            return []
    
    async def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Get a specific JIRA ticket by ID"""
        try:
            all_tickets = {**self.tickets, **self.new_tickets}
            return all_tickets.get(ticket_id)
        except Exception as e:
            logger.error(f"Error fetching ticket {ticket_id}: {e}")
            return None
    
    async def search_tickets(self, query: str) -> List[Dict]:
        """Search JIRA tickets by title or description"""
        try:
            results = []
            all_tickets = {**self.tickets, **self.new_tickets}
            
            for ticket in all_tickets.values():
                if (query.lower() in ticket["title"].lower() or 
                    query.lower() in ticket["description"].lower()):
                    results.append(ticket)
            
            return results
        except Exception as e:
            logger.error(f"Error searching tickets with query '{query}': {e}")
            return []
    
    async def create_ticket(self, title: str, description: str, priority: str = "Medium", 
                          ticket_type: str = "Bug") -> Optional[Dict]:
        """Create a new JIRA ticket"""
        try:
            ticket_id = f"UI-{self.ticket_counter:03d}"
            self.ticket_counter += 1
            
            new_ticket = {
                "id": ticket_id,
                "title": title,
                "description": description,
                "status": "Todo",
                "priority": priority,
                "type": ticket_type,
                "created": datetime.now().isoformat() + "Z",
                "updated": datetime.now().isoformat() + "Z",
                "assignee": "frontend.dev",
                "reporter": "ui_regression.agent"
            }
            
            self.new_tickets[ticket_id] = new_ticket
            return new_ticket
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return None
    
    async def update_ticket_status(self, ticket_id: str, status: str) -> Optional[Dict]:
        """Update the status of a JIRA ticket"""
        try:
            if ticket_id in self.tickets:
                self.tickets[ticket_id]["status"] = status
                self.tickets[ticket_id]["updated"] = datetime.now().isoformat() + "Z"
                return self.tickets[ticket_id]
            elif ticket_id in self.new_tickets:
                self.new_tickets[ticket_id]["status"] = status
                self.new_tickets[ticket_id]["updated"] = datetime.now().isoformat() + "Z"
                return self.new_tickets[ticket_id]
            
            return None
        except Exception as e:
            logger.error(f"Error updating ticket {ticket_id} status: {e}")
            return None
    
    async def get_tickets_by_status(self, status: str) -> List[Dict]:
        """Get all tickets with a specific status"""
        try:
            results = []
            all_tickets = {**self.tickets, **self.new_tickets}
            
            for ticket in all_tickets.values():
                if ticket["status"].lower() == status.lower():
                    results.append(ticket)
            
            return results
        except Exception as e:
            logger.error(f"Error fetching tickets with status '{status}': {e}")
            return []
    
    def format_tickets_for_analysis(self, tickets: List[Dict]) -> str:
        """Format tickets for LLM analysis"""
        if not tickets:
            return "No JIRA tickets found."
        
        formatted = "Existing JIRA Tickets:\n"
        for ticket in tickets:
            formatted += f"\nTicket ID: {ticket['id']}\n"
            formatted += f"Title: {ticket['title']}\n"
            formatted += f"Description: {ticket['description']}\n"
            formatted += f"Status: {ticket['status']}\n"
            formatted += f"Priority: {ticket['priority']}\n"
            formatted += f"Type: {ticket['type']}\n"
            formatted += "---\n"
        
        return formatted
    
    async def find_matching_tickets(self, ui_change_description: str) -> List[Dict]:
        """Find JIRA tickets that might match a UI change"""
        search_terms = [
            ui_change_description,
            *ui_change_description.lower().split()
        ]
        
        matching_tickets = []
        for term in search_terms:
            if len(term) > 3:
                tickets = await self.search_tickets(term)
                for ticket in tickets:
                    if ticket not in matching_tickets:
                        matching_tickets.append(ticket)
        
        return matching_tickets
    
    async def update_ticket_status_based_on_analysis(self, analysis_results: List[Dict]) -> List[Dict]:
        """Update ticket statuses based on regression analysis results"""
        updated_tickets = []
        
        for result in analysis_results:
            jira_match = result.get('jira_match')
            classification = result.get('classification')
            implementation_correct = result.get('implementation_correct', False)
            
            if jira_match and classification == 'EXPECTED':
                if implementation_correct:
                    ticket = await self.update_ticket_status(jira_match, 'Done')
                else:
                    ticket = await self.update_ticket_status(jira_match, 'Changes Requested')
                
                if ticket:
                    updated_tickets.append(ticket)
        
        return updated_tickets


if __name__ == "__main__":
    mcp.run()

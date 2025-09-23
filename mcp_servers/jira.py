"""
JIRA MCP Server - SQLite-based implementation for UI regression testing
Provides persistent storage across different processes (app vs tests)
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from fastmcp import FastMCP


DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "databases", "jira.db"
)

mcp = FastMCP("JIRA Mock Server")


def get_db_connection():
    """Get SQLite database connection"""
    return sqlite3.connect(DB_PATH)


def dict_factory(cursor, row):
    """Convert SQLite row to dictionary"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@mcp.tool()
def get_all_tickets() -> List[Dict]:
    """Get all JIRA tickets from database"""
    try:
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM jira_tickets ORDER BY created DESC")
        tickets = cursor.fetchall()

        conn.close()
        return tickets
    except Exception:
        return []


@mcp.tool()
def get_ticket(ticket_id: str) -> Optional[Dict]:
    """Get a specific JIRA ticket by ID from database"""
    try:
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM jira_tickets WHERE id = ?", (ticket_id,))
        ticket = cursor.fetchone()

        conn.close()
        return ticket
    except Exception:
        return None


@mcp.tool()
def search_tickets(query: str) -> List[Dict]:
    """Search JIRA tickets by title or description"""
    try:
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM jira_tickets 
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY created DESC
        """,
            (f"%{query}%", f"%{query}%"),
        )

        tickets = cursor.fetchall()
        conn.close()
        return tickets
    except Exception:
        return []


@mcp.tool()
def get_tickets_by_status(status: str) -> List[Dict]:
    """Get tickets filtered by status"""
    try:
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM jira_tickets WHERE status = ? ORDER BY created DESC",
            (status,),
        )

        tickets = cursor.fetchall()
        conn.close()
        return tickets
    except Exception:
        return []


@mcp.tool()
def get_tickets_by_assignee(assignee: str) -> List[Dict]:
    """Get tickets filtered by assignee"""
    try:
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM jira_tickets WHERE assignee = ? ORDER BY created DESC",
            (assignee,),
        )

        tickets = cursor.fetchall()
        conn.close()
        return tickets
    except Exception:
        return []


@mcp.tool()
def update_ticket_status(ticket_id: str, new_status: str) -> Dict:
    """Update the status of a JIRA ticket"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM jira_tickets WHERE id = ?", (ticket_id,)
        )
        if not cursor.fetchone():
            conn.close()
            return {"success": False, "error": f"Ticket {ticket_id} not found"}

        updated_time = datetime.now().isoformat() + "Z"
        cursor.execute(
            """
            UPDATE jira_tickets 
            SET status = ?, updated = ?
            WHERE id = ?
        """,
            (new_status, updated_time, ticket_id),
        )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "ticket_id": ticket_id,
            "new_status": new_status,
            "updated": updated_time,
        }
    except Exception:
        return {"success": False, "error": "Update failed"}


@mcp.tool()
def update_ticket_assignee(ticket_id: str, new_assignee: str) -> Dict:
    """Update the assignee of a JIRA ticket"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM jira_tickets WHERE id = ?", (ticket_id,)
        )
        if not cursor.fetchone():
            conn.close()
            return {"success": False, "error": f"Ticket {ticket_id} not found"}

        updated_time = datetime.now().isoformat() + "Z"
        cursor.execute(
            """
            UPDATE jira_tickets 
            SET assignee = ?, updated = ?
            WHERE id = ?
        """,
            (new_assignee, updated_time, ticket_id),
        )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "ticket_id": ticket_id,
            "new_assignee": new_assignee,
            "updated": updated_time,
        }
    except Exception:
        return {"success": False, "error": "Assignee update failed"}


@mcp.tool()
def update_ticket_comment(ticket_id: str, comment: str) -> Dict:
    """Update ticket comment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat() + "Z"
        cursor.execute(
            """
            UPDATE jira_tickets 
            SET comment = ?, updated = ? 
            WHERE id = ?
        """,
            (comment, timestamp, ticket_id),
        )

        if cursor.rowcount == 0:
            conn.close()
            return {"success": False, "error": f"Ticket {ticket_id} not found"}

        conn.commit()
        conn.close()

        return {
            "success": True,
            "ticket_id": ticket_id,
            "comment": comment,
            "updated": timestamp,
        }

    except Exception:
        return {"success": False, "error": "Comment update failed"}


@mcp.tool()
def create_ticket(
    title: str,
    description: str,
    priority: str,
    ticket_type: str,
    assignee: str,
    reporter: str,
    status: str,
    comment: str = None,
) -> Dict:
    """Create a new JIRA ticket"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM jira_tickets WHERE id LIKE 'UI-%'")
        count_result = cursor.fetchone()
        next_number = (count_result[0] if count_result else 0) + 1

        ticket_id = f"UI-{next_number:03d}"

        timestamp = datetime.now().isoformat() + "Z"
        cursor.execute(
            """
            INSERT INTO jira_tickets (
                id, title, description, status, priority, type,
                created, updated, assignee, reporter, comment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                ticket_id,
                title,
                description,
                status,
                priority,
                ticket_type,
                timestamp,
                timestamp,
                assignee,
                reporter,
                comment,
            ),
        )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "ticket": {
                "id": ticket_id,
                "title": title,
                "description": description,
                "status": status,
                "priority": priority,
                "type": ticket_type,
                "created": timestamp,
                "updated": timestamp,
                "assignee": assignee,
                "reporter": reporter,
            },
        }
    except Exception:
        return {"success": False, "error": "Ticket creation failed"}


class JIRAMCPServer:
    """JIRA MCP Server class for use in other modules"""

    async def get_all_tickets(self) -> List[Dict]:
        """Get all JIRA tickets"""
        return get_all_tickets()

    async def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Get a specific JIRA ticket by ID"""
        return get_ticket(ticket_id)

    async def search_tickets(self, query: str) -> List[Dict]:
        """Search JIRA tickets"""
        return search_tickets(query)

    async def get_tickets_by_status(self, status: str) -> List[Dict]:
        """Get tickets by status"""
        return get_tickets_by_status(status)

    async def get_tickets_by_assignee(self, assignee: str) -> List[Dict]:
        """Get tickets by assignee"""
        return get_tickets_by_assignee(assignee)

    async def update_ticket_status(
        self, ticket_id: str, new_status: str
    ) -> Dict:
        """Update ticket status"""
        return update_ticket_status(ticket_id, new_status)

    async def update_ticket_assignee(
        self, ticket_id: str, new_assignee: str
    ) -> Dict:
        """Update ticket assignee"""
        return update_ticket_assignee(ticket_id, new_assignee)

    async def update_ticket_comment(
        self, ticket_id: str, comment: str
    ) -> Dict:
        """Update ticket comment"""
        return update_ticket_comment(ticket_id, comment)

    async def create_ticket(
        self,
        title: str,
        description: str,
        priority: str,
        ticket_type: str,
        assignee: str,
        reporter: str,
        status: str,
        comment: str = None,
    ) -> Dict:
        """Create a new ticket"""
        return create_ticket(
            title,
            description,
            priority,
            ticket_type,
            assignee,
            reporter,
            status,
            comment,
        )


if __name__ == "__main__":
    print("JIRA MCP Server")
    print(f"Database path: {DB_PATH}")

    tickets = get_all_tickets()
    print(f"Found {len(tickets)} tickets")

    if tickets:
        print("Sample ticket:", tickets[0])

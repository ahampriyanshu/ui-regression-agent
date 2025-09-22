#!/usr/bin/env python3
"""
Seed JIRA data for UI Regression Testing

Creates SQLite database with initial JIRA tickets and schema for persistence
between app runs and test executions.
"""

import json
import os
import sqlite3
from datetime import datetime


def create_jira_database():
    """Create and populate JIRA database for UI regression testing"""
    db_path = "data/databases/jira.db"
    
    # Create databases directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create jira_tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jira_tickets (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            type TEXT NOT NULL,
            created TEXT NOT NULL,
            updated TEXT NOT NULL,
            assignee TEXT NOT NULL,
            reporter TEXT NOT NULL
        )
    """)
    
    # Load initial JIRA tickets from JSON
    json_file = os.path.join(os.path.dirname(__file__), "jira_tickets.json")
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            jira_tickets = data["JIRA_TICKETS"]
            
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"Error loading JIRA data from {json_file}: {e}")
        return
    
    # Clear existing data (for fresh seeding)
    cursor.execute("DELETE FROM jira_tickets")
    
    # Insert initial JIRA tickets
    for ticket_data in jira_tickets.items():
        cursor.execute("""
            INSERT INTO jira_tickets (
                id, title, description, status, priority, type,
                created, updated, assignee, reporter
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_data["id"],
            ticket_data["title"],
            ticket_data["description"],
            ticket_data["status"],
            ticket_data["priority"],
            ticket_data["type"],
            ticket_data["created"],
            ticket_data["updated"],
            ticket_data["assignee"],
            ticket_data["reporter"]
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ JIRA database seeded successfully at {db_path}")
    print(f"   - {len(jira_tickets)} initial tickets loaded")


def main():
    """Main function to seed JIRA database"""
    print("🔄 Seeding JIRA database for UI regression testing...")
    create_jira_database()


if __name__ == "__main__":
    main()
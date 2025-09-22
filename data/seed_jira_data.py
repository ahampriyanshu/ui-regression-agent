"""
Test Case 1: OOO for 3 days from January 1-3, 2024
This script creates mock data for a 3-day OOO period with realistic scenarios.
"""

import sqlite3
import os

def create_email_database():
    """Create and populate email database for test case 1"""
    conn = sqlite3.connect("data/databases/emails.db")
    cursor = conn.cursor()
    
    # Create emails table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            custom_id TEXT UNIQUE,
            sender TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            received_date TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            thread_id TEXT,
            meeting_date TEXT,
            meeting_duration INTEGER,
            attendees TEXT
        )
    """)
    
    # Test Case 1: 3-day OOO period (Jan 1-3, 2024) - 20% important, 80% noise
    emails = [
        # IMPORTANT EMAILS (20% - 2 out of 10)
        {
            "id": "email_001",
            "sender": "client@external.com",
            "subject": "URGENT: Production Issue - API Down",
            "body": "Our production API is down and customers are affected. Need immediate attention.",
            "received_date": "2024-01-02 09:00:00",
            "is_read": 0,
            "thread_id": "urgent_001"
        },
        {
            "id": "email_002",
            "sender": "manager@company.com",
            "subject": "Q1 Planning Meeting - Reschedule Request",
            "body": "We need to reschedule the Q1 planning meeting. Please confirm your availability for next week.",
            "received_date": "2024-01-03 14:30:00",
            "is_read": 0,
            "thread_id": "planning_001"
        },
        
        # NOISE EMAILS (80% - 8 out of 10)
        # New Year greetings
        {
            "id": "email_003",
            "sender": "hr@company.com",
            "subject": "Happy New Year 2024!",
            "body": "Wishing everyone a prosperous and successful new year!",
            "received_date": "2024-01-01 00:01:00",
            "is_read": 1,
            "thread_id": "greetings_001"
        },
        {
            "id": "email_004",
            "sender": "ceo@company.com",
            "subject": "New Year Message from Leadership",
            "body": "Thank you for your hard work in 2023. Looking forward to an amazing 2024!",
            "received_date": "2024-01-01 08:00:00",
            "is_read": 1,
            "thread_id": "ceo_message_001"
        },
        
        # Meeting reminders
        {
            "id": "email_005",
            "sender": "calendar@company.com",
            "subject": "Reminder: Team Standup Tomorrow",
            "body": "Don't forget about tomorrow's team standup at 9 AM.",
            "received_date": "2024-01-02 17:00:00",
            "is_read": 0,
            "thread_id": "reminder_001"
        },
        {
            "id": "email_006",
            "sender": "calendar@company.com",
            "subject": "Reminder: All Hands Meeting",
            "body": "Monthly all hands meeting scheduled for next Friday.",
            "received_date": "2024-01-03 10:00:00",
            "is_read": 0,
            "thread_id": "reminder_002"
        },
        
        # Product promotions
        {
            "id": "email_007",
            "sender": "marketing@company.com",
            "subject": "New Year Special: 50% Off Premium Features",
            "body": "Start 2024 with our premium features at half price!",
            "received_date": "2024-01-01 12:00:00",
            "is_read": 0,
            "thread_id": "promo_001"
        },
        {
            "id": "email_008",
            "sender": "sales@company.com",
            "subject": "Q1 Sales Targets and Incentives",
            "body": "New Q1 sales targets and incentive structure announced.",
            "received_date": "2024-01-02 11:00:00",
            "is_read": 0,
            "thread_id": "sales_001"
        },
        
        # IT notifications
        {
            "id": "email_009",
            "sender": "it@company.com",
            "subject": "System Maintenance Completed",
            "body": "Scheduled system maintenance has been completed successfully.",
            "received_date": "2024-01-03 06:00:00",
            "is_read": 1,
            "thread_id": "maintenance_001"
        },
        {
            "id": "email_010",
            "sender": "security@company.com",
            "subject": "Security Awareness Training - January",
            "body": "Monthly security awareness training materials are now available.",
            "received_date": "2024-01-03 15:00:00",
            "is_read": 0,
            "thread_id": "security_001"
        }
    ]
    
    for email in emails:
        cursor.execute("""
            INSERT OR IGNORE INTO emails (custom_id, sender, subject, body, received_date, is_read, thread_id, meeting_date, meeting_duration, attendees)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            email["id"], email["sender"], email["subject"], email["body"], email["received_date"],
            email["is_read"], email["thread_id"], 
            email.get("meeting_date"), email.get("meeting_duration"), 
            email.get("attendees")
        ))
    
    conn.commit()
    conn.close()

def create_calendar_database():
    """Create and populate calendar database for test case 1"""
    conn = sqlite3.connect("data/databases/calendar.db")
    cursor = conn.cursor()
    
    # Create events table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            custom_id TEXT UNIQUE,
            title TEXT NOT NULL,
            description TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            location TEXT,
            attendees TEXT,
            event_type TEXT DEFAULT 'meeting',
            is_all_day BOOLEAN DEFAULT 0,
            reminder_set BOOLEAN DEFAULT 1,
            project_name TEXT
        )
    """)
    
    # Test Case 1: 3-day OOO period (Jan 1-3, 2024) - 20% important, 80% noise
    events = [
        # IMPORTANT EVENTS (20% - 2 out of 10)
        {
            "id": "event_001",
            "title": "Production Issue Resolution",
            "description": "Critical production issue needs immediate attention",
            "start_time": "2024-01-02 10:00:00",
            "end_time": "2024-01-02 12:00:00",
            "location": "War Room",
            "attendees": "dev-team@company.com,manager@company.com",
            "event_type": "meeting"
        },
        {
            "id": "event_002",
            "title": "Q1 Planning Deadline",
            "description": "Final deadline for Q1 planning documents",
            "start_time": "2024-01-03 17:00:00",
            "end_time": "2024-01-03 17:00:00",
            "event_type": "deadline",
            "project_name": "Q1 Planning"
        },
        
        # NOISE EVENTS (80% - 8 out of 10)
        # New Year events
        {
            "id": "event_003",
            "title": "New Year Holiday",
            "description": "Company holiday for New Year",
            "start_time": "2024-01-01 00:00:00",
            "end_time": "2024-01-01 23:59:59",
            "event_type": "holiday",
            "is_all_day": 1
        },
        {
            "id": "event_004",
            "title": "New Year Team Lunch",
            "description": "Team lunch to celebrate the new year",
            "start_time": "2024-01-02 12:00:00",
            "end_time": "2024-01-02 13:30:00",
            "location": "Company Cafeteria",
            "attendees": "team@company.com",
            "event_type": "social"
        },
        
        # Regular meetings
        {
            "id": "event_005",
            "title": "Weekly Team Standup",
            "description": "Daily standup meeting for the development team",
            "start_time": "2024-01-02 09:00:00",
            "end_time": "2024-01-02 09:30:00",
            "location": "Conference Room A",
            "attendees": "dev-team@company.com",
            "event_type": "meeting"
        },
        {
            "id": "event_006",
            "title": "Weekly Team Standup",
            "description": "Daily standup meeting for the development team",
            "start_time": "2024-01-03 09:00:00",
            "end_time": "2024-01-03 09:30:00",
            "location": "Conference Room A",
            "attendees": "dev-team@company.com",
            "event_type": "meeting"
        },
        
        # Training sessions
        {
            "id": "event_007",
            "title": "New Year Security Training",
            "description": "Annual security awareness training session",
            "start_time": "2024-01-02 14:00:00",
            "end_time": "2024-01-02 15:00:00",
            "location": "Training Room",
            "attendees": "all@company.com",
            "event_type": "training"
        },
        {
            "id": "event_008",
            "title": "Q1 Goals Setting Workshop",
            "description": "Workshop to set Q1 individual and team goals",
            "start_time": "2024-01-03 10:00:00",
            "end_time": "2024-01-03 11:30:00",
            "location": "Conference Room B",
            "attendees": "team@company.com",
            "event_type": "workshop"
        },
        
        # Company events
        {
            "id": "event_009",
            "title": "New Year All Hands",
            "description": "Company-wide all hands meeting to kick off 2024",
            "start_time": "2024-01-03 15:00:00",
            "end_time": "2024-01-03 16:00:00",
            "location": "Main Auditorium",
            "attendees": "all@company.com",
            "event_type": "meeting"
        },
        {
            "id": "event_010",
            "title": "IT Infrastructure Review",
            "description": "Monthly IT infrastructure review meeting",
            "start_time": "2024-01-03 11:00:00",
            "end_time": "2024-01-03 12:00:00",
            "location": "IT Conference Room",
            "attendees": "it-team@company.com",
            "event_type": "meeting"
        }
    ]
    
    for event in events:
        cursor.execute("""
            INSERT OR IGNORE INTO events (custom_id, title, description, start_time, end_time, location, attendees, event_type, project_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event["id"], event["title"], event["description"], event["start_time"], event["end_time"],
            event.get("location"), event.get("attendees"), event["event_type"],
            event.get("project_name")
        ))
    
    conn.commit()
    conn.close()

def create_slack_database():
    """Create and populate Slack database for test case 1"""
    conn = sqlite3.connect("data/databases/slack.db")
    cursor = conn.cursor()
    
    # Create messages table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            custom_id TEXT UNIQUE,
            channel TEXT NOT NULL,
            user TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            is_mention BOOLEAN DEFAULT 0,
            thread_id TEXT
        )
    """)
    
    # Test Case 1: 3-day OOO period (Jan 1-3, 2024) - 20% important, 80% noise
    messages = [
        # IMPORTANT MESSAGES (20% - 2 out of 10)
        {
            "id": "slack_001",
            "channel": "#dev-team",
            "user": "manager@company.com",
            "message": "@john.doe URGENT: Production API is down. Need you to investigate immediately when you're back.",
            "timestamp": "2024-01-02 09:15:00",
            "is_mention": 1,
            "thread_id": "urgent_001"
        },
        {
            "id": "slack_002",
            "channel": "#general",
            "user": "cto@company.com",
            "message": "@john.doe We need to discuss the Q1 technical roadmap. Please schedule a meeting when you return.",
            "timestamp": "2024-01-03 16:00:00",
            "is_mention": 1,
            "thread_id": "roadmap_001"
        },
        
        # NOISE MESSAGES (80% - 8 out of 10)
        # New Year messages
        {
            "id": "slack_003",
            "channel": "#general",
            "user": "ceo@company.com",
            "message": "Happy New Year everyone! 🎉 Looking forward to an amazing 2024!",
            "timestamp": "2024-01-01 00:05:00",
            "is_mention": 0,
            "thread_id": "newyear_001"
        },
        {
            "id": "slack_004",
            "channel": "#random",
            "user": "alice@company.com",
            "message": "Anyone else excited about 2024? I have so many goals! 💪",
            "timestamp": "2024-01-01 10:30:00",
            "is_mention": 0,
            "thread_id": "goals_001"
        },
        
        # General chatter
        {
            "id": "slack_005",
            "channel": "#dev-team",
            "user": "bob@company.com",
            "message": "Good morning team! Hope everyone had a great New Year break.",
            "timestamp": "2024-01-02 08:30:00",
            "is_mention": 0,
            "thread_id": "morning_001"
        },
        {
            "id": "slack_006",
            "channel": "#general",
            "user": "sarah@company.com",
            "message": "The office coffee machine is working great today! ☕",
            "timestamp": "2024-01-02 09:45:00",
            "is_mention": 0,
            "thread_id": "coffee_001"
        },
        
        # Meeting discussions
        {
            "id": "slack_007",
            "channel": "#meetings",
            "user": "hr@company.com",
            "message": "Reminder: Q1 Goals Setting Workshop tomorrow at 10 AM",
            "timestamp": "2024-01-02 17:00:00",
            "is_mention": 0,
            "thread_id": "workshop_001"
        },
        {
            "id": "slack_008",
            "channel": "#announcements",
            "user": "it@company.com",
            "message": "System maintenance completed successfully. All services are back online.",
            "timestamp": "2024-01-03 06:30:00",
            "is_mention": 0,
            "thread_id": "maintenance_001"
        },
        
        # Team updates
        {
            "id": "slack_009",
            "channel": "#dev-team",
            "user": "alice@company.com",
            "message": "Just finished reviewing the new API documentation. Looks good!",
            "timestamp": "2024-01-03 11:00:00",
            "is_mention": 0,
            "thread_id": "docs_001"
        },
        {
            "id": "slack_010",
            "channel": "#general",
            "user": "marketing@company.com",
            "message": "New Year promotion is live! Check out our latest features 🚀",
            "timestamp": "2024-01-03 14:00:00",
            "is_mention": 0,
            "thread_id": "promo_001"
        }
    ]
    
    for message in messages:
        cursor.execute("""
            INSERT OR IGNORE INTO messages (custom_id, channel, user, message, timestamp, is_mention, thread_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            message["id"], message["channel"], message["user"], message["message"], message["timestamp"],
            message["is_mention"], message["thread_id"]
        ))
    
    conn.commit()
    conn.close()

def main():
    """Main function to create all databases for Test Case 1"""
    
    # Create databases directory if it doesn't exist
    os.makedirs("data/databases", exist_ok=True)
    
    create_email_database()
    create_calendar_database()
    create_slack_database()

if __name__ == "__main__":
    main()

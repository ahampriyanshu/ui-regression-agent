#!/usr/bin/env python3
"""
Test script for JIRA ticket creation functionality
"""

import asyncio
import json
import os
from src.agent import UIRegressionAgent

async def test_jira_creation():
    """Test JIRA ticket creation with improved error handling"""
    
    print("🧪 Testing JIRA Ticket Creation...")
    print("=" * 50)
    
    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  No OpenAI API key found. This test will use fallback mode.")
        print("   Set OPENAI_API_KEY to test with real LLM responses.")
    else:
        print("✅ OpenAI API key found. Testing with real LLM responses.")
    
    # Create agent
    agent = UIRegressionAgent()
    
    # Test issue details (simulating a critical issue)
    test_issue = {
        "difference_id": 1,
        "element_type": "button",
        "change_description": "Register button text changed to 'Sign Up' without JIRA ticket",
        "location": "bottom right of form",
        "severity": "high",
        "classification": "CRITICAL",
        "reasoning": "Button text changed from 'Register' to 'Sign Up' with no corresponding JIRA ticket",
        "jira_match": None,
        "action_required": "file_jira"
    }
    
    print(f"\n🎫 Creating JIRA ticket for test issue...")
    print(f"Issue: {test_issue['change_description']}")
    
    try:
        # Test ticket creation
        ticket = await agent.create_jira_ticket_for_issue(test_issue)
        
        if ticket:
            print(f"✅ JIRA ticket created successfully!")
            print(f"   Ticket ID: {ticket['id']}")
            print(f"   Title: {ticket['title']}")
            print(f"   Priority: {ticket['priority']}")
            print(f"   Status: {ticket['status']}")
            
            # Show full ticket details
            print(f"\n📋 Full Ticket Details:")
            print(json.dumps(ticket, indent=2))
            
        else:
            print("❌ Failed to create JIRA ticket")
            
    except Exception as e:
        print(f"❌ Error during ticket creation: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_jira_creation())

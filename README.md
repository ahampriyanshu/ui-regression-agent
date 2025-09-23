## Scenario
You're a QA engineer and your team has deployed three UI updates to the login page. The product manager is asking about regression testing, but you're staring at folders full of before/after screenshots and a JIRA board with dozens of tickets.

You need to check if the changes match planned features or if there are unexpected regressions. For each issue found, you'll need to decide whether to file a critical bug report, log a minor issue, or simply confirm an expected change.

Your manager expects a comprehensive report by noon, but doing this manually means you'll miss other important testing work. You need an AI agent that can automate this entire UI regression workflow.

## Task
Build a multi-modal AI agent that compares webpage screenshots and manages UI regression issues by:

Comparing baseline and updated screenshots using LLM vision capabilities to detect UI differences.

Analyzing detected differences against existing JIRA tickets to classify changes as expected, minor issues, or critical regressions.

Taking automated actions like creating JIRA tickets for critical issues, updating ticket statuses, and logging minor issues.

Providing structured feedback on all UI changes and actions taken.

Returns detailed analysis results and JIRA ticket updates.

## Requirements
Implement a three-agent system with specialized responsibilities:

ImageDiffAgent
Uses LLM vision to compare two webpage screenshots and identify differences.

Detects changes in UI elements like buttons, text, layouts, colors, and positioning.

Returns structured list of differences with descriptions and severity levels.

Must handle error cases like identical images or invalid image types.

ClassificationAgent
Analyzes UI differences against existing JIRA tickets to classify changes.

Determines if changes match planned features or represent unexpected regressions.

Categorizes differences into resolved tickets, pending work, and new issues.

Filters only UI-related tickets for analysis.

OrchestratorAgent
Executes actions based on classification results with JIRA integration.

Updates resolved tickets to "done" status for completed features.

Moves pending tickets to "on_hold" with explanatory comments.

Creates new JIRA tickets for critical regression issues.

Tracks all actions taken and validates successful execution.

Workflow must run in this order:
ImageDiffAgent compares screenshots and identifies UI differences

ClassificationAgent analyzes differences against JIRA tickets and categorizes changes

OrchestratorAgent executes appropriate actions and updates JIRA tickets

System returns summary of differences found and actions taken

## Examples
Input Screenshots
Baseline: Login page with blue "Login" button and text input
Updated: Login page with green "Login" button and password input with eye icon

Expected JIRA Tickets:
UI-001: Add "Forgot Password?" link (with question mark)
UI-002: Change password input type from text to password  
UI-003: Change Login button color from blue to green

ImageDiffAgent Output
[
  {
    "description": "Forgot Password link added but without question mark",
    "element_type": "link",
    "severity": "low"
  },
  {
    "description": "Password input field now shows as password type with eye icon",
    "element_type": "input",
    "severity": "low"
  },
  {
    "description": "Login button color changed from blue to green",
    "element_type": "button", 
    "severity": "medium"
  },
  {
    "description": "Register button text changed to Sign Up", 
    "element_type": "button",
    "severity": "high"
  },
  {
    "description": "About link missing from navigation header",
    "element_type": "navigation",
    "severity": "high"
  }
]

ClassificationAgent Output
{
  "resolved_tickets": [
    {
      "ticket_id": "UI-002",
      "reason": "Password input change matches ticket requirements exactly"
    },
    {
      "ticket_id": "UI-003", 
      "reason": "Login button color change implemented as specified"
    }
  ],
  "pending_tickets": [
    {
      "ticket_id": "UI-001",
      "reason": "Forgot Password link added but missing question mark as specified"
    }
  ],
  "new_tickets": [
    {
      "title": "Unexpected button text change",
      "description": "Register button text changed to Sign Up without authorization",
      "severity": "critical",
      "priority": "high",
      "type": "fix",
      "assignee": "frontend.dev",
      "reporter": "ui_regression.agent",
      "status": "todo"
    },
    {
      "title": "Missing About link in header",
      "description": "About navigation link missing from header - critical navigation issue",
      "severity": "critical",
      "priority": "high", 
      "type": "fix",
      "assignee": "frontend.dev",
      "reporter": "ui_regression.agent",
      "status": "todo"
    }
  ]
}

Final Output
{
  "status": "completed",
  "differences_found": 5,
  "jira_updates": 4,
  "details": {
    "resolved_tickets": ["UI-002", "UI-003"],
    "pending_tickets": ["UI-001"],
    "new_tickets": ["UI-004", "UI-005"]
  }
}

Error Example
Input Screenshots
Two identical login page screenshots

ImageDiffAgent Output
{
  "error": "IMAGES_TOO_SIMILAR"
}

Final Output
{
  "status": "error",
  "message": "Images are too similar to detect meaningful differences"
}

Constraints
The challenge focuses on implementing specific components while leveraging existing infrastructure:

Implement prompts for ImageDiffAgent and ClassificationAgent in text files.
Implement Python logic for OrchestratorAgent methods and JIRA operations.
Work with provided tools and infrastructure:
llm.py for LLM calls and vision processing
mcp_servers/jira.py for JIRA ticket operations  
constants/ for ticket status, priority, and user definitions
All agent scaffolding and workflow orchestration is provided.

Error handling is mandatory:
ImageDiffAgent must detect and report similar images or invalid image types
ClassificationAgent must handle cases with no differences or no matching tickets
OrchestratorAgent must validate successful JIRA operations and handle failures

Output format requirements:
ImageDiffAgent returns list of difference objects with description, element_type, severity
ClassificationAgent returns three lists: resolved_tickets, pending_tickets, new_tickets  
OrchestratorAgent returns summary with ticket counts and action details
Error cases return status "error" with descriptive message

Implementation Guide
Build the working UI regression agent by completing these components:

### Prompts
prompts/image_diff_agent.txt - LLM prompt for screenshot comparison and difference detection
prompts/classification_agent.txt - LLM prompt for analyzing differences against JIRA tickets

### Python Code  
src/orchestrator_agent.py methods:
execute_actions() - Main orchestration method
update_resolved_tickets() - Mark completed tickets as done
update_pending_tickets() - Move tickets to on_hold with comments
create_tickets_for_new_issues() - Create JIRA tickets for critical issues

### Streamlit Web Interface
The project includes a beautiful web interface built with Streamlit for interactive testing and visualization:

Run and Test
# Run the app
bash setup/run.sh

# Run test cases
bash setup/test.sh

## Tips for Success
Focus on prompt writing - Clear, specific prompts lead to better LLM outputs
Test incrementally - Run tests after implementing each method
Use the provided examples - Study the test data to understand expected outputs
Handle edge cases - Consider empty data, malformed inputs, and error scenarios
Use the Streamlit app - Visualize your results and test interactively
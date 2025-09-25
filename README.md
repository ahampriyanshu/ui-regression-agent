# UI Regression Testing Agent

## Scenario

You have joined a new team as a QA engineer and discovered several JIRA tickets in review status with corresponding changes deployed to the preview environment. Your approval is required before these changes can be deployed to production. You need an AI agent that can automate the entire UI regression workflow by comparing screenshots from different environments, analyzing changes against existing tickets, and making appropriate updates to JIRA tickets.

## Task

Build a multi-modal AI agent system that automates UI regression testing by implementing three specialized agents:

- **ImageDiffAgent** - Uses LLM to compare webpage screenshots and detect UI differences.
- **ClassificationAgent** - Analyzes UI differences against existing JIRA tickets to categorize the differences.
- **OrchestratorAgent** - Executes JIRA workflow actions: updates resolved tickets, moves pending tickets to on_hold, creates new tickets.

## Implementation Requirements

Complete the missing components to create a working UI regression system:

**Prompts**
- `prompts/image_diff_agent.txt` - Screenshot comparison logic
- `prompts/classification_agent.txt` - JIRA ticket analysis logic

**Core orchestration logic**
- `src/orchestrator_agent.py` methods:
  - `orchestrate_jira_workflow()` - Main workflow orchestrator
  - `update_resolved_issues()` - Mark completed tickets as done
  - `update_pending_issues()` - Move tickets to on_hold with comments  
  - `create_new_issues()` - Create JIRA tickets for differences not covered by existing JIRA tickets

**New Ticket Requirements**
All newly created tickets must follow organizational standards:

  - **Priority**: Set based on severity from the classifier
  - **Type**: Bug (unplanned UI regressions)
  - **Assignee**: frontend.dev (UI issues routed to frontend team)
  - **Reporter**: ui_regression.agent (automated system identification)
  - **Status**: todo (ready for development team pickup)

## Evaluation

Your implementation will be tested against a realistic scenario with multiple JIRA tickets and UI changes:

### Initial State
- **7 total JIRA tickets** exist in the system (UI, Backend, DevOps, Data tickets)
- **3 UI-specific tickets** are relevant for regression testing:
  - UI-001: Add "Forgot Password?" link (with question mark)
  - UI-002: Change password input type to password with eye icon
  - UI-003: Change Login button color from blue to green

### Expected Outcomes
Your agent implementation should achieve these specific results:
- **2 tickets resolved** (UI-002, UI-003) - Changes match JIRA requirements perfectly
- **1 ticket on hold** (UI-001) - Implementation differs from specification (missing question mark)
- **2 new tickets created** - For unexpected header navigation issue (About link removal) and for text change in signup button (Register -> Sign Up)
- **Other tickets** - Non-UI tickets remain unchanged

This evaluation tests your ability to correctly classify UI changes, apply business logic for ticket status updates, and maintain data integrity across the JIRA system.

## Sample Cases

### Case 1: Valid UI Changes
**Input**
- **production.png**: Screenshot of the production environment
- **preview.png**: Screenshot of the preview environment

**ImageDiffAgent Output**
```json
{
  "differences":  [
        {
            "description": "Forgot Password link added but without question mark",
            "element_type": "link",
            "severity": "low"
        },
        ...
    ]
}
```

### Case 2: Similar Images
**Input**
- **production.png**: Login page screenshot
- **production.png**: Login page screenshot

**ImageDiffAgent Output**
```json
{
  "error": "IMAGES_TOO_SIMILAR"
}
```

### Case 3: Mismatched UI Screenshots
**Input**
- **production.png**: Login page screenshot
- **profile.png**: Profile Page screenshot

**ImageDiffAgent Output**
```json
{
  "error": "INVALID_IMAGE"
}
```

### Case 4: Blank/Invalid Screenshots
**Input**
- **production.png**: Login page screenshot
- **invalid.png**: Random placeholder image

**ImageDiffAgent Output**
```json
{
  "error": "INVALID_IMAGE"
}
```

## Success Tips

- **Prompt Engineering**: Write concise, deterministic prompts with examples
- **Classification Rules**: Mark resolved only for perfect matches, pending for partial implementations, and raise new tickets for any uncovered regressions
- **Error Handling**: Handle edge cases like identical or invalid images
- **Use the Streamlit app** - Visualize your results and test interactively

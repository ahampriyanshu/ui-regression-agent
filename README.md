# 🔍 UI Regression Agent Challenge

## 🧩 Challenge Overview

Build an AI agent that detects UI regressions between two screenshots (baseline vs new build) and decides whether to escalate them based on existing JIRA tickets.

### The Challenge

Your task is to create a **multi-modal agentic AI** that can:

1. **Compare Screenshots**: Analyze baseline vs updated UI screenshots using LLM vision capabilities
2. **Detect Changes**: Identify missing, misaligned, or changed UI elements
3. **Cross-check with JIRA**: Determine if changes match existing feature tickets
4. **Take Action**: Escalate critical issues, log minor ones, or confirm expected changes
5. **Validate Results**: Ensure all actions were completed successfully

### Real-World Scenario

You're working on a login page that has 4 JIRA tickets for planned changes:

**Existing JIRA Tickets:**
- `UI-001`: Add new href 'Forgot Password?'
- `UI-002`: Change password input from text to password type
- `UI-003`: Change Login button from blue to green
- `UI-004`: Add header with 'Home' (left) and 'About' (right)

**What Actually Changed:**
1. ✅ 'Forgot Password' link added (but missing `?`) → **Minor Issue**
2. ✅ Password field with eye icon → **Expected Change**
3. ⚠️ Login button is green BUT 'Register' changed to 'Sign Up' → **Critical Issue**
4. ⚠️ Header added BUT 'About' is next to 'Home', not on right → **Critical Issue**

## 🎯 Expected Behavior

| Change | JIRA Match | Classification | Action |
|--------|------------|----------------|---------|
| 'Forgot Password' (no ?) | Partial match UI-001 | MINOR | Log locally |
| Password field + eye icon | Exact match UI-002 | EXPECTED | Confirm & exit |
| 'Register' → 'Sign Up' | No match | CRITICAL | File new JIRA |
| 'About' positioning wrong | Partial match UI-004 | CRITICAL | File new JIRA |

## 🏗️ Architecture

```
UI Regression Agent
├── 📸 Image Analysis (LLM Vision)
├── 🎫 JIRA Integration (MCP Server)
├── 📝 Logging System
├── 🔄 Action Engine
└── ✅ Validation System
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key (for GPT-4V)
- Basic understanding of async Python

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
export OPENAI_API_KEY="your-api-key-here"
```

### Quick Demo

```bash
# Run the complete regression test
python main.py screenshots/login_baseline.png screenshots/login_updated.png

# Or use the web interface
streamlit run app.py --server.port 8000
```

## 📁 Project Structure

```
ui-regress/
├── src/
│   ├── agent.py              # Main UI Regression Agent
│   ├── prompts.py            # LLM prompts for analysis
│   ├── engine/
│   │   └── jira_integration.py  # JIRA MCP integration
│   ├── mcp_servers/
│   │   └── jira_server.py    # Mock JIRA server
│   └── utils/
│       └── logger.py         # Logging utilities
├── screenshots/
│   ├── login_baseline.png    # Original UI
│   └── login_updated.png     # Updated UI with changes
├── main.py                   # CLI interface
├── app.py                    # Streamlit web interface
└── requirements.txt          # Dependencies
```

## 🔧 Key Components

### 1. UI Regression Agent (`src/agent.py`)

The main agent that orchestrates the entire workflow:

```python
class ImageDiffAgent:
    async def run_regression_test(self, baseline_path, updated_path):
        # 1. Compare screenshots using LLM vision
        differences = await self.compare_screenshots(baseline_path, updated_path)
        
        # 2. Analyze against JIRA tickets
        analysis = await self.analyze_against_jira(differences)
        
        # 3. Take appropriate actions
        actions = await self.take_action(analysis)
        
        # 4. Validate actions succeeded
        validation = await self.validate_actions(actions)
        
        return result
```

### 2. JIRA Integration (`src/engine/jira_integration.py`)

Handles all JIRA operations through MCP server:

```python
class JIRAIntegration:
    async def get_all_tickets(self) -> List[Dict]
    async def create_ticket(self, title, description, priority) -> Dict
    async def search_tickets(self, query) -> List[Dict]
```

### 3. Logging System (`src/utils/logger.py`)

Comprehensive logging for all agent activities:

```python
class UIRegressionLogger:
    def log_minor_issue(self, issue)      # → logs/minor_issues.jsonl
    def log_critical_issue(self, issue)   # → logs/critical_issues.jsonl
    def log_expected_change(self, change) # → logs/expected_changes.jsonl
```

## 🧪 Testing

Run the test suite to validate your implementation:

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/test_ui_regression_agent.py::TestImageDiffAgent
```

### Test Scenarios

The test suite covers:
- ✅ Image encoding and processing
- ✅ LLM integration and error handling
- ✅ JIRA ticket operations
- ✅ Action execution and validation
- ✅ Expected regression scenarios

## 📊 Expected Output

When you run the agent, you should see:

```
🔍 Starting UI Regression Analysis...
📸 Baseline: screenshots/login_baseline.png
📸 Updated: screenshots/login_updated.png
--------------------------------------------------
✅ Status: completed
🔍 Differences Found: 4
⚡ Actions Taken: 3
✅ Validation: Successful

📊 Summary Report:
  • Minor Issues: 1
  • Critical Issues: 2
  • Expected Changes: 1
  • Actions Taken: 3

🎯 Actions Taken:
  • 📝 Minor Issue Logged
  • 🎫 JIRA Ticket Created: UI-005
  • 🎫 JIRA Ticket Created: UI-006
  • ✅ Expected Change Confirmed (JIRA: UI-002)
```

## 🎓 Learning Objectives

By completing this challenge, you'll learn:

1. **Multi-modal AI**: Using LLM vision capabilities for image analysis
2. **Agent Architecture**: Building complex, stateful AI agents
3. **Integration Patterns**: Working with external systems (JIRA) via MCP
4. **Error Handling**: Robust error handling in async environments
5. **Testing**: Comprehensive testing of AI agent systems
6. **Real-world Applications**: Practical automation for QA workflows

## 🏆 Success Criteria

Your agent should:
- ✅ Correctly identify all 4 UI differences
- ✅ Properly classify each change (MINOR/CRITICAL/EXPECTED)
- ✅ Take appropriate actions (log/escalate/confirm)
- ✅ Validate all actions completed successfully
- ✅ Pass all test cases
- ✅ Handle errors gracefully

## 🚨 Common Pitfalls

1. **Image Processing**: Ensure proper base64 encoding for LLM vision
2. **Async Handling**: All JIRA operations are async - don't forget `await`
3. **JSON Parsing**: LLM responses need robust JSON parsing with error handling
4. **File Paths**: Use absolute paths for cross-platform compatibility
5. **Validation**: Always validate that actions actually succeeded

## 🔍 Debugging Tips

1. **Check Logs**: All activities are logged in the `logs/` directory
2. **Use Streamlit**: The web interface shows detailed analysis results
3. **Mock Responses**: Test with mocked LLM responses first
4. **JIRA Server**: Ensure the MCP JIRA server is running
5. **Image Files**: Verify screenshot files exist and are readable

## 🌟 Extensions

Once you've completed the basic challenge, try these extensions:

1. **Batch Processing**: Handle multiple screenshot pairs
2. **Confidence Scores**: Add confidence levels to classifications
3. **Historical Analysis**: Track regression trends over time
4. **Custom Rules**: Add configurable business rules
5. **Slack Integration**: Send notifications to team channels

## 📚 Resources

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [OpenAI Vision API](https://platform.openai.com/docs/guides/vision)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 🤝 Support

If you get stuck:
1. Check the test cases for expected behavior
2. Review the logs for detailed error information
3. Use the Streamlit interface for visual debugging
4. Refer to the comprehensive docstrings in the code

---

**Good luck building your UI Regression Agent! 🚀**
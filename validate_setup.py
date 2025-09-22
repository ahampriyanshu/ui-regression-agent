#!/usr/bin/env python3
"""
Validation script for UI Regression Agent Challenge
"""

import os
import sys
import asyncio
from pathlib import Path

def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (NOT FOUND)")
        return False

def check_directory_structure():
    """Validate the project directory structure"""
    print("🔍 Checking Project Structure...")
    print("=" * 50)
    
    required_files = [
        ("README.md", "Main documentation"),
        ("requirements.txt", "Python dependencies"),
        ("main.py", "CLI interface"),
        ("app.py", "Streamlit web interface"),
        ("setup.py", "Setup script"),
        ("hackerrank.yml", "HackerRank configuration"),
        ("src/agent.py", "Main UI Regression Agent"),
        ("src/prompts.py", "LLM prompts"),
        ("src/engine/jira_integration.py", "JIRA integration"),
        ("src/utils/logger.py", "Logging utilities"),
        ("src/test_agent.py", "Test suite"),
        ("screenshots/login_baseline.png", "Baseline screenshot"),
        ("screenshots/login_updated.png", "Updated screenshot"),
    ]
    
    all_exist = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Check if required dependencies are available"""
    print("\n🔧 Checking Dependencies...")
    print("=" * 50)
    
    required_modules = [
        "fastapi",
        "llama_index",
        "streamlit", 
        "PIL",
        "pytest"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} is installed")
        except ImportError:
            print(f"❌ {module} is NOT installed")
            missing_modules.append(module)
    
    return len(missing_modules) == 0

def check_environment():
    """Check environment variables"""
    print("\n🌍 Checking Environment...")
    print("=" * 50)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"✅ OPENAI_API_KEY is set (length: {len(openai_key)})")
        return True
    else:
        print("❌ OPENAI_API_KEY is not set")
        print("   Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False

async def test_agent_functionality():
    """Test basic agent functionality"""
    print("\n🧪 Testing Agent Functionality...")
    print("=" * 50)
    
    try:
        from src.agent import UIRegressionAgent
        
        # Test agent initialization
        agent = UIRegressionAgent()
        print("✅ Agent initialization successful")
        
        # Test JIRA integration
        tickets = await agent.jira.get_all_tickets()
        print(f"✅ JIRA integration working ({len(tickets)} tickets found)")
        
        # Test logger
        agent.logger.logger.info("Test log message")
        print("✅ Logger working")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent functionality test failed: {e}")
        return False

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running Test Suite...")
    print("=" * 50)
    
    import subprocess
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "src/test_agent.py", "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def print_challenge_summary():
    """Print the challenge summary"""
    print("\n🎯 UI Regression Agent Challenge Summary")
    print("=" * 50)
    print("""
This challenge implements a complete UI Regression Detection Agent that:

🔍 **Core Functionality:**
  • Compares baseline vs updated screenshots using LLM vision
  • Detects UI differences (missing, changed, misaligned elements)
  • Cross-references changes with existing JIRA tickets
  • Classifies issues as CRITICAL, MINOR, or EXPECTED
  • Takes appropriate actions (file JIRA, log locally, confirm expected)

🏗️ **Architecture:**
  • Multi-modal AI agent using GPT-4V for image analysis
  • Mock JIRA integration for ticket management
  • Comprehensive logging system for audit trails
  • Async/await pattern for scalable operations
  • Full test coverage with pytest

📊 **Expected Scenarios:**
  1. 'Forgot Password' (no ?) → MINOR (log locally)
  2. Password field + eye icon → EXPECTED (confirm & exit)
  3. 'Register' → 'Sign Up' → CRITICAL (file new JIRA)
  4. 'About' positioning wrong → CRITICAL (file new JIRA)

🚀 **Usage:**
  • CLI: python main.py screenshots/login_baseline.png screenshots/login_updated.png
  • Web: streamlit run app.py --server.port 8000
  • Tests: python -m pytest

🎓 **Learning Objectives:**
  • Multi-modal AI development
  • Agent architecture patterns
  • Async Python programming
  • Real-world QA automation
  • Testing AI systems
""")

async def main():
    """Main validation function"""
    print("🔍 UI Regression Agent Challenge Validation")
    print("=" * 60)
    
    checks = []
    
    # Check project structure
    checks.append(check_directory_structure())
    
    # Check dependencies
    checks.append(check_dependencies())
    
    # Check environment
    env_ok = check_environment()
    checks.append(env_ok)
    
    # Test agent functionality (only if environment is OK)
    if env_ok:
        checks.append(await test_agent_functionality())
        checks.append(run_tests())
    else:
        print("\n⚠️  Skipping functionality tests due to missing OPENAI_API_KEY")
        checks.extend([False, False])
    
    # Print results
    print("\n📊 Validation Results")
    print("=" * 50)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"🎉 ALL CHECKS PASSED ({passed}/{total})")
        print("\n✅ The UI Regression Agent Challenge is ready!")
        print("\nNext steps:")
        print("1. Set OPENAI_API_KEY if not already set")
        print("2. Run: python main.py screenshots/login_baseline.png screenshots/login_updated.png")
        print("3. Or try the web interface: streamlit run app.py --server.port 8000")
    else:
        print(f"⚠️  SOME CHECKS FAILED ({passed}/{total})")
        print("\nPlease fix the issues above before proceeding.")
    
    # Print challenge summary
    print_challenge_summary()
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

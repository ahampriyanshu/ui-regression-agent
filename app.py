"""
UI Regression Detection Agent - Unified Interface
Supports both CLI and Streamlit web interface
"""

import asyncio
import os
import sys
from typing import Dict

import streamlit as st
from PIL import Image

from src.image_diff_agent import ImageDiffAgent
from src.classification_agent import ClassificationAgent
from src.orchestrator_agent import OrchestratorAgent
from utils.logger import ui_logger


async def run_regression_test(baseline_path: str, updated_path: str) -> Dict:
    """Run the complete UI regression test workflow using all three agents"""
    ui_agent = ImageDiffAgent()
    classification_agent = ClassificationAgent()
    orchestrator_agent = OrchestratorAgent()
    logger = ui_logger

    logger.logger.info("Starting UI regression test")

    try:
        logger.logger.info(
            "Phase 1: Screenshot comparison and difference detection"
        )
        differences = await ui_agent.compare_screenshots(
            baseline_path, updated_path
        )

        if not differences.get("differences"):
            logger.logger.info("No differences found - test passed")
            return {
                "status": "success",
                "result": "no_differences",
                "message": "No UI differences detected",
            }

        logger.logger.info(
            "Found %s differences", len(differences["differences"])
        )

        logger.logger.info(
            "Phase 2: Classification and analysis against JIRA tickets"
        )
        analysis = await classification_agent.analyze_differences(
            differences["differences"]
        )

        logger.log_regression_analysis(
            baseline_path, updated_path, differences["differences"], analysis
        )

        logger.logger.info("Phase 3: Action execution and workflow management")
        results = await orchestrator_agent.execute_actions(analysis)

        summary = logger.get_summary_report()

        result = {
            "status": "completed",
            "differences_found": len(differences["differences"]),
            "jira_updates": len(results.get("resolved_tickets", []))
            + len(results.get("pending_tickets", []))
            + len(results.get("new_tickets", [])),
            "summary": summary,
            "details": {
                "differences": differences,
                "results": results,
            },
        }

        logger.logger.info("UI regression test completed successfully")
        return result

    except Exception as e:
        logger.logger.error("UI regression test failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__,
        }


async def run_cli_mode(baseline_path: str, updated_path: str):
    """Run UI regression test in CLI mode"""

    if not os.path.exists(baseline_path):
        print(f"Error: Baseline image not found at {baseline_path}")
        return

    if not os.path.exists(updated_path):
        print(f"Error: Updated image not found at {updated_path}")
        return

    print("🔍 Starting UI Regression Analysis...")
    print(f"📸 Baseline: {baseline_path}")
    print(f"📸 Updated: {updated_path}")
    print("-" * 50)

    try:
        result = await run_regression_test(baseline_path, updated_path)

        print(f"✅ Status: {result['status']}")

        if result["status"] == "completed":
            print(f"🔍 UI Changes Detected: {result['differences_found']}")

            results = result["details"]["results"]
            if any(
                [
                    results.get("resolved_tickets"),
                    results.get("pending_tickets"),
                    results.get("new_tickets"),
                ]
            ):
                print("\n📋 JIRA Ticket Updates:")

                if results.get("resolved_tickets"):
                    for ticket in results["resolved_tickets"]:
                        ticket_id = ticket.get('ticket_id', ticket.get('id', 'Unknown'))
                        print(f"  • ✅ Completed: {ticket_id}")

                if results.get("pending_tickets"):
                    for ticket in results["pending_tickets"]:
                        ticket_id = ticket.get('ticket_id', ticket.get('id', 'Unknown'))
                        print(f"  • 🔄 Needs Work: {ticket_id}")

                if results.get("new_tickets"):
                    for ticket in results["new_tickets"]:
                        ticket_id = ticket.get('id', ticket.get('ticket_id', 'Unknown'))
                        print(f"  • 🆕 New Issue: {ticket_id}")


        elif result["status"] == "success":
            print(f"✅ {result['message']}")

        else:
            print(f"❌ Error: {result.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def streamlit_interface():
    """Streamlit web interface"""
    st.set_page_config(
        page_title="UI Regression Agent", page_icon="🔍", layout="wide"
    )

    st.title("🔍 UI Regression Detection Agent")
    st.markdown("**Detect UI regressions and cross-check with JIRA tickets**")

    st.sidebar.header("Configuration")

    st.header("📸 Upload Screenshots")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Baseline Screenshot")
        baseline_file = st.file_uploader(
            "Upload baseline image",
            type=["png", "jpg", "jpeg"],
            key="baseline",
        )

        if baseline_file:
            baseline_image = Image.open(baseline_file)
            st.image(
                baseline_image,
                caption="Baseline Screenshot",
                use_container_width=True,
            )

    with col2:
        st.subheader("Updated Screenshot")
        updated_file = st.file_uploader(
            "Upload updated image", type=["png", "jpg", "jpeg"], key="updated"
        )

        if updated_file:
            updated_image = Image.open(updated_file)
            st.image(
                updated_image,
                caption="Updated Screenshot",
                use_container_width=True,
            )

    if not baseline_file or not updated_file:
        st.info(
            "💡 **Tip**: You can also use the default screenshots for testing"
        )

        if st.button("🎯 Use Default Screenshots"):
            baseline_path = "screenshots/baseline.png"
            updated_path = "screenshots/updated.png"

            if os.path.exists(baseline_path) and os.path.exists(updated_path):
                st.success("✅ Using default screenshots")

                col1, col2 = st.columns(2)
                with col1:
                    st.image(
                        baseline_path,
                        caption="Default Baseline",
                        use_container_width=True,
                    )
                with col2:
                    st.image(
                        updated_path,
                        caption="Default Updated",
                        use_container_width=True,
                    )

                st.session_state.baseline_path = baseline_path
                st.session_state.updated_path = updated_path
            else:
                st.error("❌ Default screenshots not found")

    st.header("🔍 Run Analysis")

    if st.button("🚀 Start UI Regression Analysis", type="primary"):
        baseline_path = None
        updated_path = None

        if baseline_file and updated_file:
            baseline_path = f"temp_baseline_{baseline_file.name}"
            updated_path = f"temp_updated_{updated_file.name}"

            with open(baseline_path, "wb") as f:
                f.write(baseline_file.getbuffer())
            with open(updated_path, "wb") as f:
                f.write(updated_file.getbuffer())

        elif hasattr(st.session_state, "baseline_path") and hasattr(
            st.session_state, "updated_path"
        ):
            baseline_path = st.session_state.baseline_path
            updated_path = st.session_state.updated_path

        else:
            st.error("❌ Please upload both screenshots or use default ones")
            return

        with st.spinner(
            "🔍 Analyzing screenshots and checking JIRA tickets..."
        ):
            try:
                result = asyncio.run(
                    run_regression_test(baseline_path, updated_path)
                )

                if baseline_file and updated_file:
                    try:
                        os.remove(baseline_path)
                        os.remove(updated_path)
                    except BaseException:
                        pass

                display_results(result)

            except Exception as e:
                st.error(f"❌ Error during analysis: {e}")


def display_results(result):
    """Display analysis results in Streamlit"""
    st.header("📊 Analysis Results")

    status = result.get("status", "unknown")
    if status == "completed":
        st.success("✅ Analysis completed successfully")
    elif status == "success":
        st.success(f"✅ {result.get('message', 'No differences found')}")
        return
    else:
        st.error(
            f"❌ Analysis failed: {result.get('message', 'Unknown error')}"
        )
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🔍 UI Changes", result.get("differences_found", 0))

    with col2:
        ticket_updates = result.get("jira_updates", 0)
        st.metric("📋 JIRA Updates", ticket_updates)

    with col3:
        timestamp = result.get("summary", {}).get("timestamp", "N/A")
        if timestamp != "N/A":
            timestamp = timestamp[:19].replace("T", " ")
        st.metric("⏰ Completed", timestamp)

    with col4:
        status = result.get("status", "unknown").title()
        st.metric("✅ Status", status)


    if "details" in result and "differences" in result["details"]:
        st.subheader("🔍 Differences Detected")

        differences = result["details"]["differences"].get("differences", [])
        if differences:
            for diff in differences:
                severity_color = {
                    "critical": "🔴",
                    "minor": "🟡",
                    "cosmetic": "🟢",
                }.get(diff.get("severity", "cosmetic"), "⚪")

                st.write(
                    f"{severity_color} **{diff.get('element_type', 'Unknown')}** - {diff.get('change_description', 'No description')}"
                )
                st.write(f"   📍 Location: {diff.get('location', 'Unknown')}")
                st.write(f"   ℹ️ Details: {diff.get('details', 'No details')}")
                st.write("---")
        else:
            st.info("No differences detected")

    with st.expander("🔧 Raw Analysis Data"):
        st.json(result)


def main():
    """Main entry point - CLI or Streamlit based on execution context"""
    if len(sys.argv) > 1:
        if len(sys.argv) != 3:
            print(
                "Usage: python app.py <baseline_image_path> <updated_image_path>"
            )
            print(
                "Example: python app.py screenshots/login_baseline.png screenshots/login_updated.png"
            )
            print("Or run: streamlit run app.py")
            sys.exit(1)

        baseline_path = sys.argv[1]
        updated_path = sys.argv[2]

        asyncio.run(run_cli_mode(baseline_path, updated_path))
    else:
        streamlit_interface()


if __name__ == "__main__":
    main()

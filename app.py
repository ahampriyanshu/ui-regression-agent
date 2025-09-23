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

        elif result["status"] == "error":
            error_message = result.get("message", "Unknown error")
            
            # Handle specific error types with user-friendly messages
            if "Images are too similar" in error_message:
                print("⚠️  Images Too Similar")
                print("The provided screenshots appear to be identical or nearly identical.")
                print("Please provide screenshots with visible differences for comparison.")
            elif "not valid webpage screenshots" in error_message:
                print("⚠️  Invalid Image Type")
                print("One or both images do not appear to be webpage screenshots.")
                print("Please provide valid webpage screenshots for UI regression testing.")
            else:
                print(f"❌ Analysis Error: {error_message}")
        else:
            print(f"❌ Error: {result.get('message', 'Unknown error')}")

    except Exception as e:
        error_message = str(e)
        
        # Handle specific error types with user-friendly messages
        if "Images are too similar" in error_message:
            print("⚠️  Images Too Similar")
            print("The provided screenshots appear to be identical or nearly identical.")
            print("Please provide screenshots with visible differences for comparison.")
        elif "not valid webpage screenshots" in error_message:
            print("⚠️  Invalid Image Type")
            print("One or both images do not appear to be webpage screenshots.")
            print("Please provide valid webpage screenshots for UI regression testing.")
        else:
            print(f"❌ Unexpected error: {e}")


def streamlit_interface():
    """Streamlit web interface"""
    st.set_page_config(
        page_title="UI Regression Agent", page_icon="🔍", layout="wide"
    )

    st.title("🔍 UI Regression Detection Agent")
    st.markdown("**Detect UI regressions and cross-check with JIRA tickets**")
    st.header("📸 Upload Screenshots")

    col1, col2 = st.columns(2)

    with col1:
        baseline_file = st.file_uploader(
            "Upload baseline image",
            type=["png", "jpg", "jpeg"],
            key="baseline",
            help="Maximum file size: 1MB. Supported formats: PNG, JPG, JPEG"
        )

        if baseline_file:
            # Check file size (1MB = 1024*1024 bytes)
            if baseline_file.size > 1024 * 1024:
                st.error("❌ Baseline image must be less than 1MB")
            else:
                baseline_image = Image.open(baseline_file)
                st.image(
                    baseline_image,
                    caption="Baseline Screenshot",
                    width="stretch",
                )

    with col2:
        updated_file = st.file_uploader(
            "Upload updated image", 
            type=["png", "jpg", "jpeg"], 
            key="updated",
            help="Maximum file size: 1MB. Supported formats: PNG, JPG, JPEG"
        )

        if updated_file:
            # Check file size (1MB = 1024*1024 bytes)
            if updated_file.size > 1024 * 1024:
                st.error("❌ Updated image must be less than 1MB")
            else:
                updated_image = Image.open(updated_file)
                st.image(
                    updated_image,
                    caption="Updated Screenshot",
                    width="stretch",
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
                        width="stretch",
                    )
                with col2:
                    st.image(
                        updated_path,
                        caption="Default Updated",
                        width="stretch",
                    )

                st.session_state.baseline_path = baseline_path
                st.session_state.updated_path = updated_path
            else:
                st.error("❌ Default screenshots not found")

    st.header("🔍 Run Analysis")

    if st.button("🚀 Start UI Regression Analysis", type="primary"):
        # Check file sizes before processing
        if baseline_file and baseline_file.size > 1024 * 1024:
            st.error("❌ Baseline image must be less than 1MB")
            return
        
        if updated_file and updated_file.size > 1024 * 1024:
            st.error("❌ Updated image must be less than 1MB")
            return
        
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
                error_message = str(e)
                
                # Handle specific error types with user-friendly messages
                if "Images are too similar" in error_message:
                    st.warning("⚠️ Images Too Similar")
                    st.info("The provided screenshots appear to be identical or nearly identical. Please provide screenshots with visible differences for comparison.")
                elif "not valid webpage screenshots" in error_message:
                    st.warning("⚠️ Invalid Image Type")
                    st.info("One or both images do not appear to be webpage screenshots. Please provide valid webpage screenshots for UI regression testing.")
                else:
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
    elif status == "error":
        error_message = result.get("message", "Unknown error")
        
        # Handle specific error types with user-friendly messages
        if "Images are too similar" in error_message:
            st.warning("⚠️ Images Too Similar")
            st.info("The provided screenshots appear to be identical or nearly identical. Please provide screenshots with visible differences for comparison.")
        elif "not valid webpage screenshots" in error_message:
            st.warning("⚠️ Invalid Image Type")
            st.info("One or both images do not appear to be webpage screenshots. Please provide valid webpage screenshots for UI regression testing.")
        else:
            st.error(f"❌ Analysis failed: {error_message}")
        return
    else:
        st.error(
            f"❌ Analysis failed: {result.get('message', 'Unknown error')}"
        )
        return

    if "details" in result and "differences" in result["details"]:
        st.subheader("🔍 Differences Detected")

        differences = result["details"]["differences"].get("differences", [])
        if differences:
            # Create table data
            table_data = []
            for diff in differences:
                severity_icon = {
                    "high": "🔴",
                    "medium": "🟡", 
                    "low": "🟢",
                    "critical": "🔴",
                    "minor": "🟡",
                    "cosmetic": "🟢",
                }.get(diff.get("severity", "low"), "⚪")
                
                table_data.append({
                    "Element Type": diff.get("element_type", "Unknown").title(),
                    "Description": diff.get("description", "No description available"),
                    "Severity": f"{severity_icon} {diff.get('severity', 'unknown').title()}"
                })
            
            # Display as table
            st.dataframe(
                table_data,
                width="stretch",
                hide_index=True
            )
        else:
            st.info("No differences detected")

    # Display JIRA ticket updates if available
    if "details" in result and "results" in result["details"]:
        results = result["details"]["results"]
        
        # Check if we have any ticket updates to show
        has_updates = any([
            results.get("resolved_tickets"),
            results.get("pending_tickets"), 
            results.get("new_tickets")
        ])
        
        if has_updates:
            st.subheader("📋 JIRA Ticket Updates")
            
            if results.get("resolved_tickets"):
                st.success("**✅ Resolved Tickets**")
                for ticket in results["resolved_tickets"]:
                    ticket_id = ticket.get('ticket_id', ticket.get('id', 'Unknown'))
                    st.write(f"• {ticket_id} - Marked as completed")
            
            if results.get("pending_tickets"):
                st.warning("**🔄 Pending Tickets**") 
                for ticket in results["pending_tickets"]:
                    ticket_id = ticket.get('ticket_id', ticket.get('id', 'Unknown'))
                    reason = ticket.get('reason', 'Needs further work')
                    st.write(f"• {ticket_id} - On hold: {reason}")
            
            if results.get("new_tickets"):
                st.error("**🆕 New Issues Created**")
                for ticket in results["new_tickets"]:
                    ticket_id = ticket.get('id', ticket.get('ticket_id', 'Unknown'))
                    st.write(f"• {ticket_id} - New critical issue reported")

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

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


async def run_regression_test(production_path: str, preview_path: str) -> Dict:
    """Run the complete UI regression test workflow using all three agents"""
    ui_agent = ImageDiffAgent()
    classification_agent = ClassificationAgent()
    orchestrator_agent = OrchestratorAgent()

    print("🔍 Starting UI regression analysis...")

    try:
        print("📷 Analyzing screenshots for differences...")
        differences = await ui_agent.compare_screenshots(
            production_path, preview_path
        )

        if not differences.get("differences"):
            print("✅ No differences detected - analysis complete")
            return {
                "status": "success",
                "result": "no_differences",
                "message": "No UI differences detected",
            }

        print("🎯 Classifying changes against JIRA tickets...")
        analysis = await classification_agent.analyze_differences(
            differences["differences"]
        )

        print("📋 Updating JIRA tickets...")
        await orchestrator_agent.orchestrate_jira_workflow(analysis)

        result = {
            "status": "completed",
            "differences_found": len(differences["differences"]),
            "details": {
                "differences": differences,
                "analysis": analysis,
            },
        }

        print("✅ UI regression analysis completed successfully")
        return result

    except Exception as e:
        print("❌ Analysis failed - check error details above")
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__,
        }


async def run_cli_mode(production_path: str, preview_path: str):
    """Run UI regression test in CLI mode"""

    if not os.path.exists(production_path):
        print(f"Error: Production image not found at {production_path}")
        return

    if not os.path.exists(preview_path):
        print(f"Error: Preview image not found at {preview_path}")
        return


    try:
        result = await run_regression_test(production_path, preview_path)

        print(f"✅ Status: {result['status']}")

        if result["status"] == "completed":
            print(f"🔍 UI Changes Detected: {result['differences_found']}")

            analysis = result["details"]["analysis"]
            if any(
                [
                    analysis.get("resolved_tickets"),
                    analysis.get("pending_tickets"),
                    analysis.get("new_tickets"),
                ]
            ):
                print("\n📋 JIRA Ticket Updates:")

                if analysis.get("resolved_tickets"):
                    for ticket in analysis["resolved_tickets"]:
                        ticket_id = ticket.get('ticket_id', 'Unknown')
                        print(f"  > ✅ Completed: {ticket_id}")

                if analysis.get("pending_tickets"):
                    for ticket in analysis["pending_tickets"]:
                        ticket_id = ticket.get('ticket_id', 'Unknown')
                        print(f"  > 🔄 On Hold: {ticket_id}")

                if analysis.get("new_tickets"):
                    for ticket in analysis["new_tickets"]:
                        title = ticket.get('title', 'Unknown')
                        print(f"  > 🆕 New Issue: {title}")


        elif result["status"] == "success":
            print(f"✅ {result['message']}")

        elif result["status"] == "error":
            error_message = result.get("message", "Unknown error")
            
            if "Images are too similar" in error_message:
                print("⚠️  Images Too Similar")
                print("The provided screenshots appear to be identical or nearly identical.")
                print("Please provide screenshots with visible differences for comparison.")
            elif "Invalid or mismatched webpage screenshots" in error_message:
                print("⚠️  Invalid Image Type")
                print("One or both images do not appear to be webpage screenshots.")
                print("Please provide valid webpage screenshots for UI regression testing.")
            else:
                print(f"❌ Analysis Error: {error_message}")
        else:
            print(f"❌ Error: {result.get('message', 'Unknown error')}")

    except Exception as e:
        error_message = str(e)
        
        if "Images are too similar" in error_message:
            print("⚠️  Images Too Similar")
            print("The provided screenshots appear to be identical or nearly identical.")
            print("Please provide screenshots with visible differences for comparison.")
        elif "Invalid or mismatched webpage screenshots" in error_message:
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
        production_file = st.file_uploader(
            "Upload production image",
            type=["png", "jpg", "jpeg"],
            key="baseline",
            help="Maximum file size: 1MB. Supported formats: PNG, JPG, JPEG"
        )

        if production_file:
            if production_file.size > 1024 * 1024:
                st.error("❌ Baseline image must be less than 1MB")
            else:
                production_image = Image.open(production_file)
                st.image(
                    production_image,
                    caption="Baseline Screenshot",
                    width="stretch",
                )

    with col2:
        preview_file = st.file_uploader(
            "Upload preview image", 
            type=["png", "jpg", "jpeg"], 
            key="preview",
            help="Maximum file size: 1MB. Supported formats: PNG, JPG, JPEG"
        )

        if preview_file:
            if preview_file.size > 1024 * 1024:
                st.error("❌ Updated image must be less than 1MB")
            else:
                preview_image = Image.open(preview_file)
                st.image(
                    preview_image,
                    caption="Updated Screenshot",
                    width="stretch",
                )

    if not production_file or not preview_file:
        st.info(
            "💡 **Tip**: You can also use the default screenshots for testing"
        )

        if st.button("🎯 Use Default Screenshots"):
            production_path = "screenshots/production.png"
            preview_path = "screenshots/preview.png"

            if os.path.exists(production_path) and os.path.exists(preview_path):
                st.success("✅ Using default screenshots")

                col1, col2 = st.columns(2)
                with col1:
                    st.image(
                        production_path,
                        caption="Default Baseline",
                        width="stretch",
                    )
                with col2:
                    st.image(
                        preview_path,
                        caption="Default Updated",
                        width="stretch",
                    )

                st.session_state.production_path = production_path
                st.session_state.preview_path = preview_path
            else:
                st.error("❌ Default screenshots not found")

    st.header("🔍 Run Analysis")

    if st.button("🚀 Start UI Regression Analysis", type="primary"):
        if production_file and production_file.size > 1024 * 1024:
            st.error("❌ Production image must be less than 1MB")
            return
        
        if preview_file and preview_file.size > 1024 * 1024:
            st.error("❌ Preview image must be less than 1MB")
            return
        
        production_path = None
        preview_path = None

        if production_file and preview_file:
            production_path = f"temp_production_{production_file.name}"
            preview_path = f"temp_preview_{preview_file.name}"

            with open(production_path, "wb") as f:
                f.write(production_file.getbuffer())
            with open(preview_path, "wb") as f:
                f.write(preview_file.getbuffer())

        elif hasattr(st.session_state, "production_path") and hasattr(
            st.session_state, "preview_path"
        ):
            production_path = st.session_state.production_path
            preview_path = st.session_state.preview_path

        else:
            st.error("❌ Please upload both screenshots or use default ones")
            return

        with st.spinner(
            "🔍 Analyzing screenshots and checking JIRA tickets..."
        ):
            try:
                result = asyncio.run(
                    run_regression_test(production_path, preview_path)
                )

                if production_file and preview_file:
                    try:
                        os.remove(production_path)
                        os.remove(preview_path)
                    except BaseException:
                        pass

                display_results(result)

            except Exception as e:
                error_message = str(e)
                
                if "Images are too similar" in error_message:
                    st.warning("⚠️ Images Too Similar")
                    st.info("The provided screenshots appear to be identical or nearly identical. Please provide screenshots with visible differences for comparison.")
                elif "Invalid or mismatched webpage screenshots" in error_message:
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
        
        if "Images are too similar" in error_message:
            st.warning("⚠️ Images Too Similar")
            st.info("The provided screenshots appear to be identical or nearly identical. Please provide screenshots with visible differences for comparison.")
        elif "Invalid or mismatched webpage screenshots" in error_message:
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
            
            st.dataframe(
                table_data,
                width="stretch",
                hide_index=True
            )
    else:
            st.info("No differences detected")

    if "details" in result and "analysis" in result["details"]:
        analysis = result["details"]["analysis"]
        
        has_updates = any([
            analysis.get("resolved_tickets"),
            analysis.get("pending_tickets"), 
            analysis.get("new_tickets")
        ])
        
        if has_updates:
            st.subheader("📋 JIRA Ticket Updates")
            
            if analysis.get("resolved_tickets"):
                st.success("**✅ Resolved Tickets**")
                for ticket in analysis["resolved_tickets"]:
                    ticket_id = ticket.get('ticket_id', 'Unknown')
                    st.write(f"> {ticket_id} - Marked as completed")
            
            if analysis.get("pending_tickets"):
                st.warning("**🔄 Pending Tickets**") 
                for ticket in analysis["pending_tickets"]:
                    ticket_id = ticket.get('ticket_id', 'Unknown')
                    reason = ticket.get('reason', 'Needs further work')
                    st.write(f"> {ticket_id} - On hold: {reason}")
            
            if analysis.get("new_tickets"):
                st.error("**🆕 New Issues Created**")
                for ticket in analysis["new_tickets"]:
                    title = ticket.get('title', 'Unknown')
                    st.write(f"> {title} - New critical issue reported")

    with st.expander("🔧 Raw Analysis Data"):
        st.json(result)


def main():
    """Main entry point - CLI or Streamlit based on execution context"""
    if len(sys.argv) > 1:
        if len(sys.argv) != 3:
            print(
                "Usage: python app.py <production_image_path> <preview_image_path>"
            )
            print(
                "Example: python app.py screenshots/production.png screenshots/preview.png"
            )
            print("Or run: streamlit run app.py")
            sys.exit(1)

        production_path = sys.argv[1]
        preview_path = sys.argv[2]

        asyncio.run(run_cli_mode(production_path, preview_path))
    else:
        streamlit_interface()


if __name__ == "__main__":
    main()

"""
Streamlit Web Interface for UI Regression Agent
"""

import asyncio
import json
import os
from io import BytesIO

import streamlit as st
from PIL import Image

from src.agent import agent


def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="UI Regression Agent",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 UI Regression Detection Agent")
    st.markdown("**Detect UI regressions and cross-check with JIRA tickets**")
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # File upload section
    st.header("📸 Upload Screenshots")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Baseline Screenshot")
        baseline_file = st.file_uploader(
            "Upload baseline image",
            type=['png', 'jpg', 'jpeg'],
            key="baseline"
        )
        
        if baseline_file:
            baseline_image = Image.open(baseline_file)
            st.image(baseline_image, caption="Baseline Screenshot", use_column_width=True)
    
    with col2:
        st.subheader("Updated Screenshot")
        updated_file = st.file_uploader(
            "Upload updated image",
            type=['png', 'jpg', 'jpeg'],
            key="updated"
        )
        
        if updated_file:
            updated_image = Image.open(updated_file)
            st.image(updated_image, caption="Updated Screenshot", use_column_width=True)
    
    # Use default screenshots if none uploaded
    if not baseline_file or not updated_file:
        st.info("💡 **Tip**: You can also use the default screenshots for testing")
        
        if st.button("🎯 Use Default Screenshots"):
            baseline_path = "screenshots/login_baseline.png"
            updated_path = "screenshots/login_updated.png"
            
            if os.path.exists(baseline_path) and os.path.exists(updated_path):
                st.success("✅ Using default screenshots")
                
                # Display default images
                col1, col2 = st.columns(2)
                with col1:
                    st.image(baseline_path, caption="Default Baseline", use_column_width=True)
                with col2:
                    st.image(updated_path, caption="Default Updated", use_column_width=True)
                
                # Store paths in session state
                st.session_state.baseline_path = baseline_path
                st.session_state.updated_path = updated_path
            else:
                st.error("❌ Default screenshots not found")
    
    # Analysis section
    st.header("🔍 Run Analysis")
    
    if st.button("🚀 Start UI Regression Analysis", type="primary"):
        # Determine image paths
        baseline_path = None
        updated_path = None
        
        if baseline_file and updated_file:
            # Save uploaded files temporarily
            baseline_path = f"temp_baseline_{baseline_file.name}"
            updated_path = f"temp_updated_{updated_file.name}"
            
            with open(baseline_path, "wb") as f:
                f.write(baseline_file.getbuffer())
            with open(updated_path, "wb") as f:
                f.write(updated_file.getbuffer())
        
        elif hasattr(st.session_state, 'baseline_path') and hasattr(st.session_state, 'updated_path'):
            baseline_path = st.session_state.baseline_path
            updated_path = st.session_state.updated_path
        
        else:
            st.error("❌ Please upload both screenshots or use default ones")
            return
        
        # Run analysis
        with st.spinner("🔍 Analyzing screenshots and checking JIRA tickets..."):
            try:
                # Run the async function
                result = asyncio.run(agent.run_regression_test(baseline_path, updated_path))
                
                # Clean up temporary files
                if baseline_file and updated_file:
                    try:
                        os.remove(baseline_path)
                        os.remove(updated_path)
                    except:
                        pass
                
                # Display results
                display_results(result)
                
    except Exception as e:
                st.error(f"❌ Error during analysis: {e}")


def display_results(result):
    """Display analysis results"""
    st.header("📊 Analysis Results")
    
    # Status
    status = result.get('status', 'unknown')
    if status == 'completed':
        st.success("✅ Analysis completed successfully")
    elif status == 'success':
        st.success(f"✅ {result.get('message', 'No differences found')}")
        return
    else:
        st.error(f"❌ Analysis failed: {result.get('message', 'Unknown error')}")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔍 Differences Found", result.get('differences_found', 0))
    
    with col2:
        st.metric("⚡ Actions Taken", result.get('actions_taken', 0))
    
    with col3:
        validation_status = "✅ Success" if result.get('validation_successful') else "❌ Failed"
        st.metric("✅ Validation", validation_status)
    
    with col4:
        summary = result.get('summary', {})
        total_issues = summary.get('minor_issues', 0) + summary.get('critical_issues', 0)
        st.metric("🚨 Total Issues", total_issues)
    
    # Detailed summary
    if 'summary' in result:
        st.subheader("📈 Summary Report")
        summary = result['summary']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Issue Breakdown:**")
            st.write(f"• Minor Issues: {summary.get('minor_issues', 0)}")
            st.write(f"• Critical Issues: {summary.get('critical_issues', 0)}")
            st.write(f"• Expected Changes: {summary.get('expected_changes', 0)}")
        
        with col2:
            st.write("**Actions Summary:**")
            st.write(f"• Actions Taken: {summary.get('actions_taken', 0)}")
            st.write(f"• Successful Validations: {summary.get('successful_validations', 0)}")
            st.write(f"• Failed Validations: {summary.get('failed_validations', 0)}")
    
    # Actions taken
    if 'details' in result and 'actions' in result['details']:
        st.subheader("🎯 Actions Taken")
        
        actions = result['details']['actions']
        if actions:
            for i, action in enumerate(actions):
                action_type = action['action']
                
                if action_type == 'jira_ticket_created':
                    st.success(f"🎫 **JIRA Ticket Created**: {action['ticket_id']}")
                    with st.expander(f"View Issue Details - {action['ticket_id']}"):
                        st.json(action['issue'])
                
                elif action_type == 'minor_issue_logged':
                    st.warning("📝 **Minor Issue Logged**")
                    with st.expander("View Minor Issue Details"):
                        st.json(action['issue'])
                
                elif action_type == 'expected_change_confirmed':
                    st.info(f"✅ **Expected Change Confirmed** (JIRA: {action['jira_ticket']})")
                    with st.expander("View Change Details"):
                        st.json(action['issue'])
                
                elif action_type == 'jira_creation_failed':
                    st.error("❌ **JIRA Ticket Creation Failed**")
                    with st.expander("View Failed Issue"):
                        st.json(action['issue'])
        else:
            st.info("No actions were required")
    
    # Differences found
    if 'details' in result and 'differences' in result['details']:
        st.subheader("🔍 Differences Detected")
        
        differences = result['details']['differences'].get('differences', [])
        if differences:
            for i, diff in enumerate(differences):
                severity_color = {
                    'high': '🔴',
                    'medium': '🟡', 
                    'low': '🟢'
                }.get(diff.get('severity', 'low'), '⚪')
                
                st.write(f"{severity_color} **{diff.get('element_type', 'Unknown')}** - {diff.get('change_description', 'No description')}")
                st.write(f"   📍 Location: {diff.get('location', 'Unknown')}")
                st.write(f"   ℹ️ Details: {diff.get('details', 'No details')}")
                st.write("---")
        else:
            st.info("No differences detected")
    
    # Analysis details
    if 'details' in result and 'analysis' in result['details']:
        st.subheader("🧠 JIRA Analysis")
        
        analysis = result['details']['analysis'].get('analysis', [])
        if analysis:
            for item in analysis:
                classification = item.get('classification', 'UNKNOWN')
                
                if classification == 'CRITICAL':
                    st.error(f"🚨 **Critical Issue** - {item.get('reasoning', 'No reasoning')}")
                elif classification == 'MINOR':
                    st.warning(f"⚠️ **Minor Issue** - {item.get('reasoning', 'No reasoning')}")
                elif classification == 'EXPECTED':
                    st.success(f"✅ **Expected Change** - {item.get('reasoning', 'No reasoning')}")
else:
                    st.info(f"ℹ️ **{classification}** - {item.get('reasoning', 'No reasoning')}")
                
                if item.get('jira_match'):
                    st.write(f"   🎫 Matches JIRA: {item['jira_match']}")
                
                st.write("---")
    
    # Raw data (collapsible)
    with st.expander("🔧 Raw Analysis Data"):
        st.json(result)


if __name__ == "__main__":
    main()
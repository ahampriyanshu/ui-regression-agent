"""
Logging utilities for UI Regression Agent
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List


class UIRegressionLogger:
    """Custom logger for UI regression testing"""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize logger with specified directory"""
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup main logger
        self.logger = logging.getLogger("ui_regression")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = os.path.join(log_dir, "ui_regression.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_regression_analysis(self, baseline_image: str, updated_image: str, 
                              differences: List[Dict], analysis: Dict):
        """Log the complete regression analysis"""
        timestamp = datetime.now().isoformat()
        
        analysis_data = {
            "timestamp": timestamp,
            "baseline_image": baseline_image,
            "updated_image": updated_image,
            "differences_found": len(differences),
            "differences": differences,
            "analysis": analysis
        }
        
        # Log to main log file
        self.logger.info(f"UI Regression Analysis completed: {len(differences)} differences found")
        
        # Save detailed analysis to JSON file
        analysis_file = os.path.join(self.log_dir, f"analysis_{timestamp.replace(':', '-')}.json")
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        self.logger.info(f"Detailed analysis saved to: {analysis_file}")
    
    def log_minor_issue(self, issue: Dict):
        """Log minor issues that don't require JIRA escalation"""
        timestamp = datetime.now().isoformat()
        
        minor_issue_data = {
            "timestamp": timestamp,
            "type": "MINOR_ISSUE",
            "issue": issue
        }
        
        # Log to main log
        self.logger.warning(f"Minor UI issue detected: {issue.get('change_description', 'Unknown')}")
        
        # Append to minor issues file
        minor_issues_file = os.path.join(self.log_dir, "minor_issues.jsonl")
        with open(minor_issues_file, 'a') as f:
            f.write(json.dumps(minor_issue_data) + '\n')
        
        self.logger.info(f"Minor issue logged to: {minor_issues_file}")
    
    def log_critical_issue(self, issue: Dict, jira_ticket: Dict = None):
        """Log critical issues that require JIRA escalation"""
        timestamp = datetime.now().isoformat()
        
        critical_issue_data = {
            "timestamp": timestamp,
            "type": "CRITICAL_ISSUE",
            "issue": issue,
            "jira_ticket": jira_ticket
        }
        
        # Log to main log
        self.logger.error(f"Critical UI issue detected: {issue.get('change_description', 'Unknown')}")
        
        if jira_ticket:
            self.logger.info(f"JIRA ticket created: {jira_ticket.get('id', 'Unknown')}")
        
        # Append to critical issues file
        critical_issues_file = os.path.join(self.log_dir, "critical_issues.jsonl")
        with open(critical_issues_file, 'a') as f:
            f.write(json.dumps(critical_issue_data) + '\n')
        
        self.logger.info(f"Critical issue logged to: {critical_issues_file}")
    
    def log_expected_change(self, change: Dict, jira_ticket: Dict):
        """Log expected changes that match JIRA tickets"""
        timestamp = datetime.now().isoformat()
        
        expected_change_data = {
            "timestamp": timestamp,
            "type": "EXPECTED_CHANGE",
            "change": change,
            "matching_jira_ticket": jira_ticket
        }
        
        # Log to main log
        self.logger.info(f"Expected UI change confirmed: {change.get('change_description', 'Unknown')}")
        self.logger.info(f"Matches JIRA ticket: {jira_ticket.get('id', 'Unknown')}")
        
        # Append to expected changes file
        expected_changes_file = os.path.join(self.log_dir, "expected_changes.jsonl")
        with open(expected_changes_file, 'a') as f:
            f.write(json.dumps(expected_change_data) + '\n')
    
    def log_action_taken(self, action: str, details: Dict):
        """Log actions taken by the agent"""
        timestamp = datetime.now().isoformat()
        
        action_data = {
            "timestamp": timestamp,
            "action": action,
            "details": details
        }
        
        self.logger.info(f"Action taken: {action}")
        
        # Append to actions file
        actions_file = os.path.join(self.log_dir, "actions.jsonl")
        with open(actions_file, 'a') as f:
            f.write(json.dumps(action_data) + '\n')
    
    def log_validation_result(self, action: str, success: bool, details: Dict):
        """Log validation results for actions taken"""
        timestamp = datetime.now().isoformat()
        
        validation_data = {
            "timestamp": timestamp,
            "action": action,
            "success": success,
            "details": details
        }
        
        if success:
            self.logger.info(f"Action validation successful: {action}")
        else:
            self.logger.error(f"Action validation failed: {action}")
        
        # Append to validation file
        validation_file = os.path.join(self.log_dir, "validations.jsonl")
        with open(validation_file, 'a') as f:
            f.write(json.dumps(validation_data) + '\n')
    
    def get_summary_report(self) -> Dict:
        """Generate a summary report of all logged activities"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "minor_issues": 0,
            "critical_issues": 0,
            "expected_changes": 0,
            "actions_taken": 0,
            "successful_validations": 0,
            "failed_validations": 0
        }
        
        # Count minor issues
        minor_issues_file = os.path.join(self.log_dir, "minor_issues.jsonl")
        if os.path.exists(minor_issues_file):
            with open(minor_issues_file, 'r') as f:
                summary["minor_issues"] = len(f.readlines())
        
        # Count critical issues
        critical_issues_file = os.path.join(self.log_dir, "critical_issues.jsonl")
        if os.path.exists(critical_issues_file):
            with open(critical_issues_file, 'r') as f:
                summary["critical_issues"] = len(f.readlines())
        
        # Count expected changes
        expected_changes_file = os.path.join(self.log_dir, "expected_changes.jsonl")
        if os.path.exists(expected_changes_file):
            with open(expected_changes_file, 'r') as f:
                summary["expected_changes"] = len(f.readlines())
        
        # Count actions and validations
        actions_file = os.path.join(self.log_dir, "actions.jsonl")
        if os.path.exists(actions_file):
            with open(actions_file, 'r') as f:
                summary["actions_taken"] = len(f.readlines())
        
        validations_file = os.path.join(self.log_dir, "validations.jsonl")
        if os.path.exists(validations_file):
            with open(validations_file, 'r') as f:
                for line in f:
                    validation = json.loads(line)
                    if validation.get("success"):
                        summary["successful_validations"] += 1
                    else:
                        summary["failed_validations"] += 1
        
        return summary


# Global logger instance
ui_logger = UIRegressionLogger()

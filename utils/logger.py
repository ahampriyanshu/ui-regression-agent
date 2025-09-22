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
        

        self.logger = logging.getLogger("ui_regression")
        self.logger.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
    
    def initialize_logs(self):
        """Initialize log files with empty content"""
        log_files = {
            "minor_issues.json": []
        }
        
        for log_file, initial_content in log_files.items():
            file_path = os.path.join(self.log_dir, log_file)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(initial_content, f, indent=2)
    
    def log_regression_analysis(self, baseline_image: str, updated_image: str, 
                              differences: List[Dict], analysis: Dict):
        """Log the complete regression analysis"""

        self.logger.info(f"UI Regression Analysis completed: {len(differences)} differences found")
    
    def log_minor_issue(self, issue: Dict):
        """Log minor issues that don't require JIRA escalation"""
        timestamp = datetime.now().isoformat()
        
        minor_issue_data = {
            "timestamp": timestamp,
            "type": "MINOR_ISSUE",
            "issue": issue
        }
        

        self.logger.warning(f"Minor UI issue detected: {issue.get('change_description', 'Unknown')}")
        

        minor_issues_file = os.path.join(self.log_dir, "minor_issues.json")
        
        try:
            with open(minor_issues_file, 'r', encoding='utf-8') as f:
                existing_issues = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_issues = []
        
        existing_issues.append(minor_issue_data)
        
        with open(minor_issues_file, 'w', encoding='utf-8') as f:
            json.dump(existing_issues, f, indent=2)
        
        self.logger.info(f"Minor issue logged to: {minor_issues_file}")
    
    
    def get_summary_report(self) -> Dict:
        """Generate a summary report of all logged activities"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "minor_issues": 0
        }
        

        minor_issues_file = os.path.join(self.log_dir, "minor_issues.json")
        if os.path.exists(minor_issues_file):
            try:
                with open(minor_issues_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    summary["minor_issues"] = len(data) if isinstance(data, list) else 0
            except (json.JSONDecodeError, FileNotFoundError):
                summary["minor_issues"] = 0
        
        return summary

ui_logger = UIRegressionLogger()

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
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(console_handler)


    def log_regression_analysis(
        self,
        baseline_image: str,
        updated_image: str,
        differences: List[Dict],
        analysis: Dict,
    ):
        """Log the complete regression analysis"""

        self.logger.info(
            f"UI Regression Analysis completed: {len(differences)} differences found"
        )


    def get_summary_report(self) -> Dict:
        """Generate a summary report of all logged activities"""
        return {"timestamp": datetime.now().isoformat()}


ui_logger = UIRegressionLogger()

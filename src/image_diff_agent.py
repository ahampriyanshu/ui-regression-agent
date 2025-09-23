import os
import re
from typing import Dict
import json

from llm import complete_vision
from utils.logger import ui_logger


class ImageDiffAgent:
    """Agent responsible for comparing screenshots and detecting UI differences
    using LLM"""

    def __init__(self):
        """Initialize the UI regression agent"""
        self.logger = ui_logger
        self.ui_regression_prompt = self._load_ui_regression_prompt()

    def _load_ui_regression_prompt(self) -> str:
        """Load the UI regression prompt from file"""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__), "..", "prompts", "image_diff_agent.txt"
            )
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return (
                "Compare the baseline and updated screenshots for "
                "UI differences."
            )

    async def compare_screenshots(
        self, baseline_path: str, updated_path: str
    ) -> Dict:
        """Compare two screenshots and identify differences using LLM"""
        self.logger.logger.info(
            "Comparing screenshots: %s vs %s", baseline_path, updated_path
        )

        self.logger.logger.info("Sending request to LLM for image comparison")

        try:
            # Use centralized LLM client for vision completion
            response_text = await complete_vision(
                self.ui_regression_prompt, [baseline_path, updated_path]
            )

            self.logger.logger.info("Received LLM response: %s", response_text)

            try:
                differences_data = json.loads(response_text)
                self.logger.logger.info(
                    "Successfully parsed LLM response as JSON"
                )
                
                # Check for error conditions
                if "error" in differences_data:
                    error_code = differences_data["error"]
                    if error_code == "IMAGES_TOO_SIMILAR":
                        raise ValueError("Images are too similar to detect meaningful differences")
                    elif error_code == "INVALID_IMAGE_TYPE":
                        raise ValueError("One or both images are not valid webpage screenshots")
                    else:
                        raise ValueError(f"LLM returned error: {error_code}")
                
                return differences_data
            except json.JSONDecodeError as e:
                self.logger.logger.warning("JSON decode error: %s", e)

                markdown_json_match = re.search(
                    r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL
                )
                if markdown_json_match:
                    try:
                        differences_data = json.loads(
                            markdown_json_match.group(1)
                        )
                        self.logger.logger.info(
                            "Successfully extracted JSON from markdown"
                        )
                        
                        # Check for error conditions
                        if "error" in differences_data:
                            error_code = differences_data["error"]
                            if error_code == "IMAGES_TOO_SIMILAR":
                                raise ValueError("Images are too similar to detect meaningful differences")
                            elif error_code == "INVALID_IMAGE_TYPE":
                                raise ValueError("One or both images are not valid webpage screenshots")
                            else:
                                raise ValueError(f"LLM returned error: {error_code}")
                        
                        return differences_data
                    except json.JSONDecodeError:
                        pass

                json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if json_match:
                    try:
                        differences_data = json.loads(json_match.group())
                        self.logger.logger.info(
                            "Successfully extracted JSON using regex"
                        )
                        
                        # Check for error conditions
                        if "error" in differences_data:
                            error_code = differences_data["error"]
                            if error_code == "IMAGES_TOO_SIMILAR":
                                raise ValueError("Images are too similar to detect meaningful differences")
                            elif error_code == "INVALID_IMAGE_TYPE":
                                raise ValueError("One or both images are not valid webpage screenshots")
                            else:
                                raise ValueError(f"LLM returned error: {error_code}")
                        
                        return differences_data
                    except json.JSONDecodeError:
                        pass

                self.logger.logger.error("No valid JSON found in LLM response")
                raise ValueError(
                    "LLM response does not contain valid JSON"
                ) from e

        except Exception as e:
            self.logger.logger.error("LLM analysis failed: %s", e)
            raise

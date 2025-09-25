import os
import re
from typing import Dict
import json

from llm import complete_vision


class ImageDiffAgent:
    """Agent responsible for comparing screenshots and detecting UI differences
    using LLM"""

    def __init__(self):
        """Initialize the UI regression agent"""
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
                "Compare the production and preview screenshots for " "UI differences."
            )

    async def compare_screenshots(
        self, production_path: str, preview_path: str
    ) -> Dict:
        """Compare two screenshots and identify differences using LLM"""
        try:
            response_text = await complete_vision(
                self.ui_regression_prompt, [production_path, preview_path]
            )

            try:
                differences_data = json.loads(response_text)

                if "error" in differences_data:
                    error_code = differences_data["error"]
                    if error_code == "IMAGES_TOO_SIMILAR":
                        raise ValueError(
                            "Images are too similar to detect meaningful differences"
                        )
                    elif error_code == "INVALID_IMAGE":
                        raise ValueError("Invalid or mismatched webpage screenshots")
                    else:
                        raise ValueError(f"LLM returned error: {error_code}")

                return differences_data
            except json.JSONDecodeError as e:
                markdown_json_match = re.search(
                    r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL
                )
                if markdown_json_match:
                    try:
                        differences_data = json.loads(markdown_json_match.group(1))

                        if "error" in differences_data:
                            error_code = differences_data["error"]
                            if error_code == "IMAGES_TOO_SIMILAR":
                                raise ValueError(
                                    "Images are too similar to detect meaningful differences"
                                )
                            elif error_code == "INVALID_IMAGE":
                                raise ValueError(
                                    "Invalid or mismatched webpage screenshots"
                                )
                            else:
                                raise ValueError(f"LLM returned error: {error_code}")

                        return differences_data
                    except json.JSONDecodeError:
                        pass

                json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if json_match:
                    try:
                        differences_data = json.loads(json_match.group())

                        if "error" in differences_data:
                            error_code = differences_data["error"]
                            if error_code == "IMAGES_TOO_SIMILAR":
                                raise ValueError(
                                    "Images are too similar to detect meaningful differences"
                                )
                            elif error_code == "INVALID_IMAGE":
                                raise ValueError(
                                    "Invalid or mismatched webpage screenshots"
                                )
                            else:
                                raise ValueError(f"LLM returned error: {error_code}")

                        return differences_data
                    except json.JSONDecodeError:
                        pass

                raise ValueError("LLM response does not contain valid JSON") from e

        except Exception:
            raise

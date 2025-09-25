import os
import json
import re
from typing import Dict

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
        response_text = await complete_vision(
            self.ui_regression_prompt, [production_path, preview_path]
        )

        differences_data = self._parse_response(response_text)
        self._raise_for_error_code(differences_data)
        return differences_data

    def _parse_response(self, response_text: str) -> Dict:
        """Best-effort JSON parsing with support for common formatting issues."""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as err:
            markdown_json_match = re.search(
                r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL
            )
            if markdown_json_match:
                try:
                    return json.loads(markdown_json_match.group(1))
                except json.JSONDecodeError:
                    pass

            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            raise ValueError("LLM response does not contain valid JSON") from err

    @staticmethod
    def _raise_for_error_code(response: Dict) -> None:
        """Raise descriptive errors for known error codes in the response."""
        error_code = response.get("error")
        if not error_code:
            return

        if error_code == "IMAGES_TOO_SIMILAR":
            raise ValueError("Images are too similar to detect meaningful differences")
        if error_code == "INVALID_IMAGE":
            raise ValueError("Invalid or mismatched webpage screenshots")
        raise ValueError(f"LLM returned error: {error_code}")

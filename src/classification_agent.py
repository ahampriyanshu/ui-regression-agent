import json
import os
import re
from typing import Dict, List

from llama_index.llms.openai import OpenAI
from mcp_servers.jira import JIRAMCPServer
from utils.logger import ui_logger


class ClassificationAgent:
    """Agent responsible for analyzing UI differences against JIRA tickets
    and classifying them"""

    def __init__(self):
        self.jira = JIRAMCPServer()
        self.logger = ui_logger
        self.analysis_prompt = self._load_analysis_prompt()

    def _load_analysis_prompt(self) -> str:
        """Load the difference analysis prompt from file"""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "prompts",
                "difference_analysis.txt",
            )
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return (
                "Analyze the UI differences against JIRA tickets to "
                "classify them."
            )

    async def analyze_differences(self, differences: List[Dict]) -> Dict:
        """Analyze UI differences against JIRA tickets and classify them"""
        self.logger.logger.info("Analyzing differences against JIRA tickets")

        if not differences:
            self.logger.logger.info("No differences to analyze")
            return {
                "resolved_tickets": [],
                "tickets_needing_work": [],
                "new_issues": [],
            }

        jira_tickets = await self.jira.get_all_tickets()

        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OpenAI API key is required for difference analysis. "
                "Please set OPENAI_API_KEY environment variable."
            )

        prompt = f"""
        {self.analysis_prompt}

        UI Differences Found:
        {json.dumps(differences, indent=2)}

        JIRA Tickets:
        {json.dumps(jira_tickets, indent=2)}
        """

        try:
            llm = OpenAI(model="gpt-4o", max_tokens=4096)
            response = await llm.acomplete(prompt)
            self.logger.logger.info(
                "Received analysis response: %s", response.text
            )

            try:
                analysis_data = json.loads(response.text)
                self.logger.logger.info(
                    "Successfully parsed analysis response as JSON"
                )
                return analysis_data
            except json.JSONDecodeError as e:
                self.logger.logger.warning(
                    "JSON decode error in analysis: %s", e
                )

                markdown_json_match = re.search(
                    r"```json\s*(\{.*?\})\s*```", response.text, re.DOTALL
                )
                if markdown_json_match:
                    try:
                        analysis_data = json.loads(
                            markdown_json_match.group(1)
                        )
                        self.logger.logger.info(
                            "Successfully extracted analysis JSON from markdown"
                        )
                        return analysis_data
                    except json.JSONDecodeError:
                        pass

                json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
                if json_match:
                    try:
                        analysis_data = json.loads(json_match.group())
                        self.logger.logger.info(
                            "Successfully extracted analysis JSON using regex"
                        )
                        return analysis_data
                    except json.JSONDecodeError:
                        pass

                self.logger.logger.error(
                    "No valid JSON found in analysis response"
                )
                raise ValueError(
                    "Analysis response does not contain valid JSON"
                ) from e

        except Exception as e:
            self.logger.logger.error("Difference analysis failed: %s", e)
            raise

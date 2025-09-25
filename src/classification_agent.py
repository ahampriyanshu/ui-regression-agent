import json
import os
import re
from typing import Dict, List

from llm import complete_text
from mcp_servers.jira import JIRAMCPServer


class ClassificationAgent:
    """Agent responsible for analyzing UI differences against JIRA tickets
    and classifying them"""

    def __init__(self):
        self.jira = JIRAMCPServer()
        self.classification_prompt = self._load_classification_prompt()

    def _load_classification_prompt(self) -> str:
        """Load the difference analysis prompt from file"""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "prompts",
                "classification_agent.txt",
            )
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return (
                "Analyze the UI differences against JIRA tickets to " "classify them."
            )

    def _load_analysis_prompt(self) -> str:
        return self._load_classification_prompt()

    async def analyze_differences(self, differences: List[Dict]) -> Dict:
        """Analyze UI differences against JIRA tickets and classify them"""
        if not differences:
            return {
                "resolved_tickets": [],
                "pending_tickets": [],
                "new_tickets": [],
            }

        all_tickets = await self.jira.get_all_tickets()
        jira_tickets = [
            ticket for ticket in all_tickets if ticket["id"].startswith("UI-")
        ]

        print(f"📋 Fetched {len(jira_tickets)} JIRA tickets from server")

        prompt = f"""
        {self.classification_prompt}

        UI Differences Found:
        {json.dumps(differences, indent=2)}

        JIRA Tickets:
        {json.dumps(jira_tickets, indent=2)}
        """

        try:
            response_text = await complete_text(prompt)

            try:
                analysis_data = json.loads(response_text)
                return analysis_data
            except json.JSONDecodeError as e:
                markdown_json_match = re.search(
                    r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL
                )
                if markdown_json_match:
                    try:
                        analysis_data = json.loads(markdown_json_match.group(1))
                        return analysis_data
                    except json.JSONDecodeError:
                        pass

                json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if json_match:
                    try:
                        analysis_data = json.loads(json_match.group())
                        return analysis_data
                    except json.JSONDecodeError:
                        pass

                raise ValueError("Analysis response does not contain valid JSON") from e

        except Exception:
            raise

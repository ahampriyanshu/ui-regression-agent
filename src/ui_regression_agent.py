import base64
import json
import os
import re
from typing import Dict, List

from src import llm
from utils.logger import ui_logger


class UIRegressionAgent:
    """Agent responsible for comparing screenshots and detecting UI differences using LLM"""
    
    def __init__(self):
        """Initialize the UI regression agent"""
        self.logger = ui_logger
        self.ui_regression_prompt = self._load_ui_regression_prompt()
    
    def _load_ui_regression_prompt(self) -> str:
        """Load the UI regression prompt from file"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'ui_regression.txt')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "Compare the baseline and updated screenshots for UI differences."
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 for LLM processing"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            self.logger.logger.error(f"Error encoding image {image_path}: {e}")
            return ""
    
    async def compare_screenshots(self, baseline_path: str, updated_path: str) -> Dict:
        """Compare two screenshots and identify differences using LLM"""
        self.logger.logger.info(f"Comparing screenshots: {baseline_path} vs {updated_path}")
        
        baseline_b64 = self.encode_image_to_base64(baseline_path)
        updated_b64 = self.encode_image_to_base64(updated_path)
        
        if not baseline_b64 or not updated_b64:
            self.logger.logger.error("Failed to encode one or both images")
            raise ValueError("Failed to encode images for comparison")
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key is required for UI comparison. Please set OPENAI_API_KEY environment variable.")
        
        prompt = f"""
        {self.ui_regression_prompt}
        
        Please analyze these two screenshots for UI differences:
        
        BASELINE IMAGE: The first image shows what the UI should look like
        UPDATED IMAGE: The second image shows the current state of the UI
        
        Compare these images carefully and identify any visual differences including:
        - Text changes, additions, or removals
        - Button color, size, or position changes  
        - Input field modifications
        - Layout shifts or spacing changes
        - New or missing UI elements
        - Color or styling differences
        
        Return your response as a JSON object with this structure:
        {{
            "differences": [
                {{
                    "element_type": "text|button|input|image|layout",
                    "change_description": "describe what changed",
                    "location": "where on the page this element is located",
                    "severity": "critical|minor|cosmetic", 
                    "details": "additional details about the change"
                }}
            ]
        }}
        
        If no differences are found, return: {{"differences": []}}
        
        Be thorough - even small changes matter for UI regression testing.
        """
        
        self.logger.logger.info("Sending request to LLM for image comparison")
        
        try:
            # Use OpenAI client directly for vision capabilities
            import openai
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI()
            
            # Read and encode images
            import base64
            
            with open(baseline_path, "rb") as f:
                baseline_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            with open(updated_path, "rb") as f:
                updated_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{baseline_b64}",
                                    "detail": "high"
                                }
                            },
                            {
                                "type": "image_url", 
                                "image_url": {
                                    "url": f"data:image/png;base64,{updated_b64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096
            )
            
            response_text = response.choices[0].message.content
            self.logger.logger.info(f"Received LLM response: {response_text[:200]}...")
            
            try:
                differences_data = json.loads(response_text)
                self.logger.logger.info("Successfully parsed LLM response as JSON")
                return differences_data
            except json.JSONDecodeError as e:
                self.logger.logger.warning(f"JSON decode error: {e}")
                
                markdown_json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if markdown_json_match:
                    try:
                        differences_data = json.loads(markdown_json_match.group(1))
                        self.logger.logger.info("Successfully extracted JSON from markdown")
                        return differences_data
                    except json.JSONDecodeError:
                        pass
                
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        differences_data = json.loads(json_match.group())
                        self.logger.logger.info("Successfully extracted JSON using regex")
                        return differences_data
                    except json.JSONDecodeError:
                        pass
                
                self.logger.logger.error("No valid JSON found in LLM response")
                raise ValueError("LLM response does not contain valid JSON")
                
        except Exception as e:
            self.logger.logger.error(f"LLM analysis failed: {e}")
            raise

"""
LLM Integration Module

Centralized module for handling all LLM interactions including:
- Environment variable management
- Error handling
- Vision and text completions
- Configuration management
"""

import os
from typing import Dict, List, Optional

from llama_index.core.schema import ImageDocument
from llama_index.llms.openai import OpenAI
from llama_index.multi_modal_llms.openai import OpenAIMultiModal


class LLMClient:
    """Centralized LLM client for all AI interactions"""

    def __init__(self):
        """Initialize LLM client with environment validation"""
        self._validate_environment()
        self._text_llm = None
        self._vision_llm = None

    def _validate_environment(self):
        """Validate required environment variables"""
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OpenAI API key is required for LLM operations. "
                "Please set environment variables:\n"
                "OPENAI_API_KEY=your_api_key\n"
                "OPENAI_API_BASE=https://api.openai.com/v1 (optional)\n"
                "Example: OPENAI_API_KEY=sk-your-key python app.py"
            )

    @property
    def text_llm(self) -> OpenAI:
        """Get text-only LLM instance (lazy initialization)"""
        if self._text_llm is None:
            self._text_llm = OpenAI(model="gpt-4o", max_tokens=4096)
        return self._text_llm

    @property
    def vision_llm(self) -> OpenAIMultiModal:
        """Get vision-enabled LLM instance (lazy initialization)"""
        if self._vision_llm is None:
            self._vision_llm = OpenAIMultiModal(
                model="gpt-4o", max_new_tokens=4096
            )
        return self._vision_llm

    async def complete_text(self, prompt: str) -> str:
        """
        Complete a text-only prompt

        Args:
            prompt: The text prompt to complete

        Returns:
            The LLM response text

        Raises:
            ValueError: If environment is not properly configured
            Exception: If LLM call fails
        """
        try:
            response = await self.text_llm.acomplete(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Text LLM completion failed: {e}") from e

    async def complete_vision(
        self, prompt: str, image_paths: List[str]
    ) -> str:
        """
        Complete a vision prompt with images

        Args:
            prompt: The text prompt to complete
            image_paths: List of paths to image files

        Returns:
            The LLM response text

        Raises:
            ValueError: If environment is not properly configured or images invalid
            Exception: If LLM call fails
        """
        try:
            image_documents = []
            for image_path in image_paths:
                if not os.path.exists(image_path):
                    raise ValueError(f"Image file not found: {image_path}")
                image_documents.append(ImageDocument(image_path=image_path))

            response = await self.vision_llm.acomplete(
                prompt=prompt, image_documents=image_documents
            )
            return response.text
        except Exception as e:
            raise Exception(f"Vision LLM completion failed: {e}") from e


_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get the global LLM client instance (singleton pattern)"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


async def complete_text(prompt: str) -> str:
    """
    Convenience function for text completion

    Args:
        prompt: The text prompt to complete

    Returns:
        The LLM response text
    """
    client = get_llm_client()
    return await client.complete_text(prompt)


async def complete_vision(prompt: str, image_paths: List[str]) -> str:
    """
    Convenience function for vision completion

    Args:
        prompt: The text prompt to complete
        image_paths: List of paths to image files

    Returns:
        The LLM response text
    """
    client = get_llm_client()
    return await client.complete_vision(prompt, image_paths)

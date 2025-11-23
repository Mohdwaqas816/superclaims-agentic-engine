import os
import json
import asyncio
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI

from .interface import LLMInterface

load_dotenv()


class OpenAIAdapter(LLMInterface):
    """
    Real LLM adapter for OpenAI Responses API (2024-2025+).
    - Uses JSON-mode for strict JSON outputs.
    - Compatible with gpt-4.1, gpt-4.1-mini, gpt-4.1-preview, gpt-4o, etc.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "o3-mini",
        max_retries: int = 3,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found. Add it to your .env file.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.max_retries = max_retries

    async def call(self, prompt: str) -> Any:
        """
        Sends prompt to OpenAI using JSON mode.
        Ensures the LLM returns valid JSON dictionary.
        """

        for attempt in range(self.max_retries):
            try:
                # OpenAI Python SDK call — async wrapper over sync SDK
                # (SDK is sync, so we run in thread executor)
                response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only strict JSON. No explanations."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0,
                )
                content = response.choices[0].message.content

                # Extract text from response object
                # content = response.output_text

                # Parse JSON
                parsed = self.parse_json(content)
                return parsed

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"OpenAI call failed after retries: {e}")
                await asyncio.sleep(0.5 * (attempt + 1))  # backoff retry

    def parse_json(self, raw: str) -> Dict[str, Any]:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON substring
            import re
            match = re.search(r"\{.*\}", raw, flags=re.S)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    pass
        return {}

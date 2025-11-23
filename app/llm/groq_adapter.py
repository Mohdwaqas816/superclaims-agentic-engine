import os
import json
import asyncio
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from groq import Groq

from .interface import LLMInterface

load_dotenv()


class GroqAdapter(LLMInterface):
    """
    LLM adapter for Groq's Llama 3.3 models.
    Free, fast, JSON-safe.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile",
        max_retries: int = 3,
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Add it to your .env file.")

        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.max_retries = max_retries

    async def call(self, prompt: str) -> Any:
        """
        Sends prompt to Groq Llama 3.3 using JSON-mode style constraint.
        Llama follows JSON instructions well even without 'response_format'.
        """

        system_msg = "Return ONLY valid JSON. No explanation, no text outside JSON."

        for attempt in range(self.max_retries):
            try:
                # Groq SDK is synchronous → wrap with thread executor
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0,
                )

                content = response.choices[0].message.content
                return self.parse_json(content)

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Groq Llama call failed after retries: {e}")
                await asyncio.sleep(0.5 * (attempt + 1))

    def parse_json(self, raw: str) -> Dict[str, Any]:
        """
        Strict JSON parsing with fallback substring extraction.
        """
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r"\{.*\}", raw, flags=re.S)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    pass
        return {}

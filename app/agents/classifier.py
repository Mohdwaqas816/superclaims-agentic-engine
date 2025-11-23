from .base import Agent
from typing import Dict

CLASSIFICATION_PROMPT = """
Classify this PDF into one of: bill, discharge_summary, id_card, pharmacy_bill, claim_form, other.
Respond as JSON: {{ "type": "<one_of_the_options>" }}
"""

class ClassifierAgent(Agent):
    async def run(self, filename: str, text: str) -> Dict[str, str]:
        # send to LLM and parse JSON
        prompt = CLASSIFICATION_PROMPT + "\n\nDocument text:\n" + (text or "")
        resp = await self.llm.call(prompt)
        # llm returns a dict under mock, or a string. Normalize:
        if isinstance(resp, dict):
            return resp
        try:
            return self.llm.parse_json(resp)
        except:
            # fallback guess
            return {"type": "other"}

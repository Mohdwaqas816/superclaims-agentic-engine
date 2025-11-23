from .base import Agent

DISCHARGE_PROMPT = """
You are DischargeAgent. Extract JSON:
- patient_name
- discharge_date (YYYY-MM-DD)
- diagnosis
- treating_doctor
Return JSON only.
"""

class DischargeAgent(Agent):
    async def run(self, filename: str, text: str):
        prompt = DISCHARGE_PROMPT + "\n\nDocument text:\n" + (text or "")
        resp = await self.llm.call(prompt)
        if isinstance(resp, dict):
            return resp
        return self.llm.parse_json(resp)

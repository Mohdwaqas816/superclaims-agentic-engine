from .base import Agent

BILL_PROMPT = """
You are BillAgent. Given the document text, extract strict JSON with:
- hospital_name
- patient_name
- invoice_number
- date (YYYY-MM-DD or null)
- total_amount (number) or null
Return JSON only.
"""

class BillAgent(Agent):
    async def run(self, filename: str, text: str):
        prompt = BILL_PROMPT + "\n\nDocument text:\n" + (text or "")
        resp = await self.llm.call(prompt)
        if isinstance(resp, dict):
            return resp
        return self.llm.parse_json(resp)

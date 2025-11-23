from .base import Agent

ID_PROMPT = """
You are IDAgent. From the provided text extract:
- name
- id_number
- dob (YYYY-MM-DD or null)
Return JSON only.
"""

class IDAgent(Agent):
    async def run(self, filename: str, text: str):
        prompt = ID_PROMPT + "\n\nDocument text:\n" + (text or "")
        resp = await self.llm.call(prompt)
        if isinstance(resp, dict):
            return resp
        return self.llm.parse_json(resp)

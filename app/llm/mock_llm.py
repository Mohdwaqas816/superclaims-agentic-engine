import json
import asyncio
from app.llm.interface import LLMInterface
from typing import Any, Dict

class MockLLM(LLMInterface):
    """
    Deterministic mock LLM used for testing and reviewers without API keys.
    It looks at keywords in the prompt to return structured JSON.
    """

    async def call(self, prompt: str) -> Any:
        # Simulate network latency
        await asyncio.sleep(0.01)
        pl = prompt.lower()

        # CLASSIFIER
        if "classify this pdf" in pl or "classify this pdf into one of" in pl:
            if "invoice" in pl or "total amount" in pl or "hospital" in pl:
                return {"type": "bill"}
            if "discharge" in pl or "diagnosis" in pl:
                return {"type": "discharge_summary"}
            if "id card" in pl or "id number" in pl or "dob" in pl:
                return {"type": "id_card"}
            return {"type": "other"}

        # EXTRACT TEXT
        if "extract the full text" in pl:
            # return a fake extracted text containing clues to other agents
            return {"text": "Patient Name: John Doe\nInvoice#: INV-1234\nTotal Amount: 12500\nDischarge Date: 2025-10-20\nID Number: ID9999\nDOB: 1980-01-01\nHospital: Good Health Hospital\nDiagnosis: Acute Appendicitis\nDoctor: Dr. Smith"}

        # BILL AGENT
        if "you are billagent" in pl or "hospital" in pl and "invoice" in pl:
            return {
                "hospital_name": "Good Health Hospital",
                "patient_name": "John Doe",
                "invoice_number": "INV-1234",
                "date": "2025-10-20",
                "total_amount": 12500
            }

        # DISCHARGE AGENT
        if "youdischargeagent" in pl or "dischargeagent" in pl or "discharge date" in pl or "diagnosis" in pl:
            return {
                "patient_name": "John Doe",
                "discharge_date": "2025-10-20",
                "diagnosis": "Acute Appendicitis",
                "treating_doctor": "Dr. Smith"
            }

        # ID AGENT
        if "you are idagent" in pl or "id number" in pl:
            return {
                "name": "John Doe",
                "id_number": "ID9999",
                "dob": "1980-01-01"
            }

        # Default: return a minimal JSON
        return json.dumps({"text": None})

import asyncio
from typing import List, Dict
from app.agents.classifier import ClassifierAgent
from app.agents.extractor import ExtractorAgent
from app.agents.bill_agent import BillAgent
from app.agents.discharge_agent import DischargeAgent
from app.agents.id_agent import IDAgent
from app.models import DocumentJSON, ProcessResult, ValidationResult, ClaimDecision

EXPECTED_DOCS = ["bill", "discharge_summary", "id_card"]

class Orchestrator:
    def __init__(self, llm):
        self.llm = llm
        self.classifier = ClassifierAgent(llm)
        self.extractor = ExtractorAgent(llm)
        self.bill_agent = BillAgent(llm)
        self.discharge_agent = DischargeAgent(llm)
        self.id_agent = IDAgent(llm)

    async def process_claim(self, uploaded_files: List[Dict]) -> ProcessResult:
        # 1. Extract text concurrently
        extract_tasks = [
            self.extractor.run(filename=f["filename"], file_bytes=f["content"])
            for f in uploaded_files
        ]
        extracted = await asyncio.gather(*extract_tasks)

        # 2. Classify files
        classify_tasks = []
        for f, ex in zip(uploaded_files, extracted):
            text = ex.get("text") if ex else None
            classify_tasks.append(self.classifier.run(filename=f["filename"], text=text))
        classifications = await asyncio.gather(*classify_tasks)

        documents = []
        structured_by_type = {}
        # 3. Run document-specific agents
        for f, ex, cl in zip(uploaded_files, extracted, classifications):
            doc_type = cl.get("type", "other") if cl else "other"
            text = ex.get("text") if ex else None
            structured = None
            if doc_type == "bill":
                structured = await self.bill_agent.run(f["filename"], text)
            elif doc_type == "discharge_summary":
                structured = await self.discharge_agent.run(f["filename"], text)
            elif doc_type == "id_card":
                structured = await self.id_agent.run(f["filename"], text)
            else:
                structured = {}

            documents.append(DocumentJSON(
                filename=f["filename"],
                classification=doc_type,
                extracted_text=text,
                structured=structured
            ))
            structured_by_type[doc_type] = structured

        # 4. Validation: missing docs and cross-checks
        validation = self._validate(structured_by_type)

        # 5. Decision logic
        decision = self._decide(validation)

        return ProcessResult(
            documents=documents,
            validation=validation,
            claim_decision=decision
        )

    def _validate(self, structured_by_type: Dict) -> ValidationResult:
        missing = [d for d in EXPECTED_DOCS if d not in structured_by_type]
        discrepancies = []

        # name match
        name_sources = []
        for t in ["bill", "discharge_summary", "id_card"]:
            s = structured_by_type.get(t)
            if s:
                # heuristics: many agents return keys 'patient_name' or 'name'
                name = s.get("patient_name") or s.get("name")
                if name:
                    name_sources.append((t, name))
        if len(name_sources) >= 2:
            names = [n for _, n in name_sources]
            # simple mismatch check
            first = names[0]
            for doc, name in name_sources[1:]:
                if (name or "").strip().lower() != (first or "").strip().lower():
                    discrepancies.append({
                        "type": "name_mismatch",
                        "details": {"expected": first, "mismatch_with": {doc: name}}
                    })

        # amount/date checks between bill and discharge (example)
        bill = structured_by_type.get("bill") or {}
        discharge = structured_by_type.get("discharge_summary") or {}
        if bill.get("total_amount") and discharge.get("discharge_date"):
            # primitive check: ensure date is present and amount > 0
            if float(bill.get("total_amount") or 0) <= 0:
                discrepancies.append({"type": "amount_invalid", "details": {"bill_total": bill.get("total_amount")}})

        return ValidationResult(missing_documents=missing, discrepancies=discrepancies)

    def _decide(self, validation: ValidationResult) -> ClaimDecision:
        if validation.missing_documents:
            return ClaimDecision(status="manual_review", reason=f"Missing documents: {validation.missing_documents}")
        if validation.discrepancies:
            return ClaimDecision(status="manual_review", reason=f"Discrepancies: {validation.discrepancies}")
        return ClaimDecision(status="approved", reason="All documents consistent")

from pydantic import BaseModel
from typing import List, Any, Optional, Dict

class DocumentJSON(BaseModel):
    filename: str
    classification: str
    extracted_text: Optional[str]
    structured: Optional[Dict[str, Any]]

class ValidationResult(BaseModel):
    missing_documents: List[str] = []
    discrepancies: List[Dict[str, Any]] = []

class ClaimDecision(BaseModel):
    status: str
    reason: Optional[str]

class ProcessResult(BaseModel):
    documents: List[DocumentJSON]
    validation: ValidationResult
    claim_decision: ClaimDecision

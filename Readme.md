# SuperClaims — FastAPI LLM-powered Claim Processor

## Overview

This repository contains a minimal but complete FastAPI backend that demonstrates processing multiple medical claim PDFs using LLM-powered _agents_. It classifies documents, extracts text, runs document-specific agents (Bill, Discharge, ID), validates cross-document consistency, and produces a final claim decision.

Key points:

- Async FastAPI app
- Modular agent design (classifier, extractor, BillAgent, DischargeAgent, IDAgent)
- Mock LLM included so reviewers can run without API keys
- Replaceable LLM adapters for production (OpenAI, Anthropic, Gemini, Grok, etc.)

### Architecture flow Diagram

<img width="517" height="891" alt="superclaims-engine-architecture" src="https://github.com/user-attachments/assets/4c4a303f-8d56-4573-8106-8db785a7fb1c" />

## Pre-requisites

<details open>
<summary>Python 3.10 - 3.12</summary>
<br>

- [Python Download](https://www.python.org/downloads/)

</details>
<details open>
<summary>Code Editor (Preferred)</summary>
<br>

- [VS Code Download](https://code.visualstudio.com/download)
</details>

### Folder structure

```
superclaims Engine/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── agents/
│   │   ├── base.py
│   │   ├── classifier.py
│   │   ├── extractor.py
│   │   ├── bill_agent.py
│   │   ├── discharge_agent.py
│   │   └── id_agent.py
│   ├── orchestrator.py
│   ├── llm/
│   │   ├── interface.py
│   │   ├── mock_llm.py
|   |   ├── groq_adapter.py
│   │   └── openai_adapter.py
│   └── utils.py
├── tests/
│   └── test_process_claim.py
|
├── README.md
├── requirements.txt
├── Dockerfile
└── .env.example
```

## AI tool usage

MockLLM — deterministic synthetic responses for local testing.

##### Suggested

To wire a real LLM (Groq default):

1.  Create an account on Groq (Llama) here is the [link](https://console.groq.com/)
2.  Create API keys (Llama gives good free tier tokens and API calls good for testing purpose) Doc [link](https://console.groq.com/docs/overview)
3.  Attach API key in .env
4.  You are good to hit the API :clinking_glasses:

## How to run in local

1. Clone the project

   ```bash
   git https://github.com/Mohdwaqas816/superclaims-agentic-engine.git
   ```

2. Create virtualenv & install dependencies For reference follow [link](https://virtualenv.pypa.io/en/latest/user_guide.html):

   ```bash
   python -m venv .venv
   .venv/Scripts/activate   # for windows
   pip install -r requirements.txt
   ```

3. Run uvicorn server:

   ```bash
   uvicorn app.main:app --reload
   ```

4. Test with curl or Postman upload multi-part form to POST /process-claim. Example using curl (replace files):
   ```bash
   curl -X POST "http://127.0.0.1:8000/process-claim" \
   -F "files=@/path/to/bill.pdf" \
   -F "files=@/path/to/discharge.pdf" \
   -F "files=@/path/to/id.pdf"
   ```

## Prompts (examples used in code)

For Classification

```
Classify this PDF into one of: bill, discharge_summary, id_card, pharmacy_bill, claim_form, other.
Respond as JSON.
Document text:
<document text here>
```

For Bill Agent

```
You are BillAgent. Given the document text, extract strict JSON with:
- hospital_name
- patient_name
- invoice_number
- date (YYYY-MM-DD or null)
- total_amount (number) or null
Return JSON only.
```

For Discharge Agent

```
You are DischargeAgent. Extract JSON:
- patient_name
- discharge_date (YYYY-MM-DD)
- diagnosis
- treating_doctor
Return JSON only.
```

For ID Agent

```
You are IDAgent. From the provided text extract:
- name
- id_number
- dob (YYYY-MM-DD or null)
Return JSON only.
```

## Sample Response expected JSON (complete)

```
{
  "documents": [
    {
      "filename": "bill.pdf",
      "classification": "bill",
      "extracted_text": "Patient Name: John Doe\nInvoice#: INV-1234\nTotal Amount: 12500\nDischarge Date: 2025-10-20\nID Number: ID9999\nDOB: 1980-01-01\nHospital: Good Health Hospital\nDiagnosis: Acute Appendicitis\nDoctor: Dr. Smith",
      "structured": {
        "hospital_name": "Good Health Hospital",
        "patient_name": "John Doe",
        "invoice_number": "INV-1234",
        "date": "2025-10-20",
        "total_amount": 12500
      }
    },
    {
      "filename": "discharge.pdf",
      "classification": "discharge_summary",
      "extracted_text": "Patient Name: John Doe\nInvoice#: INV-1234\nTotal Amount: 12500\nDischarge Date: 2025-10-20\n...",
      "structured": {
        "patient_name": "John Doe",
        "discharge_date": "2025-10-20",
        "diagnosis": "Acute Appendicitis",
        "treating_doctor": "Dr. Smith"
      }
    },
    {
      "filename": "id.pdf",
      "classification": "id_card",
      "extracted_text": "Patient Name: John Doe\nID Number: ID9999\nDOB: 1980-01-01",
      "structured": {
        "name": "John Doe",
        "id_number": "ID9999",
        "dob": "1980-01-01"
      }
    }
  ],
  "validation": {
    "missing_documents": [],
    "discrepancies": []
  },
  "claim_decision": {
    "status": "approved",
    "reason": "All documents consistent"
  }
}
```

### Limitations

1. Data is not persistent
2. Application is not deployed (can only work in local as of now)
3. LLM comes with certain restriction based on tokens and API calls limit, rigorous testing is not advised in free tier

### Future plan

1. Deployment of application
2. Data persistent using postgresql (Metadata storage)
3. In-memory caching using Redis to minimize latency and avoid LLM call for the same repeated document
4. Document storage using S3 bucket

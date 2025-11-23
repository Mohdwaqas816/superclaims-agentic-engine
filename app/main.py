import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from app.orchestrator import Orchestrator
# from app.llm.mock_llm import MockLLM
# from app.llm.openai_adapter import OpenAIAdapter # use if it contains token quota
from app.llm.groq_adapter import GroqAdapter
from app.models import ProcessResult

app = FastAPI(title="SuperClaims Engine - FastAPI LLM-powered processor")

# Initialize LLM adapter.
llm = GroqAdapter()
orchestrator = Orchestrator(llm=llm)


@app.post("/process-claim", response_model=ProcessResult)
async def process_claim(files: List[UploadFile] = File(...)):
    """
    Accepts multiple PDF files and returns processed structured JSON + final decision.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Read files concurrently
    async def read_file(f: UploadFile):
        data = await f.read()
        return {"filename": f.filename, "content": data}

    tasks = [read_file(f) for f in files]  # calling read file functions for every file
    uploaded = await asyncio.gather(*tasks)

    result = await orchestrator.process_claim(uploaded)
    return JSONResponse(status_code=200, content=result.model_dump())

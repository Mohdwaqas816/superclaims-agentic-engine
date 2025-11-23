import io
from pypdf import PdfReader
from .base import Agent

class ExtractorAgent(Agent):
    """
    Extracts text from PDF using PyPDF.
    LLM is NOT used here.
    """

    async def run(self, filename: str, file_bytes: bytes) -> dict:
        try:
            pdf_stream = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_stream)

            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            return {"text": text.strip() or None}

        except Exception as e:
            return {"text": None}

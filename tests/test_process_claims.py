# tests/test_process_claim.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_process_claim_minimal():
    files = {
        "files": (
            ("file1.pdf", b"%PDF-1.4 fakebill", "application/pdf"),
        )
    }
    # testclient expects structure as list of tuples:
    response = client.post("/process-claim", files=[("files", ("bill.pdf", b"%PDF-1.4 fake", "application/pdf"))])
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "claim_decision" in data

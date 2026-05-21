# Automated Document Classifier and Extractor

A minimal FastAPI service that accepts a single PDF or TXT file upload and returns a validated JSON analysis containing:

- **document_type**: short label for the document (e.g., `invoice`, `legal_contract`, `article`).
- **sentiment**: one of `positive`, `neutral`, or `negative`.
- **entities**: an array of 5 objects with `type`, `text`, and `confidence` (0–1).
- **summary**: ~3 sentence summary of the document.

**Features**
- File upload (PDF or TXT).
- Text extraction using `pdfminer.six` for PDFs.
- LLM-powered structured output via OpenRouter (optional). Falls back to a deterministic local analyzer when no API key is present.

**Tech stack**
- Python 3.12
- FastAPI (HTTP server)
- pdfminer.six (PDF text extraction)
- Pydantic v2 models for output validation

**API**
- **POST /analyze**: multipart form upload with form field `file` (PDF or TXT). Returns JSON matching the `DocumentAnalysis` schema.

Example response (trimmed):

```json
{
	"document_type": "invoice",
	"sentiment": "neutral",
	"entities": [
		{"type": "ORG", "text": "Acme Corp", "confidence": 0.92},
		{"type": "DATE", "text": "2026-05-20", "confidence": 0.87},
		{"type": "MONEY", "text": "$1,234.56", "confidence": 0.95},
		{"type": "PERSON", "text": "John Doe", "confidence": 0.78},
		{"type": "MISC", "text": "Invoice #1234", "confidence": 0.51}
	],
	"summary": "This invoice from Acme Corp dated 2026-05-20 requests payment of $1,234.56 for services rendered. The invoice references Invoice #1234 and lists John Doe as the contact. No unusual terms are present."
}
```

**Environment**
- Optionally create a `.env` file with:

```text
OPENROUTER_API_KEY=sk-...   # optional: enables OpenRouter Owl Alpha LLM integration
OWL_ALPHA_MODEL=openrouter/owl-alpha
```

When `OPENROUTER_API_KEY` is not set, the service uses a local fallback analyzer (simple heuristics) so you can test the endpoint offline.

**Quick start (Windows PowerShell)**

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Open the interactive docs at `http://127.0.0.1:8000/docs` to try the `POST /analyze` endpoint with file upload.

**Notes & next steps**
- To improve accuracy, provide task-specific examples and prompt templates for the LLM (see `src/analyzer.py`).
- Add a test harness and a 20-document gold set to measure accuracy and iterate on prompts.

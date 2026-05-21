from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile

from .extract import extract_text_from_bytes
from .analyzer import analyze_document

app = FastAPI(title="Document Classifier and Extractor")

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        text = extract_text_from_bytes(file.filename or "file", content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")

    try:
        analysis = analyze_document(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

    return JSONResponse(status_code=200, content=analysis.model_dump())

import os
import tempfile
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..extraction.file_extract import extract_text_from_file
from ..extraction.pipeline import process_evidence
from ..models import AnalyzeResponse, AnalyzeTextRequest

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(payload: AnalyzeTextRequest):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Evidence text cannot be empty")
    result = await process_evidence(payload.text, payload.evidence_source)
    return {"success": True, "extracted": result}


@router.post("/analyze-file", response_model=AnalyzeResponse)
async def analyze_file(file: UploadFile = File(...), evidence_source: str = Form("file")):
    suffix = os.path.splitext(file.filename or "")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name
    try:
        text, detected_source = extract_text_from_file(temp_path, file.content_type)
        if not text.strip():
            raise HTTPException(status_code=422, detail="No text could be extracted from this file")
        source = evidence_source if evidence_source != "file" else detected_source
        result = await process_evidence(text, source)
        return {"success": True, "extracted": result}
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass

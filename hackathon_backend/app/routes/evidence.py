import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..extraction.file_extract import extract_text_from_file
from ..extraction.pipeline import process_evidence
from ..integrity import calculate_sha256
from ..models import AnalyzeResponse, AnalyzeTextRequest, Evidence
from ..storage import save_evidence_metadata, save_file

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


# -----------------------------
# Existing extraction endpoints
# -----------------------------

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(payload: AnalyzeTextRequest):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Evidence text cannot be empty")

    result = await process_evidence(payload.text, payload.evidence_source)

    return {"success": True, "extracted": result}


@router.post("/analyze-file", response_model=AnalyzeResponse)
async def analyze_file(
    file: UploadFile = File(...),
    evidence_source: str = Form("file"),
):
    suffix = os.path.splitext(file.filename or "")[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    try:
        text, detected_source = extract_text_from_file(
            temp_path,
            file.content_type,
        )

        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted from this file",
            )

        source = (
            evidence_source
            if evidence_source != "file"
            else detected_source
        )

        result = await process_evidence(text, source)

        return {"success": True, "extracted": result}

    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass


# -----------------------------
# Evidence ingestion
# -----------------------------

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

ALLOWED_EXTENSIONS = {
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".pdf": "pdf",
    ".docx": "docx",
    ".txt": "text",
}


@router.post("/upload")
async def upload_evidence(file: UploadFile = File(...)):
    """Store an original evidence file and create its Evidence object."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must have a filename",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 50 MB size limit",
        )

    evidence_id = f"ev_{uuid4().hex}"

    evidence_type = ALLOWED_EXTENSIONS[extension]
    sha256 = calculate_sha256(content)

    stored_path = save_file(
        evidence_id,
        file.filename,
        content,
    )

    relative_path = stored_path.relative_to(
        Path(__file__).resolve().parent.parent.parent
    )

    evidence = Evidence(
        id=evidence_id,
        type=evidence_type,
        source="upload",
        filename=file.filename,
        mime_type=file.content_type,
        size=len(content),
        storage_path=str(relative_path).replace("\\", "/"),
        sha256=sha256,
        created_at=datetime.now(timezone.utc),
    )

    save_evidence_metadata(evidence)

    return {
        "success": True,
        "evidence": evidence,
    }

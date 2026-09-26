import json
from pathlib import Path
from typing import List

from .models import Evidence


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EVIDENCE_DIR = DATA_DIR / "evidence"
METADATA_FILE = DATA_DIR / "evidence.json"


def ensure_storage() -> None:
    """Create the evidence storage directories/files if they don't exist."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    if not METADATA_FILE.exists():
        METADATA_FILE.write_text("[]", encoding="utf-8")


def save_evidence_metadata(evidence: Evidence) -> None:
    """Persist an Evidence object to the JSON metadata file."""
    ensure_storage()

    try:
        existing = json.loads(
            METADATA_FILE.read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, OSError):
        existing = []

    existing.append(evidence.model_dump(mode="json"))

    METADATA_FILE.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_all_evidence() -> List[Evidence]:
    """Return all persisted evidence metadata."""
    ensure_storage()

    try:
        data = json.loads(
            METADATA_FILE.read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, OSError):
        return []

    return [Evidence.model_validate(item) for item in data]


def get_evidence_by_id(evidence_id: str) -> Evidence | None:
    """Find one evidence item by ID."""
    for evidence in get_all_evidence():
        if evidence.id == evidence_id:
            return evidence

    return None


def save_file(evidence_id: str, filename: str, content: bytes) -> Path:
    """Save original uploaded bytes and return the storage path."""
    ensure_storage()

    extension = Path(filename).suffix.lower()
    storage_filename = f"{evidence_id}{extension}"

    destination = EVIDENCE_DIR / storage_filename
    destination.write_bytes(content)

    return destination

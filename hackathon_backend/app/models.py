from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Recipient(BaseModel):
    type: Optional[str] = None
    value: Optional[str] = None


class ExtractionResult(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None
    payment_method: Optional[str] = None
    recipient: Recipient = Field(default_factory=Recipient)
    date: Optional[str] = None
    time: Optional[str] = None
    transaction_id: Optional[str] = None
    phone_numbers: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    upi_ids: List[str] = Field(default_factory=list)
    emails: List[str] = Field(default_factory=list)
    account_numbers: List[str] = Field(default_factory=list)
    sender: Optional[str] = None
    evidence_source: Optional[str] = None
    raw_text: str = ""
    sensitive_fields: List[str] = Field(default_factory=list)
    explicit_fields: List[str] = Field(default_factory=list)
    inferred_fields: List[str] = Field(default_factory=list)


class AnalyzeTextRequest(BaseModel):
    text: str
    evidence_source: str = "text"


class AnalyzeResponse(BaseModel):
    success: bool
    extracted: ExtractionResult


class Evidence(BaseModel):
    """
    Normalized evidence object produced by the ingestion layer.

    Binary file contents are stored on disk rather than inside this model.
    """

    id: str
    type: Literal["image", "pdf", "docx", "text", "url", "transaction"]
    source: Literal["upload", "chat", "url", "transaction"]

    filename: Optional[str] = None
    mime_type: Optional[str] = None
    size: Optional[int] = None
    content: Optional[str] = None
    storage_path: Optional[str] = None

    sha256: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

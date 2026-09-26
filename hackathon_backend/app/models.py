from typing import List, Optional
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

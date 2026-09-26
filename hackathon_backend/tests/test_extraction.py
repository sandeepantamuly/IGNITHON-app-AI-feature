import asyncio

from app.extraction.pipeline import process_evidence
from app.extraction.regex_extract import extract_deterministic
from app.models import ExtractionResult


def test_amount_extraction():
    result = extract_deterministic("Send ₹8,500 now")
    assert result["amounts"] == [8500.0]


def test_phone_extraction():
    result = extract_deterministic("Call 9876543210")
    assert result["phone_numbers"] == ["9876543210"]


def test_url_extraction():
    result = extract_deterministic("Visit https://example.com/login")
    assert result["urls"] == ["https://example.com/login"]


def test_upi_extraction():
    result = extract_deterministic("Pay fraudster@upi")
    assert result["upi_ids"] == ["fraudster@upi"]


def test_transaction_id_extraction():
    result = extract_deterministic("Reference TXN87231")
    assert result["transaction_ids"] == ["TXN87231"]


def test_missing_fields_are_none_or_empty():
    result = asyncio.run(process_evidence("Hello, please call me", "message"))
    assert result.amount is None
    assert result.date is None
    assert result.time is None
    assert result.upi_ids == []


def test_combined_extraction():
    result = asyncio.run(process_evidence(
        "Send ₹8,500 to fraudster@upi by tonight. Call 9876543210. Reference TXN87231.",
        "message",
    ))
    assert result.amount == 8500
    assert result.currency == "INR"
    assert result.payment_method == "UPI"
    assert result.recipient.type == "UPI"
    assert result.recipient.value == "fraudster@upi"
    assert result.transaction_id == "TXN87231"
    assert result.phone_numbers == ["9876543210"]


def test_pydantic_validation():
    result = asyncio.run(process_evidence("Send ₹8,500", "message"))
    validated = ExtractionResult.model_validate(result.model_dump())
    assert validated.amount == 8500


def test_llm_fallback_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = asyncio.run(process_evidence("Send ₹8,500 to fraudster@upi", "message"))
    assert result.amount == 8500
    assert result.upi_ids == ["fraudster@upi"]

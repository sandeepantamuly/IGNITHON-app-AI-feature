from typing import Any

from ..models import ExtractionResult, Recipient
from .llm_extract import extract_with_llm
from .regex_extract import extract_deterministic
from .sensitive import detect_sensitive_fields


def _first(items: list[Any]) -> Any:
    return items[0] if items else None


def _merge(text: str, source: str, deterministic: dict, llm: dict | None) -> dict:
    llm = llm or {}
    llm_recipient = llm.get("recipient") or {}

    upis = deterministic["upi_ids"]
    amounts = deterministic["amounts"]
    txns = deterministic["transaction_ids"]
    dates = deterministic["dates"]
    times = deterministic["times"]

    payment_method = deterministic.get("payment_method") or llm.get("payment_method")
    recipient_value = _first(upis) or llm_recipient.get("value")
    recipient_type = "UPI" if upis else llm_recipient.get("type")

    result = {
        "amount": _first(amounts) if amounts else llm.get("amount"),
        "currency": deterministic.get("currency") or llm.get("currency"),
        "payment_method": payment_method,
        "recipient": {"type": recipient_type, "value": recipient_value},
        "date": _first(dates) if dates else llm.get("date"),
        "time": _first(times) if times else llm.get("time"),
        "transaction_id": _first(txns) if txns else llm.get("transaction_id"),
        "phone_numbers": deterministic["phone_numbers"],
        "urls": deterministic["urls"],
        "upi_ids": upis,
        "emails": deterministic["emails"],
        "account_numbers": deterministic["account_numbers"],
        "sender": llm.get("sender"),
        "evidence_source": source,
        "raw_text": text,
        "explicit_fields": list(llm.get("explicit_fields") or []),
        "inferred_fields": list(llm.get("inferred_fields") or []),
    }
    result["sensitive_fields"] = detect_sensitive_fields(result)
    return result


async def process_evidence(text: str, evidence_source: str = "text") -> ExtractionResult:
    deterministic = extract_deterministic(text)
    llm = await extract_with_llm(text)
    merged = _merge(text, evidence_source, deterministic, llm)
    return ExtractionResult(**merged)

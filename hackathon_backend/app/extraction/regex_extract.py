import re
from typing import Any

AMOUNT_RE = re.compile(r"(?:₹|INR\s*)\s*([\d,]+(?:\.\d+)?)", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)")
URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
UPI_RE = re.compile(r"\b[A-Za-z0-9._-]+@[A-Za-z][A-Za-z0-9._-]*\b")
TXN_RE = re.compile(r"\b(?:TXN|UTR|RRN)[-_]?[A-Za-z0-9-]{4,}\b|\bREF[-_][A-Za-z0-9-]{4,}\b", re.IGNORECASE)
ACCOUNT_RE = re.compile(r"(?<!\d)\d{9,18}(?!\d)")
DATE_RE = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b")
TIME_RE = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d(?:\s?[AP]M)?\b|\b(?:1[0-2]|0?[1-9]):[0-5]\d\s?[AP]M\b", re.IGNORECASE)


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def extract_deterministic(text: str) -> dict[str, Any]:
    amounts = [float(x.replace(",", "")) for x in AMOUNT_RE.findall(text)]
    phones = _unique(PHONE_RE.findall(text))
    urls = _unique(URL_RE.findall(text))
    emails = _unique(EMAIL_RE.findall(text))
    upis = [x for x in _unique(UPI_RE.findall(text)) if x.lower() not in {e.lower() for e in emails}]
    txns = _unique(TXN_RE.findall(text))
    dates = _unique(DATE_RE.findall(text))
    times = _unique(TIME_RE.findall(text))

    # Avoid treating obvious phone/amount-like numbers as bank accounts.
    account_candidates = []
    for candidate in ACCOUNT_RE.findall(text):
        if candidate in phones:
            continue
        if any(str(int(a)) == candidate for a in amounts):
            continue
        account_candidates.append(candidate)

    lower = text.lower()
    payment_method = None
    if "upi" in lower:
        payment_method = "UPI"
    elif any(word in lower for word in ("credit card", "debit card", "card")):
        payment_method = "CARD"
    elif any(word in lower for word in ("bank transfer", "neft", "imps", "rtgs")):
        payment_method = "BANK_TRANSFER"

    return {
        "amounts": amounts,
        "currency": "INR" if amounts and ("₹" in text or re.search(r"\bINR\b", text, re.I)) else None,
        "phone_numbers": phones,
        "urls": urls,
        "emails": emails,
        "upi_ids": upis,
        "transaction_ids": txns,
        "dates": dates,
        "times": times,
        "account_numbers": _unique(account_candidates),
        "payment_method": payment_method,
    }

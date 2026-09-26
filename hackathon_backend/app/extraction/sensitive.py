from .regex_extract import extract_deterministic


def detect_sensitive_fields(extracted: dict) -> list[str]:
    sensitive: list[str] = []
    if extracted.get("phone_numbers"):
        sensitive.append("phone_number")
    if extracted.get("upi_ids"):
        sensitive.append("upi_id")
    if extracted.get("emails"):
        sensitive.append("email")
    if extracted.get("account_numbers"):
        sensitive.append("account_number")
    return sensitive


def mask_value(value: str) -> str:
    if len(value) <= 4:
        return "*" * len(value)
    return "*" * (len(value) - 4) + value[-4:]

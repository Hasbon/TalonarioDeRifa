import re


def normalize_phone(phone: str) -> str:
    """Normalize Colombian-style phones to digits only (keep leading country code if present)."""
    digits = re.sub(r"\D", "", phone or "")
    if not digits:
        raise ValueError("Teléfono inválido")
    if len(digits) < 7 or len(digits) > 15:
        raise ValueError("Teléfono inválido")
    return digits

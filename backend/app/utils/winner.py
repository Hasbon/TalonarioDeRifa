def derive_winner_code(winning_number: str) -> str:
    """Extract last two digits from the major prize number as zero-padded code."""
    digits = "".join(ch for ch in winning_number if ch.isdigit())
    if len(digits) < 2:
        raise ValueError("El número del premio mayor debe tener al menos dos dígitos")
    return digits[-2:].zfill(2)

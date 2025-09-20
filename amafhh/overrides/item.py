import frappe

def update_item_weight(doc, method):
    doc.custom_weight_per_unit = calculate_unit_weight(doc)


def safe_float(value, default=0.0):
    """Convert to float safely, even if None or invalid."""
    try:
        return float(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


def calculate_unit_weight(doc):
    # Get fields safely
    width = safe_float(getattr(doc, "width", 0))
    gsm = safe_float(getattr(doc, "gsm", 0))
    length = safe_float(getattr(doc, "length", 0))

    conversion_type = (getattr(doc, "item_group", "") or "").upper()

    # Weight calculation factors
    weight_factors = {
        "REAM": 3100,
        "PKT": 15500,
    }

    factor = weight_factors.get(conversion_type)
    if factor:
        return (width * gsm * length) / factor
    return 0.0

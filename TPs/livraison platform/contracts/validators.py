# contracts/validators.py

ALLOWED_CITIES = [
    "Fes",
    "Casablanca",
    "Rabat",
    "Marrakech",
    "Tanger"
]

ALLOWED_STATUS = [
    "created",
    "confirmed",
    "prepared",
    "dispatched",
    "delivered",
    "cancelled",
    "failed"
]


class ValidationError(Exception):
    """Exception métier pour toutes les erreurs de validation."""
    pass


# -------------------------
# VALIDATIONS ORDER
# -------------------------

def validate_required(value, field_name: str):
    if value is None or value == "":
        raise ValidationError(f"{field_name} is required")


def validate_city(city: str):
    if city not in ALLOWED_CITIES:
        raise ValidationError(f"city '{city}' is unknown")


def validate_amount(amount: float):
    if not isinstance(amount, (int, float)):
        raise ValidationError("amount must be a number")
    if amount <= 0:
        raise ValidationError("amount must be strictly positive")


def validate_items_count(count: int):
    if not isinstance(count, int):
        raise ValidationError("items_count must be integer")
    if count <= 0:
        raise ValidationError("items_count must be strictly positive")


def validate_status(status: str):
    if status not in ALLOWED_STATUS:
        raise ValidationError(f"status '{status}' is invalid")


# -------------------------
# VALIDATIONS EVENT
# -------------------------

def validate_event_type(event_type: str):
    allowed = [
        "order_created",
        "order_confirmed",
        "order_prepared",
        "order_dispatched",
        "order_delivered",
        "order_cancelled",
        "delivery_failed"
    ]

    if event_type not in allowed:
        raise ValidationError(f"event_type '{event_type}' is invalid")
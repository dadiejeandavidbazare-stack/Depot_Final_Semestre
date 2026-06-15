# contracts/order.py

from dataclasses import dataclass
from contracts.validators import (
    validate_city,
    validate_amount,
    validate_status,
    validate_items_count,
    validate_required,
    ValidationError
)


@dataclass
class Order:
    order_id: str
    customer_id: str
    city: str
    zone: str
    courier_id: str
    amount: float
    items_count: int
    status: str

    # -------------------------
    # VALIDATION AUTOMATIQUE
    # -------------------------
    def __post_init__(self):
        self.validate()

    def validate(self):
        validate_required(self.order_id, "order_id")
        validate_required(self.customer_id, "customer_id")
        validate_required(self.zone, "zone")
        validate_required(self.courier_id, "courier_id")

        validate_city(self.city)
        validate_amount(self.amount)
        validate_items_count(self.items_count)
        validate_status(self.status)

    # -------------------------
    # SERIALISATION JSON
    # -------------------------
    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "city": self.city,
            "zone": self.zone,
            "courier_id": self.courier_id,
            "amount": self.amount,
            "items_count": self.items_count,
            "status": self.status,
        }

    # -------------------------
    # DESERIALISATION JSON
    # -------------------------
    @staticmethod
    def from_dict(data: dict):
        try:
            return Order(
                order_id=data["order_id"],
                customer_id=data["customer_id"],
                city=data["city"],
                zone=data["zone"],
                courier_id=data["courier_id"],
                amount=data["amount"],
                items_count=data["items_count"],
                status=data["status"],
            )
        except KeyError as e:
            raise ValidationError(f"missing field {str(e)}")
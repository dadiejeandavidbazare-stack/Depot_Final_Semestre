# contracts/event.py

from dataclasses import dataclass
from contracts.order import Order
from contracts.validators import (
    validate_required,
    validate_event_type,
    ValidationError
)


@dataclass
class OrderEvent:
    event_id: str
    event_type: str
    timestamp: str
    partition_key: str
    order: Order

    # champs optionnels
    reason: str = None
    estimated_delivery_time: str = None
    retry_count: int = None

    def __post_init__(self):
        self.validate()

    def validate(self):
        validate_required(self.event_id, "event_id")
        validate_required(self.event_type, "event_type")
        validate_required(self.timestamp, "timestamp")
        validate_required(self.partition_key, "partition_key")

        if not isinstance(self.order, Order):
            raise ValidationError("order must be an Order object")

        validate_event_type(self.event_type)

    # -------------------------
    # SERIALISATION JSON
    # -------------------------
    def to_dict(self):
        data = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "partition_key": self.partition_key,
            "order": self.order.to_dict(),
        }

        if self.reason:
            data["reason"] = self.reason
        if self.estimated_delivery_time:
            data["estimated_delivery_time"] = self.estimated_delivery_time
        if self.retry_count is not None:
            data["retry_count"] = self.retry_count

        return data

    # -------------------------
    # DESERIALISATION JSON
    # -------------------------
    @staticmethod
    def from_dict(data: dict):
        try:
            return OrderEvent(
                event_id=data["event_id"],
                event_type=data["event_type"],
                timestamp=data["timestamp"],
                partition_key=data["partition_key"],
                order=Order.from_dict(data["order"]),
                reason=data.get("reason"),
                estimated_delivery_time=data.get("estimated_delivery_time"),
                retry_count=data.get("retry_count"),
            )
        except KeyError as e:
            raise ValidationError(f"missing field {str(e)}")
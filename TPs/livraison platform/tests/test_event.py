import pytest
from contracts.event import OrderEvent
from contracts.order import Order
from contracts.validators import ValidationError


def sample_order():
    return Order(
        order_id="ORD-1",
        customer_id="C1",
        city="Fes",
        zone="Saiss",
        courier_id="CRR-1",
        amount=100,
        items_count=2,
        status="created"
    )


def test_valid_event():
    event = OrderEvent(
        event_id="EVT-1",
        event_type="order_created",
        timestamp="2026-05-12T10:00:00",
        partition_key="Fes",
        order=sample_order()
    )
    assert event.event_type == "order_created"


def test_invalid_event_type():
    with pytest.raises(ValidationError):
        OrderEvent(
            event_id="EVT-1",
            event_type="fake_event",
            timestamp="2026-05-12T10:00:00",
            partition_key="Fes",
            order=sample_order()
        )
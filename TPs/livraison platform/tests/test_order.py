import pytest
from contracts.order import Order
from contracts.validators import ValidationError


def valid_order():
    return Order(
        order_id="ORD-1",
        customer_id="C1",
        city="Fes",
        zone="Saiss",
        courier_id="CRR-1",
        amount=100.0,
        items_count=2,
        status="created"
    )


def test_valid_order():
    order = valid_order()
    assert order.city == "Fes"


def test_negative_amount():
    with pytest.raises(ValidationError):
        Order(
            order_id="ORD-1",
            customer_id="C1",
            city="Fes",
            zone="Saiss",
            courier_id="CRR-1",
            amount=-50,
            items_count=2,
            status="created"
        )


def test_unknown_city():
    with pytest.raises(ValidationError):
        Order(
            order_id="ORD-1",
            customer_id="C1",
            city="Paris",
            zone="X",
            courier_id="CRR-1",
            amount=50,
            items_count=2,
            status="created"
        )


def test_missing_field():
    with pytest.raises(ValidationError):
        Order(
            order_id="",
            customer_id="C1",
            city="Fes",
            zone="Saiss",
            courier_id="CRR-1",
            amount=50,
            items_count=2,
            status="created"
        )
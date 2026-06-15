# producers/event_producer.py

import uuid
import datetime
import time

from contracts.event import OrderEvent
from contracts.validators import ValidationError


class EventProducer:

    def __init__(self, broker):
        self.broker = broker

    # -------------------------
    # UTIL : timestamp
    # -------------------------
    def now(self):
        return datetime.datetime.now().isoformat()

    # -------------------------
    # BASE PUBLISH
    # -------------------------
    def publish(self, event: OrderEvent):
        try:
            # validation déjà dans Event
            offset = self.broker.publish(event)

            print(f"[PRODUCER] {event.event_type} → partition={event.partition_key} offset={offset}")

            return offset

        except Exception as e:
            print("[PRODUCER] broker unavailable → retry...")
            time.sleep(1)
            return self.publish(event)  # retry simple

    # -------------------------
    # EVENT FACTORY
    # -------------------------

    def create_event(self, order, event_type: str, **kwargs):

        return OrderEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=self.now(),
            partition_key=order.city,
            order=order,
            reason=kwargs.get("reason"),
            estimated_delivery_time=kwargs.get("estimated_delivery_time"),
            retry_count=kwargs.get("retry_count"),
        )

    # -------------------------
    # PIPELINE COMPLET COMMANDE
    # -------------------------

    def run_order_lifecycle(self, order):
        """
        Simule tout le cycle de vie d'une commande
        """

        events = []

        # 1. CREATED
        events.append(self.create_event(order, "order_created"))

        # 2. CONFIRMED
        order.status = "confirmed"
        events.append(self.create_event(order, "order_confirmed"))

        # 3. PREPARED
        order.status = "prepared"
        events.append(self.create_event(order, "order_prepared"))

        # 4. DISPATCHED
        order.status = "dispatched"
        events.append(self.create_event(order, "order_dispatched"))

        # 5. DELIVERED (ou failure simulation)
        if order.amount < 500:
            order.status = "delivered"
            events.append(self.create_event(
                order,
                "order_delivered",
                estimated_delivery_time=self.now()
            ))
        else:
            order.status = "failed"
            events.append(self.create_event(
                order,
                "delivery_failed",
                reason="high value risk"
            ))

        # -------------------------
        # PUBLICATION SEQUENTIELLE
        # -------------------------
        offsets = []
        for event in events:
            offsets.append(self.publish(event))
            time.sleep(0.2)  # simulation flux réel

        return offsets
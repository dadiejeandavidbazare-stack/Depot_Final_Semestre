# service/order_service.py

import uuid
import datetime
from contracts.order import Order
from contracts.event import OrderEvent
from contracts.validators import ValidationError


class OrderService:

    def __init__(self, broker):
        self.broker = broker  # injection du broker

    # -------------------------
    # GENERATION ORDER ID
    # -------------------------
    def generate_order_id(self):
        date_part = datetime.datetime.now().strftime("%Y%m%d")
        unique_part = str(uuid.uuid4())[:4].upper()
        return f"ORD-{date_part}-{unique_part}"

    # -------------------------
    # RECEPTION + TRAITEMENT
    # -------------------------
    def create_order(self, data: dict):
        try:
            print("[SERVICE] réception commande...")

            # 1. génération ID
            order_id = self.generate_order_id()

            # 2. création Order
            order = Order(
                order_id=order_id,
                customer_id=data["customer_id"],
                city=data["city"],
                zone=data["zone"],
                courier_id=data["courier_id"],
                amount=data["amount"],
                items_count=data["items_count"],
                status="created"
            )

            print("[SERVICE] validation OK")

            # 3. création event
            event = OrderEvent(
                event_id=str(uuid.uuid4()),
                event_type="order_created",
                timestamp=datetime.datetime.now().isoformat(),
                partition_key=order.city,
                order=order
            )

            # 4. publication broker
            offset = self.broker.publish(event)

            print(f"[SERVICE] event publié offset={offset}")

            # 5. réponse succès
            return {
                "status": "success",
                "order_id": order_id,
                "offset": offset
            }

        except KeyError as e:
            return {
                "status": "error",
                "message": f"missing field {str(e)}"
            }

        except ValidationError as e:
            return {
                "status": "error",
                "message": str(e)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"internal error: {str(e)}"
            }
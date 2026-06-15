import time
from collections import defaultdict
from consumers.offset_manager import OffsetManager


class ConsumerB:

    def __init__(self, broker, partitions):
        self.broker = broker
        self.partitions = partitions

        self.offset_manager = OffsetManager()

        # offsets restaurés
        self.offsets = {
            p: self.offset_manager.get("consumer_b", p)
            for p in partitions
        }

        # agrégats livreurs
        self.courier_success = defaultdict(int)
        self.courier_failed = defaultdict(int)
        self.courier_total = defaultdict(int)

        self.running = True

    # -------------------------
    # TRAITEMENT EVENT
    # -------------------------
    def process(self, event):
        order = event["order"]

        courier = order["courier_id"]
        status = order["status"]

        self.courier_total[courier] += 1

        if status == "delivered":
            self.courier_success[courier] += 1

        elif status in ["failed", "delivery_failed"]:
            self.courier_failed[courier] += 1

    # -------------------------
    # LOOP CONSUMPTION
    # -------------------------
    def consume(self):
        print("[Consumer B] started with offsets:", self.offsets)

        while self.running:

            for partition in self.partitions:

                messages = self.broker.read(partition, self.offsets[partition])

                for event in messages:
                    try:
                        self.process(event)

                        self.offsets[partition] += 1

                        # sauvegarde offset
                        self.offset_manager.set("consumer_b", partition, self.offsets[partition])

                        print(f"[B] processed {event['event_type']} offset={self.offsets[partition]}")

                    except Exception as e:
                        print("[Consumer B ERROR]", e)

            time.sleep(1)

    # -------------------------
    # REPORT FINAL
    # -------------------------
    def report(self):
        return {
            "courier_total": dict(self.courier_total),
            "success": dict(self.courier_success),
            "failed": dict(self.courier_failed),
            "offsets": self.offsets
        }
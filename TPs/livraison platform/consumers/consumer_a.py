import time
from collections import defaultdict
from consumers.offset_manager import OffsetManager


class ConsumerA:

    def __init__(self, broker, partitions):
        self.broker = broker
        self.partitions = partitions

        self.offset_manager = OffsetManager()

        # offsets restaurés
        self.offsets = {
            p: self.offset_manager.get("consumer_a", p)
            for p in partitions
        }

        # agrégats
        self.city_stats = defaultdict(int)
        self.status_stats = defaultdict(int)

        self.running = True

    # -------------------------
    # TRAITEMENT EVENT
    # -------------------------
    def process(self, event):
        order = event["order"]

        self.city_stats[order["city"]] += 1
        self.status_stats[order["status"]] += 1

    # -------------------------
    # LOOP CONSUMPTION
    # -------------------------
    def consume(self):
        print("[Consumer A] started with offsets:", self.offsets)

        while self.running:

            for partition in self.partitions:

                messages = self.broker.read(partition, self.offsets[partition])

                for event in messages:
                    try:
                        self.process(event)

                        self.offsets[partition] += 1

                        # sauvegarde offset
                        self.offset_manager.set("consumer_a", partition, self.offsets[partition])

                        print(f"[A] processed {event['event_type']} offset={self.offsets[partition]}")

                    except Exception as e:
                        print("[Consumer A ERROR]", e)

            time.sleep(1)

    # -------------------------
    # REPORT FINAL
    # -------------------------
    def report(self):
        return {
            "city_stats": dict(self.city_stats),
            "status_stats": dict(self.status_stats),
            "offsets": self.offsets
        }
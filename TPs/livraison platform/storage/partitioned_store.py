import os
import json
from datetime import datetime


class PartitionedStore:

    def __init__(self, base_path="data"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    # -------------------------
    # WRITE EVENT
    # -------------------------
    def write_event(self, event):
        order = event["order"]
        city = order["city"]

        folder = f"{self.base_path}/city={city}"
        os.makedirs(folder, exist_ok=True)

        file_path = f"{folder}/events.jsonl"

        enriched_event = {
            **event,
            "stored_at": datetime.utcnow().isoformat()
        }

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(enriched_event) + "\n")
import json
import os


class OffsetManager:

    def __init__(self, file_path="offsets/offsets.json"):
        self.file_path = file_path
        self.data = self.load()

    # -------------------------
    # LOAD
    # -------------------------
    def load(self):
        if not os.path.exists(self.file_path):
            return {}

        with open(self.file_path, "r") as f:
            return json.load(f)

    # -------------------------
    # SAVE
    # -------------------------
    def save(self):
        os.makedirs("offsets", exist_ok=True)

        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=4)

    # -------------------------
    # GET OFFSET
    # -------------------------
    def get(self, consumer, partition):
        return self.data.get(consumer, {}).get(str(partition), 0)

    # -------------------------
    # SET OFFSET
    # -------------------------
    def set(self, consumer, partition, value):
        if consumer not in self.data:
            self.data[consumer] = {}

        self.data[consumer][str(partition)] = value
        self.save()
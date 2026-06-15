# broker/mini_broker.py

class MiniBroker:

    def __init__(self, num_partitions=3):
        self.num_partitions = num_partitions

        # stockage par partitions
        self.partitions = {
            i: [] for i in range(num_partitions)
        }

    # -------------------------
    # PARTITION DETERMINISTE
    # -------------------------
    def get_partition(self, key: str):
        """
        Partition stable (important pour cohérence système)
        """
        return sum(ord(c) for c in key) % self.num_partitions

    # -------------------------
    # PUBLISH EVENT
    # -------------------------
    def publish(self, event):
        partition = self.get_partition(event.partition_key)

        self.partitions[partition].append(event.to_dict())

        offset = len(self.partitions[partition]) - 1

        print(f"[BROKER] event={event.event_type} → partition={partition} offset={offset}")

        return offset

    # -------------------------
    # READ EVENTS (CONSUMERS)
    # -------------------------
    def read(self, partition, offset):
        return self.partitions[partition][offset:]
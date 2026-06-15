# producers/partitioner.py

class Partitioner:

    def __init__(self, num_partitions: int):
        self.num_partitions = num_partitions

    # -------------------------
    # HASH DETERMINISTE
    # -------------------------
    def get_partition(self, key: str) -> int:
        """
        Retourne une partition stable pour une clé donnée
        """

        return hash(key) % self.num_partitions
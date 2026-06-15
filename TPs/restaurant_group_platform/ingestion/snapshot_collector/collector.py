# ingestion/snapshot_collector/collector.py
import time
import random
from datetime import datetime, timezone
import logging

from contracts.snapshot_contract import RestaurantSnapshot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("snapshot_collector")

TOPIC_SNAPSHOTS = "restaurant.snapshots.v1"

class MockKafkaProducer:
    def send(self, topic: str, key: str, value: dict):
        logger.info(f"[MOCK KAFKA] Métrique Cuisine sur '{topic}' | Clé: {key} | Valeur: {value}")

producer = MockKafkaProducer()

# Liste représentative de quelques restaurants à monitorer parmi les 120
RESTAURANT_IDS = ["REST-PARIS-15-A", "REST-LYON-02-B", "REST-MARSEILLE-01-A", "REST-LILLE-04-C"]

def fetch_restaurant_metrics(restaurant_id: str) -> dict:
    """Simule la récupération des métriques matérielles en direct depuis le KDS local du restaurant."""
    return {
        "snapshot_ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "restaurant_id": restaurant_id,
        "active_orders_count": random.randint(0, 25),
        "average_prep_time_seconds": random.randint(180, 720),
        "backlog_count": random.randint(0, 10)
    }

def run_collector_loop():
    logger.info("Démarrage du collecteur périodique de snapshots (Fréquence: 30s)...")
    try:
        while True:
            for resto_id in RESTAURANT_IDS:
                try:
                    # 1. Collecte de la donnée brute
                    raw_metrics = fetch_restaurant_metrics(resto_id)
                    
                    # 2. Validation par le contrat de snapshot
                    validated_snapshot = RestaurantSnapshot(**raw_metrics)
                    
                    # 3. Envoi vers le broker Kafka partitionné par restaurant_id
                    producer.send(
                        topic=TOPIC_SNAPSHOTS,
                        key=validated_snapshot.restaurant_id,
                        value=validated_snapshot.model_dump()
                    )
                except Exception as val_err:
                    logger.error(f"Données de snapshot corrompues pour {resto_id}: {str(val_err)}")
            
            # Attente de 30 secondes avant la prochaine capture d'état conforme au flux métier
            time.sleep(30)
            
    except KeyboardInterrupt:
        logger.info("Arrêt du collecteur de snapshots demandé.")

if __name__ == "__main__":
    run_collector_loop()
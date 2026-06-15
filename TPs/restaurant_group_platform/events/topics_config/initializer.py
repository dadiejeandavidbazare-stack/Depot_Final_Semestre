# events/topics_config/initializer.py
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EventTopology_Initializer")

# Définition de la topologie des flux de la plateforme
TOPICS_CONFIGURATION = {
    "kitchen.orders.v1": {
        "partitions": 12,            # Nombre élevé pour distribuer la charge des 120 restaurants
        "replication_factor": 3,    # Haute disponibilité (Tolérance à la panne de 2 brokers)
        "partition_key": "order_id",
        "retention_ms": 604800000   # 7 jours de rétention pour permettre le re-processing
    },
    "payment.events.v1": {
        "partitions": 6,
        "replication_factor": 3,
        "partition_key": "order_id", # Même clé pour faciliter les jointures Stream (Co-partitioning)
        "retention_ms": 1209600000  # 14 jours (Données financières critiques)
    },
    "restaurant.snapshots.v1": {
        "partitions": 3,
        "replication_factor": 2,    # Données métriques volatiles, criticité moindre
        "partition_key": "restaurant_id",
        "retention_ms": 86400000    # 24 heures de rétention suffisent pour la télémétrie active
    },
    "orders.rejected.dlq": {
        "partitions": 1,
        "replication_factor": 3,
        "partition_key": "order_id",
        "retention_ms": 2592000000  # 30 jours pour laisser le temps d'analyser les bugs d'ingestion
    }
}

class EventTopologyInitializer:
    def __init__(self, config: dict):
        self.config = config

    def initialize_cluster_topics(self) -> bool:
        """Simule l'appel au AdminClient de Kafka pour provisionner l'infrastructure."""
        logger.info("Connecting to Event Broker cluster AdminClient...")
        logger.info("Checking existing topics status...")
        
        created_topics = 0
        for topic_name, settings in self.config.items():
            logger.info(f"⚙️ Configuration du topic '{topic_name}':")
            logger.info(f"  └─ Partitions: {settings['partitions']} | Réplication: {settings['replication_factor']}")
            logger.info(f"  └─ Clé de hachage: {settings['partition_key']} | Rétention: {settings['retention_ms']} ms")
            
            # Ici se trouverait la logique : admin_client.create_topics([NewTopic(...)])
            logger.info(f"🚀 Topic '{topic_name}' provisionné et actif.")
            created_topics += 1
            
        logger.info(f"🎯 Topologie réseau initialisée avec succès ({created_topics} topics configurés).")
        return True

    def export_config_json(self, output_path: str):
        """Exporte la configuration sous forme de manifeste JSON pour les outils de CI/CD ou Terraform."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)
        logger.info(f"Manifeste de topologie exporté vers : {output_path}")

if __name__ == "__main__":
    initializer = EventTopologyInitializer(TOPICS_CONFIGURATION)
    initializer.initialize_cluster_topics()
    # Optionnel : décommenter pour générer le fichier de config réutilisable
    # initializer.export_config_json("./events/topics_config/topology_manifest.json")
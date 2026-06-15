# processing/batch/bronze_to_silver/pipeline.py
import os
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Batch_BronzeToSilver")

class BronzeToSilverPipeline:
    def __init__(self, base_storage_path: str):
        self.base_path = base_storage_path
        # Référentiel métier pour l'enrichissement Silver
        self.city_mapping = {
            "REST-PARIS-15-A": "Paris",
            "REST-LYON-02-B": "Lyon",
            "REST-MARSEILLE-01-A": "Marseille",
            "REST-LILLE-04-C": "Lille"
        }

    def run(self, process_date: str):
        """Exécute le pipeline de nettoyage pour une date donnée (Format YYYY-MM-DD)."""
        logger.info(f"Démarrage du nettoyage Bronze -> Silver pour la date : {process_date}")
        
        # Définition des chemins logiques de notre arborescence Medallion
        year, month, day = process_date.split("-")
        bronze_dir = os.path.join(self.base_path, "bronze", "orders", f"year={year}", f"month={month}", f"day={day}")
        silver_dir = os.path.join(self.base_path, "silver", "orders_clean")
        
        os.makedirs(silver_dir, exist_ok=True)
        
        # On simule la lecture de fichiers bruts accumulés dans la zone Bronze
        simulated_bronze_records = [
            {"order_id": "ORD-2026-00001", "restaurant_id": "REST-PARIS-15-A", "order_type": "delivery", "status": "payee", "amount": 42.50, "items_count": 2, "event_ts": f"{process_date}T12:00:00Z"},
            {"order_id": "ORD-2026-00001", "restaurant_id": "REST-PARIS-15-A", "order_type": "delivery", "status": "payee", "amount": 42.50, "items_count": 2, "event_ts": f"{process_date}T12:00:00Z"}, # Doublon technique Kafka
            {"order_id": "ORD-2026-00002", "restaurant_id": "REST-LYON-02-B", "order_type": "salle", "status": "annulee", "amount": 12.00, "items_count": 1, "event_ts": f"{process_date}T13:15:00Z"},
        ]
        
        cleaned_records = {}
        rejected_count = 0
        
        for record in simulated_bronze_records:
            # 1. Dédublonnement analytique
            uid = f"{record['order_id']}_{record['status']}"
            if uid in cleaned_records:
                continue # Doublon ignoré
                
            # 2. Enrichissement avec les données de référence
            r_id = record["restaurant_id"]
            if r_id in self.city_mapping:
                record["city"] = self.city_mapping[r_id]
                cleaned_records[uid] = record
            else:
                rejected_count += 1
                logger.warning(f"[SILVER REJECT] Restaurant ID inconnu : {r_id}")

        # 3. Écriture finale vers la couche Silver standardisée
        output_file = os.path.join(silver_dir, f"data_{process_date}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(list(cleaned_records.values()), f, indent=4)
            
        logger.info(f"Pipeline Silver terminé. Écrits: {len(cleaned_records)} | Rejetés: {rejected_count}")
        return len(cleaned_records), rejected_count
# processing/batch/silver_to_gold/pipeline.py
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Batch_SilverToGold")

class SilverToGoldPipeline:
    def __init__(self, base_storage_path: str):
        self.base_path = base_storage_path

    def run(self, process_date: str):
        """Agrège les données Silver vers les rapports Gold d'aide à la décision."""
        logger.info(f"Démarrage de l'agrégation Silver -> Gold pour la date : {process_date}")
        
        silver_file = os.path.join(self.base_path, "silver", "orders_clean", f"data_{process_date}.json")
        gold_dir = os.path.join(self.base_path, "gold", "daily_reports")
        
        os.makedirs(gold_dir, exist_ok=True)
        
        if not os.path.exists(silver_file):
            logger.error(f"Fichier Silver introuvable pour le traitement : {silver_file}")
            return False

        with open(silver_file, "r", encoding="utf-8") as f:
            silver_data = json.load(f)

        # Calcul des métriques Gold (Revenu journalier par restaurant et par type)
        gold_aggregations = {}
        
        for row in silver_data:
            # Exclure les commandes annulées des rapports de performance de vente finaux
            if row["status"] == "annulee":
                continue
                
            repo_key = row["restaurant_id"]
            if repo_key not in gold_aggregations:
                gold_aggregations[repo_key] = {
                    "date": process_date,
                    "restaurant_id": repo_key,
                    "city": row["city"],
                    "daily_revenue": 0.0,
                    "total_orders": 0
                }
            
            gold_aggregations[repo_key]["daily_revenue"] += row["amount"]
            gold_aggregations[repo_key]["total_orders"] += 1

        # Application stricte de l'idempotence : Écrase le fichier existant de la journée
        output_gold_file = os.path.join(gold_dir, f"report_{process_date}.json")
        with open(output_gold_file, "w", encoding="utf-8") as f_out:
            json.dump(list(gold_aggregations.values()), f_out, indent=4)
            
        logger.info(f"Rapport journalier Gold généré avec succès avec surécriture : {output_gold_file}")
        return True
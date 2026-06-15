# orchestration/nightly_dag.py
import time
import logging
from datetime import datetime, timedelta

# Importation de nos composants du moteur Batch
from processing.batch.bronze_to_silver.pipeline import BronzeToSilverPipeline
from processing.batch.silver_to_gold.pipeline import SilverToGoldPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nightly_Orchestrator")

class NightlyDAG:
    def __init__(self, base_storage_path: str):
        self.base_path = base_storage_path
        self.bronze_to_silver = BronzeToSilverPipeline(base_storage_path)
        self.silver_to_gold = SilverToGoldPipeline(base_storage_path)

    def execute_task_with_retry(self, task_name: str, task_callable, max_retries=3) -> bool:
        """Exécute une tâche de traitement de données avec mécanisme de reprise."""
        for attempt in range(1, max_retries + 1):
            logger.info(f"Éxécution de la tâche '{task_name}' - Tentative {attempt}/{max_retries}...")
            start_time = time.time()
            try:
                result = task_callable()
                if result:
                    duration = time.time() - start_time
                    logger.info(f"✅ Tâche '{task_name}' réussie en {duration:.2f}s")
                    return True
                raise RuntimeError("La tâche a retourné un statut d'échec interne.")
            except Exception as e:
                logger.error(f"❌ Échec de la tâche '{task_name}' à la tentative {attempt}: {str(e)}")
                if attempt < max_retries:
                    time.sleep(2)  # Attente exponentielle simplifiée avant retry
                else:
                    logger.critical(f"💥 Tâche '{task_name}' définitivement échouée après {max_retries} essais.")
                    return False

    def run_pipeline_for_date(self, execution_date: str):
        """Orchestre la séquence complète du workflow de données de la nuit (à 02h00)."""
        logger.info(f"============================================================")
        logger.info(f"🚀 LANCEMENT DU DAG NOCTURNE POUR LA DATE : {execution_date}")
        logger.info(f"============================================================")
        
        # Étape 1 : Nettoyage & Standardisation (Bronze -> Silver)
        def step_silver():
            # Conversion de la fonction pour qu'elle renvoie un booléen de succès
            records_count, _ = self.bronze_to_silver.run(execution_date)
            return records_count >= 0

        silver_success = self.execute_task_with_retry("BRONZE_TO_SILVER_CLEANSE", step_silver)
        
        if not silver_success:
            logger.critical("🛑 Arrêt du DAG : L'étape Silver a échoué. Bloquage de la suite décisionnelle.")
            return False

        # Étape 2 : Agrégation décisionnelle et KPIs métier (Silver -> Gold)
        def step_gold():
            return self.silver_to_gold.run(execution_date)

        gold_success = self.execute_task_with_retry("SILVER_TO_GOLD_AGREGATION", step_gold)

        if gold_success:
            logger.info(f"🎉 WORKFLOW COMPLET TERMINÉ AVEC SUCCÈS POUR LA DATE : {execution_date}")
            return True
        else:
            logger.error("⚠️ WORKFLOW PARTIELLEMENT COMPROMIS : Étape Gold en échec.")
            return False

if __name__ == "__main__":
    # Simulation d'une exécution de production pour la veille
    orchestrator = NightlyDAG(base_storage_path="./data_lake")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    orchestrator.run_pipeline_for_date(yesterday)
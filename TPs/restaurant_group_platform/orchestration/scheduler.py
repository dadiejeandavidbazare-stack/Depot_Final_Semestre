# orchestration/scheduler.py
import time
import logging
from datetime import datetime
from orchestration.nightly_dag import NightlyDAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Platform_Scheduler")

class PlatformScheduler:
    def __init__(self, base_storage_path: str, target_hour: int = 2, target_minute: int = 0):
        self.dag = NightlyDAG(base_storage_path)
        self.target_hour = target_hour
        self.target_minute = target_minute
        self.is_running = False

    def start(self):
        """Démarre la boucle de surveillance horaire."""
        self.is_running = True
        logger.info(f"⏰ Ordonnanceur démarré. Planification du DAG nocturne fixée à {self.target_hour:02d}:{self.target_minute:02d} chaque jour.")
        
        try:
            while self.is_running:
                now = datetime.now()
                
                # Vérification : Est-ce qu'il est 2h00 du matin ?
                if now.hour == self.target_hour and now.minute == self.target_minute:
                    # On calcule la date de la veille à traiter (les données de la journée écoulée)
                    # Pour notre simulation, on prend la date du jour au format YYYY-MM-DD
                    date_to_process = now.strftime("%Y-%m-%d")
                    
                    logger.info(f"🔔 Heure cible atteinte ! Déclenchement automatique du pipeline nocturne.")
                    self.dag.run_pipeline_for_date(date_to_process)
                    
                    # On dort 60 secondes pour éviter de déclencher le DAG plusieurs fois dans la même minute
                    time.sleep(60)
                
                # Pause de 10 secondes entre chaque vérification d'horloge
                time.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            self.is_running = False

if __name__ == "__main__":
    # Initialisation du scheduler pointant vers notre dossier de stockage global
    scheduler = PlatformScheduler(base_storage_path="./storage", target_hour=2, target_minute=0)
    
    # Pour tester immédiatement sans attendre 2h du matin, on peut forcer une exécution manuelle :
    # logger.info("🧪 Mode Test : Déclenchement d'un run manuel immédiat...")
    # scheduler.dag.run_pipeline_for_date("2026-05-23")
    
    scheduler.start()
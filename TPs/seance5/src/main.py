import threading
import logging
import os
import time
import json
import queue
import sys

from .messages import EventMessage
from .producers import burst_producer
from .workers import worker_loop
from .metrics import PipelineMetrics, monitor_loop
from .storage import CSVStorage
from .pipeline import Pipeline

def main():
    # Création des répertoires de sortie
    os.makedirs("logs", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # 🛡️ FIX : Configuration robuste du Logging pour Windows (Support UTF-8/Émojis)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(threadName)s] %(levelname)s %(message)s"))
    
    file_handler = logging.FileHandler("logs/pipeline.log", mode="w", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(threadName)s] %(levelname)s %(message)s"))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )

    # Initialisation des composants centraux
    pipe = Pipeline(maxsize=50)
    metrics = PipelineMetrics()
    storage = CSVStorage("outputs/valid_readings.csv")

    # Lancer les workers initiaux (2)
    for i in range(2):
        t = threading.Thread(
            target=worker_loop,
            args=(pipe.main_queue, pipe.dead_letter_queue, storage, metrics, pipe.stop_event, f"Worker-{i+1}"),
            name=f"Worker-{i+1}", daemon=True
        )
        t.start()
        pipe.threads.append(t)

    # Lancer le moniteur système (gestion de l'observabilité et du scale-out)
    t_mon = threading.Thread(
        target=monitor_loop,
        args=(pipe, metrics, pipe.stop_event, storage, 2),
        name="Monitor", daemon=True
    )
    t_mon.start()
    pipe.threads.append(t_mon)

    # Lancer les producteurs de données IoT (3)
    prod_threads = []
    for i in range(3):
        t = threading.Thread(
            target=burst_producer,
            args=(pipe.main_queue, f"Prod-{i+1}", 5, 30, 0.5),
            name=f"Prod-{i+1}"
        )
        t.start()
        prod_threads.append(t)

    # Attendre la fin de la génération des messages par les producteurs
    for t in prod_threads:
        t.join()
    logging.info("Tous les producteurs ont terminé.")

    # Bloquer jusqu'à ce que tous les éléments de la file d'attente soient récupérés et traités
    pipe.main_queue.join()
    logging.info("Queue vidée.")
    
    # Arrêt propre de l'ensemble de la topologie
    pipe.shutdown(timeout=5)

    # Récupération et affichage du rapport d'observabilité final
    snap = metrics.snapshot()
    logging.info(f"=== RÉSULTAT FINAL ===")
    logging.info(f"Messages traités avec succès : {snap['success']}")
    logging.info(f"Messages échoués (DLQ)       : {snap['failures']}")
    logging.info(f"Retries effectués             : {snap['retries']}")
    logging.info(f"Débit moyen                   : {snap['rate_per_sec']} msg/s")
    logging.info(f"Latence moyenne               : {snap['avg_latency_ms']} ms")

    # Vidage de la Dead-Letter Queue et persistance au format JSON
    dead = []
    while not pipe.dead_letter_queue.empty():
        try:
            msg = pipe.dead_letter_queue.get_nowait()
            dead.append(msg.to_dict())
        except queue.Empty:
            break
            
    with open("outputs/dead_letters.json", "w", encoding="utf-8") as f:
        json.dump(dead, f, indent=2, default=str)
    logging.info(f"Dead-letters sauvegardés : {len(dead)}")

    # Affichage des métriques métiers calculées par l'agrégateur thread-safe
    agg = storage.aggregate()
    logging.info(f"Agrégation par capteur : {json.dumps(agg, indent=2)}")

    # Validation fonctionnelle via des assertions de santé
    assert snap["success"] > 0, "Aucun message traité !"
    logging.info("✅ Toutes les assertions passent.")

if __name__ == "__main__":
    main()
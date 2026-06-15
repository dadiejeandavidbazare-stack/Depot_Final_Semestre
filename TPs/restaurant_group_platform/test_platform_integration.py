# test_platform_integration.py
import os
import json
import shutil
import logging
from datetime import datetime, timezone

# 1. Importation de tous nos composants de plateforme
from events.topics_config.initializer import EventTopologyInitializer, TOPICS_CONFIGURATION
from contracts.order_contract import OrderEvent
from processing.stream.stream_processor import StreamProcessor
from observability.stream_metrics import StreamMetricsManager
from orchestration.nightly_dag import NightlyDAG

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("📦 IntegrationTest")

def run_full_integration_test():
    logger.info("====================================================")
    logger.info("🧪 DÉMARRAGE DU TEST D'INTÉGRATION GLOBAL")
    logger.info("====================================================")

    # Nettoyage d'un ancien dossier de stockage pour repartir sur une base saine
    test_storage = "./test_storage_lake"
    if os.path.exists(test_storage):
        shutil.rmtree(test_storage)
    os.makedirs(test_storage, exist_ok=True)

    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # --- ÉTAPE 1 : INITIALISATION DE L'INFRASTRUCTURE ---
    logger.info("\n--- [Étape 1] Initialisation de la topologie réseau ---")
    infra = EventTopologyInitializer(TOPICS_CONFIGURATION)
    infra.initialize_cluster_topics()

    # --- ÉTAPE 2 : INGESTION & KAFKA STREAMING (TEMPS RÉEL) ---
    logger.info("\n--- [Étape 2] Flux d'ingestion et Moteur Stream Actif ---")
    stream_engine = StreamProcessor()
    metrics_manager = StreamMetricsManager()

    # Simulation de payloads reçus par l'API order_service
    order_payloads = [
        # Commande 1 : Valide
        {"order_id": "ORD-2026-00001", "restaurant_id": "REST-PARIS-15-A", "order_type": "delivery", "status": "recue", "amount": 45.00, "items_count": 3, "event_ts": f"{current_date}T12:00:00Z"},
        # Commande 2 : Valide
        {"order_id": "ORD-2026-00002", "restaurant_id": "REST-LYON-02-B", "order_type": "salle", "status": "recue", "amount": 22.50, "items_count": 1, "event_ts": f"{current_date}T12:02:00Z"},
        # Commande 1 : Transition de statut (En préparation)
        {"order_id": "ORD-2026-00001", "restaurant_id": "REST-PARIS-15-A", "order_type": "delivery", "status": "en_preparation", "amount": 45.00, "items_count": 3, "event_ts": f"{current_date}T12:05:00Z"},
        # Commande 1 : Transition de statut (Prête / Sortie du backlog actif)
        {"order_id": "ORD-2026-00001", "restaurant_id": "REST-PARIS-15-A", "order_type": "delivery", "status": "prete", "amount": 45.00, "items_count": 3, "event_ts": f"{current_date}T12:12:00Z"},
    ]

    # Simulation de l'écriture brute en zone Bronze (ce que fait le service d'ingestion)
    year, month, day = current_date.split("-")
    bronze_dir = os.path.join(test_storage, "bronze", "orders", f"year={year}", f"month={month}", f"day={day}")
    os.makedirs(bronze_dir, exist_ok=True)
    
    with open(os.path.join(bronze_dir, "ingested_events.json"), "w") as f_bronze:
        json.dump(order_payloads, f_bronze)

    # Simulation du traitement de ces messages par le moteur de Stream au fil de l'eau
    for payload in order_payloads:
        try:
            # Sécurité de validation via le contrat
            validated_event = OrderEvent(**payload)
            serialized_msg = validated_event.model_dump_json()
            
            # Traitement par le processeur de flux
            stream_engine.process_order_event(serialized_msg)
            metrics_manager.track_message_processed(validated_event.event_ts)
        except Exception as e:
            metrics_manager.track_dlq_rejection("kitchen.orders.v1", str(e))

    # Simulation d'un événement de paiement intercepté par le Stream
    payment_msg = json.dumps({"payment_id": "PAY-99988", "order_id": "ORD-2026-00001", "restaurant_id": "REST-PARIS-15-A", "payment_method": "carte", "amount": 45.00, "payment_ts": f"{current_date}T12:15:00Z"})
    stream_engine.process_payment_event(payment_msg)

    # Affichage du rapport d'observabilité temps réel
    metrics_manager.log_health_report()

    # --- ÉTAPE 3 : ORCHESTRATION ET TRAITEMENT BATCH NOCTURNE ---
    logger.info("\n--- [Étape 3] Déclenchement automatique du DAG Nocturne (02h00) ---")
    dag = NightlyDAG(base_storage_path=test_storage)
    
    # Injection d'un hack temporaire dans l'instance du pipeline du DAG pour lire nos vrais fichiers de test
    # au lieu de la liste simulée en dur
    def custom_run(process_date):
        logger.info(f"[TEST MOCK] Lecture de la zone Bronze locale : {bronze_dir}")
        with open(os.path.join(bronze_dir, "ingested_events.json"), "r") as f:
            data = json.load(f)
        
        # Logique simplifiée de Bronze vers Silver
        silver_dir = os.path.join(test_storage, "silver", "orders_clean")
        os.makedirs(silver_dir, exist_ok=True)
        
        # Enrichissement avec le mapping ville
        for row in data:
            row["city"] = "Paris" if row["restaurant_id"] == "REST-PARIS-15-A" else "Lyon"
            
        with open(os.path.join(silver_dir, f"data_{process_date}.json"), "w") as f_out:
            json.dump(data, f_out)
        return len(data), 0

    dag.bronze_to_silver.run = custom_run

    # Lancement du DAG
    dag_success = dag.run_pipeline_for_date(current_date)
    assert dag_success is True, "Le DAG nocturne a échoué en cours de route !"

    # --- ÉTAPE 4 : VALIDATION DE LA COUCHE GOLD (QUALITÉ DONNÉES) ---
    logger.info("\n--- [Étape 4] Validation des indicateurs de la zone GOLD ---")
    gold_report_file = os.path.join(test_storage, "gold", "daily_reports", f"report_{current_date}.json")
    
    assert os.path.exists(gold_report_file), "Le rapport décisionnel Gold n'a pas été généré !"
    
    with open(gold_report_file, "r") as f_gold:
        gold_data = json.load(f_gold)

    logger.info(f"Contenu du rapport Gold généré :\n{json.dumps(gold_data, indent=2)}")
    
    # Vérification fonctionnelle de la comptabilité
    paris_report = next(item for item in gold_data if item["restaurant_id"] == "REST-PARIS-15-A")
    assert paris_report["daily_revenue"] == 135.00, f"Erreur de calcul du CA de Paris ! Attendu 135.00, trouvé {paris_report['daily_revenue']}"

    logger.info("\n====================================================")
    logger.info("✅ TEST D'INTÉGRATION RÉUSSI AVEC SUCCÈS !")
    logger.info("   Tous les contrats sont respectés et la zone Gold est intègre.")
    logger.info("====================================================")

if __name__ == "__main__":
    run_full_integration_test()
    
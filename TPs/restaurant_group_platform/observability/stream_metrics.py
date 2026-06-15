# observability/stream_metrics.py
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ObservabilityEngine")

class StreamMetricsManager:
    def __init__(self):
        # Compteurs internes pour le monitoring
        self.processed_messages_count = 0
        self.dead_letter_queue_count = 0
        self.total_processing_lag_seconds = 0.0

    def track_message_processed(self, event_ts_str: str):
        """Calcule le décalage (Lag) temporel réel d'ingestion et incrémente l'activité."""
        self.processed_messages_count += 1
        try:
            # Parsing sécurisé de la date de l'événement
            event_time = datetime.fromisoformat(event_ts_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            
            # Calcul de la latence de traitement au fil de l'eau
            lag_seconds = (now - event_time).total_seconds()
            self.total_processing_lag_seconds += lag_seconds
            
            # Alerte si le lag système dépasse un seuil critique de 5 minutes
            if lag_seconds > 300:
                logger.warning(f"⚠️ [SLA ALERT] Latence élevée détectée ! Lag actuel : {lag_seconds:.2f} secondes.")
        except Exception as e:
            logger.error(f"Impossible de calculer le lag d'observabilité : {str(e)}")

    def track_dlq_rejection(self, topic: str, reason: str):
        """Enregistre un échec d'ingestion et déclenche une alerte immédiate."""
        self.dead_letter_queue_count += 1
        logger.error(f"🚨 [CRITICAL METRIC] Message routé vers la DLQ sur le topic '{topic}'. Raison : {reason}")
        
        # Seuil d'alerte critique de production
        if self.dead_letter_queue_count >= 10:
            logger.critical("🔥 [PAGERDUTY ALERT] Taux d'anomalies trop élevé en zone Bronze ! Intervention humaine requise.")

    def get_average_lag(self) -> float:
        """Retourne la latence moyenne globale du pipeline."""
        if self.processed_messages_count == 0:
            return 0.0
        return round(self.total_processing_lag_seconds / self.processed_messages_count, 2)

    def log_health_report(self):
        """Génère le snapshot d'état pour les dashboards d'exploitation (ex: Grafana)."""
        logger.info("=== 📊 RAPPORT DE SANTÉ DU PIPELINE EN TEMPS RÉEL ===")
        logger.info(f"| Messages traités avec succès : {self.processed_messages_count}")
        logger.info(f"| Messages en erreur (DLQ)    : {self.dead_letter_queue_count}")
        logger.info(f"| Latence (Lag) moyenne        : {self.get_average_lag()} secondes")
        logger.info("====================================================")
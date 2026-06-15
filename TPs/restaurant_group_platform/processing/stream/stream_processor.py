# processing/stream/stream_processor.py
import json
import logging
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StreamProcessor")

class StreamProcessor:
    def __init__(self):
        # State Stores locaux (Simule RocksDB / Spark State Store)
        self.active_orders_store = {}  # {order_id: {status, restaurant_id, amount}}
        self.city_revenue_store = {}   # {city: total_revenue}
        
        # Référentiel statique pour l'enrichissement en temps réel
        self.restaurant_registry = {
            "REST-PARIS-15-A": "Paris",
            "REST-LYON-02-B": "Lyon",
            "REST-MARSEILLE-01-A": "Marseille",
            "REST-LILLE-04-C": "Lille"
        }
        
        # Configuration de la gestion du temps
        self.watermark_duration = timedelta(minutes=15)
        self.current_max_event_time = datetime.min.replace(tzinfo=timezone.utc)

    def update_watermark(self, event_time: datetime):
        """Met à jour dynamiquement le temps maximum observé du système."""
        if event_time > self.current_max_event_time:
            self.current_max_event_time = event_time

    def is_event_too_late(self, event_time: datetime) -> bool:
        """Applique la politique de Watermark définie dans l'architecture."""
        watermark = self.current_max_event_time - self.watermark_duration
        return event_time < watermark

    def process_order_event(self, raw_message: str):
        """Traite au fil de l'eau le cycle de vie d'une commande."""
        event = json.loads(raw_message)
        order_id = event["order_id"]
        status = event["status"]
        restaurant_id = event["restaurant_id"]
        event_ts = datetime.fromisoformat(event["event_ts"].replace("Z", "+00:00"))

        # 1. Gestion du Watermarking
        self.update_watermark(event_ts)
        if self.is_event_too_late(event_ts):
            logger.warning(f"[REJET LATE DATA] Événement {order_id} arrivé trop tard ({event['event_ts']}). Ignoré du Stream.")
            return

        # 2. Mise à jour de l'état des commandes en cours (Indicateur 1)
        if status in ["recue", "en_preparation"]:
            self.active_orders_store[order_id] = {
                "status": status,
                "restaurant_id": restaurant_id,
                "amount": event["amount"]
            }
            logger.info(f"[STREAM kpi] Commande {order_id} ACTIVE pour {restaurant_id}")
            
        elif status in ["prete", "livree", "servie", "annulee"]:
            if order_id in self.active_orders_store:
                del self.active_orders_store[order_id]
                logger.info(f"[STREAM kpi] Commande {order_id} SORTIE du backlog actif (Statut: {status})")

    def process_payment_event(self, raw_message: str):
        """Traite les flux de paiement et incrémente le chiffre d'affaires par ville."""
        event = json.loads(raw_message)
        restaurant_id = event.get("restaurant_id", "REST-PARIS-15-A") # Fallback pour démo
        amount = event["amount"]
        payment_ts = datetime.fromisoformat(event["payment_ts"].replace("Z", "+00:00"))

        if self.is_event_too_late(payment_ts):
            logger.warning(f"[REJET LATE DATA] Paiement rejeté par le Watermark.")
            return

        # Enrichissement Stream depuis le référentiel
        city = self.restaurant_registry.get(restaurant_id, "Inconnu")
        
        # Mise à jour du State Store financier (Indicateur 2)
        self.city_revenue_store[city] = self.city_revenue_store.get(city, 0.0) + amount
        logger.info(f"[STREAM KPI] CA Temps Réel - Ville: {city} | Total: {self.city_revenue_store[city]:.2f} €")

    def get_active_orders_count_by_restaurant(self, restaurant_id: str) -> int:
        """Retourne le nombre actuel de commandes en cours."""
        return sum(1 for o in self.active_orders_store.values() if o["restaurant_id"] == restaurant_id)
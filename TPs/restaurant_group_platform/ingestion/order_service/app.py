# ingestion/order_service/app.py
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import json
import logging

# Importation du contrat défini précédemment
from contracts.order_contract import OrderEvent

app = FastAPI(title="RestaurantGroup SA - Order Ingestion Service")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("order_service")

# Simulation d'un Kafka Producer pour l'architecture événementielle
class MockKafkaProducer:
    def send(self, topic: str, key: str, value: dict):
        logger.info(f"[MOCK KAFKA] Message envoyé au Topic '{topic}' | Clé: {key} | Valeur: {value}")

producer = MockKafkaProducer()

TOPIC_SUCCESS = "kitchen.orders.v1"
TOPIC_DLQ = "orders.rejected.dlq"

@app.post("/v1/orders", status_code=status.HTTP_202_ACCEPTED)
async def ingest_order(payload: dict):
    server_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    try:
        # Étape 1: Validation stricte via le contrat Pydantic
        order_event = OrderEvent(**payload)
        
        # Étape 2: Enrichissement avec le server time
        enriched_data = order_event.model_dump()
        enriched_data["server_ts"] = server_time
        
        # Étape 3: Publication asynchrone partitionnée par order_id
        producer.send(
            topic=TOPIC_SUCCESS,
            key=order_event.order_id,
            value=enriched_data
        )
        
        return {
            "status": "accepted",
            "order_id": order_event.order_id,
            "server_ts": server_time
        }

    except Exception as e:
        # Étape 4: Routage vers la Dead Letter Queue (DLQ) si invalide
        error_msg = str(e)
        logger.error(f"[INVALID_BRONZE] Échec de validation de la commande. Routage vers DLQ. Erreur: {error_msg}")
        
        dlq_payload = {
            "raw_payload": payload,
            "error_reason": error_msg,
            "failed_at": server_time,
            "tag": "INVALID_BRONZE"
        }
        
        producer.send(
            topic=TOPIC_DLQ,
            key=payload.get("order_id", "UNKNOWN_ID"),
            value=dlq_payload
        )
        
        # Renvoyer une erreur 400 claire au client synchrone
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "rejected",
                "reason": error_msg,
                "error_code": "VAL_ERR_ORDER"
            }
        )
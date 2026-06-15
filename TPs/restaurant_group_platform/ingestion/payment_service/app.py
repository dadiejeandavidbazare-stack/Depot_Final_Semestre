# ingestion/payment_service/app.py
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import logging

from contracts.payment_contract import PaymentEvent

app = FastAPI(title="RestaurantGroup SA - Payment Event Service")
logger = logging.getLogger("payment_service")

class MockKafkaProducer:
    def send(self, topic: str, key: str, value: dict):
        logger.info(f"[MOCK KAFKA] Encaissé sur '{topic}' | Clé: {key} | Valeur: {value}")

producer = MockKafkaProducer()
TOPIC_PAYMENTS = "payment.events.v1"

@app.post("/v1/payments/webhook", status_code=status.HTTP_200_OK)
async def receive_payment_webhook(payload: dict):
    try:
        # Validation du contrat de paiement
        payment_event = PaymentEvent(**payload)
        
        # Publication asynchrone (clé de partitionnement = order_id pour faciliter les futures jointures stream)
        producer.send(
            topic=TOPIC_PAYMENTS,
            key=payment_event.order_id,
            value=payment_event.model_dump()
        )
        
        return {"status": "payment_processed", "payment_id": payment_event.payment_id}
        
    except Exception as e:
        logger.error(f"Erreur traitement webhook paiement: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"status": "error", "message": str(e)}
        )
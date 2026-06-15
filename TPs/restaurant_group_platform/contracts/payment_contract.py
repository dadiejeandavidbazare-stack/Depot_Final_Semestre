# contracts/payment_contract.py
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re

class PaymentMethod(str, Enum):
    ESPECES = "especes"
    CARTE = "carte"
    APPLICATION = "application"

class PaymentEvent(BaseModel):
    payment_id: str = Field(..., description="UUID unique de la transaction financière")
    order_id: str = Field(..., description="ID de la commande associée à ce paiement")
    payment_method: PaymentMethod
    amount: float = Field(..., description="Montant exact encaissé")
    payment_ts: str = Field(..., description="Timestamp de validation du paiement au format ISO 8601 UTC")

    # Validation du lien avec l'ID commande pour cohérence avec le order_contract
    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, v: str) -> str:
        pattern = r"^ORD-\d{4}-\d{5,}$"
        if not re.match(pattern, v):
            raise ValueError(f"Le format de l'order_id lié au paiement est invalide ({pattern})")
        return v

    # Règle métier : Montant strictement positif pour éviter les fraudes à l'ingestion
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0.0:
            raise ValueError("Le montant du paiement doit être strictement supérieur à 0.00")
        return round(v, 2)

    # Validation du format de date ISO 8601 UTC
    @field_validator("payment_ts")
    @classmethod
    def validate_payment_ts(cls, v: str) -> str:
        try:
            if not v.endswith('Z') and '+' not in v and '-' not in v:
                raise ValueError("Le timestamp du paiement doit spécifier un fuseau horaire (ex: Z)")
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except Exception as e:
            raise ValueError(f"Format de date non conforme ISO 8601 pour payment_ts : {str(e)}")
        return v
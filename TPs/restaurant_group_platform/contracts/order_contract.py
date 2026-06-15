# contracts/order_contract.py
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator
import re

class OrderType(str, Enum):
    SALLE = "salle"
    EMPORTER = "emporter"
    DELIVERY = "delivery"

class OrderStatus(str, Enum):
    RECUE = "recue"
    EN_PREPARATION = "en_preparation"
    PRETE = "prete"
    LIVREE = "livree"
    SERVIE = "servie"
    PAYEE = "payee"
    ANNULEE = "annulee"

class OrderEvent(BaseModel):
    order_id: str = Field(..., description="Identifiant unique de la commande")
    restaurant_id: str = Field(..., description="ID unique du restaurant émetteur")
    order_type: OrderType
    status: OrderStatus
    amount: float = Field(..., description="Montant total de la commande")
    items_count: int = Field(..., description="Nombre total d'articles dans la commande")
    event_ts: str = Field(..., description="Timestamp de l'événement au format ISO 8601 UTC")

    # Validation du format de l'ID commande (ex: ORD-2025-00142)
    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, v: str) -> str:
        pattern = r"^ORD-\d{4}-\d{5,}$"
        if not re.match(pattern, v):
            raise ValueError(f"L'order_id doit respecter le pattern {pattern}")
        return v

    # Règle métier : Montant strictement positif
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0.0:
            raise ValueError("Le montant ('amount') doit être strictement supérieur à 0.00")
        return round(v, 2)

    # Règle métier : Au moins 1 article
    @field_validator("items_count")
    @classmethod
    def validate_items_count(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Le nombre d'articles ('items_count') doit être supérieur ou égal à 1")
        return v

    # Validation rigoureuse de la structure ISO 8601 UTC pour event_ts
    @field_validator("event_ts")
    @classmethod
    def validate_event_ts(cls, v: str) -> str:
        try:
            # Vérifie la présence du marqueur Z (UTC) ou d'un décalage
            if not v.endswith('Z') and '+' not in v and '-' not in v:
                raise ValueError("Le timestamp doit spécifier un fuseau horaire (de préférence 'Z' pour UTC)")
            
            # Essaye de parser la chaîne pour s'assurer de sa validité calendaire
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except Exception as e:
            raise ValueError(f"Format de date invalide ou non conforme ISO 8601 : {str(e)}")
        return v
# contracts/snapshot_contract.py
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class RestaurantSnapshot(BaseModel):
    snapshot_ts: str = Field(..., description="Timestamp exact de la capture d'état (ISO 8601 UTC)")
    restaurant_id: str = Field(..., description="Identifiant unique du restaurant concerné")
    active_orders_count: int = Field(..., description="Nombre de commandes actuellement en cours de préparation")
    average_prep_time_seconds: int = Field(..., description="Moyenne glissante locale du temps de préparation en secondes")
    backlog_count: int = Field(..., description="Nombre de commandes en attente d'affectation en cuisine")

    # Validation des compteurs opérationnels (strictement positifs ou nuls)
    @field_validator("active_orders_count", "average_prep_time_seconds", "backlog_count")
    @classmethod
    def validate_non_negative_counters(cls, v: int, info) -> int:
        if v < 0:
            raise ValueError(f"La métrique '{info.field_name}' ne peut pas être négative")
        return v

    # Validation du format de date ISO 8601 UTC
    @field_validator("snapshot_ts")
    @classmethod
    def validate_snapshot_ts(cls, v: str) -> str:
        try:
            if not v.endswith('Z') and '+' not in v and '-' not in v:
                raise ValueError("Le snapshot_ts doit inclure la zone de fuseau horaire (ex: Z)")
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except Exception as e:
            raise ValueError(f"Format de date non conforme ISO 8601 pour snapshot_ts : {str(e)}")
        return v
# validators.py
"""validators.py — Validateurs polymorphiques pour les données IoT."""
from abc import ABC, abstractmethod
from typing import List
from models import ValidationError


class Validator(ABC):
    @abstractmethod
    def validate(self, data: dict) -> List[ValidationError]:
        """Exécute la règle de validation et retourne une liste d'erreurs."""
        pass


class RequiredFieldsValidator(Validator):
    def __init__(self, fields: List[str]):
        self.fields = fields

    def validate(self, data: dict) -> List[ValidationError]:
        errors = []
        for field_name in self.fields:
            value = data.get(field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(
                    ValidationError(
                        field=field_name,
                        code="MISSING_FIELD",
                        message=f"Le champ '{field_name}' est requis et ne doit pas être vide.",
                    )
                )
        return errors


class RangeValidator(Validator):
    def __init__(self, field_name: str, min_val: float, max_val: float):
        self.field_name = field_name
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, data: dict) -> List[ValidationError]:
        errors = []
        value = data.get(self.field_name)
        
        if value is None:
            return errors
            
        try:
            numeric_value = float(value)
            if not (self.min_val <= numeric_value <= self.max_val):
                errors.append(
                    ValidationError(
                        field=self.field_name,
                        code="OUT_OF_RANGE",
                        message=f"La valeur {numeric_value} doit être comprise entre {self.min_val} et {self.max_val}.",
                    )
                )
        except (ValueError, TypeError):
            errors.append(
                ValidationError(
                    field=self.field_name,
                    code="INVALID_TYPE",
                    message=f"Le champ '{self.field_name}' doit être une valeur numérique.",
                )
            )
        return errors


class ConsistencyValidator(Validator):
    def validate(self, data: dict) -> List[ValidationError]:
        errors = []
        pump_status = data.get("pump_status")
        irrigation_l_min = data.get("irrigation_l_min")

        if pump_status == "on":
            try:
                flow = float(irrigation_l_min) if irrigation_l_min is not None else 0.0
                if flow <= 0:
                    errors.append(
                        ValidationError(
                            field="irrigation_l_min",
                            code="INCONSISTENT_STATE",
                            message="Le débit d'irrigation doit être supérieur à 0 quand la pompe est activée ('on').",
                        )
                    )
            except (ValueError, TypeError):
                errors.append(
                    ValidationError(
                        field="irrigation_l_min",
                        code="INVALID_TYPE",
                        message="Le débit d'irrigation doit être numérique.",
                    )
                )
        return errors


def run_validators(data: dict, validators: List[Validator]) -> List[ValidationError]:
    """Exécute l'ensemble des validateurs de manière cumulative."""
    all_errors = []
    for validator in validators:
        all_errors.extend(validator.validate(data))
    return all_errors
from typing import List, Dict, Any
from domain.validators.base_validator import BaseValidator

REQUIRED_FIELDS_CIARP = [
    "código_unidad_académica",
    "tipo_documento",
    "identivicación",
    "año",
    "título",
    "pais_producto",
]

class RequiredFieldsCiarpValidator:
    @staticmethod
    def validate(row: dict, index: int) -> List[Dict[str, Any]]:
        errors = []
        for field in REQUIRED_FIELDS_CIARP:
            value = row.get(field)
            if BaseValidator.is_empty(value):
                errors.append({
                    "fila": index,
                    "columna": field,
                    "detalle": "Campo obligatorio vacío",
                    "valor": "Vacío",
                })
        return errors
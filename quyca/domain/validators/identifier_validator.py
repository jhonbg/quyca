import re
from typing import List, Dict, Any
from domain.validators.base_validator import BaseValidator

class IdentifierValidator:
    def validate(row: dict, index: int) -> List[Dict[str, Any]]:
        warnings = []
        for field in ("doi", "issn", "isbn"):
            value = row.get(field)
            if value and BaseValidator.is_empty(value):
                warnings.append({
                    "fila": index,
                    "columna": field,
                    "detalle": f"{field.upper()} vacío",
                    "valor": value,
                })
        return warnings
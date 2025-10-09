import re
from typing import List, Dict, Any
from domain.validators.base_validator import BaseValidator

COUNTRY_RE = re.compile(r"^[A-z]{2}$")

class CountryValidator:
    def validator(row: dict, index: int) -> List[Dict[str, Any]]:
        errors = []
        country = row.get("pais_producto")
        if not BaseValidator.is_empty(country) and not COUNTRY_RE.match(str(country).upper().strip()):
            errors.append({
                "fila": index,
                "columna": "pais_producto",
                "detalle": "Formato inválido (debe ser ISO 3166-1 alfa-2, ej: 'CO', 'US')",
                "valor": country
            })
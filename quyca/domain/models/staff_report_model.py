from dataclasses import dataclass
from typing import List, Dict, Any

"""
Domain entity that represents the validation result of a staff Excel file.
Contains errors, warnings, and duplicates detected during validation.
"""


@dataclass
class StaffReport:
    total_errores: int
    total_duplicados: int
    errores: List[Dict[str, Any]]
    errores_agrupados: List[Dict[str, Any]]
    advertencias: List[Dict[str, Any]]
    advertencias_agrupadas: List[Dict[str, Any]]
    duplicados: List[Dict[str, Any]]

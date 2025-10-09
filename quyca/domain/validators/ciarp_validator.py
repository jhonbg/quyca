from typing import List, Dict, Any, Tuple
import pandas as pd
from domain.models.staff_report_model import StaffReport
from domain.validators.required_fields_validator_ciarp import RequiredFieldsCiarpValidator
from domain.validators.document_validator import DocumentValidator
from domain.validators.year_validator import YearValidator
from domain.validators.language_validator import LanguageValidator
from domain.validators.country_validator import CountryValidator
from domain.validators.identifier_validator import IdentifierValidator
from domain.validators.unit_validator import UnitValidator
from domain.validators.error_grouper import ErrorGrouper

REQUIRED_COLUMNS = [
    "codigo_unidad_academica",
    "codigo_subunidad_academica",
    "tipo_documento",
    "identificacion",
    "año",
    "titulo",
    "idioma",
    "revista",
    "editorial",
    "doi",
    "issn",
    "isbn",
    "volumen",
    "issue",
    "primera_pagina",
    "ultima_pagina",
    "pais_producto",
    "entidad_premiadora",
    "ranking",
]

class CiarpValidator:
    @staticmethod
    def validate_columns(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        raw_cols = [str(c).lower().strip() for c in df.columns]
        missing = [c for c in REQUIRED_COLUMNS if c not in raw_cols]
        extra = [c for c in raw_cols if c not in REQUIRED_COLUMNS]
        errors = []
        if missing:
            errors.append(f"Columna faltantes: {', '.join(missing)}")
        if extra:
            errors.append(f"Columnas no permitidas: {', '.join(extra)}")
        return (len(errors) == 0, errors, raw_cols)
    
    @staticmethod
    def validate_row(row: dict, index: int) -> Dict[str, List[Dict[str, Any]]]:
        errors, warnings = [], []
        
        errors.extend(RequiredFieldsCiarpValidator.validate(row, index))
        errors.extend(DocumentValidator.validate(row.get("tipo_documento"), row.get("identificación"), index))
        
        year_err = YearValidator.validate(row.get("año"), "año", index)
        if year_err:
            errors.append(year_err)
        
        warnings.extend(LanguageValidator.validator(row, index))
        errors.extend(CountryValidator.validator(row, index))
        warnings.extend(IdentifierValidator.validate(row, index))
        errors.extend(UnitValidator.validate(row, index))
        
        return {"errores": errors, "advertencias": warnings}
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> StaffReport:
        errors, warnings = [], []
        
        for idx, row in df.iterrows():
            result = CiarpValidator.validate_row(row.to_dict(), idx)
            errors.extend(result["errores"])
            warnings.extend(result["advertencias"])
            
        return StaffReport(
            total_errores=len(errors),
            total_duplicados=0,
            errores=errors,
            errores_agrupados=ErrorGrouper.group_errors(errors),
            advertencias=warnings,
            advertencias_agrupadas=ErrorGrouper.group_warnings(warnings),
            duplicados=[],
        )
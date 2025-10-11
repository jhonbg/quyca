from typing import List, Dict, Any, Tuple
import pandas as pd
from domain.models.staff_report_model import StaffReport
from domain.validators.required_fields_validator_ciarp import RequiredFieldsCiarpValidator
from domain.validators.document_validator import DocumentValidator
from domain.validators.year_validator import YearValidator
from domain.validators.language_validator import LanguageValidator
from domain.validators.country_validator import CountryValidator
from domain.validators.unit_validator import UnitValidator
from domain.validators.error_grouper import ErrorGrouper

EXTRA_ALLOWED = {"estado_de_validación", "observación"}

REQUIRED_COLUMNS = [
    "código_unidad_académica",
    "código_subunidad_académica",
    "tipo_documento",
    "identificación",
    "año",
    "título",
    "idioma",
    "revista",
    "editorial",
    "doi",
    "issn",
    "isbn",
    "volumen",
    "issue",
    "primera_página",
    "última_página",
    "pais_producto",
    "entidad_premiadora",
    "ranking",
]

class CiarpValidator:
    @staticmethod
    def validate_columns(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        raw_cols = [str(c).lower().strip() for c in df.columns]
        errors: List[str] = []
        usecols: List[str] = []

        expected = list(REQUIRED_COLUMNS)

        for idx, c in enumerate(raw_cols):
            col = str(c).strip()

            if idx == 0 and (
                col == "" or col.lower() == "index" or col.lower().startswith("unnamed")
            ):
                continue

            if col == "" or col.lower().startswith("unnamed"):
                if not df.iloc[:, idx].dropna(how="all").empty:
                    errors.append(f"Columna sin nombre en posición {idx+1}")
                continue

            usecols.append(col)
        missing = [c for c in expected if c not in usecols]
        extra = [c for c in usecols if c not in expected and c not in EXTRA_ALLOWED]
        
        if missing:
            errors.append(f"Columna faltantes: {', '.join(missing)}")
        if extra:
            errors.append(f"Columnas no permitidas: {', '.join(extra)}")
            
        business_cols = [c for c in usecols if c not in EXTRA_ALLOWED]
        
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
        warnings.extend(CountryValidator.validator(row, index))
        errors.extend(UnitValidator.validate(row, index))
        
        return {"errores": errors, "advertencias": warnings}
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> StaffReport:
        errors, warnings = [], []
        
        print(f"[DEBUG] Total filas: {len(df)}")
        for idx, row in df.iterrows():
            if idx % 100 == 0:
                print(f"[DEBUG] Procesando fila {idx}")
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
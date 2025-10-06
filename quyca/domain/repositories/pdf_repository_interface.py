import io
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IPDFRepository(ABC):
    """Generates a PDF with errors, warnings, and duplicates found in the uploaded file"""

    @abstractmethod
    def generate_quality_report(
        self,
        errors: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]],
        duplicados: List[Dict[str, Any]] | None,
        institution: str,
        filename: str,
        upload_date: str,
        user: str,
    ) -> io.BytesIO:
        pass
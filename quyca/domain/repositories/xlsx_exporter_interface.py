from __future__ import annotations

import io
from typing import Protocol

import pandas as pd

class IXlsxExporter(Protocol):
    """Port for exporting a dataframe to an Excel file in-memory."""
    
    def to_excel_bytes(self, df: pd.DataFrame) -> io.BytesIO:
        ...
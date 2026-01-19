from __future__ import annotations

from typing import Protocol

import pandas as pd

from quyca.domain.models.staff_report_model import StaffReport

class IDataFrameAnnotator(Protocol):
    """Port for annotating a dataframe based on a validation report."""
    
    def annotate(self, df: pd.DataFrame, report: StaffReport) -> pd.DataFrame:
        ...
from __future__ import annotations

from typing import List, Protocol, Tuple
import pandas as pd


class ICiarpValidator(Protocol):
    """Port for CIARP validation rules."""

    def validate_columns(self, df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        ...

from __future__ import annotations

from typing import Any, Dict, Protocol


class IFileRepository(Protocol):
    """Port for persisting uploaded files (e.g., Google Drive, local storage.)"""

    def save_file(self, file: Any, ror_id: str, institution: str, file_type: str) -> Dict[str, Any]:
        """Persist file and return a result payload (msg, ids, urls, etc.)"""

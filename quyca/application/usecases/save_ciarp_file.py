from typing import Dict
from infrastructure.repositories.file_repository import FileRepository

class SaveCiarpFileUseCase:
    def __init__(self, file_repo: FileRepository):
        self.file_repo = file_repo
    
    def execute(self, file, ror_id: str, institution: str, file_type: str = "ciarp") -> Dict[str, str]:
        return self.file_repo.save_file(file, ror_id, institution, file_type)
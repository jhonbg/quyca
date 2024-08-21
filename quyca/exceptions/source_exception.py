class SourceException(Exception):
    def __init__(self, source_id):
        self.source_id: str = source_id

    def __str__(self):
        return f"Source with id '{self.source_id}' not found."
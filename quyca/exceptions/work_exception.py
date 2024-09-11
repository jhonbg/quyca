class WorkException(Exception):
    def __init__(self, work_id):
        self.work_id: str = work_id

    def __str__(self):
        return f"Work with id '{self.work_id}' not found."

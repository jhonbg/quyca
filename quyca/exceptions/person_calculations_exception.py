class PersonCalculationsException(Exception):
    def __init__(self, person_id):
        self.person_id: str = person_id

    def __str__(self):
        return f"PersonCalculations with id '{self.person_id}' not found."
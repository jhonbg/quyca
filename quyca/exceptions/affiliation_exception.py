class AffiliationException(Exception):
    def __init__(self, affiliation_id):
        self.affiliation_id: str = affiliation_id

    def __str__(self):
        return f"Affiliation with id '{self.affiliation_id}' not found."

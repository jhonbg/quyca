import math


def clean_nan(value):
    """
    This function converts the NaN values to None. Because JSON does not support NaN values. In sources many fields like 'ranking.rank' and 'publisher.name' are affected

    Parameter
    ---------
    value: The value to be checked for NaN.

    Response
    --------
    If the value is NaN, it returns None. Otherwise, it returns the original value.
    """
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


source_type_mapping = {
    # Alias que apuntan a 'journal'
    "E": "journal",
    "EL": "journal",
    "IE": "journal",
    "IM": "journal",
    "L": "journal",
    "P": "journal",
    # Tipos normalizados
    "book series": "book series",
    "conference": "conference",
    "conference and proceedings": "conference",
    "ebook platform": "ebook platform",
    "journal": "journal",
    "metadata": "metadata",
    "other": "other",
    "repository": "repository",
    "trade journal": "trade journal",
}

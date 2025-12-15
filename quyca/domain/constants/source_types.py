TYPE_DISPLAY_MAPPING = {
    "journal": "Revista",
    "book series": "Serie de libros",
    "conference": "Conferencia",
    "ebook platform": "Plataforma de libros electrónicos",
    "metadata": "Metadatos",
    "other": "Otro",
    "repository": "Repositorio",
}

NORMALIZED_TYPE_MAPPING = {
    # Scienti types
    "E": "journal",
    "EL": "journal",
    "IE": "journal",
    "IM": "journal",
    "L": "journal",
    "P": "journal",
    # OpenAlex types
    "journal": "journal",
    "book series": "book series",
    "conference": "conference",
    "ebook platform": "ebook platform",
    "metadata": "metadata",
    "repository": "repository",
    "other": "other",
    # Scimago types
    "trade journal": "journal",
    "conference and proceedings": "conference",
}

SOURCE_TITLES = {
    "openalex": "OpenAlex",
    "scimago": "Scimago",
    "scienti": "Scienti",
}

QUARTILE_MAPPING = {"-": "Sin cuartil"}

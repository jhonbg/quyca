def parse_products_by_database(data: dict) -> dict:
    venn_source = {
        "scienti": data.get("scienti", 0),
        "minciencias": data.get("minciencias", 0),
        "openalex": data.get("openalex", 0),
        "scholar": data.get("scholar", 0),
        "scienti_minciencias": data.get("scienti_minciencias", 0),
        "scienti_openalex": data.get("scienti_openalex", 0),
        "scienti_scholar": data.get("scienti_scholar", 0),
        "minciencias_openalex": data.get("minciencias_openalex", 0),
        "minciencias_scholar": data.get("minciencias_scholar", 0),
        "openalex_scholar": data.get("openalex_scholar", 0),
        "scienti_minciencias_openalex": data.get("scienti_minciencias_openalex", 0),
        "scienti_minciencias_scholar": data.get("scienti_minciencias_scholar", 0),
        "scienti_openalex_scholar": data.get("scienti_openalex_scholar", 0),
        "minciencias_openalex_scholar": data.get("minciencias_openalex_scholar", 0),
        "minciencias_openalex_scholar_scienti": data.get("minciencias_openalex_scholar_scienti", 0),
    }
    return {"plot": venn_source}

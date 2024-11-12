def get_works_h_index_by_scholar_citations(works: list) -> int:
    citations = sorted([work.get("scholar_citations_count") for work in works], reverse=True)
    h_index = 0
    for i, cites in enumerate(citations):
        current_index = i + 1
        if cites >= current_index:
            h_index = current_index
        else:
            break
    return h_index

def hindex(citation_list: list) -> int:
    return sum(x >= i + 1 for i, x in enumerate(sorted(list(citation_list), reverse=True)))

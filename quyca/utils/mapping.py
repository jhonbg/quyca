from database.models.work_model import Work


def get_openalex_scienti(work: Work) -> int:
    for count in work.citations_count:
        if count.source == "openalex":
            return count.count
        if count.source == "scienti":
            return count.count
    return 0

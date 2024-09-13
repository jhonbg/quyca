from protocols.mongo.models.work import Work


def get_openalex_scienti(x: Work) -> int:
    for count in x.citations_count:
        if count.source == "openalex":
            return count.count
        if count.source == "scienti":
            return count.count
    return 0


def get_subjects(work: Work, level: int = 0):
    for subject in work.subjects:
        for sub in subject.subjects:
            if subject.source == "openalex" and sub.level == level:
                return sub

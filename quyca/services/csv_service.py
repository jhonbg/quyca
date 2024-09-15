from datetime import datetime

from database.models.base_model import ExternalId
from database.models.work_model import Work, Affiliation
from database.repositories import csv_repository
from enums.institutions import institutions_list
from enums.openalex_types import openalex_types_dict
from services import new_source_service
from services.new_work_service import set_title_and_language
from services.parsers import work_parser


def get_works_csv_by_affiliation(affiliation_id: str) -> str:
    works = csv_repository.get_works_csv_by_affiliation(affiliation_id)
    data = get_csv_data(works)
    return work_parser.parse_csv(data)


def get_works_csv_by_person(person_id: str) -> str:
    works = csv_repository.get_works_csv_by_person(person_id)
    data = get_csv_data(works)
    return work_parser.parse_csv(data)


def get_csv_data(works):
    data = []
    for work in works:
        set_doi(work)
        set_csv_ranking(work)
        set_csv_affiliations(work)
        set_csv_authors(work)
        set_csv_bibliographic_info(work)
        set_csv_citations_count(work)
        set_csv_subjects(work)
        set_title_and_language(work)
        set_csv_types(work)
        new_source_service.update_csv_work_source(work)
        data.append(work)
    return data


def set_csv_ranking(work):
    if work.ranking:
        rankings = []
        for ranking in work.ranking:
            if type(ranking.date) == int:
                date = datetime.fromtimestamp(ranking.date).strftime("%d-%m-%Y")
                rankings.append(str(ranking.rank) + " / " + str(ranking.source) + " / " + str(date))
            else:
                rankings.append(str(ranking.rank) + " / " + str(ranking.source))
        work.ranking = " | ".join(set(rankings))
    else:
        work.ranking = None


def set_doi(work: Work):
    work.doi = next(
        filter(lambda external_id: external_id.source == "doi", work.external_ids),
        ExternalId(),
    ).id


def set_csv_types(work: Work):
    openalex_types = []
    scienti_types = []
    for work_type in work.types:
        if work_type.source == "openalex" and work_type.type in openalex_types_dict.keys():
            openalex_types.append(openalex_types_dict.get(work_type.type))
        elif work_type.source == "scienti":
            scienti_types.append(str(work_type.type))
    work.openalex_types = " | ".join(set(openalex_types))
    work.scienti_types = " | ".join(set(scienti_types))


def set_csv_subjects(work: Work):
    if work.subjects:
        subjects = []
        for subject in work.subjects[0].subjects:
            subjects.append(str(subject.name))
        work.subjects = " | ".join(set(subjects))


def set_csv_citations_count(work: Work):
    for citation_count in work.citations_count:
        if citation_count.source == "openalex":
            work.openalex_citations_count = str(citation_count.count)
        elif citation_count.source == "scholar":
            work.scholar_citations_count = str(citation_count.count)


def set_csv_bibliographic_info(work: Work):
    work.bibtex = work.bibliographic_info.bibtex
    work.pages = work.bibliographic_info.pages
    work.issue = work.bibliographic_info.issue
    work.is_open_access = work.bibliographic_info.is_open_access
    work.open_access_status = work.bibliographic_info.open_access_status
    work.start_page = work.bibliographic_info.start_page
    work.end_page = work.bibliographic_info.end_page
    work.volume = work.bibliographic_info.volume


def set_csv_authors(work: Work):
    authors = []
    for author in work.authors:
        authors.append(str(author.full_name))
    work.authors = " | ".join(set(authors))


def set_csv_affiliations(work: Work):
    countries = []
    institutions = []
    departments = []
    faculties = []
    groups = []
    groups_ranking = []
    for author in work.authors:
        for affiliation in author.affiliations:
            affiliation_data = next(
                filter(lambda x: x.id == affiliation.id, work.affiliations_data),
                Affiliation(),
            )
            if affiliation.types and affiliation.types[0].type in institutions_list:
                institutions.append(str(affiliation.name))
                if affiliation_data.addresses:
                    countries.append(str(affiliation_data.addresses[0].country))
            elif affiliation.types and affiliation.types[0].type == "department":
                departments.append(str(affiliation.name))
            elif affiliation.types and affiliation.types[0].type == "faculty":
                faculties.append(str(affiliation.name))
            elif affiliation.types and affiliation.types[0].type == "group":
                groups.append(str(affiliation.name))
                if affiliation_data.ranking:
                    ranking = affiliation_data.ranking[0]
                    if type(ranking.from_date) == int and type(ranking.to_date) == int:
                        groups_ranking.append(
                            str(ranking.rank)
                            + " / "
                            + datetime.fromtimestamp(ranking.from_date).strftime("%d-%m-%Y")
                            + " - "
                            + datetime.fromtimestamp(ranking.to_date).strftime("%d-%m-%Y")
                        )
    work.institutions = " | ".join(set(institutions))
    work.departments = " | ".join(set(departments))
    work.faculties = " | ".join(set(faculties))
    work.groups = " | ".join(set(groups))
    work.groups_ranking = " | ".join(set(groups_ranking))
    work.countries = " | ".join(set(countries))

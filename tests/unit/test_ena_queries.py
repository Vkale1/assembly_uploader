import responses

from assembly_uploader.ena_queries import EnaQuery


def test_ena_query_study(study_data):
    responses.add(
        responses.POST,
        "https://www.ebi.ac.uk/ena/portal/api/search",
        json=[
            {
                "study_accession": "PRJEB41657",
                "study_title": "HoloFood Salmon Trial A+B Gut Metagenome",
                "first_public": "2022-08-02",
            }
        ],
    )

    responses.add(
        responses.GET,
        "https://www.ebi.ac.uk/ena/submit/report/studies/ERP125469",
        json=[
            {
                "report": {
                    "id": "ERP125469",
                    "alias": "ena-STUDY-UNIVERSITY OF COPENHAGEN-02-12-2020-08:09:52:762-111",
                    "firstCreated": "2020-12-02T08:09:55",
                    "firstPublic": "2022-08-02T17:21:21",
                    "releaseStatus": "PUBLIC",
                    "submissionAccountId": "Webin-51990",
                    "secondaryId": "PRJEB41657",
                    "title": "HoloFood Salmon Trial A+B Gut Metagenome",
                    "holdDate": "null",
                },
                "links": [],
            }
        ],
    )

    ena_study_public = EnaQuery(
        accession="ERP125469",
        private=False,
    )

    ena_study_private = EnaQuery(
        accession="ERP125469",
        private=True,
    )

    assert (
        ena_study_public.build_query() and ena_study_private.build_query() == study_data
    )


def test_ena_query_run(run_public, run_private):
    responses.add(
        responses.POST,
        "https://www.ebi.ac.uk/ena/portal/api/search",
        json=[
            {
                "run_accession": "ERR4918394",
                "sample_accession": "SAMEA7687881",
                "instrument_model": "DNBSEQ-G400",
            }
        ],
    )

    responses.add(
        responses.GET,
        "https://www.ebi.ac.uk/ena/submit/report/runs/ERR4918394",
        json=[
            {
                "report": {
                    "id": "ERR4918394",
                    "alias": "webin-reads-SA01_02C1a_metaG",
                    "instrumentModel": "DNBSEQ-G400",
                    "firstPublic": "2022-08-02T17:24:21",
                    "releaseStatus": "PUBLIC",
                    "submissionAccountId": "Webin-51990",
                    "studyId": "ERP125469",
                    "experimentId": "ERX4783303",
                    "sampleId": "ERS5444411",
                },
                "links": [],
            }
        ],
    )

    ena_run_public = EnaQuery(
        accession="ERR4918394",
        private=False,
    )
    ena_run_private = EnaQuery(
        accession="ERR4918394",
        private=True,
    )

    assert ena_run_private.build_query() == run_private
    assert ena_run_public.build_query() == run_public

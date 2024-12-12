import pytest
import responses

from assembly_uploader.submit_study import submit_study
from assembly_uploader.webin_utils import (
    ENA_WEBIN,
    ENA_WEBIN_PASSWORD,
    ensure_webin_credentials_exist,
)


def test_submit_study(study_submission_xml_dir, monkeypatch):
    ena_dropbox = responses.add(
        responses.POST,
        "https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit",
        body="""
        This is a long receipt from the dropbox.
        success="true"
        Your new study has accession="PRJEA1"
        """,
    )

    with pytest.raises(Exception):
        ensure_webin_credentials_exist()

    monkeypatch.setenv(ENA_WEBIN, "fake-webin-999")
    monkeypatch.setenv(ENA_WEBIN_PASSWORD, "fakewebinpw")

    ensure_webin_credentials_exist()

    new_study = submit_study(
        "ERP125469", is_test=True, directory=study_submission_xml_dir
    )
    assert ena_dropbox.call_count == 1
    assert new_study == "PRJEA1"

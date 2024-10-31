from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def study_submission_xml_dir():
    return Path(__file__).resolve().parent / Path("fixtures/SRP272267_upload")


@pytest.fixture(scope="module")
def study_reg_xml(study_submission_xml_dir):
    return study_submission_xml_dir / Path("SRP272267_reg.xml")


@pytest.fixture(scope="module")
def study_reg_xml_content(study_reg_xml):
    with study_reg_xml.open() as f:
        return f.readlines()


@pytest.fixture(scope="module")
def study_submission_xml(study_submission_xml_dir):
    return study_submission_xml_dir / Path("SRP272267_submission.xml")


@pytest.fixture(scope="module")
def study_submission_xml_content(study_submission_xml):
    with study_submission_xml.open() as f:
        return f.readlines()


@pytest.fixture(scope="module")
def assemblies_metadata():
    return Path(__file__).resolve().parent / Path("fixtures/test_metadata")


@pytest.fixture(scope="module")
def run_manifest(study_submission_xml_dir):
    return study_submission_xml_dir / Path("SRR12240187.manifest")


@pytest.fixture(scope="module")
def run_manifest_content(run_manifest):
    with run_manifest.open() as f:
        return f.readlines()

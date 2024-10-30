import responses

from assembly_uploader import study_xmls


def test_study_xmls(tmp_path, study_reg_xml_content, study_submission_xml_content):
    ena_api = responses.add(
        responses.POST,
        "https://www.ebi.ac.uk/ena/portal/api/v2.0/search",
        json=[
            {
                "study_accession": "PRJNA646656",
                "study_title": "Metagenomic data reveal diverse fungal and algal communities associated with the lichen symbiosis",
                "study_description": "short, metagnomic reads from lichen thalli",
                "first_public": "2020-07-18",
            }
        ],
    )
    study_reg = study_xmls.StudyXMLGenerator(
        study="SRP272267",
        center_name="EMG",
        library=study_xmls.METAGENOME,
        tpa=True,
        output_dir=tmp_path,
    )
    assert ena_api.call_count == 1

    study_reg.write_study_xml()
    assert (
        study_reg._title
        == "Metagenome assembly of PRJNA646656 data set (Metagenomic data reveal diverse fungal and algal communities associated with the lichen symbiosis)"
    )

    assert study_reg.study_xml_path.is_relative_to(tmp_path)
    assert study_reg.study_xml_path.is_file()

    with study_reg.study_xml_path.open() as f:
        content = f.readlines()
    assert content == study_reg_xml_content

    study_reg.write_submission_xml()
    assert study_reg.submission_xml_path.is_relative_to(tmp_path)
    assert study_reg.submission_xml_path.is_file()

    with study_reg.submission_xml_path.open() as f:
        content = f.readlines()
    assert content == study_submission_xml_content

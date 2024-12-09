import responses

from assembly_uploader import study_xmls


def test_study_xmls(tmp_path, study_reg_xml_content, study_submission_xml_content):
    ena_api = responses.add(
        responses.POST,
        "https://www.ebi.ac.uk/ena/portal/api/v2.0/search",
        json=[
            {
                "study_accession": "PRJEB41657",
                "study_title": "HoloFood Salmon Trial A+B Gut Metagenome",
                "study_description": "Metagenomic raw reads, assemblies, and bins derived from HoloFood salmon gut samples from trial A and B. The samples in this project contributed to the salmon MAG catalogue (project: PRJEB55376 [ERP140265])",
                "first_public": "2022-08-02",
            }
        ],
    )
    study_reg = study_xmls.StudyXMLGenerator(
        study="ERP125469",
        center_name="EMG",
        library=study_xmls.METAGENOME,
        tpa=True,
        output_dir=tmp_path,
    )
    assert ena_api.call_count == 1

    study_reg.write_study_xml()
    assert (
        study_reg._title
        == "Metagenome assembly of PRJEB41657 data set (HoloFood Salmon Trial A+B Gut Metagenome)"
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

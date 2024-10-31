from pathlib import Path

import responses

from assembly_uploader.assembly_manifest import AssemblyManifestGenerator


def test_assembly_manifest(assemblies_metadata, tmp_path, run_manifest_content):
    responses.add(
        responses.POST,
        "https://www.ebi.ac.uk/ena/portal/api/v2.0/search",
        json=[
            {
                "run_accession": "SRR12240187",
                "sample_accession": "SAMN15548970",
                "instrument_model": "Illumina HiSeq 2500",
                "instrument_platform": "ILLUMINA",
            }
        ],
    )
    assembly_manifest_gen = AssemblyManifestGenerator(
        study="SRP272267",
        assembly_study="PRJ1",
        assemblies_csv=assemblies_metadata,
        output_dir=tmp_path,
    )
    assembly_manifest_gen.write_manifests()

    manifest_file = tmp_path / Path("SRP272267_upload/SRR12240187.manifest")
    assert manifest_file.exists()

    with manifest_file.open() as f:
        assert f.readlines() == run_manifest_content

# Public ENA Assembly uploader
Upload of metagenome and metatranscriptome assemblies to ENA

Pre-requisites:
- CSV metadata file. One per study. See test/fixtures/test_metadata for an example
- Compressed assembly fasta files in the locations defined in the metadata file

Set the following environmental variables with your webin details:

ENA_WEBIN
```
export ENA_WEBIN=Webin-0000
```

ENA_WEBIN_PASSWORD
```
export ENA_WEBIN_PASSWORD=password
```

## Register study and generate pre-upload files - change this to python package installation instead?
The script needs `python`, `requests`, and `ena-webin-cli` to run. Install the package:

```bash
python3 -m pip install -i https://test.pypi.org/simple/ --no-deps assemblyuploader==0.0.0
```

**If you already have a registered study accession for your assembly files skip to step 3.**

Step 1. This step will generate a folder STUDY_upload and a project XML and submission XML within it:
```bash
study_xmls
  --study STUDY         raw reads study ID
  --library LIBRARY     metagenome or metatranscriptome
  --center CENTER       center for upload e.g. EMG
  --hold HOLD           hold date (private) if it should be different from the provided study in format dd-mm-yyyy. Will inherit the release date of the raw read study if not
                        provided.
  --tpa                 is the study a third party assembly. Default True
  --publication PUBLICATION
                        pubmed ID for connected publication if available
```

Step 2. This step submit the XML to ENA and generate a new assembly study accession. Keep note of the newly generated study accession:

```bash
submit_study
  --study STUDY         raw reads study ID
  --test                run test submission only
```


Step 3. This step will generate manifest files in the folder STUDY_UPLOAD for runs specified in the metadata file:
```bash
assembly_manifest
  --study STUDY         raw reads study ID
  --data DATA           metadata CSV - run_id, coverage, assembler, version, filepath
  --assembly_study ASSEMBLY_STUDY
                        pre-existing study ID to submit to if available. Must exist in the webin account
  --force               overwrite all existing manifests
```

## Upload assemblies
Once manifest files are generated, it is necessary to use ENA's webin-cli resource to upload genomes.

To test your submission add the `-test` argument.

A live execution example within this repo is the following:
```bash
ena-webin-cli \
  -context=genome \
  -manifest=SRR12240187.manifest \
  -userName=$ENA_WEBIN \
  -password=$ENA_WEBIN_PASSWORD \
  -submit
```

More information on ENA's webin-cli can be found [here](<https://ena-docs.readthedocs.io/en/latest/submit/general-guide/webin-cli.html>).

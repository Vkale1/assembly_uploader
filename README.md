# assembly_uploader
Upload of metagenome and metatranscriptome assemblies to ENA

This is currently running upload to the dev version of ENA

Prerequisites:
- Environment with python3
- CSV metadata file. One per study. See test/test_metadata for an example.
- Raw reads ENA study accession/s
- Assembly files zipped

Set the following environmental variables:

WEBIN_USERNAME
```
export WEBIN_USERNAME=Webin-0000
```

WEBIN_PASSWORD
```
export WEBIN_PASSWORD=password
```

This step will generate a folder STUDY_upload and a project XML and submission XML within it:
```
study_xmls.py --study READS_STUDY_ID --library metagenome --center CENTER --tpa TRUE/FALSE --publication PUBMED_ID (optional will inheret the raw study release date if not specified --hold RELEASE_DATE)
```

This step submit the XML and generate a new assembly study accession:

```
submit_study.py --study READS_STUDY_ID (optional if you have moved the XMLs above somewhere else --directory XML_LOCATION)
```


This step will generate manifest files in the folder STUDY_UPLOAD for runs specified in the metadata file:
```
assembly_manifest.py --study READS_STUDY_ID --data METADATA_CSV --assembly_study ASSEMBLY_STUDY_ID --assemblies-dir PATH_TO_ASSEMBLY_FILES --filename ASSEMBLY_FILE_SUFFIX (--force optional overwrites existing manifests) 
```

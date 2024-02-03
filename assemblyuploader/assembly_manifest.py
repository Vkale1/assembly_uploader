import os
import hashlib
import sys
import argparse
import logging
import csv
from .ena_queries import EnaQuery

logging.basicConfig(level=logging.INFO)


def parse_info(data_file):
    csvfile = open(data_file, newline='')
    csvdict = csv.DictReader(csvfile)
    return csvdict


def get_md5(path_to_file):
    md5_hash = hashlib.md5()
    with open(path_to_file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="independent to directory structure")
    parser.add_argument('--study', help='raw reads study ID', required=True)
    parser.add_argument('--data', help='metadata CSV - run_id, coverage, assembler, version, filepath')
    parser.add_argument('--assembly_study', help='pre-existing study ID to submit to if available. '
                                                 'Must exist in the webin account', required=False)
    parser.add_argument('--force', help='overwrite all existing manifests', required=False, action='store_true')
    return parser.parse_args(argv)


class AssemblyManifest:
    def __init__(self, argv=sys.argv[1:]):
        self.args = parse_args(argv)
        self.study = self.args.study
        self.metadata = parse_info(self.args.data)
        self.new_project = self.args.assembly_study
        self.upload_dir = os.path.join(os.getcwd(), f'{self.study}_upload')
        if not os.path.exists(self.upload_dir):
            os.mkdir(self.upload_dir)
        self.force = self.args.force
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    def generate_manifest(self, new_project_id, upload_dir, run_id, sample, sequencer, coverage, assembler,
                          assembler_version, assembly_path):
        logging.info('Writing manifest for ' + run_id)
        #   sanity check assembly file provided
        if not os.path.exists(assembly_path):
            logging.error(f'Assembly path {assembly_path} does not exist. Skipping manifest for run {run_id}')
            return
        substrings = ['fa.gz', 'fna.gz', 'fasta.gz']
        if not any(substring in assembly_path for substring in substrings):
            logging.error(f'Assembly file {assembly_path} is either not fasta format or not compressed for run '
                          f'{run_id}.')
            return
        #   collect variables
        assembly_alias = get_md5(assembly_path)
        assembler = f'{assembler} v{assembler_version}'
        manifest_path = os.path.join(upload_dir, f'{run_id}.manifest')
        #   skip existing manifests
        if os.path.exists(manifest_path) and not self.force:
            logging.error(f'Manifest for {run_id} already exists at {manifest_path}. Skipping')
            return
        values = (
            ('STUDY', new_project_id),
            ('SAMPLE', sample),
            ('RUN_REF', run_id),
            ('ASSEMBLYNAME', run_id+'_'+assembly_alias),
            ('ASSEMBLY_TYPE', 'primary metagenome'),
            ('COVERAGE', coverage),
            ('PROGRAM', assembler),
            ('PLATFORM', sequencer),
            ('FASTA', assembly_path),
            ('TPA', 'true')
        )
        logging.info("Writing manifest file (.manifest) for " + run_id)
        with open(manifest_path, "w") as outfile:
            for (k, v) in values:
                manifest = f'{k}\t{v}\n'
                outfile.write(manifest)

    def write_manifests(self):
        for row in self.metadata:
            ena_query = EnaQuery(row['Run'])
            ena_metadata = ena_query.build_query()
            self.generate_manifest(self.new_project, self.upload_dir, row['Run'], ena_metadata['sample_accession'],
                                   ena_metadata['instrument_model'], row['Coverage'], row['Assembler'], row['Version'],
                                   row['Filepath'])


if __name__ == "__main__":
    gen_manifest = AssemblyManifest()
    gen_manifest.write_manifests()
    logging.info('Completed')


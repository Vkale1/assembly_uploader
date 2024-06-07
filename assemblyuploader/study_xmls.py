import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
import argparse
import sys
import os
from datetime import datetime
from ena_queries import EnaQuery


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Study XML generation")
    parser.add_argument('--study', help='raw reads study ID', required=True)
    parser.add_argument('--library', help='metagenome or metatranscriptome')
    parser.add_argument('--center', help='center for upload e.g. EMG')
    parser.add_argument('--hold', help='hold date (private) if it should be different from the provided study in '
                                       'format dd-mm-yyyy. Will inherit the release date of the raw read study if not '
                                       'provided.', required=False)
    parser.add_argument('--tpa', help='is the study a third party assembly. Default True', action='store_true',
                        default=True)
    parser.add_argument('--publication', help='pubmed ID for connected publication if available', required=False)
    parser.add_argument('--output-dir', help='Path to output directory', required=False)
    return parser.parse_args(argv)


class RegisterStudy:
    def __init__(self, argv=sys.argv[1:]):
        self.args = parse_args(argv)
        self.study = self.args.study
        if self.args.output_dir:
            self.upload_dir = os.path.join(self.args.output_dir, f'{self.study}_upload')
        else:
            self.upload_dir = os.path.join(os.getcwd(), f'{self.study}_upload')
        self.study_xml_path = os.path.join(self.upload_dir, f'{self.study}_reg.xml')
        self.submission_xml_path = os.path.join(self.upload_dir, f'{self.study}_submission.xml')
        self.center = self.args.center
        self.hold = self.args.hold

        ena_query = EnaQuery(self.study)
        self.study_obj = ena_query.build_query()

        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    def write_study_xml(self):
        subtitle = self.args.library.lower()
        if self.args.tpa:
            sub_abstract = "Third Party Annotation (TPA) "
        else:
            sub_abstract = ""

        title = f"{subtitle} assembly of {self.study_obj['study_accession']} data " \
                f"set ({self.study_obj['study_title']})."
        abstract = f"The {sub_abstract}assembly was derived from the primary data " \
                   f"set {self.study_obj['study_accession']}."

        project_alias = self.study_obj['study_accession'] + "_assembly"
        with open(self.study_xml_path, "wb") as study_file:
            project_set = ET.Element("PROJECT_SET")
            project = ET.SubElement(project_set, "PROJECT")
            project.set("alias", project_alias)
            project.set("center_name", self.center)

            ET.SubElement(project, "TITLE").text = title
            ET.SubElement(project, "DESCRIPTION").text = abstract

            # submission
            submission_project = ET.SubElement(project, "SUBMISSION_PROJECT")
            ET.SubElement(submission_project, "SEQUENCING_PROJECT")

            # publication links
            if self.args.publication:
                project_links = ET.SubElement(project, "PROJECT_LINKS")
                project_link = ET.SubElement(project_links, "PROJECT_LINK")
                xref_link = ET.SubElement(project_link, "XREF_LINK")
                ET.SubElement(xref_link, "DB").text = "PUBMED"
                ET.SubElement(xref_link, "ID").text = self.args.publication

            # project attributes: TPA and assembly type
            project_attributes = ET.SubElement(project, "PROJECT_ATTRIBUTES")
            if self.args.tpa:
                project_attribute_tpa = ET.SubElement(project_attributes, "PROJECT_ATTRIBUTE")
                ET.SubElement(project_attribute_tpa, "TAG").text = "study keyword"
                ET.SubElement(project_attribute_tpa, "VALUE").text = "TPA:assembly"

            project_attribute_type = ET.SubElement(project_attributes, "PROJECT_ATTRIBUTE")
            ET.SubElement(project_attribute_type, "TAG").text = "new_study_type"
            ET.SubElement(project_attribute_type, "VALUE").text = f"{self.args.library} assembly"

            dom = minidom.parseString(ET.tostring(project_set, encoding="utf-8"))
            study_file.write(dom.toprettyxml().encode("utf-8"))

    def write_submission_xml(self):
        with open(self.submission_xml_path, "wb") as submission_file:
            submission = ET.Element("SUBMISSION")
            submission.set("center_name", self.center)

            # template
            actions = ET.SubElement(submission, "ACTIONS")
            action_sub = ET.SubElement(actions, "ACTION")
            ET.SubElement(action_sub, "ADD")

            # attributes: function and hold date
            public = self.study_obj['first_public']
            today = datetime.today().strftime('%Y-%m-%d')
            if self.hold:
                action_hold = ET.SubElement(actions, "ACTION")
                hold = ET.SubElement(action_hold, "HOLD")
                hold.set("HoldUntilDate", self.hold)
            elif public > today and not self.hold:
                action_hold = ET.SubElement(actions, "ACTION")
                hold = ET.SubElement(action_hold, "HOLD")
                hold.set("HoldUntilDate", public)

            dom = minidom.parseString(ET.tostring(submission, encoding="utf-8"))
            submission_file.write(dom.toprettyxml().encode("utf-8"))


if __name__ == "__main__":
    study_reg = RegisterStudy()
    study_reg.write_study_xml()
    study_reg.write_submission_xml()

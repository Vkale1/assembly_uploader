#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2024 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import os
import sys

import requests
import xml.dom.minidom as minidom

from time import sleep
from xml.parsers.expat import ExpatError


logging.basicConfig(level=logging.INFO)

RETRY_COUNT = 5

class NoDataException(ValueError):
    pass


def get_default_connection_headers():
    return {
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
        }
    }

def parse_accession(accession):
    if accession.startswith("PRJ"):
        return "study_accession"
    elif "RP" in accession:
        return "secondary_study_accession"
    elif "RR" in accession:
        return "run_accession"
    else:
        logging.error(f"{accession} is not a valid accession")
        sys.exit()


class EnaQuery:
    def __init__(self, accession, private=False):
        self.private_url ="https://www.ebi.ac.uk/ena/submit/report/"
        self.public_url = "https://www.ebi.ac.uk/ena/portal/api/search"
        self.accession = accession
        self.acc_type = parse_accession(accession)
        username = os.getenv("ENA_WEBIN")
        password = os.getenv("ENA_WEBIN_PASSWORD")
        if username is None or password is None:
            print("ENA_WEBIN and ENA_WEBIN_PASSWORD are not set")
            sys.exit(0)
        if username and password:
            self.auth = (username, password)
        else:
            self.auth = None
        self.private = private

    def post_request(self, data):
        response = requests.post(self.public_url, data=data, **get_default_connection_headers())
        return response

    def get_request(self, url):
        response = requests.get(url, auth=self.auth)
        return response     

    def check_api_error(self, response):
        try:
            data = json.loads(response.text)[0]
            return data
        except NoDataException:
            print("Could not find {} in ENA".format(self.accession))
        except (IndexError, TypeError, ValueError, KeyError):
            print("Failed to fetch {}, returned error: {}.".format(self.accession, response.text))

    def get_study(self,):
        if not self.private:
            data = {
                "result": "study",
                "query": f'{self.acc_type}="{self.accession}"',
                "fields": "study_accession,study_title,study_description,first_public",
                "format": "json",
                }
            data['dataPortal'] = "ena"
            try:
                response = self.post_request(data)
                if response.status_code == 204:
                    raise NoDataException()
                final_data = self.check_api_error(response)
                return final_data
            finally:
                print("{} public data returned from ENA".format(self.accession))
                
        else:
            #   get text based fields from reports API and reformat to match public portal API
            url = f"https://www.ebi.ac.uk/ena/submit/report/studies/xml/{self.accession}"
            try:
                xml_response = requests.get(url, auth=self.auth)
                xml_response.raise_for_status()  # Check for HTTP request errors
                manifestXml = minidom.parseString(xml_response.text)
                study_title = manifestXml.getElementsByTagName("STUDY_TITLE")[0].firstChild.nodeValue
                study_desc = manifestXml.getElementsByTagName("STUDY_DESCRIPTION")[0].firstChild.nodeValue
                final_data = {'study_accession': self.accession, 'study_description': study_desc, 'study_title': study_title}
            except ExpatError as e:
                print(f"XML parsing failed: {e}")
            except requests.RequestException as e:
                print(f"HTTP request failed: {e}")
            

            #   get hold date from submissions API and reformat to match public portal API
            url = f'{self.private_url}studies/{self.accession}'
            response = self.get_request(url)
            study = json.loads(response.text)[0]
            study_data = study['report']
            #   remove time and keep date
            first_public = study_data['firstPublic'].split('T')[0] 
            final_data['first_public'] = first_public
            print("{} private data returned from ENA".format(self.accession))
            return final_data


    def get_run(self, attempt=0):
        if not self.private:
            data = {
                'result': 'read_run',
                'query': f'run_accession="{self.accession}"',
                'fields': 'run_accession,sample_accession,instrument_model',
                'format': 'json'
            }
            response = self.post_request(data)
        else:
            url = f'{self.private_url}runs/{self.accession}'
            response = self.get_request(url)
            
        if response.status_code == 204:
            if attempt < 2:
                attempt += 1
                sleep(1)
                return self.get_run(self, attempt)
            else:
                raise ValueError("Could not find run {} in ENA after {} attempts".format(self.accession, RETRY_COUNT))
        run = self.check_api_error(response)
        if run is None:
            print(f"private run {self.accession} is not present in the specified Webin account")

        if self.private:
            run_data = run['report']
            final_data = {'run_accession': self.accession, 'sample_accession': run_data['sampleId'], 'instrument_model':run_data['instrumentModel']}
            print("{} private data returned from ENA".format(self.accession))
            return final_data
        else:
            print("{} public data returned from ENA".format(self.accession))
            return run

    def build_query(self):
        if 'study' in self.acc_type:
            ena_response = self.get_study()
        elif 'run' in self.acc_type:
            ena_response = self.get_run()
        return ena_response

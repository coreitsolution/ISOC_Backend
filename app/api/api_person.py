import requests
import os
from flask import json
from dotenv import load_dotenv

load_dotenv()

dss_api_url = os.getenv("DSS_API_URL")

class APIPerson:
    def api_person_list(self, token):
        resp = requests.get(
                url="https://" + dss_api_url + "/obms/api/v1.1/acs/person/page?page=1&pageSize=20&orgCode=001004&containChild=1",
                headers={"X-Subject-Token": token},
                verify=False,
            ).json()
        return resp
    
    def api_person_detail(self, token, person_id):
        resp = requests.get(
                url="https://" + dss_api_url + f"/obms/api/v1.1/acs/person/{person_id}",
                headers={"X-Subject-Token": token},
                verify=False,
            ).json()
        return resp
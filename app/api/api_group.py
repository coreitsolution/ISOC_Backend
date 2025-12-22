import requests
import os
from flask import json
from dotenv import load_dotenv

load_dotenv()


dss_api_url = os.getenv("DSS_API_URL")

class APIGroup:
    def api_group_list(token):
        resp = requests.get(
                url="https://" + dss_api_url + "/obms/api/v1.1/acs/person-group/list",
                headers={"X-Subject-Token": token},
                verify=False,
            ).json()
        return resp
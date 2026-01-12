import requests
import os
from flask import json
from dotenv import load_dotenv

load_dotenv()


dss_api_url = os.getenv("DSS_API_URL")


class APIGroup:
    def api_group_list(self, token):
        resp = requests.get(
            url="https://" + dss_api_url + "/obms/api/v1.1/acs/person-group/list",
            headers={"X-Subject-Token": token},
            verify=False,
        ).json()
        return resp

    def api_group_add(self, token, group_data):
        payload = {
            "parentOrgCode": "001",
            "orgName": group_data["orgName"],
            "roleIds": ["1", "2"],
        }
        resp = requests.post(
            url="https://" + dss_api_url + "/obms/api/v1.1/acs/person-group",
            headers={"X-Subject-Token": token, "Content-Type": "application/json"},
            data=json.dumps(payload),
            verify=False,
        ).json()
        return resp
    
    def api_group_update(self, token, group_data):
        payload = {
            "orgName": group_data["orgName"],
            "roleIds": ["1", "2"],
        }
        resp = requests.put(
            url="https://" + dss_api_url + f"/obms/api/v1.1/acs/person-group/{group_data['groupId']}",
            headers={"X-Subject-Token": token, "Content-Type": "application/json"},
            data=json.dumps(payload),
            verify=False,
        ).json()
        return resp

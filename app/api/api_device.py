import requests
import os
import logging
from flask import json
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
dss_api_url = os.getenv("DSS_API_URL")

class APIDevice:
    def api_get_device_tree(token):
        payload = {
            "orgCode": "",
        }
        resp = requests.post(
            url="https://"
            + dss_api_url
            + "/brms/api/v1.0/tree/devices",
            headers={"X-Subject-Token": token},
            json=payload,
            verify=False,
        ).json()
        return resp
    
    def api_get_device_info(token, device_id):
        resp = requests.get(
            url="https://"
            + dss_api_url
            + f"/brms/api/v1.1/device/{device_id}",
            headers={"X-Subject-Token": token},
            verify=False,
        ).json()
        return resp
    
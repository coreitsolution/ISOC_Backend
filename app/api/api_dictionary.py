import requests
import os
import logging
from flask import json
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
dss_api_url = os.getenv("DSS_API_URL")


class APIDictionary:
    def api_get_dictionary_car_brand(self, token):
        resp = requests.get(
            url="https://" + dss_api_url + f"/brms/api/v1.1/dictionary/list?types=2016",
            headers={"X-Subject-Token": token},
            verify=False,
        ).json()
        return resp

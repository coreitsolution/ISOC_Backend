import requests
import os
import logging
from flask import json
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
dss_api_url = os.getenv("DSS_API_URL")


class APIFace:
    def api_search_face(token, imageData):
        payload = {
            "beginTime": "1766016000",
            "endTime": "1766102349",
            "similarity": "92",
            "faceImageData": imageData,
            "analyseMode": "2",
        }
        resp = requests.post(
            url="https://"
            + dss_api_url
            + "/brms/api/v1.1/face/detection/record/search-by-picture/start",
            headers={"X-Subject-Token": token},
            json=payload,
            verify=False,
        ).json()
        return resp

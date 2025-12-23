import requests
import os
import logging
from flask import json
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
dss_api_url = os.getenv("DSS_API_URL")


class APIFace:
    def api_search_face_start(token, imageData, beginTime, endTime, similarity, analyseMode):
        payload = {
            "beginTime": beginTime,
            "endTime": endTime,
            "similarity": similarity,
            "faceImageData": imageData,
            "analyseMode": analyseMode,
            "channelIds": [
                "1000002$1$0$1",
                "1000002$1$0$2",
            ],
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

    def api_search_face_stop(token, session_id):
        payload = {
            "session": session_id,
        }
        resp = requests.post(
            url="https://"
            + dss_api_url
            + "/brms/api/v1.1/face/detection/record/search-by-picture/stop",
            headers={"X-Subject-Token": token},
            json=payload,
            verify=False,
        ).json()
        return resp

    def api_search_face_session(token, session_id):
        payload = {
            "page": "1",
            "pageSize": "20",
            "orderType": "2",
            "orderDirection": "1",
        }
        resp = requests.post(
            url="https://"
            + dss_api_url
            + f"/brms/api/v1.1/face/detection/record/search-by-picture/{session_id}/page",
            headers={"X-Subject-Token": token},
            json=payload,
            verify=False,
        ).json()
        return resp

    def api_search_face_download_image(token, session_id, device_code, urls):
        payload = {
            "session": session_id,
            "deviceCode": device_code,
            "urls": urls,
        }
        resp = requests.post(
            url="https://"
            + dss_api_url
            + f"/brms/api/v1.1/face/detection/record/device/picture/download",
            headers={"X-Subject-Token": token},
            json=payload,
            verify=False,
        ).json()
        return resp

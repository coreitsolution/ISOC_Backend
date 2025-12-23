import requests
import os
import logging
from flask import json
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv()
logging.basicConfig(level=logging.INFO)
dss_api_url = os.getenv("DSS_API_URL")


class APIFace:
    async def api_search_face_start(token, imageData):
        payload = {
            "beginTime": "1766016000",
            "endTime": "1766447999",
            "similarity": "70",
            "faceImageData": imageData,
            "analyseMode": "1",
            "channelIds": [
                "1000002$1$0$1",
                "1000002$1$0$2",
            ],
        }
        resp = {}
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.post(
                url="https://"
                + dss_api_url
                + "/brms/api/v1.1/face/detection/record/search-by-picture/start",
                headers={"X-Subject-Token": token},
                json=payload,
            )
            logging.info(".........Face Search Start Response: %s", resp.text)
        # resp = requests.post(
        #     url="https://"
        #     + dss_api_url
        #     + "/brms/api/v1.1/face/detection/record/search-by-picture/start",
        #     headers={"X-Subject-Token": token},
        #     json=payload,
        #     verify=False,
        # ).json()
        json_resp = resp.json()
        return json_resp

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
        logging.info("Session ID: %s", session_id)
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
        logging.info("..........Download Payload: %s", payload)
        resp = requests.post(
            url="https://"
            + dss_api_url
            + f"/brms/api/v1.1/face/detection/record/device/picture/download",
            headers={"X-Subject-Token": token},
            json=payload,
            verify=False,
        ).json()
        return resp

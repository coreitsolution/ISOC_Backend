import requests
import os
import logging
from flask import json
from dotenv import load_dotenv

load_dotenv()

dss_api_url = os.getenv("DSS_API_URL")


class APIPerson:
    def api_person_list(self, token, req):
        resp = requests.get(
            url="https://"
            + dss_api_url
            + f"/obms/api/v1.1/acs/person/page?page={req['page']}&pageSize={req['pageSize']}&orgCode={req['orgCode']}&containChild=1",
            headers={"X-Subject-Token": token},
            verify=False,
        ).json()
        result = []
        totalCount = resp["data"]["totalCount"]
        data = resp["data"]["pageData"]
        for person in data:
            person_info = {
                "personId": person["baseInfo"]["personId"],
                "firstName": person["baseInfo"]["firstName"],
                "lastName": person["baseInfo"]["lastName"],
                "orgCode": person["baseInfo"]["orgCode"],
                "facePicture": person["baseInfo"]["facePicture"],
                "orgName": person["baseInfo"]["orgName"],
                "email": person["baseInfo"]["email"],
                "tel": person["baseInfo"]["tel"],
            }
            result.append(person_info)
        return {"code": resp["code"], "desc": resp["desc"], "totalCount": totalCount, "data": result}

    def api_person_detail(self, token, person_id):
        resp = requests.get(
            url="https://" + dss_api_url + f"/obms/api/v1.1/acs/person/{person_id}",
            headers={"X-Subject-Token": token},
            verify=False,
        ).json()
        return resp

    def api_person_add(self, token, person_data):
        payload = {
            "baseInfo": {
                "personId": person_data["personId"],
                "lastName": person_data["lastName"] if "lastName" in person_data else "",
                "firstName": person_data["firstName"],
                "gender": person_data["gender"],
                "orgCode": person_data["orgCode"],
                "orgCodes": [person_data["orgCode"]],
                "email": person_data["email"] if "email" in person_data else "",
                "tel": person_data["tel"] if "tel" in person_data else "",
                "remark": person_data["remark"] if "remark" in person_data else "",
                "source": "0",
                "facePictures": person_data["facePictures"],
            },
            "extensionInfo": {
                "idType": "6",
                "nationalityId": "9999",
            },
            "authenticationInfo": {
                "startTime": "1767225600",
                "endTime": "2019686400",
            },
            "accessInfo": {"accessType": "0"},
            "faceComparisonInfo": {
                "enableFaceComparisonGroup": "1",
                "faceComparisonGroupId": "1",
            },
            "entranceInfo": {},
        }
        resp = requests.post(
            url="https://" + dss_api_url + "/obms/api/v1.1/acs/person",
            headers={"X-Subject-Token": token, "Content-Type": "application/json"},
            data=json.dumps(payload),
            verify=False,
        ).json()
        return resp

    def api_person_update(self, token, person_data):
        payload = {
            "baseInfo": {
                "personId": person_data["personId"],
                "lastName": person_data["lastName"] if "lastName" in person_data else "",
                "firstName": person_data["firstName"],
                "gender": person_data["gender"],
                "orgCode": person_data["orgCode"],
                "orgCodes": [person_data["orgCode"]],
                "email": person_data["email"] if "email" in person_data else "",
                "tel": person_data["tel"] if "tel" in person_data else "",
                "remark": person_data["remark"] if "remark" in person_data else "",
                "source": "0",
                "facePictures": person_data["facePictures"],
            },
            "extensionInfo": {
                "idType": "6",
                "nationalityId": "9999",
            },
            "authenticationInfo": {
                "startTime": "1767225600",
                "endTime": "2019686400",
            },
            "accessInfo": {"accessType": "0"},
            "faceComparisonInfo": {
                "enableFaceComparisonGroup": "1",
                "faceComparisonGroupId": "1",
            },
            "entranceInfo": {},
        }
        resp = requests.put(
            url="https://" + dss_api_url + f"/obms/api/v1.1/acs/person/{person_data['personId']}",
            headers={"X-Subject-Token": token, "Content-Type": "application/json"},
            data=json.dumps(payload),
            verify=False,
        ).json()
        return resp
    
    def api_person_delete(self, token, personIds):
        payload = {
            "personIds": personIds,
        }
        resp = requests.post(
            url="https://" + dss_api_url + "/obms/api/v1.1/acs/person-group/person/delete/batch",
            headers={"X-Subject-Token": token, "Content-Type": "application/json"},
            data=json.dumps(payload),
            verify=False,
        ).json()
        return resp

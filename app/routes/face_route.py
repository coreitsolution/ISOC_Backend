import logging
import time
from flask import Blueprint, jsonify, request
from utils.utils import Utils
from api.api_face import APIFace

face_route = Blueprint("face_route", __name__)
utils = Utils()
api_face = APIFace()


@face_route.route("/dss/api/v1/face/search/image", methods=["POST"])
def api_dss_face_search():
    resp = utils.get_token()
    token = resp["token"]
    credential = resp["credential"]
    req = request.json
    req_key = [
        "analyseMode",
        "beginTime",
        "endTime",
        "similarity",
        "faceImageData",
        "channelIds",
    ]
    not_in_keys = utils.key_validation(req, req_key)
    if not_in_keys:
        return jsonify({"error": f"missing keys: {', '.join(not_in_keys)}"}), 400
    face_image_data = req["faceImageData"]
    if utils.is_valid_base64_image(face_image_data):
        logging.info("api_search_face_start called")
        face_search_resp = api_face.api_search_face_start(
            token,
            face_image_data,
            req["beginTime"],
            req["endTime"],
            req["similarity"],
            req["analyseMode"],
            req["channelIds"],
        )
        if face_search_resp["desc"] != "Success":
            return jsonify(face_search_resp), 500
        session = face_search_resp["data"]["session"]
        time.sleep(5)
        logging.info("api_search_face_stop called")
        api_face.api_search_face_stop(token, session)
        time.sleep(1)
        logging.info("api_search_face_session called")
        face_search_session_resp = api_face.api_search_face_session(token, session)
        data = face_search_session_resp["data"]["pageData"]
        result = []
        if len(data) > 0:
            for item in data:
                device_code = item["channelId"].split("$")[0]
                urls = [
                    {
                        "id": item["id"],
                        "type": "1",
                        "url": item["faceImageUrl"],
                    },
                    {
                        "id": item["id"],
                        "type": "2",
                        "url": item["pictureUrl"],
                    },
                ]
                face_search_download_resp = api_face.api_search_face_download_image(
                    token, session, device_code, urls
                )
                download_results = face_search_download_resp["data"]["results"]
                face_base64 = ""
                picture_base64 = ""
                for download_item in download_results:
                    if download_item["type"] == "1":
                        face_base64 = utils.image_url_to_base64(
                            download_item["url"] + "?token=" + credential
                        )
                    elif download_item["type"] == "2":
                        picture_base64 = utils.image_url_to_base64(
                            download_item["url"] + "?token=" + credential
                        )
                result.append(
                    {
                        "id": item["id"],
                        "eventCode": item["eventCode"],
                        "channelId": item["channelId"],
                        "channelName": item["channelName"],
                        "recordSource": item["recordSource"],
                        "faceImageUrl": item["faceImageUrl"],
                        "faceBase64": face_base64,
                        "pictureUrl": item["pictureUrl"],
                        "pictureBase64": picture_base64,
                        "captureTime": item["captureTime"],
                        "similarity": item["similarity"],
                        "personId": item["personId"],
                        "personName": item["personName"],
                        "personSimilarity": item["personSimilarity"],
                        "age": item["age"],
                        "gender": item["gender"],
                    }
                )
        return (
            jsonify(
                {
                    "code": face_search_session_resp["code"],
                    "message": face_search_session_resp["desc"],
                    "data": result,
                }
            ),
            200,
        )
    else:
        return jsonify({"error": "faceImageData base64 is invalid"}), 400


@face_route.route("/dss/api/v1/face/search/feature", methods=["POST"])
def api_face_search():
    resp = utils.get_token()
    token = resp["token"]
    credential = resp["credential"]
    req = request.json
    not_in_keys = []
    req_key = ["beginTime", "endTime", "page", "pageSize", "currentPage", "channelIds"]
    not_in_keys = utils.key_validation(req, req_key)
    if not_in_keys:
        return jsonify({"error": f"missing keys: {', '.join(not_in_keys)}"}), 400

    face_search_resp = api_face.api_search_face_feature(
        token,
        req["beginTime"],
        req["endTime"],
        req["page"],
        req["pageSize"],
        req["currentPage"],
        req["channelIds"],
    )
    if face_search_resp["desc"] != "Success":
        return jsonify(face_search_resp), 500
    data = face_search_resp["data"]["pageData"]
    result = []
    if len(data) > 0:
        for item in data:
            face_base64 = ""
            picture_base64 = ""
            face_base64 = utils.image_url_to_base64(
                item["faceImageUrl"] + "?token=" + credential
            )
            picture_base64 = utils.image_url_to_base64(
                item["pictureUrl"] + "?token=" + credential
            )
            result.append(
                {
                    "id": item["id"],
                    "channelId": item["channelId"],
                    "channelName": item["channelName"],
                    "recordSource": item["recordSource"],
                    "faceImageUrl": item["faceImageUrl"],
                    "faceBase64": face_base64,
                    "pictureUrl": item["pictureUrl"],
                    "pictureBase64": picture_base64,
                    "captureTime": item["captureTime"],
                    "personId": item["personId"],
                    "personName": item["personName"],
                    "personSimilarity": item["personSimilarity"],
                    "age": item["age"],
                    "gender": item["gender"],
                }
            )
    return (
        jsonify(
            {
                "code": face_search_resp["code"],
                "message": face_search_resp["desc"],
                "totalCount": face_search_resp["data"]["totalCount"],
                "data": result,
            }
        ),
        200,
    )


@face_route.route("/dss/api/v1/face/search/stop", methods=["POST"])
def api_face_search_stop():
    resp = utils.get_token()
    token = resp["token"]
    req = request.json
    if "session_id" not in req:
        return jsonify({"error": "Missing session_id"}), 400
    session_id = req["session_id"]
    face_search_stop_resp = api_face.api_search_face_stop(token, session_id)
    return jsonify(face_search_stop_resp)


@face_route.route("/dss/api/v1/face/search/session", methods=["POST"])
def api_face_search_session():
    resp = utils.get_token()
    token = resp["token"]
    req = request.json
    req_key = ["session_id"]
    not_in_keys = utils.key_validation(req, req_key)
    if not_in_keys:
        return jsonify({"error": f"missing keys: {', '.join(not_in_keys)}"}), 400
    session_id = req["session_id"]
    face_search_session_resp = api_face.api_search_face_session(token, session_id)
    return jsonify(face_search_session_resp)


@face_route.route("/dss/api/v1/face/search/download", methods=["POST"])
def api_face_search_download():
    resp = utils.get_token()
    token = resp["token"]
    credential = resp["credential"]
    req = request.json
    req_key = ["session_id", "device_code", "urls"]
    not_in_keys = utils.key_validation(req, req_key)
    if not_in_keys:
        return jsonify({"error": f"missing keys: {', '.join(not_in_keys)}"}), 400
    session_id = req["session_id"]
    device_code = req["device_code"]
    urls = req["urls"]
    face_search_download_resp = api_face.api_search_face_download_image(
        token, session_id, device_code, urls
    )
    logging.info(f"face_search_download_resp: {face_search_download_resp}")
    results = face_search_download_resp["data"]["results"]
    results_new = []
    for result in results:
        url = result["url"] + "?token=" + credential
        results_new.append(
            {
                "id": result["id"],
                "type": result["type"],
                "url": url,
            }
        )
    face_search_download_resp["data"]["results"] = results_new
    return jsonify(face_search_download_resp)


@face_route.route("/dss/api/v1/face/search/feature/test", methods=["POST"])
def api_face_search():
    resp = utils.get_token()
    token = resp["token"]
    credential = resp["credential"]
    req = request.json
    not_in_keys = []
    req_key = ["beginTime", "endTime", "page", "pageSize", "currentPage", "channelIds"]
    not_in_keys = utils.key_validation(req, req_key)
    if not_in_keys:
        return jsonify({"error": f"missing keys: {', '.join(not_in_keys)}"}), 400

    face_search_resp = api_face.api_search_face_feature(
        token,
        req["beginTime"],
        req["endTime"],
        req["page"],
        req["pageSize"],
        req["currentPage"],
        req["channelIds"],
    )
    if face_search_resp["desc"] != "Success":
        return jsonify(face_search_resp), 500
    data = face_search_resp["data"]["pageData"]
    result = []
    for item in data:
        result.append(
            {
                "id": item["id"],
            }
        )
    return jsonify(
        {
            "code": face_search_resp["code"],
            "message": face_search_resp["desc"],
            "totalCount": face_search_resp["data"]["totalCount"],
            "data": result,
        }
    ), 200
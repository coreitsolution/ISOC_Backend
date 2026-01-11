import os
import logging
import time
from flask import Flask, jsonify, request
from flask_cors import CORS

# from db import db
import base64
from PIL import Image
from io import BytesIO
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from dotenv import load_dotenv
from sqlalchemy import null
from dss_auth import DSSAuth
from api.api_group import APIGroup
from api.api_face import APIFace
from api.api_device import APIDevice
from api.api_person import APIPerson
from models.mq_logs_model import MqLogsModel
from utils.ulits import Utils

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# db.init_app(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

dss_auth = DSSAuth()
api_group = APIGroup()
api_face = APIFace()
api_device = APIDevice()
api_person = APIPerson()
utils = Utils()

# with app.app_context():
#     # db.drop_all()
#     db.create_all()


def is_valid_base64_image(base64_string):
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        image.verify()
        return True
    except (ValueError, Exception):
        return False


def get_token():
    key = RSA.generate(2048)
    public_key = (
        key.publickey()
        .export_key()
        .decode("utf-8")
        .replace("-----BEGIN PUBLIC KEY-----", "")
        .replace("-----END PUBLIC KEY-----", "")
        .replace("\n", "")
    )
    first_authentication_resp = dss_auth.first_authentication()
    signature = dss_auth.get_signature(
        first_authentication_resp["realm"], first_authentication_resp["randomKey"]
    )
    signature = dss_auth.get_signature(
        first_authentication_resp["realm"], first_authentication_resp["randomKey"]
    )
    second_authentication_resp = dss_auth.second_authentication(
        signature, first_authentication_resp["randomKey"], public_key
    )
    return second_authentication_resp


@app.route("/")
def index():
    return ""


@app.route("/dss/api/v1/auth/token", methods=["POST"])
def auth_token():
    resp = get_token()
    token = resp["token"]
    return jsonify(
        {
            "token": token,
        }
    )


@app.route("/dss/api/v1/auth/alive", methods=["POST"])
def auth_alive():
    req = request.json
    if "token" not in req:
        return jsonify({"error": "Missing token"}), 400
    token = req["token"]
    alive_resp = dss_auth.keep_alive(token)
    if "code" not in alive_resp:
        return jsonify({"error": "Invalid token"}), 500
    return jsonify(alive_resp)


@app.route("/dss/api/v1/auth/refresh", methods=["POST"])
def auth_refresh():
    req = request.json
    if "token" not in req:
        return jsonify({"error": "Missing token"}), 400
    token = req["token"]
    refresh_resp = dss_auth.update_token(token)
    if "code" not in refresh_resp:
        return jsonify({"error": "Invalid token"}), 500
    return jsonify(refresh_resp)


@app.route("/dss/api/v1/group/list", methods=["GET"])
def api_group_list():
    resp = get_token()
    token = resp["token"]
    group_list_resp = api_group.api_group_list(token)
    return jsonify(group_list_resp)


@app.route("/dss/api/v1/face/search", methods=["POST"])
def api_face_search():
    resp = get_token()
    token = resp["token"]
    req = request.json
    not_in_keys = []
    req_key = [
        "analyseMode",
        "beginTime",
        "endTime",
        "similarity",
        "faceImageData",
        "channelIds",
    ]
    not_in_keys = []
    for key in req_key:
        if key not in req:
            not_in_keys.append(key)
    if not_in_keys:
        return jsonify({"error": f"missing keys: {', '.join(not_in_keys)}"}), 400
    face_image_data = req["faceImageData"]
    if is_valid_base64_image(face_image_data):
        face_search_resp = api_face.api_search_face_start(
            token,
            face_image_data,
            req["beginTime"],
            req["endTime"],
            req["similarity"],
            req["analyseMode"],
            req["channelIds"],
        )
        return face_search_resp
    else:
        return jsonify({"error": "faceImageData base64 is invalid"}), 400


@app.route("/dss/api/v1/face/search/stop", methods=["POST"])
def api_face_search_stop():
    resp = get_token()
    token = resp["token"]
    req = request.json
    if "session_id" not in req:
        return jsonify({"error": "Missing session_id"}), 400
    session_id = req["session_id"]
    face_search_stop_resp = api_face.api_search_face_stop(token, session_id)
    return jsonify(face_search_stop_resp)


@app.route("/dss/api/v1/face/search/session", methods=["POST"])
def api_face_search_session():
    resp = get_token()
    token = resp["token"]
    req = request.json
    if "session_id" not in req:
        return jsonify({"error": "Missing session_id"}), 400
    session_id = req["session_id"]
    face_search_session_resp = api_face.api_search_face_session(token, session_id)
    return jsonify(face_search_session_resp)


@app.route("/dss/api/v1/face/search/download", methods=["POST"])
def api_face_search_download():
    resp = get_token()
    # logging.info(f"response: {resp}")
    token = resp["token"]
    credential = resp["credential"]
    req = request.json
    if "session_id" not in req:
        return jsonify({"error": "Missing session_id"}), 400
    if "device_code" not in req:
        return jsonify({"error": "Missing device_code"}), 400
    if "urls" not in req:
        return jsonify({"error": "Missing urls"}), 400
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


@app.route("/dss/api/v1/device/get", methods=["GET"])
def api_device_tree():
    resp = get_token()
    token = resp["token"]
    device_tree_resp = api_device.api_get_device_tree(token)
    return jsonify(device_tree_resp)


@app.route("/dss/api/v1/device/info/<device_id>", methods=["GET"])
def api_device_info(device_id):
    resp = get_token()
    token = resp["token"]
    device_info_resp = api_device.api_get_device_info(token, device_id)
    return jsonify(device_info_resp)


@app.route("/dss/api/v1/person/list", methods=["GET"])
def api_person_list():
    resp = get_token()
    token = resp["token"]
    person_list_resp = api_person.api_person_list(token)
    return jsonify(person_list_resp)


@app.route("/dss/api/v1/person/detail/<person_id>", methods=["GET"])
def api_person_detail(person_id):
    resp = get_token()
    token = resp["token"]
    person_detail_resp = api_person.api_person_detail(token, person_id)
    return jsonify(person_detail_resp)


@app.route("/dss/api/v1/face/search_by_image", methods=["POST"])
def api_dss_face_search():
    resp = get_token()
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
    not_in_keys = []
    for key in req_key:
        if key not in req:
            not_in_keys.append(key)
    if not_in_keys:
        return jsonify({"error": f"missing keys: {', '.join(not_in_keys)}"}), 400
    face_image_data = req["faceImageData"]
    if is_valid_base64_image(face_image_data):
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
                logging.info(f"face_search_download_resp: {face_search_download_resp}")
                download_results = face_search_download_resp["data"]["results"]
                face_base64 = ""
                face_url = ""
                picture_base64 = ""
                picture_url = ""
                for download_item in download_results:
                    logging.info(download_item["url"] + "?token=" + credential)
                    if download_item["type"] == "1":
                        face_url = download_item["url"] + "?token=" + credential
                        # face_base64 = utils.image_url_to_base64(
                        #     download_item["url"] + "?token=" + credential
                        # )
                    elif download_item["type"] == "2":
                        picture_url = download_item["url"] + "?token=" + credential
                        # picture_base64 = utils.image_url_to_base64(
                        #     download_item["url"] + "?token=" + credential
                        # )
                result.append(
                    {
                        "id": item["id"],
                        "eventCode": item["eventCode"],
                        "channelId": item["channelId"],
                        "channelName": item["channelName"],
                        "recordSource": item["recordSource"],
                        "faceImageUrl": face_url,
                        "faceBase64": face_base64,
                        "pictureUrl": picture_url,
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3333, debug=os.getenv("DEBUG"), use_reloader=False)

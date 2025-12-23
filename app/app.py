import json
import os
import logging
import ssl
import certifi
from flask import Flask, jsonify, request
from flask_cors import CORS
from db import db
import base64
from PIL import Image
from io import BytesIO
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from dss_auth import DSSAuth
from api.api_group import APIGroup
from api.api_face import APIFace
from api.api_device import APIDevice

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

db.init_app(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# app.config["MQTT_BROKER_URL"] = os.getenv("MQTT_BROKER_URL")
# app.config["MQTT_BROKER_PORT"] = int(os.getenv("MQTT_BROKER_PORT", 1883))
# app.config["MQTT_USERNAME"] = os.getenv("MQTT_USERNAME")
# app.config["MQTT_KEEPALIVE"] = int(os.getenv("MQTT_KEEPALIVE", 60))
# app.config["MQTT_TLS_ENABLED"] = os.getenv("MQTT_TLS_ENABLED") == "True"

dssAuth = DSSAuth()
apiGreoup = APIGroup()
apiFace = APIFace()
apiDevice = APIDevice()

with app.app_context():
    # db.drop_all()
    db.create_all()


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
    first_authentication_resp = dssAuth.first_authentication()
    signature = dssAuth.get_signature(
        first_authentication_resp["realm"], first_authentication_resp["randomKey"]
    )
    signature = dssAuth.get_signature(
        first_authentication_resp["realm"], first_authentication_resp["randomKey"]
    )
    second_authentication_resp = dssAuth.second_authentication(
        signature, first_authentication_resp["randomKey"], public_key
    )
    return second_authentication_resp


@app.route("/")
def index():
    return "ISOC Backend is running."


@app.route("/isoc/api/v1/auth/token", methods=["POST"])
def auth_token():
    resp = get_token()
    token = resp["token"]
    return jsonify(
        {
            "token": token,
        }
    )


@app.route("/isoc/api/v1/auth/alive", methods=["POST"])
def auth_alive():
    req = request.json
    if "token" not in req:
        return jsonify({"error": "Missing token"}), 400
    token = req["token"]
    alive_resp = dssAuth.keep_alive(token)
    if "code" not in alive_resp:
        return jsonify({"error": "Invalid token"}), 500
    return jsonify(alive_resp)


@app.route("/isoc/api/v1/auth/refresh", methods=["POST"])
def auth_refresh():
    req = request.json
    if "token" not in req:
        return jsonify({"error": "Missing token"}), 400
    token = req["token"]
    refresh_resp = dssAuth.update_token(token)
    if "code" not in refresh_resp:
        return jsonify({"error": "Invalid token"}), 500
    return jsonify(refresh_resp)


@app.route("/isoc/api/v1/group/list", methods=["GET"])
def api_group_list():
    resp = get_token()
    token = resp["token"]
    group_list_resp = APIGroup.api_group_list(token)
    return jsonify(group_list_resp)


@app.route("/isoc/api/v1/face/search", methods=["POST"])
def api_face_search():
    resp = get_token()
    token = resp["token"]
    req = request.json
    not_in_keys = []
    if "image_base64" not in req:
        not_in_keys.append("image_base64")
    if "begin_time" not in req:
        not_in_keys.append("begin_time")
    if "end_time" not in req:
        not_in_keys.append("end_time")
    if "similarity" not in req:
        not_in_keys.append("similarity")
    if "analyse_mode" not in req:
        not_in_keys.append("analyse_mode")
    if not_in_keys:
        return jsonify({"error": f"Missing keys: {', '.join(not_in_keys)}"}), 400
    imageData = req["image_base64"]
    if is_valid_base64_image(imageData):
        face_search_resp = APIFace.api_search_face_start(token, imageData, req["begin_time"], req["end_time"], req["similarity"], req["analyse_mode"])
        return face_search_resp
    else:
        return jsonify({"error": "image base64 is invalid"}), 400


@app.route("/isoc/api/v1/face/search/stop", methods=["POST"])
def api_face_search_stop():
    resp = get_token()
    token = resp["token"]
    req = request.json
    if "session_id" not in req:
        return jsonify({"error": "Missing session_id"}), 400
    session_id = req["session_id"]
    face_search_stop_resp = APIFace.api_search_face_stop(token, session_id)
    return jsonify(face_search_stop_resp)


@app.route("/isoc/api/v1/face/search/session", methods=["POST"])
def api_face_search_session():
    resp = get_token()
    token = resp["token"]
    req = request.json
    if "session_id" not in req:
        return jsonify({"error": "Missing session_id"}), 400
    session_id = req["session_id"]
    face_search_session_resp = APIFace.api_search_face_session(token, session_id)
    return jsonify(face_search_session_resp)


@app.route("/isoc/api/v1/face/search/download", methods=["POST"])
def api_face_search_download():
    resp = get_token()
    token = resp["token"]
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
    face_search_download_resp = APIFace.api_search_face_download_image(
        token, session_id, device_code, urls
    )
    return jsonify(face_search_download_resp)


@app.route("/isoc/api/v1/device/get", methods=["GET"])
def api_device_tree():
    resp = get_token()
    token = resp["token"]
    device_tree_resp = APIDevice.api_get_device_tree(token)
    return jsonify(device_tree_resp)


@app.route("/isoc/api/v1/device/info/<device_id>", methods=["GET"])
def api_device_info(device_id):
    resp = get_token()
    token = resp["token"]
    device_info_resp = APIDevice.api_get_device_info(token, device_id)
    return jsonify(device_info_resp)


################################# MQTT Section #################################

def on_connect(client, userdata, flags, reason_code):
        if reason_code == 0:
            print("Connected to MQTT Broker!")
            client.subscribe("your/topic")
        else:
            print(f"Failed to connect, return code {reason_code}")


def on_message(client, userdata, msg):
        payload_json = msg.payload.decode('utf-8')
        json_data = json.loads(payload_json)
        print(f"json_data: {json_data['info']}")

def on_subscribe(mqttc, obj, mid, reason_code_list):
    print("Subscribed: " + str(mid) + " " + str(reason_code_list))
    
def on_error(headers, message):
    print('received an error "%s"' % message)
    
def dss_mqtt():
    mqtt_pass, data = dssAuth.get_dss_mq_password()
    userId = "001"
    topic = "mq/alarm/msg/topic/" + userId
    topic_event = "mq/event/msg/topic/" + userId
    topic_publish = "mq/common/msg/topic"
    topic_group = "mq/alarm/msg/group/topic/" + userId
    mq_username = "consumer"
    broker_address = os.getenv("MQTT_BROKER_URL")
    broker_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
    client = mqtt.Client(protocol=mqtt.MQTTv31)
    client.username_pw_set(mq_username, mqtt_pass)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_log = on_error
    client.tls_set(certifi.where(), cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
    client.connect(broker_address, broker_port, 60)
    logging.info("Connecting to MQTT Broker...")
    client.subscribe(topic)
    client.subscribe(topic_event)
    client.subscribe(topic_publish)
    client.subscribe(topic_group)
    client.loop_start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info("Disconnecting from MQTT Broker...")
        client.loop_stop()
        client.disconnect()

################################### End of MQTT Section ###############################


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3333, debug=os.getenv("DEBUG"), use_reloader=False)
    dss_mqtt()
import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mqtt import Mqtt
from db import db
import base64
from PIL import Image
from io import BytesIO
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from binascii import unhexlify
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
import paho.mqtt.client as mqtt
from flask_socketio import SocketIO
from dotenv import load_dotenv
from dss_auth import DSSAuth
from api.api_group import APIGroup
from api.api_face import APIFace

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

db.init_app(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config["MQTT_BROKER_URL"] = os.getenv("MQTT_BROKER_URL")
app.config["MQTT_BROKER_PORT"] = int(os.getenv("MQTT_BROKER_PORT", 1883))
app.config["MQTT_USERNAME"] = os.getenv("MQTT_USERNAME")
app.config["MQTT_KEEPALIVE"] = int(os.getenv("MQTT_KEEPALIVE", 60))
app.config["MQTT_TLS_ENABLED"] = os.getenv("MQTT_TLS_ENABLED") == "True"
# mqtt = Mqtt(app)
# socketio = SocketIO(app)

dssAuth = DSSAuth()
apiGreoup = APIGroup()
apiFace = APIFace()

with app.app_context():
    # db.drop_all()
    db.create_all()


# @mqtt.on_connect()
# def handle_connect(client, userdata, flags, rc):
#     dss_mq_password, _ = dssAuth.get_dss_mq_password()
#     logging.INFO("DSS MQTT Password: %s", dss_mq_password)
#     if rc == 0:
#         app.logger.info("Connected to MQTT Broker!")
#     else:
#         app.logger.error("Failed to connect, return code %d\n", rc)


# @mqtt.on_message()
# def handle_mqtt_message(client, userdata, message):
#     app.logger.info(
#         "Received MQTT message on topic %s: %s", message.topic, message.payload.decode()
#     )


# @mqtt.on_log()
# def handle_logging(client, userdata, level, buf):
#     print(level, buf)


def is_valid_base64_image(base64_string):
    try:
        # Decode the base64 string
        image_data = base64.b64decode(base64_string)
        # Attempt to open and verify as an image
        image = Image.open(BytesIO(image_data))
        image.verify()  # Checks if it's a valid image without loading fully
        return True
    except (ValueError, Exception):
        # Invalid base64 or not a valid image
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
    if "image_base64" not in req:
        return jsonify({"error": "Missing image_base64"}), 400
    imageData = req["image_base64"]
    if is_valid_base64_image(imageData):
        face_search_resp = APIFace.api_search_face(token, imageData)
        return jsonify(face_search_resp)
    else:
        return jsonify({"error": "image base64 is invalid"}), 400



if __name__ == "__main__":
    # socketio.run(app, host="0.0.0.0", port=3333, debug=os.getenv("DEBUG"), use_reloader=False)
    app.run(host="0.0.0.0", port=3333, debug=os.getenv("DEBUG"), use_reloader=False)

import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_mqtt import Mqtt
from db import db
import base64
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from binascii import unhexlify
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

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
app.config["MQTT_PASSWORD"] = os.getenv("MQTT_PASSWORD")
app.config["MQTT_KEEPALIVE"] = int(os.getenv("MQTT_KEEPALIVE", 60))
app.config["MQTT_TLS_ENABLED"] = os.getenv("MQTT_TLS_ENABLED") == "True"
mqtt = Mqtt(app)

with app.app_context():
    # db.drop_all()
    db.create_all()


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        app.logger.info("Connected to MQTT Broker!")
    else:
        app.logger.error("Failed to connect, return code %d\n", rc)


@mqtt.on_disconnect()
def handle_disconnect(client, userdata, rc):
    app.logger.info("Disconnected from MQTT Broker with return code %d", rc)


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    app.logger.info(
        "Received MQTT message on topic %s: %s", message.topic, message.payload.decode()
    )


@app.route("/")
def index():
    return "ISOC Backend is running."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3333, debug=os.getenv("DEBUG"))

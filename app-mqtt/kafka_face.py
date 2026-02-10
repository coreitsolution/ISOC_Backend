import base64
import json
import os
import time
import logging
from confluent_kafka import Producer
import requests
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from binascii import unhexlify
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
from dotenv import load_dotenv
import hashlib

load_dotenv()
conf = {
    "bootstrap.servers": os.getenv("KAFKA_BOKER_URL", "localhost:9092"),
}
producer = Producer(**conf)

dss_host = os.getenv("DSS_API_URL")
dss_mqtt = os.getenv("MQTT_BROKER_URL", dss_host)
dss_mqtt_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
dss_username = os.getenv("DSS_USERNAME")
dss_password = os.getenv("DSS_PASSWORD")

################################# DSS Authentication #################################


def first_authentication():
    response = requests.post(
        url="https://" + dss_host + "/brms/api/v1.0/accounts/authorize",
        json={"userName": dss_username, "clientType": "WINPC_V2"},
        verify=False,
    ).json()
    return response


def get_signature(realm, randomKey):
    temp1 = hashlib.md5(dss_password.encode("utf-8")).hexdigest()
    temp2 = hashlib.md5(f"{dss_username}{temp1}".encode("utf-8")).hexdigest()
    temp3 = hashlib.md5(temp2.encode("utf-8")).hexdigest()
    temp4 = hashlib.md5(f"{dss_username}:{realm}:{temp3}".encode("utf-8")).hexdigest()
    signature = hashlib.md5(f"{temp4}:{randomKey}".encode("utf-8")).hexdigest()
    return signature


def second_authentication(signature, randomKey, publicKey):
    data = {
        "userName": dss_username,
        "signature": signature,
        "randomKey": randomKey,
        "publicKey": publicKey,
        "encryptType": "MD5",
        "ipAddress": "",
        "clientType": "WINPC_V2",
        "userType": "0",
    }
    response = requests.post(
        url="https://" + dss_host + "/brms/api/v1.0/accounts/authorize",
        json=data,
        verify=False,
    ).json()
    return response


def get_mq_credentials(token):
    response = requests.post(
        url="https://" + dss_host + "/brms/api/v1.0/BRM/Config/GetMqConfig",
        headers={"X-Subject-Token": token},
        json={},
        verify=False,
    ).json()
    return response


def rsa_decrypt(word, private_key):
    sentinel = Random.new().read(256)
    ciphertext_bytes = base64.b64decode(word)
    rsa_private_key = PKCS1_v1_5.new(RSA.import_key(private_key))
    decrypted_text = rsa_private_key.decrypt(ciphertext_bytes, sentinel)
    return decrypted_text


def aes_decrypt(word, secret_key, secret_vector):
    key = secret_key
    iv = secret_vector
    encrypted_hex_word = unhexlify(word)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_word = unpad(cipher.decrypt(encrypted_hex_word), AES.block_size)
    return decrypted_word.decode("utf-8")


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
    first_authentication_resp = first_authentication()
    signature = get_signature(
        first_authentication_resp["realm"], first_authentication_resp["randomKey"]
    )
    signature = get_signature(
        first_authentication_resp["realm"], first_authentication_resp["randomKey"]
    )
    second_authentication_resp = second_authentication(
        signature, first_authentication_resp["randomKey"], public_key
    )
    return second_authentication_resp


def callback(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def image_url_to_base64(image_url):
    try:
        response = requests.get(image_url, verify=False)
        response.raise_for_status()
        image_bytes = response.content
        encoded_image = base64.b64encode(image_bytes)
        base64_string = encoded_image.decode("utf-8")
        return base64_string
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the image: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def main():
    data_test = {
        "info": [
            {
                "alarmCode": "",
                "appearTimes": "0",
                "beginTime": "1766480461",
                "channelId": "1000002$1$0$1",
                "endTime": "1766480461",
                "faceImageUrl": "https://amic-center.local/face_images/W6d3uFYkoVbv4INO-jMni0qDP.jpg",
                "hited": "1",
                "pictureUrl": "https://amic-center.local/face_images/cdILtXm80G0khOWY-H6Kq0c91.jpg",
                "pictureUrlRelativePath": "https://amic-center.local/face_images/cdILtXm80G0khOWY-H6Kq0c91.jpg",
                "recAge": "35",
                "recBeard": "2",
                "recEmotion": "9",
                "recEye": "3",
                "recFringe": "0",
                "recGender": "2",
                "recGlasses": "0",
                "recMask": "2",
                "recMouth": "2",
                "serviceCode": "400101",
                "similarFaces": [],
            }
        ],
        "method": "brms.notifyFaceInfos",
    }
    resp = get_token()
    token = resp["token"]
    credential = resp["credential"]
    while True:
        info = data_test["info"]
        for item in info:
            json_payload = json.dumps(item).encode("utf-8")
            producer.produce(
                os.getenv("KAFKA_DETECT_FACE_TOPIC"), key="", value=json_payload, callback=callback
            )
            producer.flush()
            time.sleep(10)

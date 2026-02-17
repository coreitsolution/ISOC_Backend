import os
import hashlib
import json
import ssl
from time import timezone
import certifi
import certifi
import requests
import base64
import logging
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from binascii import unhexlify
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import Json
import uuid
from datetime import datetime
from confluent_kafka import Producer

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

dss_host = os.getenv("DSS_API_URL")
dss_mqtt = os.getenv("MQTT_BROKER_URL", dss_host)
dss_mqtt_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
dss_username = os.getenv("DSS_USERNAME")
dss_password = os.getenv("DSS_PASSWORD")

userId = ""
userGroupId = ""
client = mqtt.Client()

# kafka_topic_detect_person = "dss.event.detect.person"
# conf = {
#     "bootstrap.servers": os.getenv("KAFKA_BOKER_URL", "localhost:9092"),
# }
# producer = Producer(**conf)

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

################################# PostgreSQL #################################


def get_db_connection():
    """Establish connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "isoc_backend"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            port=os.getenv("DB_PORT", "5432"),
        )
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None


def create_mq_log(topic, message, mq_method):
    """Insert MQTT message log into PostgreSQL database"""
    conn = get_db_connection()
    if conn is None:
        return False

    try:
        with conn.cursor() as cursor:
            mq_logs_id = str(uuid.uuid4())
            created_at = datetime.now()

            insert_query = """
            INSERT INTO mq_logs (mq_logs_id, mq_topic, mq_message, created_at, mq_method)
            VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(insert_query, (mq_logs_id, topic, Json(message), created_at, mq_method))
            conn.commit()

            logging.info(f"Inserted MQ log for topic: {topic}")
            return True

    except Exception as e:
        logging.error(f"Error inserting MQ log: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
        

def create_face_data(face_data, method, credential):
    """ Insert face data into PostgreSQL database"""
    conn = get_db_connection()
    if conn is None:    
        return False
    try:        
        with conn.cursor() as cursor:
            insert_query = """
            INSERT INTO center.face_data (
                alarm_code, channel_id, appear_times, begin_time, end_time,
                age, hited, beard, emotion, eye, fringe, gender, glasses, mask, mount, face_image_url,
                picture_url, service_code, similar_faces, is_watchlist, method
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            isWatchlist = False
            if len(face_data["similarFaces"]) > 0:
                isWatchlist = True
            beginTime = datetime.fromtimestamp(int(face_data["beginTime"])).astimezone()
            endTime = datetime.fromtimestamp(int(face_data["endTime"])).astimezone()
            faceImageUrl = face_data["faceImageUrl"] + "?token=" + credential
            pictureUrl = face_data["pictureUrl"] + "?token=" + credential
            faceImageFile = download_image_from_url(faceImageUrl, "data/face_images")
            pictureImageFile = download_image_from_url(pictureUrl, "data/picture_images")
            cursor.execute(insert_query, (
                face_data["alarmCode"],
                face_data["channelId"],
                face_data["appearTimes"],
                beginTime,
                endTime,
                int(face_data["recAge"]),
                recHited(face_data["hited"]),
                recBeard(face_data["recBeard"]),
                recEmotion(face_data["recEmotion"]),
                recEye(face_data["recEye"]),
                recFringe(face_data["recFringe"]),
                recGender(face_data["recGender"]),
                recGlasses(face_data["recGlasses"]),
                recMask(face_data["recMask"]),
                recMouth(face_data["recMouth"]),
                faceImageFile,
                pictureImageFile,
                face_data["serviceCode"],
                json.dumps(face_data["similarFaces"]),
                isWatchlist,
                method,
            ))
            conn.commit()
            logging.info("Inserted Face Data successfully")
            return True
    except Exception as e:
        logging.error(f"Error inserting Face Data: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
        
        
def download_image_from_url(image_url, destination_dir):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            filename = os.path.basename(image_url.split('?')[0]) 
            file_path = os.path.join(destination_dir, filename)
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            logging.info(f"Image downloaded successfully and saved to: {file_path}")
            return file_path
        else:
            logging.warning(f"Failed to download image. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred during the request: {e}")
        return None
    except IOError as e:
        logging.error(f"An I/O error occurred while saving the file: {e}")
        return None
        
# hited Whether to recognize: 0: Capture; 1: Recognize
def recHited(hited):
    if hited == "1":
        return "Recognize"
    else:
        return "Capture"
        
# recGender Gender: 0: Unrecognized; 1: Male; 2: Female
def recGender(gender):
    if gender == "1":
        return "Male"
    elif gender == "2":
        return "Female"
    else:
        return "Unrecognized"

# recFringe Feature, fringe: 0: No; 1: Yes
def recFringe(fringe):
    if fringe == "1":
        return "Yes"
    else:
        return "No"

# recEye Feature, eye: 1: Unrecognized; 2: Closed; 3: Opened
def recEye(eye):
    if eye == "2":
        return "Closed"
    elif eye == "3":
        return "Opened"
    else:
        return "Unrecognized"

# recMouth Feature, mouth: 1: Unrecognized; 2: Closed; 3: Opened
def recMouth(mouth):
    if mouth == "2":
        return "Closed"
    elif mouth == "3":
        return "Opened"
    else:
        return "Unrecognized"

# recMask Feature, mask: 0: Unknown (SDK); 1: Unrecognized; 2: Without mask; 3: With mask
def recMask(mask):
    if mask == "2":
        return "Without mask"
    elif mask == "3":
        return "With mask"
    else:
        return "Unrecognized"
    
# recBeard Feature, beard: 0: Unknown (SDK); 1: Unrecognized; 2: Without beard; 3: With beard
def recBeard(beard):
    if beard == "2":
        return "Without beard"
    elif beard == "3":
        return "With beard"
    else:
        return "Unrecognized"
    
    
# recGlasses Feature, glasses: 0: No; 1: With glasses; 2: Sunglasses
def recGlasses(glasses):
    if glasses == "1":
        return "With glasses"
    elif glasses == "2":
        return "Sunglasses"
    else:
        return "No"
    
# recEmotion Feature, expressions: 0: Smile; 1: Angry; 2: Sad; 3: Disgusted; 4: Scared; 5: Surprised; 6: Normal; 7: Laugh; 8: Happy; 9: Confused; 10: Scream
def recEmotion(emotion):
    emotion_mapping = {
        "0": "Smile",
        "1": "Angry",
        "2": "Sad",
        "3": "Disgusted",
        "4": "Scared",
        "5": "Surprised",
        "6": "Normal",
        "7": "Laugh",
        "8": "Happy",
        "9": "Confused",
        "10": "Scream"
    }
    return emotion_mapping.get(emotion, "Unrecognized")

################################# DSS MQTT #################################
def on_connect(client, userdata, flags, reason_code):
    if reason_code == 0:
        topic_alarm = "mq/alarm/msg/topic"
        topic_event = "mq/event/msg/topic"
        topic_common = "mq/common/msg/topic"
        # topic_group = "mq/alarm/msg/group/topic/" + userGroupId
        client.subscribe(topic_alarm)
        client.subscribe(topic_event)
        client.subscribe(topic_common)
        # client.subscribe(topic_group)
    else:
        logging.error(f"Failed to connect, return code {reason_code}")


def on_disconnect(client, userdata, rc):
    logging.warning("Disconnected from MQTT Broker.")


def on_message(client, userdata, msg):
    payload_json = msg.payload.decode("utf-8")
    json_data = json.loads(payload_json)
    resp = get_token()
    token = resp["token"]
    credential = resp["credential"]
    logging.info(f"Received MQTT message on topic {msg.topic}")
    logging.info(f"method: {json_data['method']}")
    if "method" in json_data:
        if json_data["method"] == "vms.notifyUserTokenExpiration" or json_data["method"] == "vms.notifyUserOnlineStatus":
            return
        logging.info(f"json_data: {json_data}")
        if json_data["method"] == "brms.notifyAlarms":
            info = json_data["info"]
            for item in info:
                ext_data = json.loads(item["extData"])
                if "faceRecognitionInfo" in ext_data:
                    faceRecognitionInfo = ext_data["faceRecognitionInfo"]
                    personFaceImageBase64 = image_url_to_base64(faceRecognitionInfo["personFaceImageUrl"] + "?token=" + credential)
                    captureFaceImageBase64 = image_url_to_base64(faceRecognitionInfo["captureFaceImageUrl"] + "?token=" + credential)
                    alarmPictureBase64 = image_url_to_base64(item["alarmPicture"] + "?token=" + credential)
                    resp = {
                        "deviceCode": item["deviceCode"],
                        "channelId": item["nodeCode"],
                        "alarmCode": item["alarmCode"],
                        "alarmDate": item["alarmDate"],
                        "personId": faceRecognitionInfo["personId"],
                        "personName": faceRecognitionInfo["personName"],
                        "captureFaceImageBase64": captureFaceImageBase64,
                        "personFaceImageBase64": personFaceImageBase64,
                        "alarmPictureBase64": alarmPictureBase64,
                        "similarity": faceRecognitionInfo["similarity"],
                    }
                    json_payload = json.dumps(resp).encode("utf-8")
                    # producer.produce(
                    #     "dss.event.detect.person", key="", value=json_payload, callback=kafka_callback
                    # )
                    # producer.flush()
                    logging.info("produced successfully to kafka")
        elif json_data["method"] == "brms.notifyFaceInfos":
            logging.info(f"Event data: {json_data}")
            info = json_data["info"]
            for item in info:
                recEmotion = ""
                if "recEmotion"  in item:
                    recEmotion = item["recEmotion"]
                payload = {
                    "alarmCode": item["alarmCode"],
                    "channelId": item["channelId"],
                    "appearTimes": item["appearTimes"],
                    "beginTime": item["beginTime"],
                    "endTime": item["endTime"],
                    "recAge": item["recAge"],
                    "hited": item["hited"],
                    "recBeard": item["recBeard"],
                    "recEmotion": recEmotion,
                    "recEye": item["recEye"],
                    "recFringe": item["recFringe"],
                    "recGender": item["recGender"],
                    "recGlasses": item["recGlasses"],
                    "recMask": item["recMask"],
                    "recMouth": item["recMouth"],
                    "faceImageUrl": item["faceImageUrl"] + "?token=" + credential,
                    "pictureUrl": item["pictureUrl"] + "?token=" + credential,
                    "serviceCode": item["serviceCode"],
                    "similarFaces": item["similarFaces"],
                }
                create_face_data(payload, json_data["method"], credential)
        # create_mq_log(msg.topic, json_data, json_data["method"])


def on_subscribe(mqttc, obj, mid, reason_code_list):
    logging.info("Subscribed: " + str(mid) + " " + str(reason_code_list))
    logging.info("Subscription successful.")


def on_error(headers, message):
    logging.error('received an error "%s"' % message)


################################### kafka #################################
def kafka_callback(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


################################### App Start #################################
if __name__ == "__main__":
    key = RSA.generate(2048)
    private_key = key.export_key().decode("utf-8")
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
    second_authentication_resp = second_authentication(
        signature, first_authentication_resp["randomKey"], public_key
    )
    secret_key = rsa_decrypt(second_authentication_resp["secretKey"], private_key)
    secret_vector = rsa_decrypt(second_authentication_resp["secretVector"], private_key)
    mq_credentials = get_mq_credentials(second_authentication_resp["token"])
    decrypted_pass = aes_decrypt(
        mq_credentials["data"]["password"], secret_key, secret_vector
    )
    userId = second_authentication_resp["userId"]
    # userGroupId = second_authentication_resp['userGroupId']
    # logging.info(f"second_authentication_resp: {second_authentication_resp}")
    # userGroupId = "001004"

    mq_username = mq_credentials["data"]["userName"]
    # logging.info(f"dss_mq_username: {mq_username}")
    # logging.info(f"dss_mq_password: {decrypted_pass}")
    client.username_pw_set(mq_username, decrypted_pass)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_log = on_error
    client.on_disconnect = on_disconnect

    client.tls_set(
        certifi.where(), cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2
    )
    logging.info("Connecting to MQTT Broker...")
    client.connect(dss_mqtt, dss_mqtt_port, 60)
    client.loop_start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Disconnecting from MQTT Broker.")
        client.loop_stop()
        client.disconnect()

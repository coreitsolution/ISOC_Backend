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
from mapping import FaceMapping, HumanMapping, VehicleMapping
# from confluent_kafka import Producer

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

car_brands = []

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

            cursor.execute(
                insert_query, (mq_logs_id, topic, Json(message), created_at, mq_method)
            )
            conn.commit()

            logging.info(f"Inserted MQ log for topic: {topic}")
            return True

    except Exception as e:
        logging.error(f"Error inserting MQ log: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def create_face_data(face_data, method):
    """Insert face data into PostgreSQL database"""
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
            similarFaces = []
            if len(face_data["similarFaces"]) > 0:
                isWatchlist = True
                for face in face_data["similarFaces"]:
                    similarFaces.append(
                        {
                            "personId": face["personId"],
                            "similarity": face["similarity"],
                        }
                    )
            beginTime = datetime.fromtimestamp(int(face_data["beginTime"])).astimezone()
            endTime = datetime.fromtimestamp(int(face_data["endTime"])).astimezone()
            pamars = (
                face_data["alarmCode"],
                face_data["channelId"],
                face_data["appearTimes"],
                beginTime,
                endTime,
                int(face_data["recAge"]),
                FaceMapping.recHited(face_data["hited"]),
                FaceMapping.recBeard(face_data["recBeard"]),
                FaceMapping.recEmotion(face_data["recEmotion"]),
                FaceMapping.recEye(face_data["recEye"]),
                FaceMapping.recFringe(face_data["recFringe"]),
                FaceMapping.recGender(face_data["recGender"]),
                FaceMapping.recGlasses(face_data["recGlasses"]),
                FaceMapping.recMask(face_data["recMask"]),
                FaceMapping.recMouth(face_data["recMouth"]),
                face_data["faceImageUrl"],
                str(face_data["pictureUrl"]),
                str(face_data["serviceCode"]),
                json.dumps(similarFaces),
                isWatchlist,
                method,
            )
            cursor.execute(
                insert_query,
                pamars,
            )
            logging.info(cursor.mogrify(insert_query, pamars).decode("utf-8"))
            conn.commit()
            logging.info("Inserted Face Data successfully")
            return True
    except Exception as e:
        logging.error(f"Error inserting Face Data: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def create_human_detections(human_detections_data, method):
    """Insert human data into PostgreSQL database"""
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        with conn.cursor() as cursor:
            insert_query = """
            INSERT INTO center.human_detections (
                age, gender, capture_time, channel_id, detect_mode, direction, emotion, glasses, hat, hat_type,
                beard, mask, bag, bag_type, coat, coat_color, trousers, trousers_color, face_image_top, face_image_right, face_image_left, face_image_bottom,
                face_image_url, picture_url, human_image_top, human_image_right,
                human_image_left, human_image_bottom, human_image_url, method)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            capture_time = datetime.fromtimestamp(
                int(human_detections_data["captureTime"])
            ).astimezone()
            if human_detections_data["faceImageTop"] == '':
                human_detections_data["faceImageTop"] = "0"
            if human_detections_data["faceImageRight"] == '':
                human_detections_data["faceImageRight"] = "0"
            if human_detections_data["faceImageLeft"] == '':
                human_detections_data["faceImageLeft"] = "0"
            if human_detections_data["faceImageBottom"] == '':
                human_detections_data["faceImageBottom"] = "0"
            pamars = (
                human_detections_data["age"],
                HumanMapping.gender(human_detections_data["gender"]),
                capture_time,
                human_detections_data["channelId"],
                human_detections_data["detectMode"],
                human_detections_data["direction"],
                FaceMapping.recEmotion(human_detections_data["emotion"]),
                FaceMapping.recGlasses(human_detections_data["glasses"]),
                HumanMapping.hat(human_detections_data["hat"]),
                HumanMapping.hatType(human_detections_data["hatType"]),
                FaceMapping.recBeard(human_detections_data["beard"]),
                FaceMapping.recMask(human_detections_data["mask"]),
                HumanMapping.bag(human_detections_data["bag"]),
                HumanMapping.bagType(human_detections_data["bagType"]),
                HumanMapping.clothes(human_detections_data["coat"]),
                HumanMapping.clothesColor(human_detections_data["coatColor"]),
                HumanMapping.trouser(human_detections_data["trousers"]),
                HumanMapping.trouserColors(human_detections_data["trousersColor"]),
                human_detections_data["faceImageTop"],
                human_detections_data["faceImageRight"],
                human_detections_data["faceImageLeft"],
                human_detections_data["faceImageBottom"],
                str(human_detections_data.get("faceImageUrl", "")),
                str(human_detections_data.get("pictureUrl", "")),
                human_detections_data["humanImageTop"],
                human_detections_data["humanImageRight"],
                human_detections_data["humanImageLeft"],
                human_detections_data["humanImageBottom"],
                str(human_detections_data.get("humanImageUrl", "")),
                method,
            )
            cursor.execute(
                insert_query,
                pamars,
            )
            logging.info(cursor.mogrify(insert_query, pamars).decode("utf-8"))
            conn.commit()
            logging.info("Inserted Human Detections Data successfully")
            return True
    except Exception as e:
        logging.error(f"Error inserting Human Detections Data: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def create_vehicle_detections(vehicle_detections_data, method):
    """Insert vehicle data into PostgreSQL database"""
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        with conn.cursor() as cursor:
            insert_query = """
            INSERT INTO center.vehicle_detections (
                capture_time, channel_id, detect_mode, direction, car_brand, car_color, car_type, plate, plate_color,
                face_infos, rider_number, car_image_top, car_image_right, car_image_left, car_image_bottom,
                car_image_url, plate_image_url, vehicle_image_url, picture_url, method) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            capture_time = datetime.fromtimestamp(
                int(vehicle_detections_data["capture_time"])
            ).astimezone()
            if "brms.notifyNonVehicleInfos" in method:
                vehicle_detections_data["plate"] = ""
                vehicle_detections_data["plateColor"] = ""
                vehicle_detections_data["plateImageUrl"] = ""
            else:
                vehicle_detections_data["faceInfos"] = []
            pamars = (
                capture_time,
                vehicle_detections_data["channel_id"],
                vehicle_detections_data["detectMode"],
                vehicle_detections_data["direction"],
                vehicle_detections_data["carBrand"],
                VehicleMapping.carColor(vehicle_detections_data["carColor"]),
                VehicleMapping.carType(vehicle_detections_data["carType"]),
                vehicle_detections_data["plate"],
                VehicleMapping.plateColor(vehicle_detections_data["plateColor"]),
                json.dumps(vehicle_detections_data["faceInfos"]),
                vehicle_detections_data["riderNum"],
                vehicle_detections_data["carImageTop"],
                vehicle_detections_data["carImageRight"],
                vehicle_detections_data["carImageLeft"],
                vehicle_detections_data["carImageBottom"],
                str(vehicle_detections_data["carImageUrl"]),
                str(vehicle_detections_data["plateImageUrl"]),
                str(vehicle_detections_data["vehicleUrl"]),
                str(vehicle_detections_data["pictureUrl"]),
                method,
            )
            cursor.execute(
                insert_query,
                pamars,
            )
            logging.info(cursor.mogrify(insert_query, pamars).decode("utf-8"))
            conn.commit()
            logging.info("Inserted Vehicle Detections Data successfully")
            return True
    except Exception as e:
        logging.error(f"Error inserting Vehicle Detections Data: {e}")
        conn.rollback()
        return False


def replace_ip_in_url(url, new_ip):
    try:
        from urllib.parse import urlparse, urlunparse

        parsed_url = urlparse(url)
        new_netloc = new_ip + ":" + str(parsed_url.port) if parsed_url.port else new_ip
        modified_url = urlunparse(
            (
                parsed_url.scheme,
                new_netloc,
                parsed_url.path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment,
            )
        )
        return modified_url
    except Exception as e:
        logging.error(f"Error replacing IP in URL: {e}")
        return url


def download_image_from_url(image_url, destination_dir):
    try:
        logging.info(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url, verify=False)
        if response.status_code == 200:
            filename = os.path.basename(image_url.split("?")[0])
            file_path = os.path.join(destination_dir, filename)
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            logging.info(f"Image downloaded successfully and saved to: {file_path}")
            return file_path
        else:
            logging.warning(
                f"Failed to download image. Status code: {response.status_code}"
            )
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred during the request: {e}")
        return None
    except IOError as e:
        logging.error(f"An I/O error occurred while saving the file: {e}")
        return None


################################# DSS MQTT #################################
def on_connect(client, userdata, flags, reason_code):
    if reason_code == 0:
        topic_alarm = "mq/alarm/msg/topic/" + userId
        topic_event = "mq/event/msg/topic/" + userId
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
    logging.info(f"Received MQTT message on topic {msg.topic}")
    logging.info(f"method: {json_data['method']}")
    credential = ""
    if "method" in json_data:
        if json_data["method"] == "brms.notifyFaceInfos":
            try:
                resp = get_token()
                credential = resp["credential"]
            except Exception as e:
                logging.error(f"Error getting token: {e}")
                return
            logging.info(f"Event data: {json_data}")
            info = json_data["info"]
            for item in info:
                recEmotion = ""
                if "recEmotion" in item:
                    recEmotion = item["recEmotion"]
                faceImageUrl = (
                    replace_ip_in_url(item["faceImageUrl"], os.getenv("DSS_API_URL"))
                    + "?token="
                    + credential
                )
                pictureUrl = (
                    replace_ip_in_url(item["pictureUrl"], os.getenv("DSS_API_URL"))
                    + "?token="
                    + credential
                )

                faceImageFile = download_image_from_url(
                    faceImageUrl, "data/face_images"
                )
                pictureImageFile = download_image_from_url(
                    pictureUrl, "data/face_images"
                )
                if faceImageFile == None:
                    faceImageFile = ""
                else:
                    faceImageFile = faceImageFile.replace("\\", "/")
                if pictureImageFile == None:
                    pictureImageFile = ""
                else:
                    pictureImageFile = pictureImageFile.replace("\\", "/")
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
                    "faceImageUrl": faceImageFile,
                    "pictureUrl": pictureImageFile,
                    "serviceCode": item["serviceCode"],
                    "similarFaces": item["similarFaces"],
                }
                create_face_data(payload, json_data["method"])
        elif json_data["method"] == "brms.notifyHumanInfos":
            try:
                resp = get_token()
                credential = resp["credential"]
            except Exception as e:
                logging.error(f"Error getting token: {e}")
                return
            logging.info(f"json_data: {json_data}")
            info = json_data["info"]
            for item in info:
                emotion = ""
                if "emotion" in item:
                    emotion = item["emotion"]
                faceImageFile = ""
                pictureImageFile = ""
                humanImageFile = ""
                if item["faceImageUrl"] != "":
                    faceImageUrl = (
                        replace_ip_in_url(
                            item["faceImageUrl"], os.getenv("DSS_API_URL")
                        )
                        + "?token="
                        + credential
                    )
                    faceImageFile = download_image_from_url(
                        faceImageUrl, "data/human_images"
                    )
                if item["pictureUrl"] != "":
                    pictureUrl = (
                        replace_ip_in_url(item["pictureUrl"], os.getenv("DSS_API_URL"))
                        + "?token="
                        + credential
                    )
                    pictureImageFile = download_image_from_url(
                        pictureUrl, "data/human_images"
                    )
                if item["humanImageUrl"] != "":
                    humanImageUrl = (
                        replace_ip_in_url(item["humanImageUrl"], os.getenv("DSS_API_URL"))
                        + "?token="
                        + credential
                    )
                    humanImageFile = download_image_from_url(
                        humanImageUrl, "data/human_images"
                    )
                if faceImageFile == None:
                    faceImageFile = ""
                else:
                    faceImageFile = faceImageFile.replace("\\", "/")
                if pictureImageFile == None:
                    pictureImageFile = ""
                else:
                    pictureImageFile = pictureImageFile.replace("\\", "/")
                human_detections_data = {
                    "age": item["age"],
                    "gender": item["gender"],
                    "captureTime": item["captureTime"],
                    "channelId": item["channelId"],
                    "detectMode": item["detectMode"],
                    "direction": item["direction"],
                    "emotion": item["emotion"],
                    "glasses": item["glasses"],
                    "hat": item["hat"],
                    "hatType": item["hatType"],
                    "beard": item["beard"],
                    "mask": item["mask"],
                    "bag": item["bag"],
                    "bagType": item["bagType"],
                    "coat": item["coat"],
                    "coatColor": item["coatColor"],
                    "trousers": item["trousers"],
                    "trousersColor": item["trousersColor"],
                    "faceImageTop": item["faceImageTop"],
                    "faceImageRight": item["faceImageRight"],
                    "faceImageLeft": item["faceImageLeft"],
                    "faceImageBottom": item["faceImageBottom"],
                    "faceImageUrl": faceImageFile,
                    "pictureUrl": pictureImageFile,
                    "humanImageUrl": humanImageFile,
                    "humanImageBottom": item["humanImageBottom"],
                    "humanImageLeft": item["humanImageLeft"],
                    "humanImageRight": item["humanImageRight"],
                    "humanImageTop": item["humanImageTop"],
                }
                create_human_detections(human_detections_data, json_data["method"])
        elif (
            json_data["method"] == "brms.notifyVehicleInfos"
            or json_data["method"] == "brms.notifyNonVehicleInfos"
        ):
            try:
                resp = get_token()
                credential = resp["credential"]
            except Exception as e:
                logging.error(f"Error getting token: {e}")
                return
            logging.info(f"json_data: {json_data}")
            info = json_data["info"]
            for item in info:
                plateImageFile = ""
                vehicleImageFile = ""
                carImageFile = ""
                pictureImageFile = ""
                faceInfos = []
                riderNum = "0"
                car_brand = ""
                if json_data["method"] == "brms.notifyNonVehicleInfos":
                    if item["carImageUrl"] != "":
                        carImageUrl = (
                            replace_ip_in_url(item["carImageUrl"], os.getenv("DSS_API_URL"))
                            + "?token="
                            + credential
                        )
                        carImageFile = download_image_from_url(
                            carImageUrl, "data/vehicle_images"
                        )
                        faceInfos = item["faceInfos"]
                        riderNum = item["riderNum"]
                else:
                    if item["plateImageUrl"] != "":
                        plateImageUrl = (
                            replace_ip_in_url(
                                item["plateImageUrl"], os.getenv("DSS_API_URL")
                            )
                            + "?token="
                            + credential
                        )
                        plateImageFile = download_image_from_url(
                            plateImageUrl, "data/vehicle_images"
                        )
                    if item["vehicleUrl"] != "":
                        vehicleImageUrl = (
                            replace_ip_in_url(
                                item["vehicleUrl"], os.getenv("DSS_API_URL")
                            )
                            + "?token="
                            + credential
                        )
                        vehicleImageFile = download_image_from_url(
                            vehicleImageUrl, "data/vehicle_images"
                        )
                    result = next((brand for brand in car_brands if brand["code"] == item["carBrand"]), None)
                    if result:
                        car_brand = result["name"]
                if item["pictureUrl"] != "":
                    pictureUrl = (
                        replace_ip_in_url(item["pictureUrl"], os.getenv("DSS_API_URL"))
                        + "?token="
                        + credential
                    )
                    pictureImageFile = download_image_from_url(
                        pictureUrl, "data/vehicle_images"
                    )
                if carImageFile == None:
                    carImageFile = ""
                else:
                    carImageFile = carImageFile.replace("\\", "/")
                if plateImageFile == None:
                    plateImageFile = ""
                else:
                    plateImageFile = plateImageFile.replace("\\", "/")
                if vehicleImageFile == None:
                    vehicleImageFile = ""
                else:
                    vehicleImageFile = vehicleImageFile.replace("\\", "/")
                if pictureImageFile == None:
                    pictureImageFile = ""
                else:
                    pictureImageFile = pictureImageFile.replace("\\", "/")
                vehicle_detections_data = {
                    "capture_time": item["captureTime"],
                    "channel_id": item["channelId"],
                    "detectMode": item["detectMode"],
                    "direction": item["direction"],
                    "carBrand": car_brand,
                    "carColor": VehicleMapping.carColor(item["carColor"]),
                    "carType": VehicleMapping.carType(item["carType"]),
                    "carImageUrl": carImageFile,
                    "plateImageUrl": plateImageFile,
                    "vehicleUrl": vehicleImageFile,
                    "pictureUrl": pictureImageFile,
                    "plate": item["plate"],
                    "plateColor": VehicleMapping.plateColor(item["plateColor"]),
                    "faceInfos": faceInfos,
                    "riderNum": riderNum,
                    "carImageBottom": item["carImageBottom"],
                    "carImageLeft": item["carImageLeft"],
                    "carImageRight": item["carImageRight"],
                    "carImageTop": item["carImageTop"],
                }
                create_vehicle_detections(vehicle_detections_data, json_data["method"])
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
    car_brands_data = []
    with open("car_brands.json", "r") as file:
        car_brands_data = json.load(file)

    car_brands = car_brands_data["car_brands"]
        
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
    client.connect(dss_mqtt, dss_mqtt_port, 3600)
    client.loop_start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Disconnecting from MQTT Broker.")
        client.loop_stop()
        client.disconnect()

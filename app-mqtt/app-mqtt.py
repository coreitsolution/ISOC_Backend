import os
import hashlib
import json
import ssl
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

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

dss_host = os.getenv("DSS_API_URL")
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

def insert_mq_log(topic, message):
    """Insert MQTT message log into PostgreSQL database"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cursor:
            mq_logs_id = str(uuid.uuid4())
            created_at = datetime.now()
            
            insert_query = """
            INSERT INTO mq_logs (mq_logs_id, mq_topic, mq_message, created_at)
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (mq_logs_id, topic, Json(message), created_at))
            conn.commit()
            
            logging.info(f"Inserted MQ log for topic: {topic}")
            return True
            
    except Exception as e:
        logging.error(f"Error inserting MQ log: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

################################# DSS MQTT #################################
def on_connect(client, userdata, flags, reason_code):
        if reason_code == 0:
            logging.info("Connected to MQTT Broker!")
            # client.subscribe("your/topic")
        else:
            logging.error(f"Failed to connect, return code {reason_code}")

def on_message(client, userdata, msg):
        payload_json = msg.payload.decode('utf-8')
        json_data = json.loads(payload_json)
        logging.info(f"json_data: {json_data['info']}")
        insert_mq_log(msg.topic, json_data)

def on_subscribe(mqttc, obj, mid, reason_code_list):
    logging.info("Subscribed: " + str(mid) + " " + str(reason_code_list))

def on_error(headers, message):
    logging.error('received an error "%s"' % message)
    
    
################################### App Start #################################
if __name__ == '__main__':
    key = RSA.generate(2048)
    private_key = key.export_key().decode('utf-8')
    public_key = key.publickey().export_key().decode('utf-8').replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").replace("\n", "")
    first_authentication_resp = first_authentication()
    signature = get_signature(first_authentication_resp['realm'], first_authentication_resp['randomKey'])
    second_authentication_resp = second_authentication(signature, first_authentication_resp['randomKey'], public_key)
    secret_key = rsa_decrypt(second_authentication_resp['secretKey'], private_key)
    secret_vector = rsa_decrypt(second_authentication_resp['secretVector'], private_key)
    mq_credentials = get_mq_credentials(second_authentication_resp['token'])
    decrypted_pass = aes_decrypt(mq_credentials['data']['password'], secret_key, secret_vector)
    logging.info(f"dss_mq_password: {decrypted_pass}")
    userId = second_authentication_resp['userId']

    topic = "mq/alarm/msg/topic/" + userId
    topic_event = "mq/event/msg/topic/" + userId
    topic_publish = "mq/common/msg/topic"
    topic_group = "mq/alarm/msg/group/topic/" + userId
    mq_username = mq_credentials['data']['userName']

    client = mqtt.Client()
    client.username_pw_set(mq_username, decrypted_pass)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_log = on_error
    
    client.tls_set(certifi.where(), cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)   
    logging.info("Connecting to MQTT Broker...")

    client.connect(dss_host, dss_mqtt_port, 60)
    logging.info("Connected to MQTT Broker.")
    
    client.subscribe(topic)
    client.subscribe(topic_event)
    client.subscribe(topic_publish)
    client.subscribe(topic_group)
    
    client.loop_start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Disconnecting from MQTT Broker.")
        client.loop_stop()
        client.disconnect()
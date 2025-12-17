import hashlib
import os
import json
import ssl
import uuid
import certifi
import requests
import base64
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from binascii import unhexlify
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
from dotenv import load_dotenv

load_dotenv()

dss_api_url = os.getenv("DSS_API_URL")
dss_username = os.getenv("DSS_USERNAME")
dss_password = os.getenv("DSS_PASSWORD")


def first_authentication():
    response = requests.post(
        url="https://" + dss_api_url + "/brms/api/v1.0/accounts/authorize",
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
        url="https://" + dss_api_url + "/brms/api/v1.0/accounts/authorize",
        json=data,
        verify=False,
    ).json()
    return response


def get_mq_credentials(token):
    response = requests.post(
        url="https://" + dss_api_url + "/brms/api/v1.0/BRM/Config/GetMqConfig",
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

def get_dss_mq_password():
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
    return decrypted_pass, mq_credentials['data']

dss_mq_password, data = get_dss_mq_password()
print(f"dss_mq_password: {dss_mq_password}")
print(f"data: {data}")

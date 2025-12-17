import hashlib
import os
import json
import ssl
import uuid
import certifi
import certifi
import requests
import base64
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from binascii import unhexlify
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES

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

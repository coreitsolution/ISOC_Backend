import hashlib
import os
import json
import ssl
import uuid
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
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

dss_api_url = os.getenv("DSS_API_URL")
dss_username = os.getenv("DSS_USERNAME")
dss_password = os.getenv("DSS_PASSWORD")


class DSSAuth:
    def first_authentication(self):
        resp = requests.post(
            url="https://" + dss_api_url + "/brms/api/v1.0/accounts/authorize",
            json={"userName": dss_username, "clientType": "WINPC_V2"},
            verify=False,
        ).json()
        return resp

    def get_signature(self, realm, randomKey):
        temp1 = hashlib.md5(dss_password.encode("utf-8")).hexdigest()
        temp2 = hashlib.md5(f"{dss_username}{temp1}".encode("utf-8")).hexdigest()
        temp3 = hashlib.md5(temp2.encode("utf-8")).hexdigest()
        temp4 = hashlib.md5(
            f"{dss_username}:{realm}:{temp3}".encode("utf-8")
        ).hexdigest()
        signature = hashlib.md5(f"{temp4}:{randomKey}".encode("utf-8")).hexdigest()
        return signature

    def second_authentication(self, signature, randomKey, publicKey):
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
        resp = requests.post(
            url="https://" + dss_api_url + "/brms/api/v1.0/accounts/authorize",
            json=data,
            verify=False,
        ).json()
        return resp

    def keep_alive(self, token):
        resp = requests.put(
            url="https://" + dss_api_url + "/brms/api/v1.0/accounts/keepalive",
            headers={"X-Subject-Token": token},
            json={token: token},
            verify=False,
        ).json()
        return resp
    
    def update_token(self, token):
        resp = requests.post(
            url="https://" + dss_api_url + "/brms/api/v1.0/accounts/updateToken",
            headers={"X-Subject-Token": token},
            json={},
            verify=False,
        ).json()
        return resp

    def get_mq_credentials(self, token):
        resp = requests.post(
            url="https://" + dss_api_url + "/brms/api/v1.0/BRM/Config/GetMqConfig",
            headers={"X-Subject-Token": token},
            json={},
            verify=False,
        ).json()
        return resp

    def rsa_decrypt(self, word, private_key):
        sentinel = Random.new().read(256)
        ciphertext_bytes = base64.b64decode(word)
        rsa_private_key = PKCS1_v1_5.new(RSA.import_key(private_key))
        decrypted_text = rsa_private_key.decrypt(ciphertext_bytes, sentinel)
        return decrypted_text

    def aes_decrypt(self, word, secret_key, secret_vector):
        key = secret_key
        iv = secret_vector
        encrypted_hex_word = unhexlify(word)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_word = unpad(cipher.decrypt(encrypted_hex_word), AES.block_size)
        return decrypted_word.decode("utf-8")

    def get_dss_mq_password(self):
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
        first_authentication_resp = self.first_authentication()
        signature = self.get_signature(
            first_authentication_resp["realm"], first_authentication_resp["randomKey"]
        )
        second_authentication_resp = self.second_authentication(
            signature, first_authentication_resp["randomKey"], public_key
        )
        secret_key = self.rsa_decrypt(
            second_authentication_resp["secretKey"], private_key
        )
        secret_vector = self.rsa_decrypt(
            second_authentication_resp["secretVector"], private_key
        )
        mq_credentials = self.get_mq_credentials(second_authentication_resp["token"])
        decrypted_pass = self.aes_decrypt(
            mq_credentials["data"]["password"], secret_key, secret_vector
        )
        print(f"dss_mq_password: {decrypted_pass}")
        return decrypted_pass, mq_credentials["data"]


# dss_mq_password, data = get_dss_mq_password()
# print(f"dss_mq_password: {dss_mq_password}")
# print(f"data: {data}")

import base64
from datetime import datetime, timedelta
import requests
import base64
from PIL import Image
from io import BytesIO
from Crypto.PublicKey import RSA
from dss_auth import DSSAuth

dss_auth = DSSAuth()


class Utils:
    def get_token(self):
        key = RSA.generate(2048)
        public_key = (
            key.publickey()
            .export_key()
            .decode("utf-8")
            .replace("-----BEGIN PUBLIC KEY-----", "")
            .replace("-----END PUBLIC KEY-----", "")
            .replace("\n", "")
        )
        first_authentication_resp = dss_auth.first_authentication()
        signature = dss_auth.get_signature(
            first_authentication_resp["realm"], first_authentication_resp["randomKey"]
        )
        signature = dss_auth.get_signature(
            first_authentication_resp["realm"], first_authentication_resp["randomKey"]
        )
        second_authentication_resp = dss_auth.second_authentication(
            signature, first_authentication_resp["randomKey"], public_key
        )
        return second_authentication_resp

    def is_valid_base64_image(self, base64_string):
        try:
            image_data = base64.b64decode(base64_string)
            image = Image.open(BytesIO(image_data))
            image.verify()
            return True
        except (ValueError, Exception):
            return False

    def image_url_to_base64(self, image_url):
        try:
            response = requests.get(image_url, verify=False)
            response.raise_for_status()
            image_bytes = response.content
            content_type = response.headers["content-type"]
            encoded_image = base64.b64encode(image_bytes)
            base64_string = encoded_image.decode("utf-8")
            # data_uri = f"data:{content_type};base64,{base64_string}"
            return base64_string
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the image: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def key_validation(self, req, req_key):
        not_in_keys = []
        for key in req_key:
            if key not in req:
                not_in_keys.append(key)
        return not_in_keys

    def generate_date_list(self, begin_timestamp, end_timestamp):
        begin_date = datetime.fromtimestamp(float(begin_timestamp))
        end_date = datetime.fromtimestamp(float(end_timestamp))
        begin_for_date = begin_date.date()
        end_for_date = end_date.date()
        begin_time = begin_date.time()
        end_time = end_date.time()

        delta = end_for_date - begin_for_date 
        date_list = []
        for i in range(delta.days + 1):
            day = begin_date + timedelta(days=i)
            if i == 0:
                date_list.append({
                    "date": day.strftime("%Y-%m-%d"),
                    "begin_time": begin_time.strftime("%H:%M:%S"),
                    "end_time": "23:59:59",
                    "begin_in_day_timestamp": int(begin_date.timestamp()),
                    "end_in_day_timestamp": int(datetime.combine(begin_for_date, datetime.max.time()).timestamp())
                })
            elif i == delta.days:
                date_list.append({
                    "date": day.strftime("%Y-%m-%d"),
                    "begin_time": "00:00:00",
                    "end_time": end_time.strftime("%H:%M:%S"),
                    "begin_in_day_timestamp": int(datetime.combine(end_for_date, datetime.min.time()).timestamp()),
                    "end_in_day_timestamp": int(end_date.timestamp())
                })
            else:
                date_list.append({
                    "date": day.strftime("%Y-%m-%d"),
                    "begin_time": "00:00:00",
                    "end_time": "23:59:59",
                    "begin_in_day_timestamp": int(datetime.combine(day.date(), datetime.min.time()).timestamp()),
                    "end_in_day_timestamp": int(datetime.combine(day.date(), datetime.max.time()).timestamp())})
        return date_list
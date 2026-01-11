import base64
import requests


class Utils:
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

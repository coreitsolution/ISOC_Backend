import base64
import json
import os
import time
import logging
from confluent_kafka import Producer
import requests
from dotenv import load_dotenv
load_dotenv()
conf = {
    "bootstrap.servers": os.getenv("KAFKA_BOKER_URL", "localhost:9092"),
}
producer = Producer(**conf)


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
    while True:
        base64_image = image_url_to_base64(
            "https://amic-center.local/api-storage/uploads/images/2026-01-30/112028-YyYoQyfm2fm0.jpg"
        )
        resp = {
            "deviceCode": "1000004",
            "channelId": "1000003$1$0$0",
            "alarmCode": "{8C2C8056-D0A7-454B-845B-C566746D3B42}",
            "alarmDate": "1547014708",
            "personId": "8Ujr4N83JuJ2cpjGWLti0fScLdLnn3",
            "personName": "Jack",
            "captureFaceImageBase64": base64_image,
            "personFaceImageBase64": base64_image,
            "similarity": "50",
        }
        json_payload = json.dumps(resp).encode('utf-8')
        producer.produce(
            "dss.event.detect.person", key="", value=json_payload, callback=callback
        )
        producer.flush()
        logging.info(
            "Message sent to Kafka topic. dss.event.detect.person successfully."
        )
        time.sleep(10)


if __name__ == "__main__":
    main()

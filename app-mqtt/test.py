import json
import logging
data = "{\"enableDeviceContact\":\"0\",\"faceRecognitionInfo\":{\"birthday\":\"\",\"captureFaceImageUrl\":\"https://192.168.29.200:443/v1/s/3232243144/9901/1a9b7adb-fce4-11f0-8923-b496913132ed/20260203/1/dsf_730d67f4-00af-11f1-bc88-b496913132ed_14894122_14915989.jpg\",\"gender\":\"0\",\"nationality\":\"9999\",\"personFaceImageUrl\":\"https://192.168.29.200:443/upload/obms/headPic/41487033@1@1770003398502.jpg\",\"personId\":\"41487033\",\"personName\":\"ทดสอบ\",\"personTypeId\":\"\",\"personTypeName\":\"\",\"repositoryId\":\"2\",\"repositoryName\":\"Face Arming\",\"similarity\":\"99\",\"tel\":\"\"}}"

json_data = json.loads(data)
logging.info(f"json_data: {json_data['faceRecognitionInfo']}")
print(json_data)
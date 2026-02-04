import json
import logging

# data = "{\"enableDeviceContact\":\"0\",\"faceRecognitionInfo\":{\"birthday\":\"\",\"captureFaceImageUrl\":\"https://192.168.29.200:443/v1/s/3232243144/9901/1a9b7adb-fce4-11f0-8923-b496913132ed/20260203/1/dsf_730d67f4-00af-11f1-bc88-b496913132ed_14894122_14915989.jpg\",\"gender\":\"0\",\"nationality\":\"9999\",\"personFaceImageUrl\":\"https://192.168.29.200:443/upload/obms/headPic/41487033@1@1770003398502.jpg\",\"personId\":\"41487033\",\"personName\":\"ทดสอบ\",\"personTypeId\":\"\",\"personTypeName\":\"\",\"repositoryId\":\"2\",\"repositoryName\":\"Face Arming\",\"similarity\":\"99\",\"tel\":\"\"}}"

# json_data = json.loads(data)
# logging.info(f"json_data: {json_data['faceRecognitionInfo']}")
# print(json_data)
data_test = {
    "method": "brms.notifyAlarms",
    "info": [
        {
            "deviceCode": "1000012",
            "channelSeq": 0,
            "unitType": 1,
            "unitSeq": 0,
            "nodeType": "2",
            "nodeCode": "1000012$1$0$0",
            "alarmCode": "{06e859d060a243999a574b348ea26646}",
            "alarmStat": "1",
            "alarmType": "100002",
            "alarmGrade": "1",
            "alarmPicture": "https://192.168.29.200:443/v1/s/3232243144/9901/1a9b7adb-fce4-11f0-8923-b496913132ed/20260204/1/dsf_01a23902-016c-11f1-8170-b496913132ed_13002230_13327303.jpg",
            "alarmDate": "1770171272",
            "memo": "",
            "extData": '{"enableDeviceContact": "0","faceRecognitionInfo": {"birthday": "","captureFaceImageUrl": "https://192.168.29.200:443/v1/s/3232243144/9901/1a9b7adb-fce4-11f0-8923-b496913132ed/20260204/1/dsf_01a23902-016c-11f1-8170-b496913132ed_13327303_13365627.jpg","gender": "0","nationality": "9999","personFaceImageUrl": "https://192.168.29.200:443/upload/obms/headPic/jeueRlb5dvxMPRDDLR7qJbAIqmNrbz@1@1769746877236.jpg","personId": "jeueRlb5dvxMPRDDLR7qJbAIqmNrbz","personName": "อธิป ทรการ","personTypeId": "","personTypeName": "","repositoryId": "2","repositoryName": "Face Arming","similarity": "99","tel": ""}}',
            "linkVideoChannels": [],
            "userIds": [],
            "alarmSourceName": "IPC",
            "gpsX": 0.0,
            "gpsY": 0.0,
            "ruleThreshold": 0,
            "stayNumber": 0,
            "planTemplateId": "",
            "deviceName": "NVR-Face-5",
            "linkedOutput": "0",
            "linkedAudioLight": "0",
            "linkedAudio": "0",
            "mapIds": [""],
            "linkedVoicePrompt": "0",
            "voicePromptContent": "",
            "allowViewLinkInfo": "1",
        }
    ],
}
info = data_test["info"]
for item in info:
    ext_data = json.loads(item["extData"])
    faceRecognitionInfo = ext_data["faceRecognitionInfo"]
    print(ext_data)
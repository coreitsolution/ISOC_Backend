class FaceMapping:
    # hited Whether to recognize: 0: Capture; 1: Recognize
    def recHited(hited):
        if hited == "1":
            return "Recognize"
        else:
            return "Capture"


    # recGender Gender: 0: Unrecognized; 1: Male; 2: Female
    def recGender(gender):
        if gender == "1":
            return "Male"
        elif gender == "2":
            return "Female"
        else:
            return "Unrecognized"


    # recFringe Feature, fringe: 0: No; 1: Yes
    def recFringe(fringe):
        if fringe == "1":
            return "Yes"
        else:
            return "No"


    # recEye Feature, eye: 1: Unrecognized; 2: Closed; 3: Opened
    def recEye(eye):
        if eye == "2":
            return "Closed"
        elif eye == "3":
            return "Opened"
        else:
            return "Unrecognized"


    # recMouth Feature, mouth: 1: Unrecognized; 2: Closed; 3: Opened
    def recMouth(mouth):
        if mouth == "2":
            return "Closed"
        elif mouth == "3":
            return "Opened"
        else:
            return "Unrecognized"


    # recMask Feature, mask: 0: Unknown (SDK); 1: Unrecognized; 2: Without mask; 3: With mask
    def recMask(mask):
        if mask == "2":
            return "Without mask"
        elif mask == "3":
            return "With mask"
        else:
            return "Unrecognized"


    # recBeard Feature, beard: 0: Unknown (SDK); 1: Unrecognized; 2: Without beard; 3: With beard
    def recBeard(beard):
        if beard == "2":
            return "Without beard"
        elif beard == "3":
            return "With beard"
        else:
            return "Unrecognized"


    # recGlasses Feature, glasses: 0: No; 1: With glasses; 2: Sunglasses
    def recGlasses(glasses):
        if glasses == "1":
            return "With glasses"
        elif glasses == "2":
            return "Sunglasses"
        else:
            return "No"


    # recEmotion Feature, expressions: 0: Smile; 1: Angry; 2: Sad; 3: Disgusted; 4: Scared; 5: Surprised; 6: Normal; 7: Laugh; 8: Happy; 9: Confused; 10: Scream
    def recEmotion(emotion):
        emotion_mapping = {
            "0": "Smile",
            "1": "Angry",
            "2": "Sad",
            "3": "Disgusted",
            "4": "Scared",
            "5": "Surprised",
            "6": "Normal",
            "7": "Laugh",
            "8": "Happy",
            "9": "Confused",
            "10": "Scream",
        }
        return emotion_mapping.get(emotion, "Unrecognized")
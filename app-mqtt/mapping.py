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


class HumanMapping:
    # Gender, 0 = unknown, 1 = male, 2 = female, empty = all
    def gender(gender):
        if gender == "1":
            return "Male"
        elif gender == "2":
            return "Female"
        else:
            return "Unknown"

    # clothes, 0 = unknown, 1 = long sleeve, 2 = short sleeve, 3 = sleeveless, empty = all
    def clothes(clothes):
        if clothes == "1":
            return "Long sleeve"
        elif clothes == "2":
            return "Short sleeve"
        elif clothes == "3":
            return "Sleeveless"
        else:
            return "Unknown"

    # clothes color, 0 = unknown, 1 = white, 2 = orange, 3 = pink, 4 = black, 5 = red, 6 = yellow, 7 = gray, 8 = blue, 9 = green, 10 = purple, 11 = brown, 12 = silver, 13 = gold, 14 = green, empty = all
    def clothesColor(clothes_color):
        clothes_color_mapping = {
            "0": "Unknown",
            "1": "White",
            "2": "Orange",
            "3": "Pink",
            "4": "Black",
            "5": "Red",
            "6": "Yellow",
            "7": "Gray",
            "8": "Blue",
            "9": "Green",
            "10": "Purple",
            "11": "Brown",
            "12": "Silver",
            "13": "Gold",
        }
        return clothes_color_mapping.get(clothes_color, "Unknown")

    # trouser , 0 = unknown, 1 = pants, 2 = shorts, 3 = skirt, empty = all
    def trouser(trouser):
        if trouser == "1":
            return "Pants"
        elif trouser == "2":
            return "Shorts"
        elif trouser == "3":
            return "Skirt"
        else:
            return "Unknown"

    # trouserColors 0 = unknown, 1 = white, 2 = orange, 3 = pink, 4 = black, 5 = red, 6 = yellow, 7 = gray, 8 = blue, 9 = green, 10 = purple, 11 = brown, 12 = silver, 13 = gold, 14 = green, empty = all
    def trouserColors(trouser_colors):
        trouser_colors_mapping = {
            "0": "Unknown",
            "1": "White",
            "2": "Orange",
            "3": "Pink",
            "4": "Black",
            "5": "Red",
            "6": "Yellow",
            "7": "Gray",
            "8": "Blue",
            "9": "Green",
            "10": "Purple",
            "11": "Brown",
            "12": "Silver",
            "13": "Gold",
        }
        return trouser_colors_mapping.get(trouser_colors, "Unknown")

    # Hat, 0 = unknown, 1 = no, 2 = bands, empty = all
    def hat(hat):
        if hat == "1":
            return "No"
        elif hat == "2":
            return "Bands"
        else:
            return "Unknown"

    # Hat type, 0=unknown, 1=normal hat, 2=helmet, 3=safety helmet, 10=no hat
    def hatType(hat_type):
        if hat_type == "1":
            return "Normal hat"
        elif hat_type == "2":
            return "Helmet"
        elif hat_type == "3":
            return "Safety helmet"
        elif hat_type == "10":
            return "No hat"
        else:
            return "Unknown"

    # bag, 0 = unknown, 1 = no package, 2 = with package, empty = all
    def bag(bag):
        if bag == "1":
            return "No package"
        elif bag == "2":
            return "With package"
        else:
            return "Unknown"

    # Bag type, 0=unknown, 1=handbag, 2=shoulder bag, 3=backpack, 4=trolley case, 5=waist bag, 6=no bag
    def bagType(bag_type):
        if bag_type == "1":
            return "Handbag"
        elif bag_type == "2":
            return "Shoulder bag"
        elif bag_type == "3":
            return "Backpack"
        elif bag_type == "4":
            return "Trolley case"
        elif bag_type == "5":
            return "Waist bag"
        elif bag_type == "6":
            return "No bag"
        else:
            return "Unknown"


class VehicleMapping:
    def plateColor(plate_color):
        plate_color_mapping = {
            "0": "Blue",
            "1": "Yellow",
            "2": "White",
            "3": "Black",
            "4": "Green",
            "5": "Shadow Green",
            "99": "Unrecognized",
            "100": "Other colors",
        }
        return plate_color_mapping.get(plate_color, "Unknown")
    def carType(vehicle_type):
        vehicle_type_mapping = {
            "-1": "Other",
            "0": "Unrecognized",
            "17": "Public Bus",
            "18": "Motorcycle",
            "19": "Bus",
            "20": "Large Truck",
            "21": "Medium Truck",
            "22": "Sedan",
            "23": "Van",
            "24": "Small Truck",
            "26": "Medium Bus",
            "27": "SUV",
            "28": "MPV",
            "29": "Pickup",
            "32": "Mini Sedan",
        }
        return vehicle_type_mapping.get(vehicle_type, "Unknown")

    def carColor(vehicle_color):
        vehicle_color_mapping = {
            "0": "White",
            "1": "Black",
            "2": "Red",
            "3": "Yellow",
            "4": "Gray",
            "5": "Blue",
            "6": "Green",
            "8": "Purple",
            "10": "Pink",
            "11": "Brown",
            "17": "Sliver",
            "21": "Dark Orange",
            "99": "Unrecognized",
            "100": "Other",
        }
        return vehicle_color_mapping.get(vehicle_color, "Unknown")
    
    def nonMotorType(non_motor_type):
        non_motor_type_mapping = {
            "-1": "Other",
            "0": "Unrecognized",
            "1": "Tricycle",
            "4": "Bicycle",
            "14": "Van Cargo Tricycle",
            "15": "Open Tricycle with Passenger",
            "16": "Open Tricycle without Passenger",
        }
        return non_motor_type_mapping.get(non_motor_type, "Unknown")

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from routes.face_route import face_route
from routes.auth_route import auth_route
from routes.group_route import group_route
from routes.device_route import device_route
from routes.person_route import person_route
from api.api_dictionary import APIDictionary
from utils.utils import Utils

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.register_blueprint(face_route)
app.register_blueprint(auth_route)
app.register_blueprint(group_route)
app.register_blueprint(device_route)
app.register_blueprint(person_route)

utils = Utils()
api_dictionary = APIDictionary()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/api/dictionary/car-brands", methods=["GET"])
def get_car_brands():
    resp = utils.get_token()
    token = resp["token"]
    car_brands = api_dictionary.api_get_dictionary_car_brand(token)
    return jsonify(car_brands)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3334, debug=os.getenv("DEBUG"), use_reloader=False)

from flask import Blueprint, jsonify, request
from utils.utils import Utils
from dss_auth import DSSAuth

auth_route = Blueprint("auth_route", __name__)
utils = Utils()
dss_auth = DSSAuth()


@auth_route.route("/dss/api/v1/auth/token", methods=["POST"])
def auth_token():
    resp = utils.get_token()
    token = resp["token"]
    return jsonify(
        {
            "token": token,
        }
    )


@auth_route.route("/dss/api/v1/auth/alive", methods=["POST"])
def auth_alive():
    req = request.json
    if "token" not in req:
        return jsonify({"error": "Missing token"}), 400
    token = req["token"]
    alive_resp = dss_auth.keep_alive(token)
    if "code" not in alive_resp:
        return jsonify({"error": "Invalid token"}), 500
    return jsonify(alive_resp)


@auth_route.route("/dss/api/v1/auth/refresh", methods=["POST"])
def auth_refresh():
    req = request.json
    if "token" not in req:
        return jsonify({"error": "Missing token"}), 400
    token = req["token"]
    refresh_resp = dss_auth.update_token(token)
    if "code" not in refresh_resp:
        return jsonify({"error": "Invalid token"}), 500
    return jsonify(refresh_resp)

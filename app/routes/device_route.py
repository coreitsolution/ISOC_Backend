from flask import Blueprint, app, jsonify, request
from utils.utils import Utils
from api.api_device import APIDevice

device_route = Blueprint("device_route", __name__)
utils = Utils()
api_device = APIDevice()


@device_route.route("/dss/api/v1/device/get", methods=["GET"])
def api_device_tree():
    resp = utils.get_token()
    token = resp["token"]
    device_tree_resp = api_device.api_get_device_tree(token)
    return jsonify(device_tree_resp)


@device_route.route("/dss/api/v1/device/info/<device_id>", methods=["GET"])
def api_device_info(device_id):
    resp = utils.get_token()
    token = resp["token"]
    device_info_resp = api_device.api_get_device_info(token, device_id)
    return jsonify(device_info_resp)

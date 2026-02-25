import logging
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
    camera_devices = []
    if device_tree_resp["desc"] == "Success":
        devices = device_tree_resp["data"]["devices"]
        for device in devices:
            units = device["units"]
            for unit in units:
                channels = unit["channels"]
                for channel in channels:
                    if channel["status"] == "1":
                        camera_devices.append({
                            "channelCode":channel["channelCode"],
                            "channelName": channel["channelName"],
                            "deviceIp": device["deviceIp"],
                            "deviceModelStr": device["deviceModelStr"],
                            "name": device["name"],
                            "orgCode": device["orgCode"],
                            "sn": device["sn"]
                        })
    return jsonify({
        "code": 1000,
        "desc": "Success",
        "data": camera_devices
    })


@device_route.route("/dss/api/v1/device/info/<device_id>", methods=["GET"])
def api_device_info(device_id):
    resp = utils.get_token()
    token = resp["token"]
    device_info_resp = api_device.api_get_device_info(token, device_id)
    return jsonify(device_info_resp)

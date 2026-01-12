from flask import Blueprint, jsonify, request
from utils.utils import Utils
from api.api_group import APIGroup

group_route = Blueprint("group_route", __name__)
utils = Utils()
api_group = APIGroup()


@group_route.route("/dss/api/v1/group/list", methods=["GET"])
def api_group_list():
    resp = utils.get_token()
    token = resp["token"]
    group_list_resp = api_group.api_group_list(token)
    return jsonify(group_list_resp)


@group_route.route("/dss/api/v1/group/add", methods=["POST"])
def api_group_add():
    resp = utils.get_token()
    token = resp["token"]
    req = request.json
    req_key = ["orgName"]
    not_in_keys = utils.key_validation(req, req_key)
    if not_in_keys:
        return jsonify({"error": f"missing keys: {', '.join(not_in_keys)}"}), 400
    data = {
        "orgName": req["orgName"],
    }
    group_add_resp = api_group.api_group_add(token, data)
    return jsonify(group_add_resp)


@group_route.route("/dss/api/v1/group/update", methods=["PUT"])
def api_group_update():
    resp = utils.get_token()
    token = resp["token"]
    req = request.json
    req_key = ["groupId", "orgName"]
    not_in_keys = utils.key_validation(req, req_key)
    if not_in_keys:
        return jsonify({"error": f"missing keys: {', '.join(not_in_keys)}"}), 400
    data = {
        "groupId": req["groupId"],
        "orgName": req["orgName"],
    }
    group_update_resp = api_group.api_group_update(token, data)
    return jsonify(group_update_resp)

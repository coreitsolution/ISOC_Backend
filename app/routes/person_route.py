from flask import Blueprint, app, jsonify, request
from utils.utils import Utils
from api.api_person import APIPerson

person_route = Blueprint("person_route", __name__)
utils = Utils()
api_person = APIPerson()


@person_route.route("/dss/api/v1/person/list", methods=["POST"])
def api_person_list():
    resp = utils.get_token()
    token = resp["token"]
    req = request.json
    req_key = ["page", "pageSize", "orgCode"]
    not_in_keys = utils.key_validation(req, req_key)
    if not_in_keys:
        return jsonify({"error": f"missing keys: {', '.join(not_in_keys)}"}), 400
    person_list_resp = api_person.api_person_list(token, req)
    return jsonify(person_list_resp)


@person_route.route("/dss/api/v1/person/detail/<person_id>", methods=["GET"])
def api_person_detail(person_id):
    resp = utils.get_token()
    token = resp["token"]
    person_detail_resp = api_person.api_person_detail(token, person_id)
    return jsonify(person_detail_resp)


@person_route.route("/dss/api/v1/person/add", methods=["POST"])
def api_person_add():
    resp = utils.get_token()
    token = resp["token"]
    req = request.json
    req_key = ["personId", "firstName", "gender", "orgCode", "facePictures"]
    not_in_keys = utils.key_validation(req, req_key)
    if not_in_keys:
        return jsonify({"error": f"missing keys: {', '.join(not_in_keys)}"}), 400
    if req["facePictures"] == [] or req["facePictures"] is None:
        return (
            jsonify({"error": "facePictures key array base64 string can not be empty"}),
            400,
        )
    if len(req["facePictures"]) > 0:
        not_base64 = []
        for i in range(len(req["facePictures"])):
            if not utils.is_valid_base64_image(req["facePictures"][i]):
                not_base64.append(i)
        if len(not_base64) > 0:
            return (
                jsonify(
                    {
                        "error": f"facePictures index {', '.join(map(str, not_base64))} is not valid base64 image string"
                    }
                ),
                400,
            )
    person_add_resp = api_person.api_person_add(token, req)
    return jsonify(person_add_resp)


@person_route.route("/dss/api/v1/person/update", methods=["PUT"])
def api_person_update():
    resp = utils.get_token()
    token = resp["token"]
    req = request.json
    req_key = ["personId", "firstName", "gender", "orgCode", "facePictures"]
    not_in_keys = utils.key_validation(req, req_key)
    if not_in_keys:
        return jsonify({"error": f"missing keys: {', '.join(not_in_keys)}"}), 400
    if req["facePictures"] == [] or req["facePictures"] is None:
        return (
            jsonify({"error": "facePictures key array base64 string can not be empty"}),
            400,
        )
    if len(req["facePictures"]) > 0:
        not_base64 = []
        for i in range(len(req["facePictures"])):
            if not utils.is_valid_base64_image(req["facePictures"][i]):
                not_base64.append(i)
        if len(not_base64) > 0:
            return (
                jsonify(
                    {
                        "error": f"facePictures index {', '.join(map(str, not_base64))} is not valid base64 image string"
                    }
                ),
                400,
            )
    person_update_resp = api_person.api_person_update(token, req)
    return jsonify(person_update_resp)

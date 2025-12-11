from flask import Blueprint, request, jsonify
import requests
from config import DJANGO_BASE_URL
from decorator.auth_decorator import jwt_required

users_bp = Blueprint("users_bp", __name__)
@users_bp.route("/api/users/", methods=["GET", "POST"])
@jwt_required
def users():
    tenant_id = request.user.get("tenant_id")
    jwt_token = request.headers.get("Authorization")  

    headers = {
        "X-Tenant-ID": tenant_id,
        "Authorization": jwt_token  
    }

    if request.method == "GET":
        try:
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/users/",
                params=dict(request.args),
                headers=headers
            )
            return django_response.json(), django_response.status_code
        except requests.exceptions.RequestException as e:
            return {"message": str(e), "status": "fail", "data": None}, 500

    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return {"message": "Missing JSON body", "status": "fail", "data": None}, 400
        try:
            django_response = requests.post(
                f"{DJANGO_BASE_URL}/users/create/",
                json=data,
                headers=headers
            )
            return django_response.json(), django_response.status_code
        except requests.exceptions.RequestException as e:
            return {"message": str(e), "status": "fail", "data": None}, 500



@users_bp.route("/api/login/", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    tenant_id = data.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tenant_id:
        return jsonify({"error": "Missing tenant_id"}), 400

    headers = {"X-Tenant-ID": tenant_id}
    try:
        django_response = requests.post(
            f"{DJANGO_BASE_URL}/login/",
            json=data,
            headers=headers
        )
        return jsonify(django_response.json()), django_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
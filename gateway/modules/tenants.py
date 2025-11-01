from flask import Blueprint, request, jsonify
import requests
from config import BASE_API

tenants_bp = Blueprint("tenants_bp", __name__)

@tenants_bp.route("/api/tenants/create/", methods=["POST"])
def create_tenant():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    try:
        django_response = requests.post(f"{BASE_API}/create-tenant/", json=data)
        return jsonify(django_response.json()), django_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@tenants_bp.route("/api/tenants/", methods=["GET"])
def list_tenants():
    try:
        django_response = requests.get(f"{BASE_API}/tenants/")
        return jsonify(django_response.json()), django_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@tenants_bp.route("/api/tenants/<int:id>/", methods=["GET", "PUT", "DELETE"])
def tenant_detail(id):
    data = request.get_json(silent=True)
    method = request.method

    try:
        if method == "GET":
            django_response = requests.get(f"{BASE_API}/tenants/{id}/")
        elif method == "PUT":
            django_response = requests.put(f"{BASE_API}/tenants/{id}/update/", json=data)
        elif method == "DELETE":
            django_response = requests.delete(f"{BASE_API}/tenants/{id}/delete/")
        else:
            return jsonify({"error": "Method not allowed"}), 405

        return jsonify(django_response.json()), django_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

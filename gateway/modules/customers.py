from flask import Blueprint, request, jsonify
import requests
from config import BASE_API

customers_bp = Blueprint("customers_bp", __name__)

@customers_bp.route("/api/customers/", methods=["GET", "POST"])
def customers():
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")

    if request.method == "GET":
        if not tenant_id:
            return jsonify({"error": "Missing tenant_id"}), 400
        headers = {"X-Tenant-ID": tenant_id}
        try:
            django_response = requests.get(f"{BASE_API}/", params=dict(request.args), headers=headers)
            return jsonify(django_response.json()), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400
        tenant_id = data.get("tenant_id") or request.headers.get("X-Tenant-ID")
        if not tenant_id:
            return jsonify({"error": "Missing tenant_id"}), 400
        headers = {"X-Tenant-ID": tenant_id}
        try:
            django_response = requests.post(f"{BASE_API}/create/", json=data, headers=headers)
            return jsonify(django_response.json()), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

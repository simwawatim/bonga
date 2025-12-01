from flask import Blueprint, request, jsonify
import requests
from config import DJANGO_BASE_URL

purchase_bp = Blueprint("purchase_bp", __name__)


def safe_json(response):
    try:
        return response.json()
    except ValueError:
        if response.text:
            return {"error": response.text}
        return {"error": "Empty response from server."}


@purchase_bp.route("/api/purchases/", methods=["GET", "POST"])
def purchases():
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")
    headers = {"X-Tenant-ID": tenant_id} if tenant_id else {}

    if request.method == "GET":
        if not tenant_id:
            return jsonify({"error": "Missing tenant_id"}), 400
        try:
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/purchases/",
                params=dict(request.args),
                headers=headers
            )
            return jsonify(safe_json(django_response)), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400
        tenant_id = data.get("tenant_id")
        if not tenant_id:
            return jsonify({"status": "error", "message": "Missing tenant_id in body"}), 400
        headers = {"X-Tenant-ID": tenant_id}

        try:
            django_response = requests.post(
                f"{DJANGO_BASE_URL}/purchases/",
                json=data,
                headers=headers
            )
            return jsonify(safe_json(django_response)), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500


@purchase_bp.route("/api/purchases/<int:purchase_id>/", methods=["GET", "PUT", "DELETE"])
def purchase_by_id(purchase_id):
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tenant_id:
        return jsonify({"error": "Missing tenant_id"}), 400
    headers = {"X-Tenant-ID": tenant_id}

    try:
        if request.method == "GET":
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/purchases/{purchase_id}/", headers=headers
            )
        elif request.method == "PUT":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing JSON body"}), 400
            django_response = requests.put(
                f"{DJANGO_BASE_URL}/purchases/{purchase_id}/", json=data, headers=headers
            )
        elif request.method == "DELETE":
            django_response = requests.delete(
                f"{DJANGO_BASE_URL}/purchases/{purchase_id}/", headers=headers
            )
        else:
            return jsonify({"error": "Method not allowed"}), 405

        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

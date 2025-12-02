from flask import Blueprint, request, jsonify
import requests
from config import DJANGO_BASE_URL

quotation_bp = Blueprint("quotation_bp", __name__)

def safe_json(response):
    """Safely parse response as JSON, fallback to text or error."""
    try:
        return response.json()
    except ValueError:
        if response.text:
            return {"error": response.text}
        return {"error": "Empty response from server."}

@quotation_bp.route("/api/quotation-create/", methods=["POST"])
def quotation_create():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    tenant_id = data.get("tenant_id")
    if not tenant_id:
        return jsonify({
            "status": "error",
            "message": "Missing tenant_id in body"
        }), 400

    headers = {"X-Tenant-ID": tenant_id}

    try:
        django_response = requests.post(
            f"{DJANGO_BASE_URL}/quotation/create/",
            json=data,
            headers=headers
        )
        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500



@quotation_bp.route("/api/quotations/", methods=["GET"])
def quotation_list():
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")

    if not tenant_id:
        return jsonify({"error": "Missing tenant_id"}), 400

    headers = {"X-Tenant-ID": tenant_id}

    try:
        django_response = requests.get(
            f"{DJANGO_BASE_URL}/quotation/list/",
            params=dict(request.args),
            headers=headers
        )
        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500



@quotation_bp.route("/api/quotations/<int:quotation_id>/", methods=["GET"])
def quotation_detail(quotation_id):
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")

    if not tenant_id:
        return jsonify({"error": "Missing tenant_id"}), 400

    headers = {"X-Tenant-ID": tenant_id}

    try:
        django_response = requests.get(
            f"{DJANGO_BASE_URL}/quotation/{quotation_id}/",
            headers=headers
        )
        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

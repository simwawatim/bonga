from flask import Blueprint, request, jsonify
import requests
from config import BASE_API, DJANGO_BASE_URL

suppliers_bp = Blueprint("suppliers_bp", __name__)

def safe_json(response):
    """Safely parse response as JSON, fallback to text or generic error."""
    try:
        return response.json()
    except ValueError:
        if response.text:
            return {"error": response.text}
        return {"error": "Empty response from server."}


@suppliers_bp.route("/api/suppliers/", methods=["GET", "POST"])
def suppliers():
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")
    headers = {"X-Tenant-ID": tenant_id} if tenant_id else {}

    # ------------------- GET ALL SUPPLIERS -------------------
    if request.method == "GET":
        if not tenant_id:
            return jsonify({"error": "Missing tenant_id"}), 400
        try:
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/suppliers/",
                params=dict(request.args),
                headers=headers
            )
            return jsonify(safe_json(django_response)), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

    # ------------------- CREATE NEW SUPPLIER -------------------
    elif request.method == "POST":
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        tenant_id = data.get("tenant_id") or tenant_id
        if not tenant_id:
            return jsonify({"error": "Missing tenant_id in body or headers"}), 400

        headers = {"X-Tenant-ID": tenant_id}

        try:
            django_response = requests.post(
                f"{DJANGO_BASE_URL}/suppliers/",
                json=data,
                headers=headers
            )
            return jsonify(safe_json(django_response)), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500


@suppliers_bp.route("/api/suppliers/<int:supplier_id>/", methods=["GET", "PUT", "DELETE"])
def supplier_by_id(supplier_id):
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tenant_id:
        return jsonify({"error": "Missing tenant_id"}), 400

    headers = {"X-Tenant-ID": tenant_id}

    try:
        if request.method == "GET":
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/suppliers/{supplier_id}/",
                headers=headers
            )

        elif request.method == "PUT":
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"error": "Missing JSON body"}), 400

            django_response = requests.put(
                f"{DJANGO_BASE_URL}/suppliers/{supplier_id}/",
                json=data,
                headers=headers
            )

        elif request.method == "DELETE":
            django_response = requests.delete(
                f"{DJANGO_BASE_URL}/suppliers/{supplier_id}/",
                headers=headers
            )

        else:
            return jsonify({"error": "Method not allowed"}), 405

        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

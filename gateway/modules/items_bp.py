from flask import Blueprint, request, jsonify
import requests
from config import BASE_API, DJANGO_BASE_URL

items_bp = Blueprint("items_bp", __name__)

def safe_json(response):
    """Safely parse response as JSON, fallback to text or error."""
    try:
        return response.json()
    except ValueError:
        if response.text:
            return {"error": response.text}
        return {"error": "Empty response from server."}


@items_bp.route("/api/items/", methods=["GET", "POST"])
def items():
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")
    headers = {"X-Tenant-ID": tenant_id} if tenant_id else {}
    if request.method == "GET":
        if not tenant_id:
            return jsonify({"error": "Missing tenant_id"}), 400
        try:
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/items/",
                params=dict(request.args),
                headers=headers,
            )
            return jsonify(safe_json(django_response)), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 415

        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "status": "error",
                "message": "Missing JSON body"
            }), 400

        tenant_id = data.get("tenant_id")
        if not tenant_id:
            return jsonify({
                "status": "error",
                "message": "Missing tenant_id in body"
            }), 400

        headers = {"X-Tenant-ID": tenant_id}

        try:
            django_response = requests.post(
                f"{DJANGO_BASE_URL}/items/",
                json=data,
                headers=headers,
            )
            return jsonify(safe_json(django_response)), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500


@items_bp.route("/api/items/<int:item_id>/", methods=["GET", "PUT", "DELETE"])
def item_by_id(item_id):
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tenant_id:
        return jsonify({"error": "Missing tenant_id"}), 400
    headers = {"X-Tenant-ID": tenant_id}

    try:

        if request.method == "GET":
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/items/{item_id}/", headers=headers
            )


        elif request.method == "PUT":
            if not request.is_json:
                return jsonify({
                    "status": "error",
                    "message": "Content-Type must be application/json"
                }), 415

            data = request.get_json(silent=True)
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "Missing JSON body"
                }), 400

            django_response = requests.put(
                f"{DJANGO_BASE_URL}/items/{item_id}/",
                json=data,
                headers=headers
            )

        elif request.method == "DELETE":
            django_response = requests.delete(
                f"{DJANGO_BASE_URL}/items/{item_id}/", headers=headers
            )

        else:
            return jsonify({"error": "Method not allowed"}), 405

        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

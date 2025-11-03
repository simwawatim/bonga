from flask import Blueprint, request, jsonify
import requests
from config import BASE_API, DJANGO_BASE_URL

stock_master_bp = Blueprint("stock_master_bp", __name__)


def safe_json(response):
    try:
        return response.json()
    except ValueError:
        if response.text:
            return {"error": response.text}
        return {"error": "Empty response from server."}


def get_tenant_id():
    return request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")


@stock_master_bp.route("/api/stock-master/", methods=["GET", "POST"])
def stockitems():
    try:
        if request.method == "GET":
            tenant_id = get_tenant_id()
            if not tenant_id:
                return jsonify({"error": "Missing tenant_id"}), 400

            headers = {"X-Tenant-ID": tenant_id}
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/stock-masters/",
                params=dict(request.args),
                headers=headers
            )
            return jsonify(safe_json(django_response)), django_response.status_code

        elif request.method == "POST":
            data = request.get_json()

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
            if not data:
                return jsonify({"error": "Missing JSON body"}), 400

            if "tenant_id" not in data:
                data["tenant_id"] = tenant_id

            django_response = requests.post(
                f"{DJANGO_BASE_URL}/stock-masters/",
                json=data,
                headers=headers
            )
            return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request to Django API failed: {str(e)}"}), 500


@stock_master_bp.route("/api/stock-master/<int:stock_id>/", methods=["GET", "PUT", "DELETE"])
def stockitem_by_id(stock_id):
    tenant_id = get_tenant_id()
    if not tenant_id:
        return jsonify({"error": "Missing tenant_id"}), 400

    headers = {"X-Tenant-ID": tenant_id}

    try:
        if request.method == "GET":
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/stock-masters/{stock_id}/",
                headers=headers
            )

        elif request.method == "PUT":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing JSON body"}), 400
            django_response = requests.put(
                f"{DJANGO_BASE_URL}/stock-masters/{stock_id}/",
                json=data,
                headers=headers
            )

        elif request.method == "DELETE":
            django_response = requests.delete(
                f"{DJANGO_BASE_URL}/stock-masters/{stock_id}/",
                headers=headers
            )

        else:
            return jsonify({"error": "Method not allowed"}), 405

        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request to Django API failed: {str(e)}"}), 500

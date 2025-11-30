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



@stock_master_bp.route("/api/stock-master/<string:stock_id>/", methods=["GET", "PUT", "DELETE"])
def stockitem_by_id(stock_id):
    tenant_id = get_tenant_id()
    if not tenant_id:
        return jsonify({"error": "Missing tenant_id"}), 400

    headers = {"X-Tenant-ID": tenant_id}

    try:
        if request.method == "GET":
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/stock-master/item/{stock_id}/",
                headers=headers
            )

        else:
            return jsonify({"error": "Method not allowed"}), 405

        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request to Django API failed: {str(e)}"}), 500
